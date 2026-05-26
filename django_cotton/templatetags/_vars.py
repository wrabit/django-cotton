from typing import Any, NamedTuple

from django.template import Library, TemplateSyntaxError
from django.template.base import Node

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


class CottonVarsNode(Node):
    def __init__(
        self,
        var_dict: dict[str, Any],
        empty_vars: list[str],
        active_library: Library | None = None,
    ):
        self.empty_vars = empty_vars
        self.active_library = active_library

        self._prepared_vars = []

        for key, raw_value in var_dict.items():
            value, was_quoted = strip_quotes_with_status(raw_value)

            if key.startswith(":"):
                exclude_key = key[1:]
                accessible_key = exclude_key.replace("-", "_")
                pv = PreparedValue(value, active_library=active_library)
                self._prepared_vars.append(PreparedVar(
                    key, exclude_key, accessible_key, AttrKind.DYNAMIC, value, pv,
                ))

            elif not was_quoted and isinstance(value, str) and value:
                accessible_key = key.replace("-", "_")
                pv = PreparedValue(value, active_library=active_library)
                self._prepared_vars.append(PreparedVar(
                    key, key, accessible_key, AttrKind.UNQUOTED, value, pv,
                ))

            else:
                accessible_key = key.replace("-", "_")
                compiled = _try_compile_template(value, active_library)
                kind = AttrKind.ESCAPED if compiled else AttrKind.STATIC
                self._prepared_vars.append(PreparedVar(
                    key, key, accessible_key, kind, value, compiled,
                ))

    def extract_vars(self, context: "Context", attrs: Attrs, slots: dict[str, str]) -> dict[str, Any]:
        """Extract and process vars, returning a dict of resolved values."""
        vars = {}

        for var in self._prepared_vars:
            attrs.exclude_from_string_output(var.exclude_key)

            # Parent already set this attr, skip the default
            if var.key in attrs.exclude_unprocessable():
                continue
            # Slot content overrides the default
            if var.exclude_key in slots:
                continue

            # : prefix — explicit dynamic binding
            if var.kind == AttrKind.DYNAMIC:
                try:
                    vars[var.accessible_key] = var.compiled.resolve(context)
                except UnprocessableDynamicAttr:
                    pass  # Var couldn't be resolved, skip it

            # No quotes — treated as dynamic, falls back to string literal
            elif var.kind == AttrKind.UNQUOTED:
                try:
                    vars[var.accessible_key] = var.compiled.resolve(context)
                except UnprocessableDynamicAttr:
                    vars[var.accessible_key] = var.value

            # Quoted value containing {{ }} or {% %} — render the template
            elif var.kind == AttrKind.ESCAPED:
                try:
                    vars[var.accessible_key] = var.compiled.render(context) if var.compiled else var.value
                except (TemplateSyntaxError, ValueError, SyntaxError):
                    vars[var.accessible_key] = var.value

            # Plain static value
            else:
                vars[var.accessible_key] = var.value

        # Process cvars without values
        for empty_var in self.empty_vars:
            attrs.exclude_from_string_output(empty_var)

        return vars

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
