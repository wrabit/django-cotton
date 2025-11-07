"""
Utilities for formatting Cotton template tag syntax for documentation display.
"""
import re
from django_cotton.compiler_regex import CottonCompiler


def compile_to_template_tags(html_code):
    """
    Convert Cotton HTML syntax to template tag syntax using Cotton's compiler.
    Post-processes the output for better readability.

    Args:
        html_code: HTML-style Cotton code (e.g., '<c-button>Click</c-button>')

    Returns:
        Formatted template tag syntax (e.g., '{% c button %}Click{% endc %}')
    """
    try:
        # Run through Cotton's compiler
        compiler = CottonCompiler()
        compiled = compiler.process(html_code)

        # Format for readability
        formatted = format_template_output(compiled)

        return formatted
    except Exception as e:
        # If compilation fails, return error message for debugging
        return f"<!-- Compilation error: {str(e)} -->\n{html_code}"


def format_template_output(compiled_code):
    """
    Clean and format compiled template tag output for documentation display.

    - Normalizes whitespace
    - Ensures consistent indentation
    - Removes excessive blank lines
    - Standardizes quote usage
    """
    # Remove excessive blank lines (more than 2 consecutive)
    formatted = re.sub(r'\n{3,}', '\n\n', compiled_code)

    # Normalize spaces around template tags
    # Add newlines after closing tags if followed by opening tag
    formatted = re.sub(r'(%})\s*({%)', r'\1\n\2', formatted)

    # Clean up whitespace at start and end
    formatted = formatted.strip()

    # Preserve intentional indentation by detecting common indent level
    lines = formatted.split('\n')
    if lines:
        # Find minimum indentation (excluding empty lines)
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if indents:
            min_indent = min(indents)
            # Remove common leading indentation
            if min_indent > 0:
                formatted = '\n'.join(
                    line[min_indent:] if len(line) > min_indent else line
                    for line in lines
                )

    return formatted
