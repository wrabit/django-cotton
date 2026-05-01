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

    def test_unquoted_attrs_preserved_in_compilation(self):
        """Unquoted attrs should stay unquoted when HTML is compiled to template tag"""
        compiled = get_compiled('<c-test disabled=True count=5 />')
        self.assertIn('disabled=True', compiled)
        self.assertIn('count=5', compiled)
        # Should NOT wrap in quotes
        self.assertNotIn('disabled="True"', compiled)
        self.assertNotIn('count="5"', compiled)

    def test_quoted_attrs_stay_quoted_in_compilation(self):
        """Quoted attrs should stay quoted when compiled"""
        compiled = get_compiled('<c-test disabled="True" count="5" />')
        self.assertIn('disabled="True"', compiled)
        self.assertIn('count="5"', compiled)

    def test_mixed_quoted_unquoted_attrs_compilation(self):
        """Both quoted and unquoted attrs in same component should be preserved correctly"""
        compiled = get_compiled('<c-test quoted="string" unquoted=True />')
        self.assertIn('quoted="string"', compiled)
        self.assertIn('unquoted=True', compiled)
        # Make sure unquoted isn't wrapped
        self.assertNotIn('unquoted="True"', compiled)

    def test_unquoted_cvars_preserved_in_compilation(self):
        """Unquoted c-vars attrs should stay unquoted"""
        compiled = get_compiled('<c-vars enabled=True count=42 />')
        self.assertIn('enabled=True', compiled)
        self.assertIn('count=42', compiled)
        self.assertNotIn('enabled="True"', compiled)
        self.assertNotIn('count="42"', compiled)

    def test_compile_x_prefix_component_tag(self):
        """x- prefix tags should compile to cotton template tags with x- prefix preserved"""
        source = '<x-test_button>Click</x-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton x-test_button %}Click{% endcotton %}'
        self.assertEqual(result, expected)

    def test_compile_x_prefix_self_closing_component(self):
        """x- prefix self-closing tags should compile correctly"""
        source = '<x-test_button />'
        result = self.compiler.process(source)
        expected = '{% cotton x-test_button %}{% endcotton %}'
        self.assertEqual(result, expected)

    def test_compile_x_prefix_component_with_attrs(self):
        """x- prefix tags with attributes should compile correctly"""
        source = '<x-test_button class="btn" :count="5">Text</x-test_button>'
        result = self.compiler.process(source)
        expected = '{% cotton x-test_button class="btn" :count="5" %}Text{% endcotton %}'
        self.assertEqual(result, expected)

    def test_compile_x_prefix_with_dot_notation(self):
        """x- prefix tags with dot notation should compile correctly"""
        source = '<x-admin.button>Click</x-admin.button>'
        result = self.compiler.process(source)
        expected = '{% cotton x-admin.button %}Click{% endcotton %}'
        self.assertEqual(result, expected)

    def test_x_prefix_ignored_in_django_comments(self):
        """x- prefix tags in Django comments should be ignored"""
        source = '{% comment %}<x-test_button />{% endcomment %}'
        result = self.compiler.process(source)
        self.assertEqual(result, source)

    def test_x_prefix_ignored_in_cotton_verbatim(self):
        """x- prefix tags in cotton:verbatim should be preserved as-is"""
        source = '{% cotton:verbatim %}<x-test_button />{% endcotton:verbatim %}'
        result = self.compiler.process(source)
        expected = '<x-test_button />'
        self.assertEqual(result, expected)

    def test_mixed_c_and_x_prefix_components(self):
        """Both c- and x- prefix tags should work in the same template"""
        source = '<c-wrapper><x-inner>Content</x-inner></c-wrapper>'
        result = self.compiler.process(source)
        expected = '{% cotton wrapper %}{% cotton x-inner %}Content{% endcotton %}{% endcotton %}'
        self.assertEqual(result, expected)
