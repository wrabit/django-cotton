import unittest

from django_cotton.tag_parser import (
    _skip_whitespace,
    _parse_component_name,
    _parse_attribute_key,
    _parse_unquoted_value,
    _parse_quoted_value,
    parse_component_tag,
    parse_vars_tag,
)


class TagParserTests(unittest.TestCase):
    def test_skip_whitespace(self):
        self.assertEqual(_skip_whitespace("   hello", 0), 3)
        self.assertEqual(_skip_whitespace("\t\nhello", 0), 2)
        self.assertEqual(_skip_whitespace("hello", 0), 0)
        self.assertEqual(_skip_whitespace("  ", 0), 2)

    def test_parse_component_name(self):
        name, idx = _parse_component_name("test_button class='test'", 0)
        self.assertEqual(name, "test_button")
        self.assertEqual(idx, 11)

        name, idx = _parse_component_name("test_card\tattr='val'", 0)
        self.assertEqual(name, "test_card")
        self.assertEqual(idx, 9)

    def test_parse_attribute_key(self):
        key, idx = _parse_attribute_key("class='test'", 0)
        self.assertEqual(key, "class")
        self.assertEqual(idx, 5)

        key, idx = _parse_attribute_key("disabled ", 0)
        self.assertEqual(key, "disabled")
        self.assertEqual(idx, 8)

    def test_parse_unquoted_value(self):
        val, idx = _parse_unquoted_value("true class", 0)
        self.assertEqual(val, "true")
        self.assertEqual(idx, 4)

        val, idx = _parse_unquoted_value("123\t", 0)
        self.assertEqual(val, "123")
        self.assertEqual(idx, 3)

    def test_parse_quoted_value_basic(self):
        val, idx = _parse_quoted_value("hello'", 0, "'")
        self.assertEqual(val, "'hello'")
        self.assertEqual(idx, 6)

        val, idx = _parse_quoted_value('world"', 0, '"')
        self.assertEqual(val, '"world"')
        self.assertEqual(idx, 6)

    def test_parse_quoted_value_with_django_vars(self):
        val, idx = _parse_quoted_value('test {{ var }}"', 0, '"')
        self.assertEqual(val, '"test {{ var }}"')
        self.assertEqual(idx, 15)

    def test_parse_quoted_value_with_django_tags(self):
        val, idx = _parse_quoted_value('test {% if x %}yes{% endif %}"', 0, '"')
        self.assertEqual(val, '"test {% if x %}yes{% endif %}"')
        self.assertEqual(idx, 30)

    def test_parse_quoted_value_with_nested_quotes(self):
        val, idx = _parse_quoted_value('id-{{ date|date:"Y-m-d" }}"', 0, '"')
        self.assertEqual(val, '"id-{{ date|date:"Y-m-d" }}"')
        self.assertEqual(idx, 27)

    def test_parse_component_tag_basic(self):
        result = parse_component_tag("cotton test_comp")
        self.assertEqual(result.name, "test_comp")
        self.assertEqual(result.attrs, {})
        self.assertEqual(result.only, False)

    def test_parse_component_tag_with_attrs(self):
        result = parse_component_tag('cotton test_comp class="btn" :count="5"')
        self.assertEqual(result.name, "test_comp")
        self.assertEqual(result.attrs["class"], '"btn"')
        self.assertEqual(result.attrs[":count"], '"5"')

    def test_parse_component_tag_with_only(self):
        result = parse_component_tag("cotton test_comp only")
        self.assertEqual(result.name, "test_comp")
        self.assertEqual(result.only, True)

    def test_parse_component_tag_self_closing(self):
        result = parse_component_tag("cotton test_comp /")
        self.assertEqual(result.name, "test_comp")

        result = parse_component_tag("cotton test_comp / ")
        self.assertEqual(result.name, "test_comp")

    def test_parse_vars_tag_basic(self):
        result = parse_vars_tag("cotton:vars")
        self.assertEqual(result.attrs, {})
        self.assertEqual(result.empty_attrs, [])

    def test_parse_vars_tag_with_attrs(self):
        result = parse_vars_tag('cotton:vars title="Test" count="5"')
        self.assertEqual(result.attrs["title"], '"Test"')
        self.assertEqual(result.attrs["count"], '"5"')
        self.assertEqual(result.empty_attrs, [])

    def test_parse_vars_tag_with_empty_attrs(self):
        result = parse_vars_tag("cotton:vars active disabled")
        self.assertEqual(result.attrs, {})
        self.assertIn("active", result.empty_attrs)
        self.assertIn("disabled", result.empty_attrs)

    def test_parse_component_tag_unquoted_values(self):
        """Unquoted values should be preserved without quotes"""
        result = parse_component_tag('cotton test_comp count=5 disabled=True')
        self.assertEqual(result.attrs["count"], '5')  # No quotes
        self.assertEqual(result.attrs["disabled"], 'True')  # No quotes

    def test_parse_component_tag_quoted_values_have_quotes(self):
        """Quoted values should retain quotes in parsed result"""
        result = parse_component_tag('cotton test_comp count="5" disabled="True"')
        self.assertEqual(result.attrs["count"], '"5"')  # Has quotes
        self.assertEqual(result.attrs["disabled"], '"True"')  # Has quotes

    def test_parse_component_tag_mixed_quoted_unquoted(self):
        """Mix of quoted and unquoted should preserve each correctly"""
        result = parse_component_tag('cotton test_comp quoted="string" unquoted=True number=42')
        self.assertEqual(result.attrs["quoted"], '"string"')  # Quoted
        self.assertEqual(result.attrs["unquoted"], 'True')  # Unquoted
        self.assertEqual(result.attrs["number"], '42')  # Unquoted

    def test_parse_vars_tag_unquoted_values(self):
        """Unquoted values in vars tag should be preserved without quotes"""
        result = parse_vars_tag('cotton:vars enabled=True count=42')
        self.assertEqual(result.attrs["enabled"], 'True')  # No quotes
        self.assertEqual(result.attrs["count"], '42')  # No quotes

    def test_parse_vars_tag_mixed_quoted_unquoted(self):
        """Mix of quoted and unquoted in vars tag should preserve each correctly"""
        result = parse_vars_tag('cotton:vars label="Hello" enabled=True')
        self.assertEqual(result.attrs["label"], '"Hello"')  # Quoted
        self.assertEqual(result.attrs["enabled"], 'True')  # Unquoted

