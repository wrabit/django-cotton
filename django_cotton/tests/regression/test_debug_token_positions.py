"""
With debug on, Django reads ``token.position`` to build the error page. The
cotton tokenizer used to leave it as None on cotton tags (a TypeError hid the
real error) and relative to a chunk on the tokens after one.
"""

from django.template import Context, Engine, TemplateDoesNotExist, TemplateSyntaxError

from django_cotton.tests.utils import CottonTestCase, get_compiled


class DebugTokenPositionTests(CottonTestCase):
    def setUp(self):
        self.engine = Engine(debug=True, builtins=["django_cotton.templatetags.cotton"])

    def test_error_in_component_keeps_original_exception(self):
        source = get_compiled("<p>hi</p><c-does-not-exist />")
        template = self.engine.from_string(source)

        with self.assertRaises(TemplateDoesNotExist) as cm:
            template.render(Context({}))

        self.assertTrue(cm.exception.template_debug["during"].startswith("{% cotton does-not-exist"))

    def test_error_after_component_points_at_failing_tag(self):
        source = get_compiled('<c-x label="a" />\n{{ value|no_such_filter }}')

        with self.assertRaises(TemplateSyntaxError) as cm:
            self.engine.from_string(source)

        debug = cm.exception.template_debug
        self.assertEqual(debug["during"], "{{ value|no_such_filter }}")
        self.assertEqual(debug["line"], 2)
