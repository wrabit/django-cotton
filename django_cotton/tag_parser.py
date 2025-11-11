"""
Parser for Cotton's native Django template tag syntax.

This module provides proper parsing of {% cotton %} and {% cotton:vars %} tags that handle quoted strings
as atomic units, allowing template tags and variables within attribute values.

Based on django-components' approach to handle complex attribute values.
"""
from typing import Dict, List, Tuple, Any, NamedTuple
from django.template.exceptions import TemplateSyntaxError


# Parsing delimiters
WHITESPACE = " \t\n"
ATTR_KEY_DELIMITERS = "= \t\n"  # Attribute keys stop at '=' or whitespace


class ComponentTagResult(NamedTuple):
    """Result of parsing a {% cotton %} tag."""

    name: str
    attrs: Dict[str, Any]
    only: bool


class VarsTagResult(NamedTuple):
    """Result of parsing a {% cotton:vars %} tag."""

    attrs: Dict[str, Any]
    empty_attrs: List[str]


def _skip_whitespace(tag_content: str, index: int) -> int:
    while index < len(tag_content) and tag_content[index] in WHITESPACE:
        index += 1
    return index


def _parse_component_name(tag_content: str, index: int) -> Tuple[str, int]:
    name_start = index
    while index < len(tag_content) and tag_content[index] not in WHITESPACE:
        index += 1
    return tag_content[name_start:index], index


def _parse_attribute_key(tag_content: str, index: int) -> Tuple[str, int]:
    key_start = index
    while index < len(tag_content) and tag_content[index] not in ATTR_KEY_DELIMITERS:
        index += 1
    return tag_content[key_start:index], index


def _parse_unquoted_value(tag_content: str, index: int) -> Tuple[str, int]:
    value_start = index
    while index < len(tag_content) and tag_content[index] not in WHITESPACE:
        index += 1
    return tag_content[value_start:index], index


def _skip_tag_name(tag_content: str, tag_name: str) -> int:
    """Skip tag name ('cotton' or 'cotton:vars') and return index after it."""
    tag_len = len(tag_name)
    if (
        tag_content.startswith(f"{tag_name} ")
        or tag_content.startswith(f"{tag_name}\t")
        or tag_content.startswith(f"{tag_name}\n")
    ):
        return tag_len + 1
    return tag_len


def _is_keyword_at_position(tag_content: str, index: int, keyword: str) -> bool:
    """Check if keyword appears at index as a whole word (not part of another word)."""
    end = index + len(keyword)
    if tag_content[index:end] == keyword:
        return end >= len(tag_content) or tag_content[end] in WHITESPACE
    return False


def _parse_quoted_value(tag_content: str, start_index: int, quote_char: str) -> Tuple[str, int]:
    """
    Parse quoted attribute value, ignoring quotes inside Django template syntax.

    Supports nested quotes like:
    - @click="modal = 'id-{{ date|date:"Y-m-d" }}'"
    - x-data='{ name: "{{ user|default:"Guest" }}" }'

    Returns: (value_with_quotes, new_index)
    """
    index = start_index
    value_start = index

    # Track when we're inside {{ }} or {% %} blocks to ignore quotes within them
    django_var_depth = 0
    django_tag_depth = 0

    while index < len(tag_content):
        if tag_content[index] == "\\" and index + 1 < len(tag_content):
            index += 2
        elif tag_content[index : index + 2] == "{{":
            django_var_depth += 1
            index += 2
        elif tag_content[index : index + 2] == "}}":
            django_var_depth = max(0, django_var_depth - 1)
            index += 2
        elif tag_content[index : index + 2] == "{%":
            django_tag_depth += 1
            index += 2
        elif tag_content[index : index + 2] == "%}":
            django_tag_depth = max(0, django_tag_depth - 1)
            index += 2
        elif tag_content[index] == quote_char and django_var_depth == 0 and django_tag_depth == 0:
            value = tag_content[value_start:index]
            value_with_quotes = quote_char + value + quote_char
            index += 1
            return value_with_quotes, index
        else:
            index += 1

    # Unclosed quote
    value = tag_content[value_start:]
    value_with_quotes = quote_char + value
    return value_with_quotes, index


def _parse_attributes(
    tag_content: str, start_index: int, check_only: bool = False
) -> Tuple[Dict[str, Any], List[str], bool, int]:
    """
    Parse attributes from tag content.

    Returns: (attrs_dict, empty_attrs_list, only_flag, final_index)
    """
    attrs = {}
    empty_attrs = []
    only = False
    index = start_index

    while index < len(tag_content):
        index = _skip_whitespace(tag_content, index)

        if index >= len(tag_content):
            break

        # Check for 'only' flag
        if check_only and _is_keyword_at_position(tag_content, index, "only"):
            only = True
            index += 4
            continue

        # Parse attribute key
        key, index = _parse_attribute_key(tag_content, index)

        if not key:
            index += 1
            continue

        index = _skip_whitespace(tag_content, index)

        # Check for '='
        if index < len(tag_content) and tag_content[index] == "=":
            index += 1
            index = _skip_whitespace(tag_content, index)

            # Parse value
            if index < len(tag_content):
                if tag_content[index] in ('"', "'"):
                    quote_char = tag_content[index]
                    index += 1
                    value_with_quotes, index = _parse_quoted_value(tag_content, index, quote_char)
                    attrs[key] = value_with_quotes
                else:
                    value, index = _parse_unquoted_value(tag_content, index)
                    attrs[key] = value
            else:
                attrs[key] = ""
        else:
            # Boolean/empty attribute
            if check_only:
                attrs[key] = True
            else:
                empty_attrs.append(key)

    return attrs, empty_attrs, only, index


def parse_component_tag(tag_content: str) -> ComponentTagResult:
    """
    Parse {% cotton component-name attr="value" :dynamic="expr" %} tags.

    Handles quoted strings, template tags inside quotes, dynamic attributes,
    boolean attributes, the 'only' flag, and self-closing syntax (/%} or / %}).
    """
    # Remove trailing self-closing syntax if present
    tag_content = tag_content.rstrip()
    if tag_content.endswith("/"):
        tag_content = tag_content[:-1].rstrip()

    if tag_content == "cotton":
        raise TemplateSyntaxError("Component tag must have a name")

    index = _skip_tag_name(tag_content, "cotton")
    index = _skip_whitespace(tag_content, index)

    if index >= len(tag_content):
        raise TemplateSyntaxError("Component tag must have a name")

    component_name, index = _parse_component_name(tag_content, index)

    if not component_name:
        raise TemplateSyntaxError("Component tag must have a name")

    attrs, empty_attrs, only, _ = _parse_attributes(tag_content, index, check_only=True)

    return ComponentTagResult(name=component_name, attrs=attrs, only=only)


def parse_vars_tag(tag_content: str) -> VarsTagResult:
    """
    Parse {% cotton:vars attr="value" :dynamic="expr" empty_attr %} tags.

    Handles quoted strings, template tags inside quotes, dynamic attributes,
    and empty attributes (no value).
    """
    if tag_content == "cotton:vars":
        return VarsTagResult(attrs={}, empty_attrs=[])

    index = _skip_tag_name(tag_content, "cotton:vars")
    index = _skip_whitespace(tag_content, index)

    attrs, empty_attrs, _, _ = _parse_attributes(tag_content, index, check_only=False)

    return VarsTagResult(attrs=attrs, empty_attrs=empty_attrs)
