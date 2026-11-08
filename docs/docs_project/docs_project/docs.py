"""Markdown-authored docs pages.

The `.md` files under `docs_project/docs/` are the single source of truth for
the pages listed in `SECTIONS`. They render to HTML for humans inside the
existing docs chrome, are served raw at `/docs/<slug>.md` and are indexed in
`/llms.txt` so agents get clean markdown. `SECTIONS` is also the reading
order: the routes, the prev/next links and llms.txt all derive from it.

The markdown stays standard. A fenced code block with a known language
(```python, ```html, ```django ...) is rendered as the live `<c-snippet>` widget
(label, copy button, c-tags/DTL toggle) instead of a plain code block, so the
raw file reads as ordinary GitHub markdown while the page gets the widget. The
fence's info string carries the widget's options: `label=settings.py`,
`hide-label`, `flipped` and so on.

Live previews: `preview=<component>` on any fence renders that component under
the code. Adjacent fences that each carry `tab=<name>` become one tabbed widget
(the first may carry the preview). The one custom fence is ```cotton-demo, whose
body is rendered live as the preview *and* shown as the code, so the sample on
the page is the markup that produced it.
"""
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import markdown as md_lib
from django.template import engines
from django.utils.html import escape
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

DOCS_ROOT = Path(__file__).resolve().parent / "docs"

# Editorial nav / reading order. Mirrors the sidebar (cotton/sidebar.html); the
# home page is not prose and stays as a template.
SECTIONS: list[tuple[str, list[str]]] = [
    ("Getting Started", [
        "quickstart.md",
        "components.md",
        "fundamentals.md",
        "configuration.md",
        "thinking-in-components.md",
    ]),
    ("Tutorials", [
        "form-fields.md",
        "alpine-js.md",
        "layouts.md",
        "icons.md",
    ]),
    ("Usage Patterns", [
        "variants.md",
        "attribute-proxying.md",
        "index-component.md",
        "htmx-examples.md",
    ]),
    ("Community", [
        "ecosystem.md",
    ]),
]

_MD_LINK_RE = re.compile(r"\(((?:[\w./-]+/)?([\w-]+)\.md)(#[^)]*)?\)")
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _slug(rel_path: str) -> str:
    return Path(rel_path).stem


def _ordered_slugs() -> list[str]:
    return [_slug(rel) for _, pages in SECTIONS for rel in pages]


def page_map() -> dict[str, Path]:
    """slug -> absolute file path, from the TOC (never the filesystem - a stray
    draft file shouldn't become a live page)."""
    return {_slug(rel): DOCS_ROOT / rel for _, pages in SECTIONS for rel in pages}


def title_of(path: Path) -> str:
    m = _TITLE_RE.search(path.read_text())
    return m.group(1).strip() if m else path.stem.replace("-", " ").title()


_INLINE_MD_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)|[`*_]+")
_SKIP_LINE_RE = re.compile(r"^\s*(#|>|```|[-*+]\s|\d+\.\s|\|)")


_GENERIC_DESCRIPTION = (
    "{title} - Django Cotton: build reusable server-side UI components in single "
    "HTML files, no Python required, fully interoperable with Django templates."
)


