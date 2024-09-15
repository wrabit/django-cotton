from django.template import Library
from django.template.base import (
    Node,
    TemplateSyntaxError,
)
from django.utils.safestring import mark_safe

from django_cotton.templatetags import UnprocessableDynamicAttr, DynamicAttr
from django_cotton.utils import get_cotton_data

register = Library()


def cotton_attr(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) < 1:
        raise TemplateSyntaxError("cotton complex-attr must include a 'name'")

    nodelist = parser.parse(("endattr",))
    parser.delete_first_token()
    return ComplexAttrNode(bits[0], nodelist)


class ComplexAttrNode(Node):
    def __init__(self, attr_name, nodelist):
        self.attr_name = attr_name
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            if self.attr_name.startswith(":"):
                key = self.attr_name[1:]
                try:
                    cotton_data["stack"][-1]["attrs"][key] = DynamicAttr(content).resolve(context)
                except UnprocessableDynamicAttr:
                    cotton_data["stack"][-1]["attrs"].unprocessable(key)
            else:
                # just template partial
                cotton_data["stack"][-1]["attrs"][self.attr_name] = mark_safe(content)
        return ""
