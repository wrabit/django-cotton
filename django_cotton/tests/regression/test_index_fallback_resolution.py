"""
Regression tests for component template path resolution.

``CottonComponentNode._get_cached_template`` probes ``<name>.html`` first and
falls back to ``<name>/index.html``. Its template cache lives in
``context.render_context``, which only exists for a single render, so
index-style components used to raise and catch ``TemplateDoesNotExist`` on
*every* render. The resolved path is now memoized on the node itself
(``_resolved_paths``), which lives as long as the compiled template.

These tests render the same compiled ``Template`` twice — a fresh
``render_context`` each time, as in production — so they exercise both the
first resolution and the memoized second render. The missing-component test
guards the edge where a failed resolution must not be memoized as a success.
"""

from django.template import Context, Template, TemplateDoesNotExist

from django_cotton.tests.utils import CottonTestCase, get_compiled


class IndexFallbackResolutionTests(CottonTestCase):
    def test_index_component_renders_repeatedly(self):
        self.create_template(
            "cotton/dropdown/index.html",
            "I'm an index file!",
        )

        template = Template(get_compiled("<c-dropdown />"))

        for _ in range(2):
            self.assertTrue("I'm an index file!" in template.render(Context({})))

    def test_flat_component_renders_repeatedly(self):
        self.create_template(
            "cotton/badge.html",
            "I'm a flat file!",
        )

        template = Template(get_compiled("<c-badge />"))

        for _ in range(2):
            self.assertTrue("I'm a flat file!" in template.render(Context({})))

    def test_missing_component_raises_on_every_render(self):
        template = Template(get_compiled("<c-does-not-exist />"))

        for _ in range(2):
            with self.assertRaises(TemplateDoesNotExist):
                template.render(Context({}))
