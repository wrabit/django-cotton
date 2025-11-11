from typing import List

from django.template.base import (
    Variable,
    VariableDoesNotExist,
    Node,
    Template,
)

from django_cotton.templatetags import (
    DynamicAttr,
    UnprocessableDynamicAttr,
    Attrs,
    strip_quotes_safely,
)
from django_cotton.utils import get_cotton_data


class CottonVarsNode(Node):
    def __init__(self, var_dict, empty_vars: List, loaded_libraries: List[str]):
        self.var_dict = var_dict
        self.empty_vars = empty_vars
        self.loaded_libraries = loaded_libraries

    def extract_vars(self, context, attrs, slots):
        """Extract and process vars, returning a dict of resolved values."""
        vars = {}

        for key, value in self.var_dict.items():
            key_to_exclude = key
            if key not in attrs.exclude_unprocessable():
                if key.startswith(":"):
                    key_to_exclude = key[1:]
                    if key_to_exclude not in slots:
                        try:
                            # Convert hyphens to underscores for template accessibility
                            accessible_key = key_to_exclude.replace("-", "_")
                            vars[accessible_key] = DynamicAttr(value, is_cvar=True).resolve(context)
                        except UnprocessableDynamicAttr:
                            pass
                else:
                    # Static attribute - check if it contains template syntax
                    if key not in slots:
                        # If value contains template tags or variables, evaluate it at render time
                        if "{{" in value or "{%" in value:
                            try:
                                # Prepend {% load %} tags for libraries that were loaded at parse time
                                load_tags = [f"{{% load {lib} %}}" for lib in self.loaded_libraries]
                                template_str = "".join(load_tags) + value

                                mini_template = Template(template_str)
                                rendered_value = mini_template.render(context)
                                # Convert hyphens to underscores for template accessibility
                                accessible_key = key_to_exclude.replace("-", "_")
                                vars[accessible_key] = rendered_value
                            except Exception:
                                # If rendering fails, fall back to the raw value
                                # Convert hyphens to underscores for template accessibility
                                accessible_key = key_to_exclude.replace("-", "_")
                                vars[accessible_key] = value
                        else:
                            # Plain static value
                            # Convert hyphens to underscores for template accessibility
                            accessible_key = key_to_exclude.replace("-", "_")
                            vars[accessible_key] = value
            attrs.exclude_from_string_output(key_to_exclude)

        # Process cvars without values
        for empty_var in self.empty_vars:
            attrs.exclude_from_string_output(empty_var)

        return vars

    def render(self, context):
        # When rendered standalone (not as part of a component extraction),
        # inject vars into the context
        cotton_data = get_cotton_data(context)

        # If there's a component on the stack, vars will be extracted by the component
        # So we only need to inject if we're rendering standalone
        if not cotton_data["stack"]:
            # Standalone rendering - inject vars into context
            attrs = Attrs({})
            slots = {}
            vars = self.extract_vars(context, attrs, slots)
            context.update(vars)

        # Vars node itself doesn't render anything
        return ""


def cotton_cvars(parser, token):
    """
    Parse standalone cotton:vars template tag using a custom character-by-character parser.

    This allows template tags like {% trans %} to work in cotton:vars defaults:
        {% cotton:vars label="{% trans 'Loading' %}" %}

    The custom parser treats quoted strings as atomic units, preserving
    template tags inside them for Django to evaluate naturally at render time.
    """
    from django_cotton.tag_parser import parse_vars_tag

    # Use the custom parser that handles quoted strings properly
    result = parse_vars_tag(token.contents)

    # Strip quotes from all values (parser returns them with quotes)
    var_dict = {k: strip_quotes_safely(v) for k, v in result.attrs.items()}

    # Capture which template libraries were loaded at parse time
    loaded_libraries = []
    if hasattr(parser, 'libraries'):
        # parser.libraries is a dict with library names (strings) as keys
        loaded_libraries = list(parser.libraries.keys())

    return CottonVarsNode(var_dict, result.empty_attrs, loaded_libraries)
