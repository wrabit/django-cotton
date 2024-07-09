import ast
from functools import lru_cache

from django import template
from django.template import Node
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted


@lru_cache(maxsize=128)
def get_cached_template(template_name):
    return get_template(template_name)


def render_template(template_name, context):
    template = get_cached_template(template_name)
    return template.render(context)


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
        local_context = context.flatten()
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
        local_context["slot"] = self.nodelist.render(context)

        # Merge slots and attributes into the local context
        all_slots = context.get("cotton_slots", {})
        component_slots = all_slots.get(self.component_key, {})
        local_context.update(component_slots)

        # We need to check if any dynamic attributes are present in the component slots and move them over to attrs
        if "ctn_template_expression_attrs" in component_slots:
            for expression_attr in component_slots["ctn_template_expression_attrs"]:
                attrs[expression_attr] = component_slots[expression_attr]

        # Build attrs string before formatting any '-' to '_' in attr names
        attrs_string = " ".join(
            f"{key}={ensure_quoted(value)}" for key, value in attrs.items()
        )
        local_context["attrs"] = mark_safe(attrs_string)

        # Make the attrs available in the context for the vars frame, also before formatting the attr names
        local_context["attrs_dict"] = attrs

        # Store attr names in a callable format, i.e. 'x-init' will be accessible by {{ x_init }} when called explicitly and not in {{ attrs }}
        attrs = {key.replace("-", "_"): value for key, value in attrs.items()}
        local_context.update(attrs)

        # Reset the component's slots in context to prevent bleeding into sibling components
        all_slots[self.component_key] = {}

        return render_template(self.template_path, local_context)

    def process_dynamic_attribute(self, value, context):
        """
        Process a dynamic attribute, resolving template variables and evaluating literals.
        """
        try:
            return template.Variable(value).resolve(context)
        except template.VariableDoesNotExist:
            pass

        # Check for boolean attribute
        if value == "":
            return True

        # It's not a template var or boolean attribute,
        # attempt to evaluate literal string or pass back raw value
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
