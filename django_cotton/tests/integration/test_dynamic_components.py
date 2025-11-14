from django_cotton.tests.utils import CottonTestCase
from django_cotton.tests.utils import get_rendered


class DynamicComponentTests(CottonTestCase):
    def test_dynamic_components_via_string(self):
        self.create_template(
            "cotton/dynamic_component_via_string.html",
            """
            <div>I am dynamic<div>
            """,
        )

        html = """
            <c-component is="dynamic-component-via-string" />
        """

        rendered = get_rendered(html)

        self.assertTrue("I am dynamic" in rendered)

    def test_dynamic_components_via_variable(self):
        self.create_template(
            "cotton/dynamic_component_via_variable.html",
            """
            <div>I am dynamic<div>
            """,
        )

        html = """
            <c-component :is="is" />
        """

        rendered = get_rendered(html, {"is": "dynamic-component-via-variable"})

        self.assertTrue("I am dynamic" in rendered)

    def test_dynamic_components_via_expression(self):
        self.create_template(
            "cotton/dynamic_component_expression.html",
            """
            <div>I am dynamic component from expression<div>
            """,
        )

        html = """
            <c-component is="dynamic-{{ is }}" />
        """

        rendered = get_rendered(html, {"is": "component-expression"})

        self.assertTrue("I am dynamic component from expression" in rendered)

    def test_dynamic_components_in_subfolders(self):
        self.create_template(
            "cotton/subfolder/dynamic_component_expression.html",
            """
            <div>I am dynamic component from expression<div>
            """,
        )

        html = """
            <c-component is="subfolder.{{ is }}" />
        """

        rendered = get_rendered(html, {"is": "dynamic-component-expression"})

        self.assertTrue("I am dynamic component from expression" in rendered)
