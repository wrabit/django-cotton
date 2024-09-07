from django import template
from django.utils.safestring import mark_safe


def cotton_slot(parser, token):
    """
    Template tag to render a cotton slot.
    is_expression_attr: bool whether we are using the named_slot as an "expression attribute" or not.
        expression attributes are from the use of native tags {{ {% and \n newlines within the attribute. We put them
        through as a named slot so they can be rendered and provided as a template variable
    """
    try:
        tag_name, slot_name, component_key, *optional = token.split_contents()
        is_expression_attr = optional[0] if optional else None
    except ValueError:
        raise template.TemplateSyntaxError("incomplete c-slot %r" % token.contents)

    nodelist = parser.parse(("end_cotton_slot",))
    parser.delete_first_token()
    return CottonSlotNode(slot_name, nodelist, component_key, is_expression_attr)


class CottonSlotNode(template.Node):
    def __init__(self, slot_name, nodelist, component_key, is_expression_attr):
        self.nodelist = nodelist
        self.slot_name = slot_name
        self.component_key = component_key
        self.is_expression_attr = is_expression_attr

    def render(self, context):
        output = self.nodelist.render(context)
        cotton_named_slots = context.setdefault("cotton_named_slots", {})
        component_slots = cotton_named_slots.setdefault(self.component_key, {})
        component_slots[self.slot_name] = mark_safe(output)

        # If the slot is being used to hold an expression attribute, we record it so it
        # can be transferred to attrs in the component
        if self.is_expression_attr:
            component_slots = context["cotton_named_slots"][self.component_key]
            expression_attrs = component_slots.setdefault("ctn_template_expression_attrs", [])
            expression_attrs.append(self.slot_name)

        return ""
