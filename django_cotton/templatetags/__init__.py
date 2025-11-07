import ast
from collections.abc import Mapping
from typing import Set, Any, Dict, List

from django.template import Variable, TemplateSyntaxError, Context
from django.template.base import VariableDoesNotExist, Template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted


def parse_template_tag_attributes(bits: List[str]) -> tuple[Dict[str, Any], List[str]]:
    """
    Parse template tag attributes handling quoted values with spaces.

    This function properly handles cases like:
        label="{% trans 'Loading' %}"

    Where Django's default split_contents() would break on the space between 'trans' and 'Loading'.

    This logic is extracted from cotton_component() to be reused across template tags.

    Args:
        bits: List of tokens from token.split_contents()[1:]

    Returns:
        Tuple of (attributes_dict, empty_attributes_list)
        Note: Quoted values will still have their quotes - use _strip_quotes_safely() to remove them
    """
    attrs = {}
    empty_attrs = []
    current_key = None
    current_value = []

    for bit in bits:
        if "=" in bit:
            # If we were building a previous value, store it
            if current_key:
                attrs[current_key] = " ".join(current_value)
                current_value = []

            # Start new key-value pair
            key, value = bit.split("=", 1)
            if value.startswith(("'", '"')):
                if value.endswith(("'", '"')) and value[0] == value[-1]:
                    # Complete quoted value
                    attrs[key] = value
                else:
                    # Start of quoted value
                    current_key = key
                    current_value = [value]
            else:
                # Simple unquoted value
                attrs[key] = value
        else:
            if current_key:
                # Continue building quoted value
                current_value.append(bit)
            else:
                # Empty attribute (no value)
                empty_attrs.append(bit)

    # Store any final value being built
    if current_key:
        attrs[current_key] = " ".join(current_value)

    return attrs, empty_attrs


def strip_quotes_safely(value: Any) -> Any:
    """
    Strip surrounding quotes from a string value if present.

    Handles both single and double quotes - strips the outer quote pair
    while preserving any inner quotes in the value.

    Args:
        value: The value to strip quotes from

    Returns:
        The value with outer quotes removed, or the original value if not a quoted string
    """
    if type(value) is str:
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1]
    return value


class UnprocessableDynamicAttr(Exception):
    pass


class DynamicAttr:
    def __init__(self, value: str, is_cvar=False):
        self.value = value
        self._is_cvar = is_cvar
        self._resolved_value = None

    def resolve(self, context: Context) -> Any:
        if self._resolved_value is not None:
            return self._resolved_value

        resolvers = [
            self._resolve_as_variable,
            self._resolve_as_boolean,
            self._resolve_as_template,
            self._resolve_as_literal,
        ]

        for resolver in resolvers:
            try:
                # noinspection PyArgumentList
                self._resolved_value = resolver(context)
                return self._resolved_value
            except (VariableDoesNotExist, TemplateSyntaxError, ValueError, SyntaxError):
                continue

        raise UnprocessableDynamicAttr

    def _resolve_as_variable(self, context):
        value = Variable(self.value).resolve(context)
        if isinstance(value, Attrs):
            return value.attrs_dict()
        return value

    def _resolve_as_boolean(self, _):
        if self.value == "":
            return True
        raise ValueError

    def _resolve_as_template(self, context):
        template = Template(self.value)
        rendered_value = template.render(context)
        if rendered_value != self.value:
            # Try to evaluate the rendered value as a Python literal
            # This handles cases like :attr="{'key': {{ var }}}" where {{ var }} is rendered first
            try:
                return ast.literal_eval(rendered_value)
            except (ValueError, SyntaxError):
                # Not a valid literal, return as string
                return rendered_value
        raise TemplateSyntaxError

    def _resolve_as_literal(self, _):
        return ast.literal_eval(self.value)


class Attrs(Mapping):
    def __init__(self, attrs: Dict[str, Any]):
        self._attrs = attrs
        self._exclude_from_str: Set[str] = set()
        self._unprocessable: List[str] = []

    def __str__(self):
        return mark_safe(
            " ".join(
                f"{k}" if v is True else f"{k}={ensure_quoted(v)}"
                for k, v in self._attrs.items()
                if k not in self._exclude_from_str
            )
        )

    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, value):
        self._attrs[key] = value

    def __iter__(self):
        return iter(self._attrs)

    def __len__(self):
        return len(self._attrs)

    def items(self):
        return self._attrs.items()

    def keys(self):
        return self._attrs.keys()

    def values(self):
        return self._attrs.values()

    # Custom methods to allow modifications
    @property
    def dict(self):
        return self._attrs

    def attrs_dict(self):
        return {k: v for k, v in self._attrs.items() if k not in self._exclude_from_str}

    def unprocessable(self, key):
        self._unprocessable.append(key)

    def exclude_unprocessable(self):
        return {k: v for k, v in self._attrs.items() if k not in self._unprocessable}

    def exclude_from_string_output(self, key):
        self._exclude_from_str.add(key)

    def make_attrs_accessible(self):
        return {k.replace("-", "_"): v for k, v in self._attrs.items()}
