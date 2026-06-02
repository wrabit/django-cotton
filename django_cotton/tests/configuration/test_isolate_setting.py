import warnings

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
        with self.settings(COTTON_ISOLATE_BY_DEFAULT=False, COTTON_ENABLE_CONTEXT_ISOLATION=False):
            rendered = get_rendered(html, context)
            self.assertIn("Child: I am from parent", rendered)

        # Case 2: Global isolation enabled
        with self.settings(COTTON_ISOLATE_BY_DEFAULT=True):
            rendered = get_rendered(html, context)
            self.assertIn("Child: ", rendered)
            self.assertNotIn("I am from parent", rendered)

    def test_legacy_setting_emits_deprecation_warning(self):
        """COTTON_ENABLE_CONTEXT_ISOLATION should still work but emit a DeprecationWarning."""
        # Reset the one-shot flag so the warning fires for this test
        from django_cotton.templatetags import _component as component_module
        component_module._deprecation_warned = False

        self.create_template("cotton/child.html", "Child: {{ parent_var }}")
        html = """<c-child />"""
        context = {"parent_var": "leak"}

        with self.settings(COTTON_ENABLE_CONTEXT_ISOLATION=True, COTTON_ISOLATE_BY_DEFAULT=False):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                rendered = get_rendered(html, context)

        # Behavior still applies (parent var blocked)
        self.assertNotIn("leak", rendered)

        # And the deprecation warning was emitted
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)
                        and "COTTON_ENABLE_CONTEXT_ISOLATION" in str(w.message)]
        self.assertTrue(deprecations, "Expected DeprecationWarning for COTTON_ENABLE_CONTEXT_ISOLATION")

    def test_explicit_only_still_works_with_global_isolation_enabled(self):
        """`only` should remain total isolation even when COTTON_ISOLATE_BY_DEFAULT is True."""
        self.create_template(
            "cotton/child.html",
            "Child: {{ parent_var }}",
        )

        html = """<c-child only />"""
        context = {"parent_var": "I am from parent"}

        with self.settings(COTTON_ISOLATE_BY_DEFAULT=True):
            rendered = get_rendered(html, context)
            self.assertIn("Child: ", rendered)
            self.assertNotIn("I am from parent", rendered)
