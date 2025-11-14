import unittest

from django_cotton.compiler_regex import CottonCompiler
from django_cotton.tests.utils import get_compiled


class CompilerUnitTests(unittest.TestCase):
    def setUp(self):
        self.compiler = CottonCompiler()

    def test_compile_cvars_tag(self):
        source = '<c-vars title="Test" />'
        result = self.compiler.process(source)
        expected = '{% cotton:vars title="Test" %}'
        self.assertEqual(result, expected)

    def test_compile_component_tag(self):
        source = '<c-test_button>Click</c-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton test_button %}Click{% endcotton %}'
        self.assertEqual(result, expected)

    def test_compile_self_closing_component(self):
        source = '<c-test_button />'
        result = self.compiler.process(source)
        expected = '{% cotton test_button %}{% endcotton %}'
        self.assertEqual(result, expected)

    def test_compile_component_with_attrs(self):
        source = '<c-test_button class="btn" :count="5">Text</c-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton test_button class="btn" :count="5" %}Text{% endcotton %}'
        self.assertEqual(result, expected)

    def test_ignore_components_in_django_comments(self):
        source = '{% comment %}<c-test_button />{% endcomment %}'
        result = self.compiler.process(source)
        self.assertEqual(result, source)

    def test_ignore_components_in_django_verbatim(self):
        source = '{% verbatim %}<c-test_button />{% endverbatim %}'
        result = self.compiler.process(source)
        self.assertEqual(result, source)

        # Test named verbatim blocks
        source_named = '{% verbatim myblock %}<c-test_button />{% endverbatim myblock %}'
        result_named = self.compiler.process(source_named)
        self.assertEqual(result_named, source_named)

    def test_ignore_components_in_template_comments(self):
        source = '{# <c-test_button /> #}'
        result = self.compiler.process(source)
        self.assertEqual(result, source)

    def test_ignore_components_in_cotton_verbatim(self):
        source = '{% cotton:verbatim %}<c-test_button />{% endcotton:verbatim %}'
        result = self.compiler.process(source)
        expected = '<c-test_button />'
        self.assertEqual(result, expected)

    def test_preserve_django_template_tags(self):
        source = '<c-test_button>{% if True %}Yes{% endif %}</c-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton test_button %}{% if True %}Yes{% endif %}{% endcotton %}'
        self.assertEqual(result, expected)

    def test_preserve_django_variables(self):
        source = '<c-test_button>{{ user.name }}</c-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton test_button %}{{ user.name }}{% endcotton %}'
        self.assertEqual(result, expected)

    def test_preserve_regular_html(self):
        source = '<div class="test"><p>Hello</p></div>'
        result = self.compiler.process(source)
        self.assertEqual(source, result)

    def test_compile_stage_ignores_django_vars_and_tags(self):
        compiled = get_compiled(
            """
            {# I'm a comment with a cotton tag <c-vars /> #}
            {% comment %}I'm a django comment with a cotton tag <c-hello />{% endcomment %}
            {{ '<c-vars />'|safe }}
            {% cotton:verbatim %}<c-ignoreme />{% endcotton:verbatim %}
        """
        )

        self.assertIn(
            "{# I'm a comment with a cotton tag <c-vars /> #}",
            compiled,
        )
        self.assertIn(
            "{% comment %}I'm a django comment with a cotton tag <c-hello />{% endcomment %}",
            compiled,
        )
        self.assertIn(
            "{{ '<c-vars />'|safe }}",
            compiled,
        )
        self.assertIn("<c-ignoreme />", compiled)
        self.assertNotIn("{% cotton:verbatim %}", compiled)

    def test_raises_error_on_duplicate_cvars(self):
        with self.assertRaises(ValueError) as cm:
            get_compiled(
                """
                <c-vars />
                <c-vars />
            """
            )

        self.assertEqual(
            str(cm.exception),
            "Multiple c-vars tags found in component template. Only one c-vars tag is allowed per template.",
        )

    def test_raises_on_slots_without_name(self):
        with self.assertRaises(ValueError) as cm:
            get_compiled(
                """
                <c-slot />
            """
            )

        self.assertIn("c-slot tag must have a name attribute:", str(cm.exception))
