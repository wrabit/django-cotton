from django.template import Library
from django.template.base import (
    Node,
    TemplateSyntaxError,
)
from django.utils.safestring import mark_safe

from django_cotton.utils import get_cotton_data

register = Library()


def cotton_slot(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) < 1:
        raise TemplateSyntaxError("cotton slot tag must include a 'name'")

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return CottonSlotNode(bits[0], nodelist)


class CottonSlotNode(Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            cotton_data["stack"][-1]["slots"][self.slot_name] = mark_safe(content)
        else:
            raise TemplateSyntaxError("<slot /> tag must be used inside a component")
        return ""
