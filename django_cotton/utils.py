import ast


def eval_string(value):
    """
    Evaluate a string representation of a constant, list, or dictionary to the actual Python object.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def ensure_quoted(value):
    if isinstance(value, str):
        if value.startswith('{"') and value.endswith("}"):
            return f"'{value}'"  # use single quotes for json-like strings
        elif value.startswith('"') and value.endswith('"'):
            return value  # already quoted
    return f'"{value}"'  # default to double quotes


def get_cotton_data(context):
    if "cotton_data" not in context:
        context["cotton_data"] = {"stack": [], "vars": {}}
    return context["cotton_data"]


def render_component(request, component_name, context=None, **kwargs):
    """
    Render a Cotton component from a view with context values passed as attributes.

    This helper allows you to render Cotton components programmatically from views,
    which is especially useful for HTMX partial responses. The signature matches
    Django's render() convention: render_component(request, component_name, context).

    Args:
        request: HttpRequest object (required, like Django's render())
        component_name: Component name using dots for folder nesting and hyphens for
                       underscores in filenames (e.g., "ui.button" -> cotton/ui/button.html,
                       "settings.user-row" -> cotton/settings/user_row.html)
        context: Dictionary of data to pass to the component as attributes
        **kwargs: Alternative way to pass component attributes

    Returns:
        Rendered HTML string

    Example:
        # Simple component: cotton/button.html
        render_component(request, "button", {"label": "Click me"})

        # Nested component: cotton/ui/button.html
        render_component(request, "ui.button", {"label": "Click me"})

        # Nested with hyphen (cotton/settings/user_row.html)
        render_component(request, "settings.user-row", {"user": user})

        # Using kwargs
        render_component(request, "button", label="Click me", pk=123)

        # Mix dict and kwargs
        render_component(request, "user-card", {"user": user}, extra_class="highlight")
    """
    from django.template import RequestContext, Template

    # Merge context dict and kwargs
    if context is None:
        context = kwargs
    elif kwargs:
        context = {**context, **kwargs}
    else:
        context = dict(context)  # Make a copy to avoid mutating original

    # Build minimal template using :attrs to pass all attributes at once
    # Note: Keep dots in component_name for folder nesting (e.g., "ui.button" -> cotton/ui/)
    # Cotton's template tag handles the path resolution correctly
    template_str = f'{{% cotton {component_name} :attrs="cotton_component_attrs" / %}}'
    template = Template(template_str)

    # Prepare render context (keep original context plus our attrs dict)
    render_context = {**context, "cotton_component_attrs": context}

    # Create RequestContext (request is now always provided)
    ctx = RequestContext(request, render_context)

    return template.render(ctx)
