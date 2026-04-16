from django.test import override_settings
from django_cotton.tests.utils import CottonTestCase

class ProcessDefaultTests(CottonTestCase):
    def test_process_by_default_true(self):
        self.create_template(
            "cotton/simple.html",
            "I am a component",
        )
        self.create_template(
            "view.html",
            "<c-simple />",
            "view/"
        )

        with self.settings(COTTON_PROCESS_BY_DEFAULT=True, ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "I am a component")

    def test_process_by_default_false_blocks_compilation(self):
        self.create_template(
            "cotton/simple.html",
            "I am a component",
        )
        self.create_template(
            "view.html",
            "<c-simple />",
            "view/"
        )

        with self.settings(COTTON_PROCESS_BY_DEFAULT=False, ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # It should not be processed, so it will just be rendered as raw <c-simple />
            self.assertContains(response, "<c-simple />")
            self.assertNotIn("I am a component", response.content.decode())

    def test_process_by_default_false_with_enable_tag(self):
        self.create_template(
            "cotton/simple.html",
            "I am a component",
        )
        self.create_template(
            "view.html",
            "{% cotton_enable %}<c-simple />",
            "view/"
        )

        with self.settings(COTTON_PROCESS_BY_DEFAULT=False, ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "I am a component")
            # The tag itself should be stripped
            self.assertNotIn("{% cotton_enable %}", response.content.decode())