def description_of(path: Path, limit: int = 160) -> str:
    """The page's first ordinary paragraph as plain text, for <meta description>.
    Headings, notes, lists, tables and code are skipped and inline markdown is
    reduced to its text. A page that opens with a short lead-in ("Run the
    following command:") gets the same generic line the template pages had."""
    text = path.read_text()
    for para in re.split(r"\n\s*\n", text):
        lines = [l for l in para.strip().splitlines() if l.strip()]
        if not lines or any(_SKIP_LINE_RE.match(l) for l in lines):
            continue
        plain = _INLINE_MD_RE.sub(lambda m: m.group(1) or "", " ".join(lines))
        plain = re.sub(r"\s+", " ", plain).strip().rstrip(":")
        if len(plain) < 60:
            break
        if len(plain) > limit:
            plain = plain[: limit - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
        return plain
    return _GENERIC_DESCRIPTION.format(title=title_of(path))


def neighbours(slug: str) -> tuple[dict | None, dict | None]:
    """(prev, next) pages in reading order, each {"slug", "title"} or None."""
    order = _ordered_slugs()
    pages = page_map()
    i = order.index(slug)

    def page(s):
        return {"slug": s, "title": title_of(pages[s])}

    prev = page(order[i - 1]) if i > 0 else None
    nxt = page(order[i + 1]) if i + 1 < len(order) else None
    return prev, nxt


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


# --- fenced code -> live widgets ---------------------------------------------

DEMO_FENCE = "cotton-demo"

# Fence language -> highlight.js language for the snippet widget. A fence whose
# language isn't listed here is left to markdown's fenced_code as a plain block.
LANGUAGES = {
    "html": "django",
    "django": "django",
    "cotton": "django",
    "jinja": "django",
    "python": "python",
    "py": "python",
    "bash": "bash",
    "sh": "bash",
    "shell": "bash",
    "xml": "xml",
    "json": "json",
    "javascript": "javascript",
    "js": "javascript",
    "css": "css",
    "toml": "toml",
    "text": "plaintext",
}

# ```lang info-string
# body
# ```
_FENCE_RE = re.compile(r"(?ms)^```([\w-]+)([^\n]*)\n(.*?)\n```[ \t]*$")
_INFO_TOKEN_RE = re.compile(r'([\w-]+)(?:=(?:"([^"]*)"|(\S+)))?')
_COMPONENT_RE = re.compile(r"^[\w.-]+$")

# Only these info-string keys reach <c-snippet>, so a fence can't inject
# arbitrary attributes. `label` takes a value, the rest are boolean flags.
# `preview` and `tab` are read by the renderer itself.
_VALUE_ATTRS = {"label"}
_FLAG_ATTRS = {"hide-label", "hide-copy", "flipped", "padded-top", "ignore-syntax-choice"}
_OPTIONS = {"preview", "tab"}


def _parse_info(info: str) -> tuple[str, dict[str, str]]:
    """`label=settings.py hide-label preview=button` ->
    ('label="settings.py" hide-label', {"preview": "button"})."""
    attrs: list[str] = []
    options: dict[str, str] = {}
    for m in _INFO_TOKEN_RE.finditer(info.strip()):
        key = m.group(1).replace("_", "-")
        val = m.group(2) if m.group(2) is not None else m.group(3)
        if key in _VALUE_ATTRS and val is not None:
            attrs.append(f'{key}="{escape(val)}"')
        elif key in _FLAG_ATTRS and val is None:
            attrs.append(key)
        elif key in _OPTIONS and val is not None:
            options[key] = val
    return " ".join(attrs), options


_TEMPLATE_SYNTAX_RE = re.compile(r"\{%|%\}|\{\{|\}\}|\{#|#\}")
_TEMPLATE_SYNTAX = {
    "{%": "{% templatetag openblock %}",
    "%}": "{% templatetag closeblock %}",
    "{{": "{% templatetag openvariable %}",
    "}}": "{% templatetag closevariable %}",
    "{#": "{% templatetag opencomment %}",
    "#}": "{% templatetag closecomment %}",
}


def _literal(body: str) -> str:
    """The author writes just the code; make it display as written.

    `{% cotton:verbatim %}` keeps the compiler off the `<c-` tags, which must
    stay raw so the snippet widget can offer its c-tags/DTL toggle. Django
    syntax is spelled with `{% templatetag %}` rather than wrapped in
    `{% verbatim %}`: cotton's tokenizer claims `{% cotton %}` tags before
    Django sees the verbatim block, so a DTL sample would otherwise execute.
    """
    body = _TEMPLATE_SYNTAX_RE.sub(lambda m: _TEMPLATE_SYNTAX[m.group(0)], body)
    return "{% cotton:verbatim %}\n" + body + "\n{% endcotton:verbatim %}"


def _render_fragment(fragment: str, request, context: dict | None, fallback: str) -> str:
    """Compile a cotton fragment and render it with the page's request. A bad
    sample degrades to a plain code block rather than taking the page down."""
    from django_cotton.compiler_regex import CottonCompiler

    try:
        compiled = CottonCompiler().process(fragment)
        return engines["django"].from_string(compiled).render(context or {}, request)
    except Exception as e:
        return (
            f"<!-- cotton docs: fragment failed to render: {escape(str(e))} -->\n"
            f"<pre><code>{escape(fallback)}</code></pre>"
        )


def _preview_slot(markup: str) -> str:
    return f'<c-slot name="preview">{markup}</c-slot>' if markup else ""


def _preview_component(options: dict[str, str]) -> str:
    """`preview=demo.inputs.basic` -> `<c-demo.inputs.basic />`, or "" when the
    option is absent or not a plain component name."""
    name = options.get("preview", "")
    return f"<c-{name} />" if _COMPONENT_RE.match(name) else ""


def _render_widget(language, attrs, preview, body, request, context) -> str:
    fragment = (
        f'<c-snippet language="{language}" {attrs}'.rstrip() + ">"
        + _preview_slot(preview)
        + _literal(body)
        + "</c-snippet>"
    )
    return _render_fragment(fragment, request, context, body)


def _render_snippet(language: str, info: str, body: str, request, context) -> str:
    """Code shown as written. `preview=<component>` adds a live preview rendered
    from that component, for samples whose output needs setup the sample itself
    doesn't carry (view data, a component that evolves over a tutorial)."""
    attrs, options = _parse_info(info)
    return _render_widget(language, attrs, _preview_component(options), body, request, context)


def _render_demo(info: str, body: str, request, context) -> str:
    """Live preview + code in one widget. The preview is the body itself unless
    `preview=<component>` names a component to render in its place."""
    attrs, options = _parse_info(info)
    preview = _preview_component(options) or body
    return _render_widget("django", attrs, preview, body, request, context)


def _render_tabs(fences: list[re.Match], request, context) -> str:
    """Adjacent `tab=` fences -> one <c-demo.snippet-tabs> with a code tab per
    fence, and the preview from whichever fence names one (normally the first)."""
    preview = ""
    tabs: list[str] = []
    for m in fences:
        lang, info, body = m.groups()
        _, options = _parse_info(info)
        preview = preview or _preview_component(options)
        tabs.append(
            f'<c-demo.snippet-tab name="{escape(options["tab"])}">'
            f'<c-snippet language="{LANGUAGES[lang]}" rounded="rounded-b-xl" hide-label>'
            + _literal(body)
            + "</c-snippet></c-demo.snippet-tab>"
        )
    fragment = (
        '<c-demo.snippet-tabs preview-label="demo">'
        + _preview_slot(preview)
        + "".join(tabs)
        + "</c-demo.snippet-tabs>"
    )
    return _render_fragment(fragment, request, context, "\n\n".join(m.group(3) for m in fences))


def _is_tab(m: re.Match) -> bool:
    return m.group(1) in LANGUAGES and "tab" in _parse_info(m.group(2))[1]


class _FencePreprocessor(Preprocessor):
    """Swap known-language fences for rendered widgets, stashed as raw HTML so
    markdown passes them through untouched.

    Runs at a higher priority than fenced_code (25), so it sees every fence
    first. A fence it doesn't claim (no language, or an unknown one) is left for
    fenced_code to render as a plain, escaped block. Fence bodies it does claim
    are made literal (see `_literal`), so `{{ }}` / `{% %}` inside a sample is
    displayed, never executed.
    """

    def __init__(self, md, request, context):
        super().__init__(md)
        self.request = request
        self.context = context

    def _stash(self, html: str) -> str:
        # Blank lines keep the placeholder its own block.
        return f"\n{self.md.htmlStash.store(html)}\n"

    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)
        matches = list(_FENCE_RE.finditer(text))
        out: list[str] = []
        pos = 0
        i = 0
        while i < len(matches):
            m = matches[i]
            lang, info, body = m.groups()
            if _is_tab(m):
                group = [m]
                # Pull in the following fences while only whitespace separates them.
                while (
                    i + 1 < len(matches)
                    and not text[matches[i].end():matches[i + 1].start()].strip()
                    and _is_tab(matches[i + 1])
                ):
                    i += 1
                    group.append(matches[i])
                html = _render_tabs(group, self.request, self.context)
                start, end = group[0].start(), group[-1].end()
            elif lang == DEMO_FENCE:
                html = _render_demo(info, body, self.request, self.context)
                start, end = m.start(), m.end()
            elif lang in LANGUAGES:
                html = _render_snippet(LANGUAGES[lang], info, body, self.request, self.context)
                start, end = m.start(), m.end()
            else:
                i += 1
                continue
            out.append(text[pos:start])
            out.append(self._stash(html))
            pos = end
            i += 1
        out.append(text[pos:])
        return "".join(out).split("\n")


