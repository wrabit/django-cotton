"""
Parser for Cotton's native Django template tag syntax.

This module provides proper parsing of {% c %} and {% vars %} tags that handle quoted strings
as atomic units, allowing template tags and variables within attribute values.

Based on django-components' approach to handle complex attribute values.
"""
from typing import Dict, List, Tuple, Optional, Any
from django.template.exceptions import TemplateSyntaxError


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
    if tag_content.startswith('c '):
        index = 2
    elif tag_content.startswith('c\t') or tag_content.startswith('c\n'):
        index = 2
    else:
        # Maybe just 'c' without space?
        if tag_content == 'c':
            raise TemplateSyntaxError("Component tag must have a name")
        index = 1
    
    # Skip whitespace after 'c'
    while index < len(tag_content) and tag_content[index] in ' \t\n':
        index += 1
    
    if index >= len(tag_content):
        raise TemplateSyntaxError("Component tag must have a name")
    
    # Extract component name
    name_start = index
    while index < len(tag_content) and tag_content[index] not in ' \t\n=':
        index += 1
    
    component_name = tag_content[name_start:index]
    
    # Parse attributes
    attrs = {}
    only = False
    
    while index < len(tag_content):
        # Skip whitespace
        while index < len(tag_content) and tag_content[index] in ' \t\n':
            index += 1
        
        if index >= len(tag_content):
            break
        
        # Check for 'only' flag
        if tag_content[index:index+4] == 'only':
            # Make sure it's the word 'only' and not part of another word
            if index + 4 >= len(tag_content) or tag_content[index+4] in ' \t\n':
                only = True
                index += 4
                continue
        
        # Parse attribute key
        key_start = index
        while index < len(tag_content) and tag_content[index] not in '= \t\n':
            index += 1
        
        if index == key_start:
            # No key found, skip
            index += 1
            continue
        
        key = tag_content[key_start:index]
        
        # Skip whitespace after key
        while index < len(tag_content) and tag_content[index] in ' \t\n':
            index += 1
        
        # Check for '='
        if index < len(tag_content) and tag_content[index] == '=':
            index += 1  # Skip '='
            
            # Skip whitespace after '='
            while index < len(tag_content) and tag_content[index] in ' \t\n':
                index += 1
            
            # Parse value - this is the critical part
            if index < len(tag_content):
                if tag_content[index] in ('"', "'"):
                    # Quoted value - read until closing quote
                    quote_char = tag_content[index]
                    index += 1
                    value_start = index

                    # Read content, handling escapes
                    while index < len(tag_content):
                        if tag_content[index] == '\\' and index + 1 < len(tag_content):
                            # Skip escaped character
                            index += 2
                        elif tag_content[index] == quote_char:
                            # Found closing quote
                            value = tag_content[value_start:index]
                            value_with_quotes = quote_char + value + quote_char
                            index += 1
                            break
                        else:
                            index += 1
                    else:
                        # Unclosed quote
                        value = tag_content[value_start:]
                        value_with_quotes = quote_char + value

                    # Store value WITH quotes to match old parser behavior
                    # The component render will strip them with _strip_quotes_safely()
                    attrs[key] = value_with_quotes
                else:
                    # Unquoted value
                    value_start = index
                    while index < len(tag_content) and tag_content[index] not in ' \t\n':
                        index += 1
                    attrs[key] = tag_content[value_start:index]
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
    if tag_content.startswith('vars '):
        index = 5
    elif tag_content.startswith('vars\t') or tag_content.startswith('vars\n'):
        index = 5
    else:
        # Maybe just 'vars' without space?
        if tag_content == 'vars':
            return {}, []
        index = 4

    # Skip whitespace after 'vars'
    while index < len(tag_content) and tag_content[index] in ' \t\n':
        index += 1

    # Parse attributes
    attrs = {}
    empty_attrs = []

    while index < len(tag_content):
        # Skip whitespace
        while index < len(tag_content) and tag_content[index] in ' \t\n':
            index += 1

        if index >= len(tag_content):
            break

        # Parse attribute key
        key_start = index
        while index < len(tag_content) and tag_content[index] not in '= \t\n':
            index += 1

        if index == key_start:
            # No key found, skip
            index += 1
            continue

        key = tag_content[key_start:index]

        # Skip whitespace after key
        while index < len(tag_content) and tag_content[index] in ' \t\n':
            index += 1

        # Check for '='
        if index < len(tag_content) and tag_content[index] == '=':
            index += 1  # Skip '='

            # Skip whitespace after '='
            while index < len(tag_content) and tag_content[index] in ' \t\n':
                index += 1

            # Parse value - this is the critical part
            if index < len(tag_content):
                if tag_content[index] in ('"', "'"):
                    # Quoted value - read until closing quote
                    quote_char = tag_content[index]
                    index += 1
                    value_start = index

                    # Read content, handling escapes
                    while index < len(tag_content):
                        if tag_content[index] == '\\' and index + 1 < len(tag_content):
                            # Skip escaped character
                            index += 2
                        elif tag_content[index] == quote_char:
                            # Found closing quote
                            value = tag_content[value_start:index]
                            value_with_quotes = quote_char + value + quote_char
                            index += 1
                            break
                        else:
                            index += 1
                    else:
                        # Unclosed quote
                        value = tag_content[value_start:]
                        value_with_quotes = quote_char + value

                    # Store value WITH quotes
                    # The vars parser will strip them with strip_quotes_safely()
                    attrs[key] = value_with_quotes
                else:
                    # Unquoted value
                    value_start = index
                    while index < len(tag_content) and tag_content[index] not in ' \t\n':
                        index += 1
                    attrs[key] = tag_content[value_start:index]
            else:
                attrs[key] = ""
        else:
            # Empty attribute (no value)
            empty_attrs.append(key)

    return attrs, empty_attrs