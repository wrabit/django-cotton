from django_cotton.tests.utils import CottonTestCase


class SelfClosingComponentTests(CottonTestCase):
    def test_self_closing_with_attributes(self):
        self.create_template(
            "cotton/attr_comp.html",
            """
                <c-vars title />
                <h1>{{ title }}</h1>
            """,
        )

        self.create_template(
            "attr_view.html",
            """
                <c-attr-comp title="Test Title" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<h1>Test Title</h1>")

    def test_self_closing_with_native_template_syntax(self):
        self.create_template(
            "cotton/msg_comp.html",
            """
                <c-vars message />
                <p>{{ message }}</p>
            """,
        )

        self.create_template(
            "msg_view.html",
            """
                {% load cotton %}
                {% cotton msg_comp message="Hello" / %}
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<p>Hello</p>")
