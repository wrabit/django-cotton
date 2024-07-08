import os
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.tag(name="escape")
def do_escape(parser, token):
    nodelist = parser.parse(("endescape",))
    parser.delete_first_token()
    return EscapeNode(nodelist)


class EscapeNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return escape(output)


@register.filter
def env(key):
    return mark_safe(os.environ.get(key, ""))
