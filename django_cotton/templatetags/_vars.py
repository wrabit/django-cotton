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
    def __init__(self, var_dict, empty_vars: List, nodelist, loaded_libraries: List[str]):
        self.var_dict = var_dict
        self.empty_vars = empty_vars
        self.nodelist = nodelist
        self.loaded_libraries = loaded_libraries

    def render(self, context):
        cotton_data = get_cotton_data(context)

        if cotton_data["stack"]:
            current_component = cotton_data["stack"][-1]
            attrs = current_component["attrs"]
            slots = current_component.get("slots", {})
        else:
            attrs = Attrs({})
            slots = {}

        vars = {}

        for key, value in self.var_dict.items():
            key_to_exclude = key
            if key not in attrs.exclude_unprocessable():
                if key.startswith(":"):
                    key_to_exclude = key[1:]
                    if key_to_exclude not in slots:
                        try:
                            vars[key_to_exclude] = DynamicAttr(value, is_cvar=True).resolve(context)
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

                                # Create a mini-template and render it in the current context
                                mini_template = Template(template_str)
                                rendered_value = mini_template.render(context)
                                attrs[key] = rendered_value
                            except Exception:
                                # If rendering fails, fall back to the raw value
                                attrs[key] = value
                        else:
                            # Plain static value
                            attrs[key] = value
            attrs.exclude_from_string_output(key_to_exclude)

        # Process cvars without values
        for empty_var in self.empty_vars:
            attrs.exclude_from_string_output(empty_var)

        with context.push({**vars, **attrs.make_attrs_accessible(), "attrs": attrs}):
            output = self.nodelist.render(context)

        return output


def cotton_cvars(parser, token):
    """
    Parse c-vars template tag using a custom character-by-character parser.

    This allows template tags like {% trans %} to work in c-vars defaults:
        {% vars label="{% trans 'Loading' %}" %}

    The custom parser treats quoted strings as atomic units, preserving
    template tags inside them for Django to evaluate naturally at render time.
    """
    from django_cotton.tag_parser import parse_vars_tag

    # Use the custom parser that handles quoted strings properly
    var_dict, empty_vars = parse_vars_tag(token.contents)

    # Strip quotes from all values (parser returns them with quotes)
    var_dict = {k: strip_quotes_safely(v) for k, v in var_dict.items()}

    # Capture which template libraries were loaded at parse time
    loaded_libraries = []
    if hasattr(parser, 'libraries'):
        # parser.libraries is a dict with library names (strings) as keys
        loaded_libraries = list(parser.libraries.keys())

    nodelist = parser.parse(("endvars",))
    parser.delete_first_token()

    return CottonVarsNode(var_dict, empty_vars, nodelist, loaded_libraries)
