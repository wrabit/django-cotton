from django.test import TestCase

from django_cotton.tests.utils import get_compiled, get_rendered


class CottonTestCase(TestCase):
    def test_parent_component_is_rendered(self):
        response = self.client.get("/parent")
        self.assertContains(response, '<div class="i-am-parent">')

    def test_child_is_rendered(self):
        response = self.client.get("/child")
        self.assertContains(response, '<div class="i-am-parent">')
        self.assertContains(response, '<div class="i-am-child">')

    def test_self_closing_is_rendered(self):
        response = self.client.get("/self-closing")
        self.assertContains(response, '<div class="i-am-parent">')

    def test_named_slots_correctly_display_in_loop(self):
        response = self.client.get("/named-slot-in-loop")
        self.assertContains(response, "item name: Item 1")
        self.assertContains(response, "item name: Item 2")
        self.assertContains(response, "item name: Item 3")

    def test_attribute_passing(self):
        response = self.client.get("/attribute-passing")
        self.assertContains(
            response, '<div and-another="woo1" attribute_1="hello" thirdforluck="yes">'
        )

    def test_attribute_merging(self):
        response = self.client.get("/attribute-merging")
        self.assertContains(
            response, 'class="form-group another-class-with:colon extra-class"'
        )

    def test_django_syntax_decoding(self):
        response = self.client.get("/django-syntax-decoding")
        self.assertContains(response, "some-class")

    def test_vars_are_converted_to_vars_frame_tags(self):
        compiled = get_compiled(
            """
            <c-vars var1="string with space" />
            
            content
        """
        )

        self.assertEquals(
            compiled,
            """{% cotton_vars_frame var1=var1|default:"string with space" %}content{% endcotton_vars_frame %}""",
        )

    def test_attrs_do_not_contain_vars(self):
        response = self.client.get("/vars-test")
        self.assertContains(response, "attr1: 'im an attr'")
        self.assertContains(response, "var1: 'im a var'")
        self.assertContains(response, """attrs: 'attr1="im an attr"'""")

    def test_strings_with_spaces_can_be_passed(self):
        response = self.client.get("/string-with-spaces")
        self.assertContains(response, "attr1: 'I have spaces'")
        self.assertContains(response, "var1: 'string with space'")
        self.assertContains(response, "default_var: 'default var'")
        self.assertContains(response, "named_slot: '")
        self.assertContains(response, "named_slot with spaces")
        self.assertContains(response, """attrs: 'attr1="I have spaces"'""")

    def test_named_slots_dont_bleed_into_sibling_components(self):
        html = """
            <c-test-component>
                component1 
                <c-slot name="named_slot">named slot 1</c-slot>
            </c-test-component>
            <c-test-component>
                component2 
            </c-test-component>
        """

        rendered = get_rendered(html)

        self.assertTrue("named_slot: 'named slot 1'" in rendered)
        self.assertTrue("named_slot: ''" in rendered)

    def test_template_variables_are_not_parsed(self):
        html = """
            <c-test-component attr1="variable" :attr2="variable">
                <c-slot name="named_slot">
                    <a href="#" silica:click.prevent="variable = 'lineage'">test</a>
                </c-slot>
            </c-test-component>
        """

        rendered = get_rendered(html, {"variable": 1})

        self.assertTrue("attr1: 'variable'" in rendered)
        self.assertTrue("attr2: '1'" in rendered)

    def test_valueless_attributes_are_process_as_true(self):
        response = self.client.get("/test/valueless-attributes")

        self.assertContains(response, "It's True")
