import json
import os
from django import template
from django.utils.safestring import mark_safe
from docs_project.utils.syntax_formatter import compile_to_template_tags

register = template.Library()


@register.filter
def env(key):
    return mark_safe(os.environ.get(key, ""))


@register.filter
def json_dumps(value):
    return json.dumps(value)


@register.filter("startswith")
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter
def json_encode(value):
    return mark_safe(json.dumps(value))


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
