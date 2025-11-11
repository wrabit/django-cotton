"""
Parser for Cotton's native Django template tag syntax.

This module provides proper parsing of {% c %} and {% vars %} tags that handle quoted strings
as atomic units, allowing template tags and variables within attribute values.

Based on django-components' approach to handle complex attribute values.
"""
from typing import Dict, List, Tuple, Any
from django.template.exceptions import TemplateSyntaxError


# Parsing delimiters
WHITESPACE = ' \t\n'
ATTR_KEY_DELIMITERS = '= \t\n'  # Attribute keys stop at '=' or whitespace


def _skip_whitespace(tag_content: str, index: int) -> int:
    """
    Skip over whitespace characters and return the new index.

    Args:
        tag_content: The tag content being parsed
        index: Current position in the tag content

    Returns:
        New index after skipping whitespace
    """
    while index < len(tag_content) and tag_content[index] in WHITESPACE:
        index += 1
    return index


def _parse_attribute_key(tag_content: str, index: int) -> Tuple[str, int]:
    """
    Parse an attribute key (name) and return it with the new index.

    Keys stop at '=' or whitespace.

    Args:
        tag_content: The tag content being parsed
        index: Current position in the tag content

    Returns:
        Tuple of (key, new_index)
    """
    key_start = index
    while index < len(tag_content) and tag_content[index] not in ATTR_KEY_DELIMITERS:
        index += 1
    return tag_content[key_start:index], index


def _parse_unquoted_value(tag_content: str, index: int) -> Tuple[str, int]:
    """
    Parse an unquoted attribute value and return it with the new index.

    Unquoted values stop at whitespace.

    Args:
        tag_content: The tag content being parsed
        index: Current position in the tag content

    Returns:
        Tuple of (value, new_index)
    """
    value_start = index
    while index < len(tag_content) and tag_content[index] not in WHITESPACE:
        index += 1
    return tag_content[value_start:index], index


def _parse_quoted_value(tag_content: str, start_index: int, quote_char: str) -> Tuple[str, int]:
    """
    Parse a quoted attribute value, handling Django template syntax.

    This function is context-aware and ignores quotes that appear inside
    Django template tags ({{ }} or {% %}) to support nested quotes like:
    - @click="modal = 'id-{{ date|date:"Y-m-d" }}'"
    - x-data='{ name: "{{ user|default:"Guest" }}" }'

    Args:
        tag_content: The full tag content being parsed
        start_index: Index of the first character after the opening quote
        quote_char: The quote character (' or ")

    Returns:
        Tuple of (value_with_quotes, new_index)
        - value_with_quotes: The parsed value including the surrounding quotes
        - new_index: The index after the closing quote
    """
    index = start_index
    value_start = index

    # Track when we're inside {{ }} or {% %} blocks to ignore quotes within them
    django_var_depth = 0  # for {{ }} blocks
    django_tag_depth = 0  # for {% %} blocks

    while index < len(tag_content):
        if tag_content[index] == "\\" and index + 1 < len(tag_content):
            # Skip escaped character
            index += 2
        elif tag_content[index : index + 2] == "{{":
            # Entering Django variable block
            django_var_depth += 1
            index += 2
        elif tag_content[index : index + 2] == "}}":
            # Exiting Django variable block
            django_var_depth = max(0, django_var_depth - 1)
            index += 2
        elif tag_content[index : index + 2] == "{%":
            # Entering Django tag block
            django_tag_depth += 1
            index += 2
        elif tag_content[index : index + 2] == "%}":
            # Exiting Django tag block
            django_tag_depth = max(0, django_tag_depth - 1)
            index += 2
        elif tag_content[index] == quote_char and django_var_depth == 0 and django_tag_depth == 0:
            # Found closing quote (only when NOT inside Django template syntax)
            value = tag_content[value_start:index]
            value_with_quotes = quote_char + value + quote_char
            index += 1
            return value_with_quotes, index
        else:
            index += 1

    # Unclosed quote - return what we have
    value = tag_content[value_start:]
    value_with_quotes = quote_char + value
    return value_with_quotes, index


