from __future__ import annotations

from typing import Any, NamedTuple

from django.template import Library, TemplateSyntaxError
from django.template.base import Node
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django_cotton.templatetags import (
    Attrs,
    UnprocessableDynamicAttr,
    snapshot_parser_library,
    strip_quotes_with_status,
)
from django_cotton.templatetags._component import AttrKind, PreparedValue, _try_compile_template
from django_cotton.utils import get_cotton_data


class PreparedVar(NamedTuple):
    key: str
    exclude_key: str
    accessible_key: str
    kind: AttrKind
    value: Any
    compiled: Any
    merge: bool = False


MERGE_SUFFIX = ":merge"
MERGEABLE_KEYS = {"class"}
_UNRESOLVED = object()


def _strip_merge(key: str) -> tuple[str, bool]:
    if not key.endswith(MERGE_SUFFIX):
        return key, False
    key = key[: -len(MERGE_SUFFIX)]
    if key.lstrip(":") not in MERGEABLE_KEYS:
        raise TemplateSyntaxError(f"'{key}{MERGE_SUFFIX}' in c-vars: only 'class' can be merged.")
    return key, True


class CottonVarsNode(Node):
    def __init__(
        self,
        var_dict: dict[str, Any],
        empty_vars: list[str],
        active_library: Library | None = None,
    ):
        self.empty_vars = [_strip_merge(key)[0] for key in empty_vars]
        self.active_library = active_library

        self._prepared_vars = []

        for key, raw_value in var_dict.items():
            value, was_quoted = strip_quotes_with_status(raw_value)

            key, merge = _strip_merge(key)

            if key.startswith(":"):
                exclude_key = key[1:]
                accessible_key = exclude_key.replace("-", "_")
                pv = PreparedValue(value, active_library=active_library)
                self._prepared_vars.append(PreparedVar(
                    key, exclude_key, accessible_key, AttrKind.DYNAMIC, value, pv, merge,
                ))

            elif not was_quoted and isinstance(value, str) and value:
                accessible_key = key.replace("-", "_")
                pv = PreparedValue(value, active_library=active_library)
                self._prepared_vars.append(PreparedVar(
                    key, key, accessible_key, AttrKind.UNQUOTED, value, pv, merge,
                ))

            else:
                accessible_key = key.replace("-", "_")
                compiled = _try_compile_template(value, active_library)
                kind = AttrKind.ESCAPED if compiled else AttrKind.STATIC
                self._prepared_vars.append(PreparedVar(
                    key, key, accessible_key, kind, value, compiled, merge,
                ))

    def extract_vars(self, context: "Context", attrs: Attrs, slots: dict[str, str]) -> dict[str, Any]:
        """Extract and process vars, returning a dict of resolved values."""
        vars = {}

        for var in self._prepared_vars:
            attrs.exclude_from_string_output(var.exclude_key)

            if var.merge:
                merged = self._merge(var, context, attrs)
                vars[var.accessible_key] = merged
                # The parent's attrs go into the context after the vars and would replace it
                if var.exclude_key in attrs:
                    attrs[var.exclude_key] = merged
                continue

            # Parent already set this attr, skip the default
            if var.key in attrs.exclude_unprocessable():
                continue
            # Slot content overrides the default
            if var.exclude_key in slots:
                continue

            value = self._resolve_default(var, context)
            if value is not _UNRESOLVED:
                vars[var.accessible_key] = value

        # Process cvars without values
        for empty_var in self.empty_vars:
            attrs.exclude_from_string_output(empty_var)

        return vars

    @staticmethod
    def _resolve_default(var: PreparedVar, context: "Context") -> Any:
        # : prefix — explicit dynamic binding
        if var.kind == AttrKind.DYNAMIC:
            try:
                return var.compiled.resolve(context)
            except UnprocessableDynamicAttr:
                return _UNRESOLVED  # Var couldn't be resolved, skip it

        # No quotes — treated as dynamic, falls back to string literal
        if var.kind == AttrKind.UNQUOTED:
            try:
                return var.compiled.resolve(context)
            except UnprocessableDynamicAttr:
                return var.value

        # Quoted value containing {{ }} or {% %} — render the template
        if var.kind == AttrKind.ESCAPED:
            try:
                return var.compiled.render(context) if var.compiled else var.value
            except (TemplateSyntaxError, ValueError, SyntaxError):
                return var.value

        # Plain static value
        return var.value

    def _merge(self, var: PreparedVar, context: "Context", attrs: Attrs) -> str:
        """The component's own classes first, then the parent's."""
        parts = (
            self._resolve_default(var, context),
            attrs.exclude_unprocessable().get(var.exclude_key),
        )
        # Rendered parts are already escaped; a plain join would escape them a second time
        return mark_safe(
            " ".join(conditional_escape(p) for p in parts if p not in (_UNRESOLVED, None, True, ""))
        )

    def render(self, context):
        # When rendered standalone (not as part of a component extraction),
        # inject vars into the context
        cotton_data = get_cotton_data(context)

        # If there's a component on the stack, vars will be extracted by the component
        # So we only need to inject if we're rendering standalone
        if not cotton_data["stack"]:
            # Standalone rendering - inject vars into context
            attrs = Attrs({})
            slots = {}
            vars = self.extract_vars(context, attrs, slots)
            context.update(vars)

        # Vars node itself doesn't render anything
        return ""


def cotton_cvars(parser, token):
    """
    Parse standalone cotton:vars template tag using a custom character-by-character parser.

    This allows template tags like {% trans %} to work in cotton:vars defaults:
        {% cotton:vars label="{% trans 'Loading' %}" %}

    The custom parser treats quoted strings as atomic units, preserving
    template tags inside them for Django to evaluate naturally at render time.
    """
    from django_cotton.tag_parser import parse_vars_tag

    # Use the custom parser that handles quoted strings properly
    result = parse_vars_tag(token.contents)

    # Keep raw values with quotes - we need to detect quote status in extract_vars()
    # to support quoteless dynamic attributes (e.g., default=True vs default="True")
    var_dict = result.attrs

    active_library = snapshot_parser_library(parser)

    return CottonVarsNode(var_dict, result.empty_attrs, active_library)
