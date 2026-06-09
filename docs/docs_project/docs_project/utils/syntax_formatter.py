"""
Utilities for formatting Cotton template tag syntax for documentation display.
"""
import re
from django_cotton.compiler_regex import CottonCompiler
from djlint.reformat import formatter


def compile_to_template_tags(html_code):
    """
    Convert Cotton HTML syntax to template tag syntax using Cotton's compiler.
    Preserves multi-line formatting from the original HTML.

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

        # The compiler emits the block form for self-closing components
        # ({% cotton x %}{% endcotton %}). Cotton's tag parser also accepts the
        # self-closing form ({% cotton x /%}), which is the cleaner native
        # equivalent, so collapse empty blocks back to it.
        compiled = collapse_self_closing(compiled)

        # Restore multi-line formatting from original HTML
        compiled = restore_multiline_formatting(compiled, html_code)

        return compiled
    except Exception as e:
        # If compilation fails, return error message for debugging
        return f"<!-- Compilation error: {str(e)} -->\n{html_code}"


def collapse_self_closing(compiled_code):
    """
    Collapse empty Cotton blocks to the self-closing tag form.

    Turns `{% cotton x attrs %}{% endcotton %}` into `{% cotton x attrs /%}`.
    Only fires when the opening tag's `%}` is immediately followed by
    `{% endcotton %}` (no content), so non-empty components are untouched. The
    `[^%]` class keeps the match inside a single tag and cannot span into
    another `{% ... %}`.

    Args:
        compiled_code: Compiled template tag code

    Returns:
        Code with empty blocks rewritten as self-closing tags
    """
    pattern = re.compile(r'\{%\s*cotton\s+([^%]*?)\s*%\}\{%\s*endcotton\s*%\}')
    return pattern.sub(lambda m: '{% cotton ' + m.group(1) + ' /%}', compiled_code)


def restore_multiline_formatting(compiled_code, original_html):
    """
    For each template tag, check if original HTML tag was multiline.
    If so, format the template tag as multiline too.

    Args:
        compiled_code: Compiled template tag code
        original_html: Original HTML code for reference

    Returns:
        Code with multi-line formatting restored
    """
    # Pattern to find Cotton template tag opening tags. Group 3 captures an
    # optional self-closing "/" so it can be preserved through reformatting.
    template_pattern = r'{%\s*cotton\s+([^\s%}]+)((?:\s+[^%}]+?)?)\s*(/?)%}'

    def format_if_multiline(match):
        component_name = match.group(1)
        attrs_string = match.group(2).strip()
        self_closing = bool(match.group(3))

        # Find corresponding HTML tag in original
        original_tag = find_original_tag(original_html, component_name, attrs_string)

        if original_tag and '\n' in original_tag:
            # Original was multiline - format as multiline
            return format_as_multiline_template_tag(
                component_name,
                attrs_string,
                original_tag,
                self_closing,
            )

        # Keep as is (single line)
        return match.group(0)

    return re.sub(template_pattern, format_if_multiline, compiled_code, flags=re.DOTALL)


def find_original_tag(original_html, component_name, attrs_string):
    """
    Find HTML tag in original that corresponds to this template tag.
    Use signature matching (component name + first attribute).

    Args:
        original_html: Original HTML code
        component_name: Component name (e.g., "ui.switch")
        attrs_string: Attribute string from template tag

    Returns:
        Matching HTML tag or None
    """
    # Extract first attribute for matching
    first_attr_match = re.search(r'(\S+?)\s*=\s*(["\'])([^"\']*)\2', attrs_string)

    if first_attr_match:
        attr_name = first_attr_match.group(1).lstrip(':')
        attr_value = first_attr_match.group(3)
        # Use [^>] (not .* with DOTALL) so a match cannot span across a tag
        # boundary into a later component. A multi-line opening tag has no '>'
        # until its end, so [^>] still matches genuinely multi-line tags while
        # preventing the value from being found in a different tag.
        html_pattern = rf'<c-{re.escape(component_name)}[^>]*?{re.escape(attr_name)}\s*=\s*["\'][^>]*?{re.escape(attr_value)}[^>]*?["\'][^>]*?/?>'
    else:
        html_pattern = rf'<c-{re.escape(component_name)}[^>]*?/?>'

    match = re.search(html_pattern, original_html)
    return match.group(0) if match else None


def format_as_multiline_template_tag(component_name, attrs_string, original_tag, self_closing=False):
    """
    Format template tag as multiline, preserving indentation from original.

    Args:
        component_name: Component name
        attrs_string: Attribute string
        original_tag: Original HTML tag for indentation reference
        self_closing: Whether the tag is self-closing (emit `/%}` instead of `%}`)

    Returns:
        Multi-line formatted template tag
    """
    closing = "/%}" if self_closing else "%}"

    # Extract base indentation from original
    indentation = extract_base_indentation(original_tag)
    attr_indent = indentation + "    "

    # Parse attributes
    attrs = parse_template_tag_attributes(attrs_string)

    if not attrs:
        return f"{{% cotton {component_name} {closing}}}" if self_closing else f"{{% cotton {component_name} %}}"

    # Build multiline
    lines = [f"{{% cotton {component_name}"]

    for attr_name, attr_value in attrs:
        if attr_value:
            lines.append(f"{attr_indent}{attr_name}={attr_value}")
        else:
            lines.append(f"{attr_indent}{attr_name}")

    lines.append(f"{indentation}{closing}")

    return '\n'.join(lines)


def extract_base_indentation(html_tag):
    """
    Extract base indentation from HTML tag.

    Args:
        html_tag: HTML tag to extract indentation from

    Returns:
        Base indentation string
    """
    lines = html_tag.split('\n')
    if len(lines) > 1:
        second_line = lines[1]
        match = re.match(r'^(\s+)', second_line)
        if match:
            full_indent = match.group(1)
            # Remove 4 spaces for attribute indent
            if len(full_indent) >= 4:
                return full_indent[:-4]
    return ""


def parse_template_tag_attributes(attrs_string):
    """
    Parse attributes from template tag.

    Args:
        attrs_string: Attribute string from template tag

    Returns:
        List of (name, value) tuples
    """
    from django_cotton.compiler_regex import Tag

    attrs = []
    for match in Tag.attr_pattern.finditer(attrs_string):
        key, quote, value, unquoted = match.groups()
        if value is not None:
            attrs.append((key, f'{quote}{value}{quote}'))
        elif unquoted is not None:
            attrs.append((key, unquoted))
        else:
            attrs.append((key, None))

    return attrs


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
