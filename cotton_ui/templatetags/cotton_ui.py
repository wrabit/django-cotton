"""Template tags and filters for Cotton UI components."""

import json
from urllib.parse import quote

from django import template

register = template.Library()


@register.filter
def json_dumps(value):
    """
    Serialize value to JSON and URL-encode for safe embedding in HTML attributes.

    Used by components like combobox that need to pass Python data structures
    to Alpine.js via HTML attributes.

    Usage:
        {{ my_list|json_dumps }}
    """
    return quote(json.dumps(value))
