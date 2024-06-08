from django import template
from django.template import Node
from django.template.loader import render_to_string


def cotton_component(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]
    template_path = bits[1]
    component_key = bits[2]

    kwargs = {}
    for bit in bits[3:]:
        key, value = bit.split("=")
        if key.startswith(":"):  # Detect variables
            key = key[1:]  # Remove ':' prefix
            value = value.strip("'\"")  # Remove quotes
            kwargs[key] = template.Variable(value)  # Treat as a variable
        else:
            kwargs[key] = value.strip("'\"")  # Treat as a literal string

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
            if isinstance(value, template.Variable):  # Resolve variables
                try:
                    resolved_value = value.resolve(context)
                    attrs[key] = resolved_value
                except template.VariableDoesNotExist:
                    pass  # Handle variable not found, if necessary
            else:
                attrs[key] = value  # Use literal string

        # Add the remainder as the default slot
        rendered = self.nodelist.render(context)
        local_context.update({"slot": rendered})

        slots = context.get("cotton_slots", {})
        component_slots = slots.get(self.component_key, {})

        local_context.update(component_slots)
        local_context.update(attrs)
        local_context.update({"attrs_dict": attrs})

        rendered = render_to_string(self.template_path, local_context)

        # Now reset the component's slots in context to prevent bleeding
        if self.component_key in slots:
            slots[self.component_key] = {}

        context.update({"cotton_slots": slots})

        return rendered
