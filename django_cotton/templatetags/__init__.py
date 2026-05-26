from __future__ import annotations

from collections.abc import Mapping
from typing import Set, Any, Dict, List, Tuple

from django.template import Library
from django.template.base import (
    DebugLexer,
    Lexer,
    Origin,
    Parser,
    UNKNOWN_SOURCE,
)
from django.template.engine import Engine
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted


class InlineTemplate:
    def __init__(self, template_string: str, nodelist, engine, origin=None, name=None):
        self.name = name
        self.origin = origin or Origin(UNKNOWN_SOURCE)
        self.engine = engine
        self.source = str(template_string)
        self.nodelist = nodelist

    def render(self, context):
        with context.render_context.push_state(self):
            if context.template is None:
                with context.bind_template(self):
                    context.template_name = self.name
                    return self.nodelist.render(context)
            return self.nodelist.render(context)


def strip_quotes_with_status(value: Any) -> Tuple[Any, bool]:
    """
    Strip surrounding quotes and return whether the value was originally quoted.

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


def snapshot_parser_library(parser: Parser) -> Library:
    """Capture the parser's active tag and filter table at this parse point."""
    active_library = Library()
    active_library.tags.update(parser.tags)
    active_library.filters.update(parser.filters)
    return active_library


def compile_inline_template(value: str, active_library: Library | None = None) -> InlineTemplate:
    """Compile a template fragment at parse time for later rendering.

    Returns an InlineTemplate whose .render(context) can be called at render time
    without re-lexing or re-parsing the template string.
    """
    engine = Engine.get_default()
    origin = Origin(UNKNOWN_SOURCE)

    if active_library is None:
        nodelist = engine.from_string(value).nodelist
    else:
        lexer = DebugLexer(value) if engine.debug else Lexer(value)
        parser = Parser(
            lexer.tokenize(),
            engine.template_libraries,
            [active_library],
            origin,
        )
        nodelist = parser.parse()

    return InlineTemplate(value, nodelist, engine, origin=origin)


class UnprocessableDynamicAttr(Exception):
    pass


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
        if not self._unprocessable:
            return self._attrs
        return {k: v for k, v in self._attrs.items() if k not in self._unprocessable}

    def exclude_from_string_output(self, key):
        self._exclude_from_str.add(key)

    def make_attrs_accessible(self):
        return {k.replace("-", "_"): v for k, v in self._attrs.items()}
