from unittest import skip

from django_cotton.tests.utils import CottonTestCase


class BasicComponentTests(CottonTestCase):
    def test_component_is_rendered(self):
        self.create_template(
            "cotton/render.html",
            """<div class="i-am-component">{{ slot }}</div>""",
        )

        self.create_template(
            "view.html",
            """<c-render>Hello, World!</c-render>""",
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '<div class="i-am-component">')
            self.assertContains(response, "Hello, World!")

    def test_nested_rendering(self):
        self.create_template(
            "cotton/parent.html",
            """
                <div class="i-am-parent">
                    {{ slot }}
                </div>            
            """,
        )

        self.create_template(
            "cotton/child.html",
            """
                <div class="i-am-child"></div>
            """,
        )

        self.create_template(
            "cotton/nested_render_view.html",
            """
            <c-parent>
                <c-child>d</c-child>
            </c-parent>            
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, '<div class="i-am-parent">')
            self.assertContains(response, '<div class="i-am-child">')

    def test_cotton_directory_can_be_configured(self):
        custom_dir = "components"

        self.create_template(
            f"{custom_dir}/custom_directory.html",
            """<div class="i-am-component">{{ slot }}</div>""",
        )

        self.create_template(
            "custom_directory_view.html",
            """<c-custom-directory>Hello, World!</c-custom-directory>""",
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR=custom_dir):
            response = self.client.get("/view/")
            self.assertContains(response, '<div class="i-am-component">')
            self.assertContains(response, "Hello, World!")

    def test_self_closing_is_rendered(self):
        self.create_template("cotton/self_closing.html", """I self closed!""")
        self.create_template(
            "self_closing_view.html",
            """
                1: <c-self-closing/>
                2: <c-self-closing />
                3: <c-self-closing  />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "1: I self closed!")
            self.assertContains(response, "2: I self closed!")
            self.assertContains(response, "3: I self closed!")

    def test_loader_scans_all_app_directories(self):
        self.create_template(
            "app_outside_of_dirs_view.html", """<c-app-outside-of-dirs />""", "view/"
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(
                response,
                """My template path was not specified in settings!""",
            )

    @skip("Not implemented")
    def test_components_have_isolated_context(self):
        self.create_template(
            "cotton/isolated_context.html",
            """{{ outer }}""",
        )git

        self.create_template(
            "isolated_context_view.html",
            """
            <c-isolated-context />
            """,
            "view/",
            context={"outer": "Outer content"},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertNotContains(response, "Outer content")
