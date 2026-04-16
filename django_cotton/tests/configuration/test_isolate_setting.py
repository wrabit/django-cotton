from django.test import override_settings
from django_cotton.tests.utils import CottonTestCase, get_rendered

class IsolateSettingTests(CottonTestCase):
    def test_isolate_by_default_setting(self):
        self.create_template(
            "cotton/child.html",
            """Child: {{ parent_var }}""",
        )

        html = """<c-child />"""
        context = {"parent_var": "I am from parent"}

        # Case 1: Default behavior (not isolated by default)
        # Note: We need to ensure COTTON_ENABLE_CONTEXT_ISOLATION is False to see full inheritance
        with self.settings(COTTON_ISOLATE_BY_DEFAULT=False, COTTON_ENABLE_CONTEXT_ISOLATION=False):
            rendered = get_rendered(html, context)
            self.assertIn("Child: I am from parent", rendered)

        # Case 2: Global isolation enabled
        with self.settings(COTTON_ISOLATE_BY_DEFAULT=True):
            rendered = get_rendered(html, context)
            self.assertIn("Child: ", rendered)
            self.assertNotIn("I am from parent", rendered)

    def test_explicit_only_overrides_global_default_if_needed(self):
        # This test is just to ensure that if global is False, explicit 'only' still works
        self.create_template(
            "cotton/child.html",
            "Child: {{ parent_var }}",
        )

        html = """<c-child only />"""
        context = {"parent_var": "I am from parent"}

        with self.settings(COTTON_ISOLATE_BY_DEFAULT=False, COTTON_ENABLE_CONTEXT_ISOLATION=False):
            rendered = get_rendered(html, context)
            self.assertIn("Child: ", rendered)
            self.assertNotIn("I am from parent", rendered)
