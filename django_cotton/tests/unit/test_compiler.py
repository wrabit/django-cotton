import unittest

from django.test import override_settings

from django_cotton.compiler_regex import CottonCompiler, _build_tag_pattern
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
        compiled = get_compiled('<c-test disabled=True count=5 />')
        self.assertIn('disabled=True', compiled)
        self.assertIn('count=5', compiled)
        self.assertNotIn('disabled="True"', compiled)
        self.assertNotIn('count="5"', compiled)

    def test_quoted_attrs_stay_quoted_in_compilation(self):
        compiled = get_compiled('<c-test disabled="True" count="5" />')
        self.assertIn('disabled="True"', compiled)
        self.assertIn('count="5"', compiled)

    def test_mixed_quoted_unquoted_attrs_compilation(self):
        compiled = get_compiled('<c-test quoted="string" unquoted=True />')
        self.assertIn('quoted="string"', compiled)
        self.assertIn('unquoted=True', compiled)
        self.assertNotIn('unquoted="True"', compiled)

    def test_unquoted_cvars_preserved_in_compilation(self):
        compiled = get_compiled('<c-vars enabled=True count=42 />')
        self.assertIn('enabled=True', compiled)
        self.assertIn('count=42', compiled)
        self.assertNotIn('enabled="True"', compiled)
        self.assertNotIn('count="42"', compiled)


class CustomPrefixCompilerUnitTests(unittest.TestCase):
    @override_settings(COTTON_TAG_PREFIX="x")
    def test_compile_component_with_x_prefix(self):
        compiler = CottonCompiler()
        source = '<x-test_button>Click</x-test_button>'
        result = compiler.process(source)
        expected = '{% cotton test_button %}Click{% endcotton %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_compile_self_closing_with_x_prefix(self):
        compiler = CottonCompiler()
        source = '<x-test_button />'
        result = compiler.process(source)
        expected = '{% cotton test_button %}{% endcotton %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_compile_component_with_attrs_x_prefix(self):
        compiler = CottonCompiler()
        source = '<x-test_button class="btn" :count="5">Text</x-test_button>'
        result = compiler.process(source)
        expected = '{% cotton test_button class="btn" :count="5" %}Text{% endcotton %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_compile_xvars_tag(self):
        compiler = CottonCompiler()
        source = '<x-vars title="Test" />'
        result = compiler.process(source)
        expected = '{% cotton:vars title="Test" %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_ignore_components_in_django_comments_x_prefix(self):
        compiler = CottonCompiler()
        source = '{% comment %}<x-test_button />{% endcomment %}'
        result = compiler.process(source)
        self.assertEqual(result, source)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_ignore_components_in_cotton_verbatim_x_prefix(self):
        compiler = CottonCompiler()
        source = '{% cotton:verbatim %}<x-test_button />{% endcotton:verbatim %}'
        result = compiler.process(source)
        expected = '<x-test_button />'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_ignores_c_prefix_tags(self):
        compiler = CottonCompiler()
        source = '<c-test_button>Click</c-test_button>'
        result = compiler.process(source)
        self.assertEqual(result, source)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_slot(self):
        compiler = CottonCompiler()
        source = '<x-slot name="header">Content</x-slot>'
        result = compiler.process(source)
        expected = '{% cotton:slot header %}Content{% endcotton:slot %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_raises_on_slots_without_name(self):
        compiler = CottonCompiler()
        with self.assertRaises(ValueError) as cm:
            compiler.process('<x-slot />')
        self.assertIn("x-slot tag must have a name attribute:", str(cm.exception))

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_raises_on_duplicate_xvars(self):
        compiler = CottonCompiler()
        with self.assertRaises(ValueError) as cm:
            compiler.process('<x-vars />\n<x-vars />')
        self.assertIn("Multiple x-vars tags found", str(cm.exception))

    @override_settings(COTTON_TAG_PREFIX="co")
    def test_custom_multi_char_prefix(self):
        compiler = CottonCompiler()
        source = '<co-test_button>Click</co-test_button>'
        result = compiler.process(source)
        expected = '{% cotton test_button %}Click{% endcotton %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="co")
    def test_multi_char_prefix_self_closing(self):
        compiler = CottonCompiler()
        source = '<co-test_button />'
        result = compiler.process(source)
        expected = '{% cotton test_button %}{% endcotton %}'
        self.assertEqual(result, expected)

    @override_settings(COTTON_TAG_PREFIX="co")
    def test_multi_char_prefix_vars(self):
        compiler = CottonCompiler()
        source = '<co-vars title="Test" />'
        result = compiler.process(source)
        expected = '{% cotton:vars title="Test" %}'
        self.assertEqual(result, expected)

    def test_default_prefix_is_c(self):
        compiler = CottonCompiler()
        self.assertEqual(compiler.prefix, "c")

    def test_build_tag_pattern_c_prefix(self):
        pattern = _build_tag_pattern("c")
        self.assertTrue(pattern.search("<c-test />"))
        self.assertFalse(pattern.search("<x-test />"))

    def test_build_tag_pattern_x_prefix(self):
        pattern = _build_tag_pattern("x")
        self.assertTrue(pattern.search("<x-test />"))
        self.assertFalse(pattern.search("<c-test />"))
