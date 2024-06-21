import ast

from django import template
from django.template import Node
from django.template.loader import render_to_string


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
                key = key[1:]  # Remove ':' prefix
                attrs[key] = self.process_dynamic_attribute(value, context)
            elif value == "":
                attrs[key] = True
            else:
                attrs[key] = value

        # Add the remainder as the default slot
        rendered = self.nodelist.render(context)
        local_context.update({"slot": rendered})

        # Merge slots and attributes into the local context
        slots = context.get("cotton_slots", {})
        component_slots = slots.get(self.component_key, {})
        local_context.update(component_slots)
        local_context.update(attrs)
        local_context.update({"attrs_dict": attrs})

        rendered = render_to_string(self.template_path, local_context)

        # Reset the component's slots in context to prevent bleeding
        if self.component_key in slots:
            slots[self.component_key] = {}
        context.update({"cotton_slots": slots})

        return rendered

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

        # Evaluate literal string or pass back raw value
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
