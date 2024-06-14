from django import template
from django.utils.safestring import mark_safe


def cotton_slot(parser, token):
    try:
        tag_name, slot_name, component_key = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("incomplete c-slot %r" % token.contents)

    nodelist = parser.parse(("end_cotton_slot",))
    parser.delete_first_token()
    return CottonSlotNode(slot_name, nodelist, component_key)


class CottonSlotNode(template.Node):
    def __init__(self, slot_name, nodelist, component_key):
        self.slot_name = slot_name
        self.nodelist = nodelist
        self.component_key = component_key

    def render(self, context):
        # Add the rendered content to the context.
        if "cotton_slots" not in context:
            context.update({"cotton_slots": {}})

        output = self.nodelist.render(context)

        if self.component_key not in context["cotton_slots"]:
            context["cotton_slots"][self.component_key] = {}

        context["cotton_slots"][self.component_key][self.slot_name] = mark_safe(output)

        return ""
