"""
Utilities for formatting Cotton template tag syntax for documentation display.
"""
import re
from django_cotton.compiler_regex import CottonCompiler
from djlint.reformat import formatter


def compile_to_template_tags(html_code):
    """
    Convert Cotton HTML syntax to template tag syntax using Cotton's compiler.
    Post-processes the output for better readability.

    Args:
        html_code: HTML-style Cotton code (e.g., '<c-button>Click</c-button>')

    Returns:
        Formatted template tag syntax (e.g., '{% cotton button %}Click{% endcotton %}')
    """
    try:
        # Check if there are any Cotton tags to convert
        has_cotton_tags = bool(re.search(r'<c-[a-zA-Z]', html_code))

        if not has_cotton_tags:
            # No Cotton tags - just format the HTML
            return format_template(html_code)

        # Run through Cotton's compiler
        compiler = CottonCompiler()
        compiled = compiler.process(html_code)

        # Format using djLint
        return format_template(compiled)
    except Exception as e:
        # If compilation fails, return error message for debugging
        return f"<!-- Compilation error: {str(e)} -->\n{html_code}"


def format_template(code):
    """
    Format template code using djLint.

    Args:
        code: Template code to format

    Returns:
        Formatted template code
    """
    try:
        # Use djLint formatter with Django profile
        formatted = formatter(
            code,
            profile="django",
            indent=4,
            preserve_blank_lines=True,
            max_line_length=120,
        )
        return formatted[0] if formatted else code
    except Exception:
        # If formatting fails, return original
        return code
