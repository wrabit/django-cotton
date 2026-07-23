"""Markdown-authored docs pages.

The `.md` files under `docs_project/docs/` are the single source of truth for
the pages listed in `SECTIONS`. They are rendered to HTML for humans (into the
existing docs chrome) and served raw at `/docs/<slug>.md` + indexed in
`/llms.txt` so agents can consume clean markdown.

The one cotton-specific twist over a plain markdown pipeline: a ```cotton fenced
block is expanded into the live `<c-snippet>` widget (dual c-tags/DTL syntax,
copy button, highlighting) instead of a static code block. The raw `.md` keeps
the clean fence, so an agent reads a plain code sample; the rendered page gets
the interactive widget. See `CottonSnippetExtension` below.
"""
from __future__ import annotations

import re
from pathlib import Path

import markdown as md_lib
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

DOCS_ROOT = Path(__file__).resolve().parent / "docs"

# Editorial nav / page order. Only pages with a real `.md` here become live
# markdown pages; everything else still renders from its `build_view` template.
SECTIONS: list[tuple[str, list[str]]] = [
    ("Getting Started", [
        "quickstart.md",
    ]),
]

_MD_LINK_RE = re.compile(r"\(((?:[\w./-]+/)?([\w-]+)\.md)(#[^)]*)?\)")
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _slug(rel_path: str) -> str:
    return Path(rel_path).stem


def page_map() -> dict[str, Path]:
    """slug -> absolute file path, from the TOC (never the filesystem - a stray
    draft file shouldn't become a live page)."""
    return {
        _slug(rel): DOCS_ROOT / rel
        for _, pages in SECTIONS
        for rel in pages
    }


def _rewrite_links(text: str) -> str:
    """`(components.md)` / `(fundamentals.md#x)` -> `(/docs/<slug>#x)`.
    Cross-doc links are written repo-relative so they also work on GitHub."""
    slugs = set(page_map())

    def repl(m):
        slug, anchor = m.group(2), m.group(3) or ""
        if slug in slugs:
            return f"(/docs/{slug}{anchor})"
        return m.group(0)

    return _MD_LINK_RE.sub(repl, text)


