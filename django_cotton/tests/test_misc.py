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

    def test_only_gives_isolated_context(self):
        self.create_template(
            "cotton/only.html",
            """
                <a class="{{ class|default:"donttouch" }}">test</a>
            """,
        )
        self.create_template(
            "no_only_view.html",
            """
            <c-only />
            """,
            "no_only_view/",
            context={"class": "herebedragons"},  # this should pass to `class` successfully
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/no_only_view/")
            self.assertNotContains(response, "donttouch")
            self.assertContains(response, "herebedragons")

        self.create_template(
            "only_view.html",
            """
            <c-only only />
            """,
            "only_view/",
            context={
                "class": "herebedragons"
            },  # this should not pass to `class` due to `only` being present
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/only_view/")
            self.assertNotContains(response, "herebedragons")
            self.assertContains(response, "donttouch")

        self.create_template(
            "only_view2.html",
            """
            <c-only class="october" only />
            """,
            "only_view2/",
            context={
                "class": "herebedragons"
            },  # this should not pass to `class` due to `only` being present
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/only_view2/")
            self.assertNotContains(response, "herebedragons")
            self.assertNotContains(response, "donttouch")
            self.assertContains(response, "october")

    def test_only_with_dynamic_components(self):
        self.create_template(
            "cotton/dynamic_only.html",
            """
            From parent comp scope: '{{ class }}'
            From view context scope: '{{ view_item }}'
            Direct attribute: '{{ direct }}'
            """,
        )

        self.create_template(
            "cotton/middle_component.html",
            """
            <c-component is="{{ comp }}" only direct="yes" />
            """,
        )

        self.create_template(
            "dynamic_only_view.html",
            """<c-middle-component class="mb-5" />""",
            "view/",
            context={"comp": "dynamic_only", "view_item": "blee"},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "From parent comp scope: ''")
            self.assertContains(response, "From view context scope: ''")
            self.assertContains(response, "Direct attribute: 'yes'")

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
