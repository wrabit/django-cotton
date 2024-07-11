import ast
from functools import lru_cache

from django import template
from django.conf import settings
from django.template import Node
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted


@lru_cache(maxsize=1024)
def get_cached_template(template_name):
    """App runtime cache for cotton templates. Turned on only when DEBUG=False."""
    return get_template(template_name)


def render_template(template_name, context):
    if settings.DEBUG:
        return get_template(template_name).render(context)
    else:
        return get_cached_template(template_name).render(context)


def cotton_component(parser, token):
    """
    Template tag to render a cotton component with dynamic attributes.

    Usage:
        {% cotton_component 'template_path' 'component_key' key1="value1" :key2="dynamic_value" %}
    """
    bits = token.split_contents()
    template_path = bits[1]
    component_key = bits[2]

    kwargs = {}
    for bit in bits[3:]:
        key, value = bit.split("=")
        kwargs[key] = value

    nodelist = parser.parse(("end_cotton_component",))
    parser.delete_first_token()

    return CottonComponentNode(nodelist, template_path, component_key, kwargs)


class CottonComponentNode(Node):
    def __init__(self, nodelist, template_path, component_key, kwargs):
        self.nodelist = nodelist
        self.template_path = template_path
        self.component_key = component_key
        self.kwargs = kwargs

    def render(self, context):
        local_ctx = context.flatten()
        attrs = {}

        for key, value in self.kwargs.items():
            value = value.strip("'\"")

            if key.startswith(":"):
                key = key[1:]
                attrs[key] = self.process_dynamic_attribute(value, context)
            elif value == "":
                attrs[key] = True
            else:
                attrs[key] = value

        # Add the remainder as the default slot
        local_ctx["slot"] = self.nodelist.render(context)

        # Merge slots and attributes into the local context
        all_slots_ctx = context.get("cotton_slots", {})
        component_slots_ctx = all_slots_ctx.get(self.component_key, {})
        local_ctx.update(component_slots_ctx)

        # We need to check if any dynamic attributes are present in the component slots and move them over to attrs
        if "ctn_template_expression_attrs" in component_slots_ctx:
            for expression_attr in component_slots_ctx["ctn_template_expression_attrs"]:
                attrs[expression_attr] = component_slots_ctx[expression_attr]

        # Build attrs string before formatting any '-' to '_' in attr names
        attrs_string = " ".join(
            f"{key}={ensure_quoted(value)}" for key, value in attrs.items()
        )
        local_ctx["attrs"] = mark_safe(attrs_string)

        # Make the attrs available in the context for the vars frame, also before formatting the attr names
        local_ctx["attrs_dict"] = attrs

        # Store attr names in a callable format, i.e. 'x-init' will be accessible by {{ x_init }}
        attrs = {key.replace("-", "_"): value for key, value in attrs.items()}
        local_ctx.update(attrs)

        # Reset the component's slots in context to prevent data leaking between components
        all_slots_ctx[self.component_key] = {}

        return render_template(self.template_path, local_ctx)

    def process_dynamic_attribute(self, value, context):
        """
        Process a dynamic attribute (prefixed with ":")
        """
        # Template variable
        try:
            return template.Variable(value).resolve(context)
        except template.VariableDoesNotExist:
            pass

        # Boolean attribute
        if value == "":
            return True

        # String literal
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
