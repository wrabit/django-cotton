"""Tests for the markdown docs pipeline (docs_project/docs.py).

Two load-bearing properties. Scoping: a fence body is displayed, never
executed, whether it becomes a snippet widget or a plain block. Coverage: every
page the TOC lists renders through the real views.
"""
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from docs_project import docs

SNIPPET_MARKER = 'x-ref="htmlCode"'  # only the <c-snippet> widget emits this


class SnippetFenceTests(SimpleTestCase):
    def test_known_language_fence_becomes_snippet_widget(self):
        out = docs.render_md("```python label=settings.py\nDEBUG = True\n```")
        self.assertIn(SNIPPET_MARKER, out)
        self.assertIn("language-python", out)
        self.assertIn("settings.py", out)  # label surfaced by the widget

    def test_html_fence_with_cotton_tags_gets_syntax_toggle(self):
        out = docs.render_md("```html\n<c-ui.button>Click</c-ui.button>\n```")
        self.assertIn("c-tags", out)
        self.assertIn("DTL", out)
        # Shown as code, not rendered as a component.
        self.assertIn("&lt;c-ui.button&gt;Click&lt;/c-ui.button&gt;", out)

    def test_template_syntax_in_fence_is_shown_literally(self):
        out = docs.render_md("```django\n<div>{{ title }}{% widthratio a b c %}</div>\n```")
        self.assertIn("{{ title }}", out)
        self.assertIn("{% widthratio a b c %}", out)

    def test_dtl_cotton_tag_in_fence_is_shown_not_executed(self):
        # Cotton's tokenizer picks up {% cotton %} even inside {% verbatim %};
        # the pipeline must not rely on verbatim for DTL samples.
        out = docs.render_md("```django\n{% cotton button %}Click{% endcotton %}\n```")
        self.assertIn("{% cotton button %}Click{% endcotton %}", out)
        self.assertNotIn('class="btn btn-primary"', out)

    def test_comment_syntax_in_fence_is_shown(self):
        out = docs.render_md("```django\n{# note #}\n```")
        self.assertIn("{# note #}", out)

    def test_python_fence_django_syntax_left_literal(self):
        # If this had been templated, `{{ danger }}` would resolve to "" and the
        # variable name would be gone.
        out = docs.render_md("```python\nvalue = {{ danger }}\n```")
        self.assertIn("{{ danger }}", out)

    def test_invalid_tag_in_fence_does_not_raise(self):
        out = docs.render_md("```python\n{% not_a_real_tag %}\n```")
        self.assertIn("not_a_real_tag", out)

    def test_bare_fence_stays_plain_code_block(self):
        out = docs.render_md("```\nplain text\n```")
        self.assertIn("<pre><code>plain text", out)
        self.assertNotIn(SNIPPET_MARKER, out)

    def test_unknown_language_fence_stays_plain_code_block(self):
        out = docs.render_md("```ruby\nputs 1\n```")
        self.assertIn('class="language-ruby"', out)
        self.assertNotIn(SNIPPET_MARKER, out)

    def test_label_with_markup_is_escaped_once(self):
        out = docs.render_md('```html label="Rendered <head>"\nx\n```')
        self.assertIn("Rendered &lt;head&gt;", out)
        self.assertNotIn("&amp;lt;", out)

    def test_unknown_info_keys_are_dropped(self):
        out = docs.render_md('```python onclick="alert(1)" label=ok\nx = 1\n```')
        self.assertNotIn("alert(1)", out)
        self.assertIn("ok", out)


    def test_preview_option_adds_live_component_under_code(self):
        out = docs.render_md("```html label=view.html preview=button\n<c-input />\n```")
        self.assertIn(">preview<", out)
        self.assertIn('class="btn btn-primary"', out)
        self.assertIn("&lt;c-input /&gt;", out)


class DemoFenceTests(SimpleTestCase):
    def test_body_is_rendered_as_preview_and_shown_as_code(self):
        out = docs.render_md("```cotton-demo\n<c-button>Click</c-button>\n```")
        self.assertIn(">preview<", out)
        self.assertIn('<button class="btn btn-primary">Click</button>', out)
        self.assertIn("&lt;c-button&gt;Click&lt;/c-button&gt;", out)

    def test_preview_option_renders_named_component_instead_of_body(self):
        out = docs.render_md("```cotton-demo preview=button\n<c-button>Later</c-button>\n```")
        self.assertIn('class="btn btn-primary"', out)
        self.assertNotIn("<button class=\"btn btn-primary\">Later</button>", out)
        self.assertIn("&lt;c-button&gt;Later&lt;/c-button&gt;", out)

    def test_invalid_preview_name_falls_back_to_body(self):
        out = docs.render_md("```cotton-demo preview=../etc\n<c-button>Click</c-button>\n```")
        self.assertIn('<button class="btn btn-primary">Click</button>', out)

    def test_broken_demo_degrades_to_code_block(self):
        out = docs.render_md("```cotton-demo\n<c-does-not-exist />\n```")
        self.assertIn("failed to render", out)
        self.assertIn("&lt;c-does-not-exist /&gt;", out)


class TabFenceTests(SimpleTestCase):
    def test_adjacent_tab_fences_become_one_tabbed_widget(self):
        out = docs.render_md(
            "```html tab=view.html preview=button\n<c-x />\n```\n"
            "```python tab=views.py\nx = 1\n```"
        )
        self.assertEqual(out.count("register('view.html')"), 1)
        self.assertEqual(out.count("register('views.py')"), 1)
        self.assertIn('class="btn btn-primary"', out)  # preview from the first fence
        self.assertIn("&lt;c-x /&gt;", out)
        self.assertIn("x = 1", out)

    def test_tab_fences_separated_by_prose_stay_separate(self):
        out = docs.render_md("```html tab=a\n1\n```\n\ntext\n\n```html tab=b\n2\n```")
        self.assertEqual(out.count('preview-label') + out.count("register('a')"), 1)
        self.assertEqual(out.count("register('b')"), 1)
        self.assertIn("<p>text</p>", out)


