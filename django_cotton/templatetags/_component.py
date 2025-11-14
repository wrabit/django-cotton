import functools
from typing import Union

from django.conf import settings
from django.template import Library, TemplateDoesNotExist
from django.template.base import (
    Node,
    Template,
)
from django.template.context import Context, RequestContext
from django.template.loader import get_template

from django_cotton.utils import get_cotton_data
from django_cotton.exceptions import CottonIncompleteDynamicComponentError
from django_cotton.templatetags import Attrs, DynamicAttr, UnprocessableDynamicAttr, strip_quotes_safely

register = Library()


class CottonComponentNode(Node):
    def __init__(self, component_name, nodelist, attrs, only, loaded_libraries=None):
        self.component_name = component_name
        self.nodelist = nodelist
        self.attrs = attrs
        self.template_cache = {}
        self.only = only
        self.loaded_libraries = loaded_libraries or []

    def render(self, context):
        cotton_data = get_cotton_data(context)

        # Push a new component onto the stack
        component_data = {
            "key": self.component_name,
            "attrs": Attrs({}),
            "slots": {},
        }
        cotton_data["stack"].append(component_data)

        # Process simple attributes and boolean attributes
        for key, value in self.attrs.items():
            value = strip_quotes_safely(value)
            if value is True:  # Boolean attribute
                component_data["attrs"][key] = True
            elif key.startswith("::"):  # Escaping 1 colon e.g for shorthand alpine
                key = key[1:]
                component_data["attrs"][key] = value
            elif key.startswith(":"):
                key = key[1:]
                try:
                    resolved_value = DynamicAttr(value).resolve(context)
                except UnprocessableDynamicAttr:
                    component_data["attrs"].unprocessable(key)
                else:
                    # Handle ":attrs" specially
                    if key == "attrs":
                        component_data["attrs"].dict.update(resolved_value)
                    else:
                        component_data["attrs"][key] = resolved_value
            else:
                # Static attribute - check if it contains template syntax
                if isinstance(value, str) and ("{{" in value or "{%" in value):
                    try:
                        # Evaluate template tags at render time (same as c-vars)
                        # Prepend {% load %} tags for libraries that were loaded at parse time
                        load_tags = [f"{{% load {lib} %}}" for lib in self.loaded_libraries]
                        template_str = "".join(load_tags) + value
                        mini_template = Template(template_str)
                        rendered_value = mini_template.render(context)
                        component_data["attrs"][key] = rendered_value
                    except Exception:
                        # If rendering fails, fall back to the raw value
                        component_data["attrs"][key] = value
                else:
                    component_data["attrs"][key] = value

        # Render the nodelist to process any slot tags and vars
        default_slot = self.nodelist.render(context)

        # Load the component template first
        template = self._get_cached_template(context, component_data["attrs"])

        # Extract vars from the component template
        vars = self._extract_vars_from_template(
            template, context, component_data["attrs"], component_data["slots"]
        )

        # Prepare the cotton-specific data
        # Vars go first so component attrs can override them
        component_state = {
            **vars,
            **component_data["slots"],
            **component_data["attrs"].make_attrs_accessible(),
            "attrs": component_data["attrs"],
            "slot": default_slot,
            "cotton_data": cotton_data,
        }

        if self.only:
            # Complete isolation
            output = template.render(Context(component_state))
        else:
            if getattr(settings, "COTTON_ENABLE_CONTEXT_ISOLATION", False) is True:
                # Default - partial isolation
                new_context = self._create_partial_context(context, component_state)
                output = template.render(new_context)
            else:
                # Legacy - no isolation
                with context.push(component_state):
                    output = template.render(context)

        cotton_data["stack"].pop()

        return output

    def _get_cached_template(self, context, attrs):
        cache = context.render_context.get(self)
        if cache is None:
            cache = context.render_context[self] = {}

        template_path = self._generate_component_template_path(self.component_name, attrs.get("is"))

        if template_path in cache:
            return cache[template_path]

        # Try to get the primary template
        try:
            template = get_template(template_path)
            if hasattr(template, "template"):
                template = template.template
            cache[template_path] = template
            return template
        except TemplateDoesNotExist:
            # If the primary template doesn't exist, try the fallback path (index.html)
            fallback_path = template_path.rsplit(".html", 1)[0] + "/index.html"

            # Check if the fallback template is already cached
            if fallback_path in cache:
                return cache[fallback_path]

            # Try to get the fallback template
            template = get_template(fallback_path)
            if hasattr(template, "template"):
                template = template.template
            cache[fallback_path] = template
            return template

    def _create_partial_context(self, original_context, component_state):
        # Get the request object from the original context
        request = original_context.get("request")

        if request:
            # Create a new RequestContext
            new_context = RequestContext(request)

            # Add the component_state to the new context
            new_context.update(component_state)
        else:
            # If there's no request object, create a simple Context
            new_context = Context(component_state)

        return new_context

    def _extract_vars_from_template(self, template, context, attrs, slots):
        """Extract vars from any CottonVarsNode instances in the template."""
        from django_cotton.templatetags._vars import CottonVarsNode

        vars = {}

        # Walk the template nodelist to find CottonVarsNode instances
        for node in template.nodelist:
            if isinstance(node, CottonVarsNode):
                # Extract vars from this node
                node_vars = node.extract_vars(context, attrs, slots)
                vars.update(node_vars)

        return vars

    @staticmethod
    @functools.lru_cache(maxsize=400)
    def _generate_component_template_path(component_name: str, is_: Union[str, None]) -> str:
        """Generate the path to the template for the given component name."""
        if component_name == "component":
            if is_ is None:
                raise CottonIncompleteDynamicComponentError(
                    'Cotton error: "<c-component>" should be accompanied by an "is" attribute.'
                )
            component_name = is_

        component_tpl_path = component_name.replace(".", "/")

        # Cotton by default will look for snake_case version of comp names. This can be configured to allow hyphenated names.
        snaked_cased_named = getattr(settings, "COTTON_SNAKE_CASED_NAMES", True)
        if snaked_cased_named:
            component_tpl_path = component_tpl_path.replace("-", "_")

        cotton_dir = getattr(settings, "COTTON_DIR", "cotton")
        return f"{cotton_dir}/{component_tpl_path}.html"

def cotton_component(parser, token):
    """
    Parse a cotton component tag and return a CottonComponentNode.

    Uses custom parser to preserve quotes and handle template tags in attributes.
    Supports self-closing syntax: {% cotton name /%} or {% cotton name / %}
    """
    from django_cotton.tag_parser import parse_component_tag
    from django.template import NodeList

    # Check if this is a self-closing tag
    is_self_closing = token.contents.rstrip().endswith('/') or token.contents.rstrip().endswith(' /')

    # Use the custom parser that preserves quotes and handles nested template tags
    result = parse_component_tag(token.contents)

    # Capture which template libraries were loaded at parse time
    loaded_libraries = list(parser.libraries.keys()) if hasattr(parser, 'libraries') else []

    if is_self_closing:
        # Self-closing tag has no content
        nodelist = NodeList()
    else:
        nodelist = parser.parse(("endcotton",))
        parser.delete_first_token()

    return CottonComponentNode(result.name, nodelist, result.attrs, result.only, loaded_libraries)
