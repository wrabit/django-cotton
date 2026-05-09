from django.test import override_settings

from django_cotton.tests.utils import CottonTestCase, get_rendered


class MiscComponentTests(CottonTestCase):
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

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR=custom_dir):
            response = self.client.get("/view/")
            self.assertContains(response, '<div class="i-am-component">')
            self.assertContains(response, "Hello, World!")

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

    @override_settings(COTTON_SNAKE_CASED_NAMES=False)
    def test_hyphen_naming_convention(self):
        self.create_template(
            "cotton/some-subfolder/hyphen-naming-convention.html",
            "I have a hyphenated component name",
        )

        html = """
            <c-some-subfolder.hyphen-naming-convention />
        """

        rendered = get_rendered(html)

        self.assertTrue("I have a hyphenated component name" in rendered)

    def test_multiple_app_subdirectory_access(self):
        self.create_template(
            "cotton/app_dir.html",
            "I'm from app templates!",
        )

        html = """
            <c-app-dir />
            <c-project-root />
            <c-app2.sub />
        """

        rendered = get_rendered(html)

        self.assertTrue("I'm from app templates!" in rendered)
        self.assertTrue("I'm from project root templates!" in rendered)
        self.assertTrue("i'm sub in project root" in rendered)

    def test_index_file_access(self):
        self.create_template(
            "cotton/accordion/index.html",
            "I'm an index file!",
        )

        html = """
            <c-accordion />
        """

        rendered = get_rendered(html)

        self.assertTrue("I'm an index file!" in rendered)


class CustomTagPrefixTests(CottonTestCase):
    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_renders_component(self):
        self.create_template(
            "cotton/prefix_button.html",
            """<div class="x-prefix-component">{{ slot }}</div>""",
        )

        self.create_template(
            "x_prefix_view.html",
            """<x-prefix-button>Hello from x prefix!</x-prefix-button>""",
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_TAG_PREFIX="x"):
            response = self.client.get("/view/")
            self.assertContains(response, '<div class="x-prefix-component">')
            self.assertContains(response, "Hello from x prefix!")

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_self_closing_renders(self):
        self.create_template(
            "cotton/self_close_x.html",
            """I am self-closed with x prefix!""",
        )

        self.create_template(
            "x_self_close_view.html",
            """<x-self-close-x />""",
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_TAG_PREFIX="x"):
            response = self.client.get("/view/")
            self.assertContains(response, "I am self-closed with x prefix!")

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_passes_attributes(self):
        self.create_template(
            "cotton/attr_comp_x.html",
            """<div class="{{ class }}">{{ label }}</div>""",
        )

        self.create_template(
            "x_attr_view.html",
            """<x-attr-comp-x class="btn-primary" label="Click me" />""",
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_TAG_PREFIX="x"):
            response = self.client.get("/view/")
            self.assertContains(response, 'class="btn-primary"')
            self.assertContains(response, "Click me")

    @override_settings(COTTON_TAG_PREFIX="x")
    def test_x_prefix_with_dot_notation(self):
        self.create_template(
            "cotton/ui/dot_button_x.html",
            """<button>{{ slot }}</button>""",
        )

        self.create_template(
            "x_dot_view.html",
            """<x-ui.dot-button-x>Dot notation!</x-ui.dot-button-x>""",
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_TAG_PREFIX="x"):
            response = self.client.get("/view/")
            self.assertContains(response, "<button>")
            self.assertContains(response, "Dot notation!")