class PipelineTests(SimpleTestCase):
    def test_render_with_toc_returns_h2_headings(self):
        html, toc = docs.render_md_with_toc("# Title\n\n## Alpha\n\ntext\n\n## Beta\n\ntext")
        self.assertEqual([t["name"] for t in toc], ["Alpha", "Beta"])
        # h2s get the scrollspy hook and anchor offset the template pages have
        self.assertIn('<h2 id="alpha" data-section-id="alpha" class="scroll-mt-24">', html)

    def test_rewrite_links_points_at_migrated_slugs(self):
        out = docs.render_md("[a](quickstart.md) [b](nope.md)")
        self.assertIn('href="/docs/quickstart"', out)
        self.assertIn("nope.md", out)

    def test_description_is_first_plain_paragraph(self):
        text = "# T\n\n> a note\n\nSome **bold** text with a [link](x.md) and `code`, long enough to count as a real paragraph.\n\nSecond."
        path = docs.DOCS_ROOT / "_tmp_desc.md"
        path.write_text(text)
        try:
            self.assertEqual(
                docs.description_of(path),
                "Some bold text with a link and code, long enough to count as a real paragraph.",
            )
            path.write_text("# My Page\n\nRun this:\n\n```bash\nx\n```")
            self.assertTrue(docs.description_of(path).startswith("My Page - Django Cotton:"))
        finally:
            path.unlink()

    def test_toc_names_are_plain_text(self):
        _, toc = docs.render_md_with_toc("# T\n\n## Editing & Delete\n\ntext")
        self.assertEqual(toc[0]["name"], "Editing & Delete")

    def test_heading_keeps_hand_picked_anchor(self):
        html, toc = docs.render_md_with_toc("# T\n\n## 5. Working with attrs {#attrs}\n\ntext")
        self.assertIn('<h2 id="attrs" data-section-id="attrs"', html)
        self.assertEqual(toc[0]["id"], "attrs")

    def test_neighbours_follow_reading_order(self):
        first = docs._ordered_slugs()[0]
        last = docs._ordered_slugs()[-1]
        self.assertIsNone(docs.neighbours(first)[0])
        self.assertIsNone(docs.neighbours(last)[1])
        prev, nxt = docs.neighbours("fundamentals")
        self.assertEqual((prev["slug"], nxt["slug"]), ("components", "thinking-in-components"))

    def test_list_right_after_text_renders_as_list(self):
        out = docs.render_md("Two options:\n- one\n- two")
        self.assertEqual(out.count("<li>"), 2)


# The test client renders the full page chrome; with DEBUG off the settings pick
# the hashed manifest storage, which needs a collectstatic run. Plain storage here.
@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class DocsPagesTests(SimpleTestCase):
    def test_every_toc_page_renders(self):
        for slug, path in docs.page_map().items():
            with self.subTest(slug=slug):
                self.assertTrue(path.exists(), f"TOC references missing file: {path}")
                response = self.client.get(f"/docs/{slug}")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, docs.title_of(path))

    def test_every_page_has_a_route_named_after_its_slug(self):
        # Templates link with {% url %}; migrating a page must keep its name.
        for slug in docs.page_map():
            self.assertEqual(reverse(slug), f"/docs/{slug}")

    def test_prev_next_navigation(self):
        response = self.client.get("/docs/fundamentals")
        self.assertContains(response, 'href="/docs/components"')
        self.assertContains(response, 'href="/docs/configuration"')

    def test_htmx_page_gets_its_scripts_and_demo_data(self):
        response = self.client.get("/docs/htmx-examples")
        self.assertContains(response, "htmx.org")
        self.assertContains(response, "Implement user authentication")
        self.assertNotContains(response, "failed to render")

    def test_no_page_has_a_broken_fragment(self):
        for slug in docs.page_map():
            with self.subTest(slug=slug):
                response = self.client.get(f"/docs/{slug}")
                self.assertNotContains(response, "failed to render")

    def test_page_links_to_its_raw_markdown(self):
        response = self.client.get("/docs/quickstart")
        self.assertContains(response, 'href="/docs/quickstart.md"')
        self.assertContains(response, 'href="/llms.txt"')

    def test_pages_have_meta_descriptions(self):
        for slug in docs.page_map():
            with self.subTest(slug=slug):
                response = self.client.get(f"/docs/{slug}")
                self.assertContains(response, '<meta name="description" content="')

    def test_readme_docs_anchors_still_exist(self):
        import re
        from pathlib import Path

        readme = (Path(__file__).resolve().parents[3] / "README.md").read_text()
        links = set(re.findall(r"django-cotton\.com/docs/([a-z-]+)#([a-z-]+)", readme))
        self.assertTrue(links)
        for slug, anchor in links:
            with self.subTest(link=f"{slug}#{anchor}"):
                self.assertContains(self.client.get(f"/docs/{slug}"), f'id="{anchor}"')

    def test_raw_markdown_endpoint(self):
        response = self.client.get("/docs/quickstart.md")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/markdown"))
        self.assertTrue(response.content.decode().startswith("# Quickstart"))

    def test_llms_txt_indexes_every_page(self):
        response = self.client.get("/llms.txt")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        for slug in docs.page_map():
            self.assertIn(f"https://django-cotton.com/docs/{slug}.md", body)

    def test_unknown_slug_404s(self):
        self.assertEqual(self.client.get("/docs/nope.md").status_code, 404)
