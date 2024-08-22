import ast

from django import template
from django.template import Node
from django.utils.safestring import mark_safe
from django.template.loader import get_template

from django_cotton.utils import ensure_quoted


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
        try:
            key, value = bit.split("=")
        except ValueError:
            # No value provided, assume boolean attribute
            key = bit
            value = ""

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
        attrs = self._build_attrs(context)

        # Add the remainder as the default slot
        local_ctx = context.flatten()
        local_ctx["slot"] = self.nodelist.render(context)

        # Merge slots and attributes into the local context
        all_named_slots_ctx = context.get("cotton_named_slots", {})
        local_named_slots_ctx = all_named_slots_ctx.get(self.component_key, {})
        local_ctx.update(local_named_slots_ctx)

        # We need to check if any dynamic attributes are present in the component slots and move them over to attrs
        if "ctn_template_expression_attrs" in local_named_slots_ctx:
            for expression_attr in local_named_slots_ctx["ctn_template_expression_attrs"]:
                attrs[expression_attr] = local_named_slots_ctx[expression_attr]

        # Build attrs string before formatting any '-' to '_' in attr names
        attrs_string = " ".join(f"{key}={ensure_quoted(value)}" for key, value in attrs.items())
        local_ctx["attrs"] = mark_safe(attrs_string)
        local_ctx["attrs_dict"] = attrs

        # Store attr names in a callable format, i.e. 'x-init' will be accessible by {{ x_init }}
        attrs = {key.replace("-", "_"): value for key, value in attrs.items()}
        local_ctx.update(attrs)

        # Reset the component's slots in context to prevent data leaking between components
        all_named_slots_ctx[self.component_key] = {}

        return get_template(self.template_path).render(local_ctx)

    def _build_attrs(self, context):
        """
        Build the attributes dictionary for the component
        """
        attrs = {}

        for key, value in self.kwargs.items():
            # strip single or double quotes only if both sides have them
            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            if key.startswith(":"):
                key = key[1:]
                attrs[key] = self._process_dynamic_attribute(value, context)
            elif value == "":
                attrs[key] = True
            else:
                attrs[key] = value

        return attrs

    def _process_dynamic_attribute(self, value, context):
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
