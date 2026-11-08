"""Portals: send markup from a component to another part of the page.

    <c-portal name="head" />              destination, usually in a layout
    <c-portal to="head">...</c-portal>    source, usually in a component

Django renders top-down, so the destination has already been emitted by the
time a component deep in the page pushes to it. The destination therefore
renders a marker, sources collect their content into the render's shared
`cotton_data`, and the outermost template swaps the markers for the collected
content once the whole page has rendered. `cotton_data` is the dict cotton
already hands to every component, including isolated (`only`) ones, so the
collector reaches every source without any request-level machinery.

The outermost render is caught by wrapping `Template.render`, installed from
the app config next to the nested-tag lexer patch. Returning a Template
subclass from the loader is not enough: Django's cached loader builds the
Template itself from the child loader's contents.

A push block renders once per page by default, identified by its source text
(hashed from its tokens when the template is parsed). The same block in two different components
shares one slot, and the first instance to render wins, so values from
context come from that instance. `multiple` on the source appends every time,
which is Blade's plain @push; the default is close to its @pushOnce.
"""
from __future__ import annotations

import re

from django.template import base as template_base
from django.utils.safestring import mark_safe

_MARKER = "<!--cotton-portal:{name}-->"
_MARKER_PREFIX = "<!--cotton-portal:"
_MARKER_RE = re.compile(r"<!--cotton-portal:([\w.-]+)-->")


def marker(name: str) -> str:
    return _MARKER.format(name=name)


def push(cotton_data: dict, name: str, content: str) -> None:
    """Append `content` to the `name` destination, trimmed of surrounding whitespace."""
    content = content.strip()
    if content:
        _portal(cotton_data, name)["pushes"].append(content)


def claim(cotton_data: dict, name: str, block: str) -> bool:
    """Reserve `block` on the `name` destination. False if an earlier push already
    holds it, which is how a block renders once per page."""
    seen = _portal(cotton_data, name)["seen"]
    if block in seen:
        return False
    seen.add(block)
    return True


def _portal(cotton_data: dict, name: str) -> dict:
    return cotton_data.setdefault("portals", {}).setdefault(name, {"pushes": [], "seen": set()})


def resolve(output: str, cotton_data: dict) -> str:
    """Replace every destination marker with its collected pushes. A destination
    nobody pushed to renders empty; a push with no destination on the page
    (a partial render, say) is dropped."""
    portals = cotton_data.get("portals", {})

    def repl(m: re.Match) -> str:
        portal = portals.get(m.group(1))
        return "\n".join(portal["pushes"]) if portal else ""

    return _MARKER_RE.sub(repl, output)


def is_root_render(context) -> bool:
    """True for the outermost `Template.render` of a page. Nested renders either
    carry the bound template (include, extends, non-isolated components) or the
    shared `cotton_data` (isolated components get a fresh Context, but cotton
    passes `cotton_data` into it)."""
    return context.template is None and "cotton_data" not in context


def enable_portals() -> None:
    """Wrap Template.render so the outermost render resolves portals. Idempotent."""
    if getattr(template_base.Template.render, "_cotton_portals", False):
        return

    original_render = template_base.Template.render

    def render(self, context):
        if not is_root_render(context):
            return original_render(self, context)
        from django_cotton.utils import get_cotton_data

        cotton_data = get_cotton_data(context)
        output = original_render(self, context)
        if "portals" in cotton_data or _MARKER_PREFIX in output:
            return mark_safe(resolve(output, cotton_data))
        return output

    render._cotton_portals = True
    template_base.Template.render = render
