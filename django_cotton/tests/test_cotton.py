import shutil
import sys

from django.test import TestCase

from django_cotton.tests.utils import get_compiled, get_rendered


from django.urls import path
from django.test import override_settings
from django.views.generic import TemplateView
from django.conf import settings
import os
import tempfile


class DynamicURLModule:
    def __init__(self):
        self.urlpatterns = []

    def __call__(self):
        return self.urlpatterns


class CottonInlineTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_dir = tempfile.mkdtemp()
        cls.url_module = DynamicURLModule()
        cls.url_module_name = f"dynamic_urls_{cls.__name__}"
        sys.modules[cls.url_module_name] = cls.url_module

        # Create a new TEMPLATES setting
        cls.new_templates_setting = settings.TEMPLATES.copy()
        cls.new_templates_setting[0]["DIRS"] = [
            cls.temp_dir
        ] + cls.new_templates_setting[0]["DIRS"]

        # Apply the new setting
        cls.templates_override = override_settings(TEMPLATES=cls.new_templates_setting)
        cls.templates_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.templates_override.disable()
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        del sys.modules[cls.url_module_name]
        super().tearDownClass()

    def create_template(self, name, content):
        path = os.path.join(self.temp_dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    def create_view(self, template_name):
        return TemplateView.as_view(template_name=template_name)

    def create_url(self, url, view):
        url_pattern = path(url, view)
        self.url_module.urlpatterns.append(url_pattern)
        return url_pattern

    def setUp(self):
        super().setUp()
        self.url_module.urlpatterns = []

    def get_url_conf(self):
        return self.url_module_name


class NewTestCase(CottonInlineTestCase):
    def test_parent_component_is_rendered(self):
        # Create component
        self.create_template(
            "cotton/parent.cotton.html",
            """
            <div class="i-am-parent">
                {{ slot }}
            </div>
            """,
        )

        # Create view template
        self.create_template(
            "parent_view.cotton.html",
            """
            <c-parent>
                Hello, World!
            </c-parent>
        """,
        )

        # Create URL
        self.create_url("parent/", self.create_view("parent_view.cotton.html"))

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.get_url_conf()):
            response = self.client.get("/parent/")
            self.assertContains(response, '<div class="i-am-parent">')
            self.assertContains(response, "Hello, World!")


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

    def test_component_attributes_can_converted_to_python_types(self):
        response = self.client.get("/test/eval-attributes")

        self.assertContains(response, "none is None")
        self.assertContains(response, "number is 1")
        self.assertContains(response, "boolean_true is True")
        self.assertContains(response, "boolean_false is False")
        self.assertContains(response, "list.0 is 1")
        self.assertContains(response, "dict.key is 'value'")
        self.assertContains(response, "listdict.0.key is 'value'")

    def test_cvars_can_be_converted_to_python_types(self):
        response = self.client.get("/test/eval-vars")

        self.assertContains(response, "none is None")
        self.assertContains(response, "number is 1")
        self.assertContains(response, "boolean_true is True")
        self.assertContains(response, "boolean_false is False")
        self.assertContains(response, "list.0 is 1")
        self.assertContains(response, "dict.key is 'value'")
        self.assertContains(response, "listdict.0.key is 'value'")

    def test_attributes_can_contain_django_native_tags(self):
        response = self.client.get("/test/native-tags-in-attributes")

        self.assertContains(response, "Attribute 1 says: 'Hello Will'")
        self.assertContains(response, "Attribute 2 says: 'world'")
        self.assertContains(response, "Attribute 3 says: 'cowabonga!'")

        self.assertContains(
            response,
            """attrs tag is: 'normal="normal" attr1="Hello Will" attr2="world" attr3="cowabonga!"'""",
        )

    # TODO: implement inline test asset creation, i.e. store_template("native-tags-in-attributes", """)
