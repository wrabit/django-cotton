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

        # Override URLconf
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


class DefaultLayoutFallbackTests(CottonTestCase):
    """A component at the default layout, cotton/<snake_case>.html, resolves
    whatever COTTON_DIR or COTTON_SNAKE_CASED_NAMES is set to."""

    def test_default_layout_resolves_with_custom_cotton_dir(self):
        self.create_template("cotton/pkg/icon.html", "default layout")
        self.create_template("pkg_dir_view.html", "<c-pkg.icon />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR="components"):
            response = self.client.get("/view/")
            self.assertContains(response, "default layout")

    def test_configured_location_wins_over_default_layout_with_custom_cotton_dir(self):
        self.create_template("cotton/pkg/icon.html", "default layout")
        self.create_template("components/pkg/icon.html", "configured location")
        self.create_template("pkg_dir_precedence_view.html", "<c-pkg.icon />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR="components"):
            response = self.client.get("/view/")
            self.assertContains(response, "configured location")
            self.assertNotContains(response, "default layout")

    def test_default_layout_resolves_with_hyphenated_names(self):
        # Created before the override: create_template rewrites names when snake case is off
        self.create_template("cotton/pkg/snake_icon.html", "default layout")
        self.create_template("pkg_hyphen_view.html", "<c-pkg.snake-icon />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_SNAKE_CASED_NAMES=False):
            response = self.client.get("/view/")
            self.assertContains(response, "default layout")

    def test_configured_location_wins_over_default_layout_with_hyphenated_names(self):
        self.create_template("cotton/pkg/snake_icon.html", "default layout")
        self.create_template("cotton/pkg/snake-icon.html", "configured location")
        self.create_template("pkg_hyphen_precedence_view.html", "<c-pkg.snake-icon />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_SNAKE_CASED_NAMES=False):
            response = self.client.get("/view/")
            self.assertContains(response, "configured location")
            self.assertNotContains(response, "default layout")

    def test_default_layout_resolves_with_both_settings_changed(self):
        self.create_template("cotton/pkg/snake_icon.html", "default layout")
        self.create_template("pkg_both_view.html", "<c-pkg.snake-icon />", "view/")

        with self.settings(
            ROOT_URLCONF=self.url_conf(), COTTON_DIR="components", COTTON_SNAKE_CASED_NAMES=False
        ):
            response = self.client.get("/view/")
            self.assertContains(response, "default layout")

    def test_default_layout_index_file_resolves_with_custom_cotton_dir(self):
        self.create_template("cotton/pkg/widget/index.html", "default layout index")
        self.create_template("pkg_index_view.html", "<c-pkg.widget />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR="components"):
            response = self.client.get("/view/")
            self.assertContains(response, "default layout index")

    def test_missing_component_error_lists_paths_tried(self):
        from django.template import TemplateDoesNotExist

        self.create_template("pkg_missing_view.html", "<c-pkg.nope />", "view/")

        with self.settings(ROOT_URLCONF=self.url_conf(), COTTON_DIR="components"):
            with self.assertRaises(TemplateDoesNotExist) as cm:
                self.client.get("/view/")

        message = str(cm.exception)
        self.assertIn("components/pkg/nope.html", message)
        self.assertIn("cotton/pkg/nope.html", message)
