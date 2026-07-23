"""Tests for the markdown docs pipeline (docs_project/docs.py).

The load-bearing property is *scoping*: only ```cotton fences are ever handed
to the template engine. A normal ```python / ```html prose fence must be left
completely literal - its `{{ }}` / `{% %}` content must never be executed.
"""
from django.test import SimpleTestCase

from docs_project import docs


class CottonFenceRenderingTests(SimpleTestCase):
    def test_cotton_fence_renders_live_snippet_widget(self):
        out = docs.render_md("```cotton\n<c-ui.button>Click</c-ui.button>\n```")
        # Rendered to the real <c-snippet> widget, not a bare code block.
        self.assertIn("<pre", out)
        self.assertIn("Click", out)
        # The dual-syntax (c-tags/DTL) toggle only appears for cotton-tag bodies,
        # proving the widget - and its to_template_tags path - actually ran.
        self.assertIn("c-tags", out)
        self.assertIn("DTL", out)

    def test_infostring_becomes_snippet_attributes(self):
        out = docs.render_md("```cotton language=python label=settings.py\nDEBUG = True\n```")
        self.assertIn("settings.py", out)  # label surfaced by the widget

    def test_cotton_body_template_syntax_is_shown_literally(self):
        # {{ }} / {% %} inside a cotton fence are wrapped in verbatim by the
        # renderer, so they are displayed as code, never executed.
        out = docs.render_md("```cotton\n<div>{{ title }}{% widthratio a b c %}</div>\n```")
        self.assertIn("{{ title }}", out)
        self.assertIn("{% widthratio a b c %}", out)


class FenceScopingTests(SimpleTestCase):
    """A plain prose fence must never reach the Django template engine."""

    def test_python_fence_django_syntax_left_literal(self):
        out = docs.render_md("```python\nvalue = {{ danger }}\n```")
        # codehilite wraps tokens in spans, so assert the literal pieces survive.
        # If this had been templated, `{{ danger }}` would resolve to "" and the
        # variable name would be gone.
        self.assertIn("danger", out)
        self.assertIn("{{", out)

    def test_python_fence_invalid_tag_does_not_raise(self):
        # {% not_a_real_tag %} would raise TemplateSyntaxError if it ever hit
        # the engine. render() must complete and keep it literal.
        out = docs.render_md("```python\n{% not_a_real_tag %}\n```")
        self.assertIn("not_a_real_tag", out)

    def test_html_fence_cotton_tag_not_executed(self):
        # A <c- tag in a *plain* html fence is documentation, not a component:
        # it must be escaped as text, not rendered into a live widget.
        out = docs.render_md("```html\n<c-ui.button>x</c-ui.button>\n```")
        self.assertNotIn("c-tags", out)  # no snippet-widget chrome
        self.assertIn("&lt;", out)  # angle brackets escaped, not rendered
        self.assertIn("c-ui.button", out)  # shown literally as text


class PipelineTests(SimpleTestCase):
    def test_render_with_toc_returns_h2_headings(self):
        html, toc = docs.render_md_with_toc(
            "# Title\n\n## Alpha\n\ntext\n\n## Beta\n\ntext"
        )
        names = [t["name"] for t in toc]
        self.assertEqual(names, ["Alpha", "Beta"])
        # headings get data-section-id so the scrollspy index can track them
        self.assertIn('data-section-id="alpha"', html)

    def test_rewrite_links_points_at_migrated_slugs(self):
        # quickstart.md is a real page -> link rewritten; unknown stays.
        out = docs.render_md("[a](quickstart.md) [b](nope.md)")
        self.assertIn('href="/docs/quickstart"', out)
        self.assertIn("nope.md", out)
