import ast
from collections.abc import Mapping
from typing import Set, Any, Dict, List, Tuple

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


def strip_quotes_with_status(value: Any) -> Tuple[Any, bool]:
    """
    Strip surrounding quotes and return whether the value was originally quoted.

    More efficient than calling a separate check then strip_quotes_safely(),
    as it only checks the string once.

    Args:
        value: The value to strip quotes from

    Returns:
        Tuple of (stripped_value, was_quoted)
    """
    if type(value) is str:
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            return value[1:-1], True
        elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1], True
    return value, False


class UnprocessableDynamicAttr(Exception):
    pass


class DynamicAttr:
    _template_cache: dict[str, Template] = {}
    _literal_cache: dict[str, Any] = {}
    _variable_cache: dict[str, Variable] = {}

    _MISSING = object()

    def __init__(self, value: str, is_cvar=False):
        self.value = value
        self._is_cvar = is_cvar
        self._resolved_value = self._MISSING

    def _resolve_variable(self, value, context):
        var = self._variable_cache.get(value)
        if var is None:
            var = Variable(value)
            self._variable_cache[value] = var
        resolved = var.resolve(context)
        return resolved.attrs_dict() if isinstance(resolved, Attrs) else resolved

    def _resolve_template(self, value, context):
        mini = self._template_cache.get(value)
        if mini is None:
            mini = Template(value)
            self._template_cache[value] = mini
        rendered = mini.render(context)
        if rendered == value:
            return self._MISSING
        try:
            return ast.literal_eval(rendered)
        except (ValueError, SyntaxError):
            return rendered

    def _resolve_literal(self, value):
        cached = self._literal_cache.get(value, self._MISSING)
        if cached is not self._MISSING:
            return cached
        result = ast.literal_eval(value)
        self._literal_cache[value] = result
        return result

    def resolve(self, context: Context) -> Any:
        if self._resolved_value is not self._MISSING:
            return self._resolved_value

        value = self.value

        if value == "":
            self._resolved_value = True
            return True

        cached = self._literal_cache.get(value, self._MISSING)
        if cached is not self._MISSING:
            self._resolved_value = cached
            return cached

        try:
            self._resolved_value = self._resolve_variable(value, context)
            return self._resolved_value
        except (VariableDoesNotExist, TemplateSyntaxError):
            pass

        if "{{" in value or "{%" in value:
            try:
                result = self._resolve_template(value, context)
                if result is not self._MISSING:
                    self._resolved_value = result
                    return result
            except Exception:
                pass

        try:
            self._resolved_value = self._resolve_literal(value)
            return self._resolved_value
        except (ValueError, SyntaxError):
            pass

        raise UnprocessableDynamicAttr


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
