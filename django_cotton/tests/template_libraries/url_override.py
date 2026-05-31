from django import template


register = template.Library()


@register.simple_tag(name="url")
def override_url(view_name, *args, **kwargs):
    """Test helper that intentionally shadows Django's built-in url tag."""
    return f"/override/{view_name}/"
