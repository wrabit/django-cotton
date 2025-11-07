import os
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from docs_project.utils.syntax_formatter import compile_to_template_tags

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


@register.filter
def to_template_tags(value):
    """
    Convert Cotton HTML syntax to template tag syntax.
    Used for dual-syntax documentation display.
    Returns the compiled code as a plain string (not mark_safe) so it can be escaped.
    """
    compiled = compile_to_template_tags(value)
    # Return as plain string so force_escape can work on it
    return compiled
