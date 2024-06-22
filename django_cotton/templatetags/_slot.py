from django import template
from django.utils.safestring import mark_safe


def cotton_slot(parser, token):
    """
    Template tag to render a cotton slot.
    is_expression_attr: bool whether the attribute is dynamic or not.
        dynamic attributes are from the use of native tags {{ {% in the component attribute. We put them through as a named
        slot so they can be rendered and provided as a template variable
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
        self.slot_name = slot_name
        self.nodelist = nodelist
        self.component_key = component_key
        self.is_expression_attr = is_expression_attr

    def render(self, context):
        # Add the rendered content to the context.
        if "cotton_slots" not in context:
            context.update({"cotton_slots": {}})

        output = self.nodelist.render(context)

        # Store the slot data in a component-namespaced dictionary
        if self.component_key not in context["cotton_slots"]:
            context["cotton_slots"][self.component_key] = {}

        context["cotton_slots"][self.component_key][self.slot_name] = mark_safe(output)

        # If the slot is a dynamic attribute, we record it so it can be transferred to attrs in the component
        if self.is_expression_attr:
            if (
                "ctn_template_expression_attrs"
                not in context["cotton_slots"][self.component_key]
            ):
                context["cotton_slots"][self.component_key][
                    "ctn_template_expression_attrs"
                ] = []

            context["cotton_slots"][self.component_key][
                "ctn_template_expression_attrs"
            ].append(self.slot_name)

        return ""