_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def _gfm_list_spacing(text: str) -> str:
    """python-markdown requires a blank line before a list; GitHub (and most
    authors) don't. Insert the blank line when a list starts right after a text
    line so `intro:\\n- item` renders as a list instead of collapsing into the
    paragraph. Fenced code blocks are left alone."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if (
            not in_fence
            and out
            and _LIST_ITEM_RE.match(line)
            and out[-1].strip()
            and not _LIST_ITEM_RE.match(out[-1])
        ):
            out.append("")
        out.append(line)
    return "\n".join(out)


def title_of(path: Path) -> str:
    m = _TITLE_RE.search(path.read_text())
    return m.group(1).strip() if m else path.stem.replace("-", " ").title()


# --- ```cotton fence -> live <c-snippet> widget -----------------------------

_COTTON_FENCE_RE = re.compile(r"(?ms)^```cotton([^\n]*)\n(.*?)\n```[ \t]*$")
_INFO_TOKEN_RE = re.compile(r'(\S+?)(?:=(?:"([^"]*)"|(\S+)))?(?:\s+|$)')

# Only these info-string keys become <c-snippet> attributes, so a fence can't
# inject arbitrary markup. `label`/`language` take a value; the rest are the
# component's boolean flags (bare, no value).
_VALUE_ATTRS = {"label", "language"}
_FLAG_ATTRS = {"hide-label", "hide_copy", "flipped", "padded_top", "ignore_syntax_choice"}


def _parse_info(info: str) -> str:
    """Turn a fence info string (`language=python hide-label`) into a cotton
    attribute string (`language="python" hide-label`)."""
    attrs: list[str] = []
    for m in _INFO_TOKEN_RE.finditer(info.strip()):
        key = m.group(1)
        val = m.group(2) if m.group(2) is not None else m.group(3)
        if key in _VALUE_ATTRS and val is not None:
            attrs.append(f'{key}="{val}"')
        elif key in _FLAG_ATTRS and val is None:
            attrs.append(key)
        # unknown keys are ignored - keeps the surface tight for the proof slice
    return " ".join(attrs)


def _render_snippet(info: str, body: str) -> str:
    """Compile + render a single <c-snippet> for `body`, returning finished HTML.

    The author writes just the code; we re-introduce the
    `{% cotton:verbatim %}{% verbatim %}` wrapping that stops Django + cotton
    from executing the sample. Rendering goes through cotton's own compiler (the
    loader path), so the dual-syntax (c-tags/DTL) toggle in snippet.html - which
    runs `to_template_tags` - keeps working untouched.
    """
    # Imported lazily so importing this module never needs Django configured
    # (the fence-scoping unit test relies on that).
    from django.template import engines
    from django.utils.html import escape
    from django_cotton.compiler_regex import CottonCompiler

    attrs = _parse_info(info)
    open_tag = f"<c-snippet {attrs}>" if attrs else "<c-snippet>"
    fragment = (
        f"{open_tag}{{% cotton:verbatim %}}{{% verbatim %}}\n"
        f"{body}\n"
        f"{{% endverbatim %}}{{% endcotton:verbatim %}}</c-snippet>"
    )
    try:
        compiled = CottonCompiler().process(fragment)
        return engines["django"].from_string(compiled).render({})
    except Exception as e:  # never let one bad snippet 500 the whole page
        return f"<!-- cotton snippet render error: {escape(str(e))} -->\n<pre><code>{escape(body)}</code></pre>"


class _CottonSnippetPreprocessor(Preprocessor):
    """Replace each ```cotton block with the rendered widget, stashed as raw
    HTML so markdown passes it through verbatim.

    Scoping guarantee: this only ever touches ```cotton fences. It runs at a
    higher priority than fenced_code (25), so a normal ```python / ```html
    prose fence is never seen here and its `{{ }}` / `{% %}` content is escaped
    by fenced_code as literal text - it never reaches the template engine.
    """

    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)

        def repl(m: re.Match) -> str:
            html = _render_snippet(m.group(1), m.group(2))
            placeholder = self.md.htmlStash.store(html)
            # Blank lines keep the placeholder its own block.
            return f"\n{placeholder}\n"

        return _COTTON_FENCE_RE.sub(repl, text).split("\n")


class CottonSnippetExtension(Extension):
    def extendMarkdown(self, md):
        # 27 > fenced_code's 25, so we grab ```cotton before it does.
        md.preprocessors.register(_CottonSnippetPreprocessor(md), "cotton_snippet", 27)


def _markdown() -> md_lib.Markdown:
    return md_lib.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists",
            "codehilite",
            "toc",
            CottonSnippetExtension(),
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
        },
    )


def _prepare(text: str) -> str:
    return _gfm_list_spacing(_rewrite_links(text))


_HEADING_ID_RE = re.compile(r'(<h[1-6])( id="([^"]+)")')


def _annotate_sections(html: str) -> str:
    """The `toc` extension gives headings an `id`; the docs' scrollspy tracks
    `[data-section-id]`. Mirror the id onto data-section-id so the right-rail
    "On this page" index highlights on scroll, same as the template pages."""
    return _HEADING_ID_RE.sub(r'\1 data-section-id="\3"\2', html)


def render_md(text: str) -> str:
    return _annotate_sections(_markdown().convert(_prepare(text)))


def _flatten_toc(tokens: list[dict]) -> list[dict]:
    out: list[dict] = []
    for t in tokens:
        out.append(t)
        out.extend(_flatten_toc(t.get("children", [])))
    return out


def render_md_with_toc(text: str) -> tuple[str, list[dict]]:
    """Rendered HTML plus the h2 TOC tokens, so the page can build its "On this
    page" index from the same markdown headings. The `toc` extension nests h2s
    under the leading h1, so flatten before selecting the section headings."""
    md = _markdown()
    html = _annotate_sections(md.convert(_prepare(text)))
    tokens = getattr(md, "toc_tokens", [])
    return html, [t for t in _flatten_toc(tokens) if t.get("level") == 2]


def render(path: Path) -> str:
    return render_md(path.read_text())


def render_with_toc(path: Path) -> tuple[str, list[dict]]:
    return render_md_with_toc(path.read_text())


def nav(active_slug: str = "") -> list[dict]:
    return [
        {
            "section": section,
            "pages": [
                {
                    "slug": _slug(rel),
                    "title": title_of(DOCS_ROOT / rel),
                    "active": _slug(rel) == active_slug,
                }
                for rel in pages
                if (DOCS_ROOT / rel).exists()
            ],
        }
        for section, pages in SECTIONS
    ]
