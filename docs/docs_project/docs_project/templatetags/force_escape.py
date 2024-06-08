from django import template
from django.utils.html import escape

register = template.Library()


def force_escape(value):
    return escape(value)


def strip(value):
    return value.strip()


register.filter("strip", strip)

register.filter("force_escape", force_escape)
