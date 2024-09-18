import ast
from collections.abc import Mapping
from typing import Set, Any, Dict, List

from django.template import Variable, TemplateSyntaxError, Context
from django.template.base import VariableDoesNotExist, Template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted


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
        return Variable(self.value).resolve(context)

    def _resolve_as_boolean(self, _):
        if self.value == "":
            return True
        raise ValueError

    def _resolve_as_template(self, context):
        template = Template(self.value)
        rendered_value = template.render(context)
        if rendered_value != self.value:
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

    def unprocessable(self, key):
        self._unprocessable.append(key)

    def exclude_unprocessable(self):
        return {k: v for k, v in self._attrs.items() if k not in self._unprocessable}

    def exclude_from_string_output(self, key):
        self._exclude_from_str.add(key)

    def make_attrs_accessible(self):
        return {k.replace("-", "_"): v for k, v in self._attrs.items()}