def parse_component_tag(tag_content: str) -> Tuple[str, Dict[str, Any], bool]:
    """
    Parse a Cotton component tag like:
    {% c component-name attr="value" :dynamic="expr" %}

    Properly handles:
    - Quoted strings with spaces
    - Template tags/variables inside quotes (preserves them as-is)
    - Dynamic attributes (prefixed with :)
    - Boolean attributes
    - The 'only' flag

    This parser works character-by-character and treats quoted strings as atomic units,
    preserving any template tags inside them for later evaluation.

    Args:
        tag_content: The full content of the tag including 'c' (e.g., "c component-name attr='value'")

    Returns:
        Tuple of (component_name, attrs_dict, only_flag)
    """
    # Skip the tag name ('c') and whitespace
    index = 0

    # Skip 'c' and any following whitespace
    if tag_content.startswith("c "):
        index = 2
    elif tag_content.startswith("c\t") or tag_content.startswith("c\n"):
        index = 2
    else:
        # Maybe just 'c' without space?
        if tag_content == "c":
            raise TemplateSyntaxError("Component tag must have a name")
        index = 1

    # Skip whitespace after 'c'
    index = _skip_whitespace(tag_content, index)

    if index >= len(tag_content):
        raise TemplateSyntaxError("Component tag must have a name")

    # Extract component name
    component_name, index = _parse_attribute_key(tag_content, index)

    # Parse attributes
    attrs = {}
    only = False

    while index < len(tag_content):
        # Skip whitespace
        index = _skip_whitespace(tag_content, index)

        if index >= len(tag_content):
            break

        # Check for 'only' flag
        if tag_content[index : index + 4] == "only":
            # Make sure it's the word 'only' and not part of another word
            if index + 4 >= len(tag_content) or tag_content[index + 4] in WHITESPACE:
                only = True
                index += 4
                continue

        # Parse attribute key
        key, index = _parse_attribute_key(tag_content, index)

        if not key:
            # No key found, skip
            index += 1
            continue

        # Skip whitespace after key
        index = _skip_whitespace(tag_content, index)

        # Check for '='
        if index < len(tag_content) and tag_content[index] == "=":
            index += 1  # Skip '='
            index = _skip_whitespace(tag_content, index)

            # Parse value
            if index < len(tag_content):
                if tag_content[index] in ('"', "'"):
                    # Quoted value - use helper function to handle Django template syntax
                    quote_char = tag_content[index]
                    index += 1
                    value_with_quotes, index = _parse_quoted_value(tag_content, index, quote_char)
                    attrs[key] = value_with_quotes
                else:
                    # Unquoted value
                    value, index = _parse_unquoted_value(tag_content, index)
                    attrs[key] = value
            else:
                attrs[key] = ""
        else:
            # Boolean attribute
            attrs[key] = True

    return component_name, attrs, only


def parse_vars_tag(tag_content: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parse a Cotton vars tag like:
    {% vars attr="value" :dynamic="expr" empty_attr %}

    Properly handles:
    - Quoted strings with spaces
    - Template tags/variables inside quotes (preserves them as-is)
    - Dynamic attributes (prefixed with :)
    - Empty attributes (no value)

    This parser works character-by-character and treats quoted strings as atomic units,
    preserving any template tags inside them for later evaluation.

    Args:
        tag_content: The full content of the tag including 'vars' (e.g., "vars attr='value'")

    Returns:
        Tuple of (attrs_dict, empty_attrs_list)
    """
    # Skip the tag name ('vars') and whitespace
    index = 0

    # Skip 'vars' and any following whitespace
    if tag_content.startswith("vars "):
        index = 5
    elif tag_content.startswith("vars\t") or tag_content.startswith("vars\n"):
        index = 5
    else:
        # Maybe just 'vars' without space?
        if tag_content == "vars":
            return {}, []
        index = 4

    # Skip whitespace after 'vars'
    index = _skip_whitespace(tag_content, index)

    # Parse attributes
    attrs = {}
    empty_attrs = []

    while index < len(tag_content):
        # Skip whitespace
        index = _skip_whitespace(tag_content, index)

        if index >= len(tag_content):
            break

        # Parse attribute key
        key, index = _parse_attribute_key(tag_content, index)

        if not key:
            # No key found, skip
            index += 1
            continue

        # Skip whitespace after key
        index = _skip_whitespace(tag_content, index)

        # Check for '='
        if index < len(tag_content) and tag_content[index] == "=":
            index += 1  # Skip '='
            index = _skip_whitespace(tag_content, index)

            # Parse value
            if index < len(tag_content):
                if tag_content[index] in ('"', "'"):
                    # Quoted value - use helper function to handle Django template syntax
                    quote_char = tag_content[index]
                    index += 1
                    value_with_quotes, index = _parse_quoted_value(tag_content, index, quote_char)
                    attrs[key] = value_with_quotes
                else:
                    # Unquoted value
                    value, index = _parse_unquoted_value(tag_content, index)
                    attrs[key] = value
            else:
                attrs[key] = ""
        else:
            # Empty attribute (no value)
            empty_attrs.append(key)

    return attrs, empty_attrs
