from django import template
from django.utils.html import format_html_join

from django_cotton.templatetags._component import cotton_component
from django_cotton.templatetags._vars import cotton_cvars
from django_cotton.templatetags._slot import cotton_slot
from django_cotton.templatetags._attr import cotton_attr

register = template.Library()
register.tag("c", cotton_component)
register.tag("slot", cotton_slot)
register.tag("vars", cotton_cvars)
register.tag("attr", cotton_attr)


@register.filter
def merge(attrs, args):
    # attrs is expected to be a dictionary of existing attributes
    # args is a string of additional attributes to merge, e.g., "class:extra-class"
    for arg in args.split(","):
        key, value = arg.split(":", 1)
        if key in attrs:
            attrs[key] = value + " " + attrs[key]
        else:
            attrs[key] = value
    return format_html_join(" ", '{0}="{1}"', attrs.items())


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
