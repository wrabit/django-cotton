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


def render_component(component_path, context=None, request=None):
    """
    Render a Cotton component from a view with context values provided as attributes so component behaviour is normal.
    """
    from django.template import Context, RequestContext, Template

    context = context or {}

    # Convert dotted notation to template path if needed
    if not component_path.endswith(".html"):
        # Convert "ui.button" to "cotton/ui/button.html"
        component_path = f"cotton/{component_path.replace('.', '/')}.html"

    # Extract component name for the wrapper (e.g., "cotton/ui/button.html" -> "ui.button")
    component_name = component_path.replace("cotton/", "").replace(".html", "").replace("/", ".")

    # Build attribute string with dynamic bindings for context values
    attrs_parts = []
    for key in context.keys():
        # Skip special Django/request variables
        if key in ("request", "csrf_token", "messages", "perms", "user"):
            continue

        # Use dynamic attribute syntax (:key="key") to provide context variables
        attrs_parts.append(f':{key}="{key}"')

    attrs_str = " ".join(attrs_parts)
    template_str = f"""{{% cotton {component_name.replace(".", "-")} {attrs_str} / %}}"""
    component_template = Template(template_str)

    if request:
        ctx = RequestContext(request, context)
    else:
        ctx = Context(context)

    # Initialize cotton_data
    get_cotton_data(ctx)

    return component_template.render(ctx)