class CottonFenceExtension(Extension):
    def __init__(self, request=None, context=None):
        super().__init__()
        self.request = request
        self.context = context

    def extendMarkdown(self, md):
        # 27 > fenced_code's 25, so fences reach us before fenced_code.
        md.preprocessors.register(
            _FencePreprocessor(md, self.request, self.context), "cotton_fences", 27
        )


def _markdown(request=None, context=None) -> md_lib.Markdown:
    # No server-side highlighting: the site runs highlight.js on load, which
    # colours the snippet widgets and any plain fenced block alike. attr_list
    # lets a heading keep a hand-picked anchor (`## Title {#id}`) where other
    # pages or the README already link to it.
    return md_lib.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists",
            "attr_list",
            "toc",
            CottonFenceExtension(request=request, context=context),
        ],
    )


def _prepare(text: str) -> str:
    return _gfm_list_spacing(_rewrite_links(text))


_H2_RE = re.compile(r'<h2 id="([^"]+)">')


def _annotate_sections(html: str) -> str:
    """The `toc` extension gives headings an `id`; the docs' scrollspy tracks
    `[data-section-id]` and the template pages offset anchors with scroll-mt.
    Mirror both onto the h2s so the right-rail index works the same here."""
    return _H2_RE.sub(r'<h2 id="\1" data-section-id="\1" class="scroll-mt-24">', html)


def _flatten_toc(tokens: list[dict]) -> list[dict]:
    out: list[dict] = []
    for t in tokens:
        out.append(t)
        out.extend(_flatten_toc(t.get("children", [])))
    return out


def render_md_with_toc(text: str, request=None, context=None) -> tuple[str, list[dict]]:
    """Rendered HTML plus the h2 TOC tokens, so the page can build its "On this
    page" index from the same markdown headings. The `toc` extension nests h2s
    under the leading h1, so flatten before selecting the section headings."""
    md = _markdown(request, context)
    html = _annotate_sections(md.convert(_prepare(text)))
    tokens = getattr(md, "toc_tokens", [])
    # The toc extension HTML-escapes names; hand the template plain text so it
    # escapes once ("Editing & Delete", not "Editing &amp;amp; Delete").
    return html, [
        {**t, "name": html_lib.unescape(t["name"])}
        for t in _flatten_toc(tokens)
        if t.get("level") == 2
    ]


def render_md(text: str, request=None, context=None) -> str:
    return render_md_with_toc(text, request, context)[0]


def render_page(path: Path, request=None, context=None) -> tuple[str, list[dict]]:
    return render_md_with_toc(path.read_text(), request, context)


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
