from django.test import override_settings

from django_cotton.tests.utils import CottonTestCase


class ContextIsolationTests(CottonTestCase):
    def test_only_gives_isolated_context(self):
        self.create_template(
            "cotton/only.html",
            """
                <a class="{{ class|default:"donttouch" }}">test</a>
            """,
        )

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
            """<c-middle-component class="mb-5" comp="dynamic_only" />""",
            "view/",
            context={"view_item": "blee"},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "From parent comp scope: ''")
            self.assertContains(response, "From view context scope: ''")
            self.assertContains(response, "Direct attribute: 'yes'")

    @override_settings(COTTON_ENABLE_CONTEXT_ISOLATION=False)
    def test_legacy_context_behaviour(self):
        """Test components do not have isolated context"""
        self.create_template(
            "cotton/legacy.html",
            """
            global_item: "{{ global_item }}"
            """,
        )

        self.create_template(
            "legacy_view.html",
            """<c-legacy class="mb-5" direct="yes" />""",
            "view/",
            context={"global_item": "blee"},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "blee")

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
            self.assertNotContains(response, "shouldnotbeseen")
            self.assertContains(response, "hello")
            self.assertContains(response, "logo.png")
            self.assertNotContains(response, 'csrf: ""')
            self.assertContains(response, 'user: "AnonymousUser"')
            self.assertNotContains(response, 'perms: ""')
