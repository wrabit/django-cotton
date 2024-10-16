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

    def test_context_isolated_by_default(self):
        self.create_template(
            "cotton/receiver.html",
            """
            {{ global }} 
            {{ direct }} 
            {{ from_context_processor }}
            
            Some context from django builtins:
            csrf: "{{ csrf_token }}" 
            request: "{{ request }}"
            messages: "{{ messages }}"
            user: "{{ user }}"
            perms: "{{ perms }}"
            debug: "{{ debug }}"
            """,
        )

        self.create_template(
            "context_isolation_view.html",
            """<c-receiver direct="hello" />""",
            "view/",
            context={"global": "shouldnotbeseen"},
        )

        # with example_processor added and 'logo' in the context

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            print(response.content.decode())
            self.assertNotContains(response, "shouldnotbeseen")
            self.assertContains(response, "hello")
            self.assertContains(response, "logo.png")
            self.assertNotContains(response, 'csrf: ""')
            self.assertContains(response, 'user: "AnonymousUser"')
            self.assertNotContains(response, 'perms: ""')
