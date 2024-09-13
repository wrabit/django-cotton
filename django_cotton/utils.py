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
        if value.startswith('{"') and value.endswith('}'):
            return f"'{value}'"  # use single quotes for json-like strings
        elif value.startswith('"') and value.endswith('"'):
            return value  # already quoted
    return f'"{value}"'  # default to double quotes
