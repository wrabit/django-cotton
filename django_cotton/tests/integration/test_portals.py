from django.template import Context, Template
from django.template.loader import render_to_string

from django_cotton.tests.utils import CottonTestCase, get_compiled



class PortalCompileTests(CottonTestCase):
    def test_destination_compiles_to_portal_tag(self):
        self.assertEqual(get_compiled('<c-portal name="head" />'), '{% cotton:portal name="head" %}')
        self.assertEqual(
            get_compiled('<c-portal name="head"></c-portal>'),
            '{% cotton:portal name="head" %}{% endcotton:portal %}',
        )

    def test_source_compiles_to_portal_block(self):
        self.assertEqual(
            get_compiled('<c-portal to="head"><script></script></c-portal>'),
            '{% cotton:portal to="head" %}<script></script>{% endcotton:portal %}',
        )
        self.assertEqual(
            get_compiled('<c-portal to="head" multiple>x</c-portal>'),
            '{% cotton:portal to="head" multiple %}x{% endcotton:portal %}',
        )

    def test_block_id_comes_from_the_block_source(self):
        def block(source):
            return Template(get_compiled(source)).nodelist[0].block

        a = block('<c-portal to="head"><script src="a.js"></script></c-portal>')
        b = block('<c-portal to="head">\n    <script src="a.js"></script>\n</c-portal>')
        c = block('<c-portal to="head"><script src="b.js"></script></c-portal>')
        self.assertEqual(a, b)  # whitespace doesn't split an id
        self.assertNotEqual(a, c)

    def test_source_must_have_content(self):
        with self.assertRaises(ValueError):
            get_compiled('<c-portal to="head" />')

    def test_portal_needs_name_or_to(self):
        with self.assertRaises(ValueError):
            get_compiled("<c-portal>x</c-portal>")


class PortalRenderTests(CottonTestCase):
    def test_push_lands_in_destination(self):
        self.create_template(
            "cotton/tooltip.html",
            """<span>{{ slot }}</span>
            <c-portal to="head"><script src="tooltip.js"></script></c-portal>""",
        )
        self.create_template(
            "portal_basic_view.html",
            """<head><c-portal name="head" /></head>
            <body><c-tooltip>hi</c-tooltip></body>""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '<head><script src="tooltip.js"></script></head>')
            self.assertContains(response, "<body><span>hi</span>")
            self.assertNotContains(response, "cotton-portal")

    def test_a_block_renders_once_however_many_instances(self):
        self.create_template(
            "cotton/widget.html",
            """<c-portal to="js">
                <script>init()</script>
            </c-portal>""",
        )
        self.create_template(
            "portal_once_view.html",
            """<c-widget /><c-widget /><c-widget />[<c-portal name="js" />]""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "[<script>init()</script>]")
            self.assertEqual(response.content.decode().count("init()"), 1)

    def test_first_instance_wins_when_content_differs(self):
        # Identity, not content: the block is the unit. Per-instance pushes need `multiple`.
        self.create_template(
            "cotton/chart.html",
            """<c-portal to="js"><script>draw("{{ id }}")</script></c-portal>""",
        )
        self.create_template(
            "portal_first_view.html",
            """<c-chart id="sales" /><c-chart id="costs" /><c-portal name="js" />""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, 'draw("sales")')
            self.assertNotContains(response, 'draw("costs")')

    def test_multiple_keeps_every_push_in_order(self):
        self.create_template(
            "cotton/row.html",
            """<c-portal to="rows" multiple><li>{{ label }}</li></c-portal>""",
        )
        self.create_template(
            "portal_multiple_view.html",
            """<c-row label="a" /><c-row label="b" /><c-row label="a" /><ul><c-portal name="rows" /></ul>""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<ul><li>a</li>\n<li>b</li>\n<li>a</li></ul>")

    def test_same_block_in_two_components_shares_a_slot(self):
        self.create_template("cotton/one.html", """<c-portal to="css"><link href="lib.css" /></c-portal>""")
        self.create_template(
            "cotton/two.html",
            """<c-portal to="css">
                <link href="lib.css" />
            </c-portal>""",
        )
        self.create_template("portal_shared_view.html", """<c-one /><c-two />[<c-portal name="css" />]""", "view/")
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '[<link href="lib.css" />]')

    def test_different_blocks_both_render(self):
        self.create_template(
            "portal_two_blocks_view.html",
            """<c-portal to="css"><link href="a.css" /></c-portal>
            <c-portal to="css"><link href="b.css" /></c-portal>
            [<c-portal name="css" />]""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '[<link href="a.css" />\n<link href="b.css" />]')

    def test_push_keeps_inner_indentation(self):
        self.create_template(
            "portal_indent_view.html",
            """<c-portal to="js">
<script>
    if (x) {
        go();
    }
</script>
</c-portal><c-portal name="js" />""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<script>\n    if (x) {\n        go();\n    }\n</script>")

    def test_context_is_available_inside_a_push(self):
        self.create_template(
            "cotton/chart.html",
            """<c-portal to="js" multiple><script>draw("{{ id }}")</script></c-portal>""",
        )
        self.create_template(
            "portal_context_view.html",
            """<c-chart id="sales" /><c-chart id="costs" /><c-portal name="js" />""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, 'draw("sales")')
            self.assertContains(response, 'draw("costs")')

    def test_push_from_isolated_component_reaches_destination(self):
        self.create_template(
            "cotton/sealed.html",
            """<c-portal to="head"><meta name="sealed" /></c-portal>""",
        )
        self.create_template(
            "portal_only_view.html",
            """<c-portal name="head" /><c-sealed only />""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '<meta name="sealed" />')

    def test_push_from_child_template_reaches_parent_layout(self):
        self.create_template(
            "portal_layout.html",
            """<html><head><c-portal name="head" /></head><body>{% block content %}{% endblock %}</body></html>""",
        )
        self.create_template(
            "portal_extends_view.html",
            """{% extends "portal_layout.html" %}
            {% block content %}<c-portal to="head"><title>Child</title></c-portal>page{% endblock %}""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<head><title>Child</title></head><body>page</body>")

    def test_destination_without_pushes_renders_empty(self):
        self.create_template("portal_empty_view.html", """<head>[<c-portal name="head" />]</head>""", "view/")
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<head>[]</head>")

    def test_push_without_destination_is_dropped(self):
        self.create_template(
            "portal_orphan_view.html",
            """<c-portal to="nowhere"><script></script></c-portal>body""",
            "view/",
        )
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertEqual(response.content.decode().strip(), "body")

    def test_works_with_render_to_string(self):
        self.create_template(
            "portal_string.html",
            """<c-portal to="foot">late</c-portal>[<c-portal name="foot" />]""",
        )
        self.assertIn("[late]", render_to_string("portal_string.html"))

    def test_string_templates_are_resolved_too(self):
        # Resolution hangs off Template.render, so it is not tied to the loader.
        compiled = get_compiled('<c-portal to="x">y</c-portal>[<c-portal name="x" />]')
        self.assertEqual(Template(compiled).render(Context({})), "[y]")

    def test_portals_do_not_touch_ordinary_output(self):
        self.assertEqual(Template("<p>{{ v }}</p>").render(Context({"v": "<x>"})), "<p>&lt;x&gt;</p>")
