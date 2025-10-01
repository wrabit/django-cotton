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
    """Ensure cotton specific state is available on the current context."""

    if "cotton_data" not in context:
        context["cotton_data"] = {"stack": [], "vars": {}}

    cotton_data = context["cotton_data"]

    # Ensure push stack bookkeeping is always present.
    cotton_data.setdefault("push_stacks", {})
    cotton_data.setdefault("stack_placeholders", [])

    request = context.get("request")
    if request is not None:
        # Expose the same dictionary on the request so middleware can post-process the response.
        setattr(request, "_cotton_stack_state", cotton_data)

    return cotton_data
