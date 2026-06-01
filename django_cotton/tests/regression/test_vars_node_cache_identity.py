"""
Regression tests for the <c-vars> node cache.

2.7.0 introduced ``CottonComponentNode._vars_node_cache`` to avoid rescanning a
component template's nodelist for ``CottonVarsNode`` instances on every render.
It was keyed by ``id(template)``, which is only unique among objects alive at the
same time: CPython reuses an address once an object is garbage collected. In
development (DEBUG, no cached template loader) templates are recreated and
discarded constantly, so a freshly loaded template could reuse the address of a
collected, *different* template and inherit its cached vars-node list.

When the wrong (or empty) list is returned, a component's ``<c-vars>`` defaults
are never injected into the context. That surfaces as an intermittent
``VariableDoesNotExist`` when the default is consumed as a *filter argument*
(e.g. ``{{ size_classes|get_item:size }}``), because Django does not swallow
missing-variable errors for filter arguments the way it does for a bare
``{{ size }}``.

The cache is now keyed by the template object itself via a ``WeakKeyDictionary``,
which keys on identity (no address aliasing) and auto-evicts when the template
dies.
"""

import weakref

from django.test import override_settings

from django_cotton.templatetags._component import CottonComponentNode
from django_cotton.tests.utils import CottonTestCase


@override_settings(ROOT_URLCONF="django_cotton.tests.urls")
class VarsNodeCacheIdentityTests(CottonTestCase):
    def test_cache_is_keyed_by_template_identity_not_id(self):
        """The cache must key on the template object, not its id().

        A plain dict keyed by ``id(template)`` is what allowed dev-reload
        address reuse to cross-contaminate components; ``WeakKeyDictionary``
        keys on identity and cannot be aliased.
        """
        self.assertIsInstance(
            CottonComponentNode._vars_node_cache, weakref.WeakKeyDictionary
        )

    def test_cvars_default_applied_when_used_as_filter_argument(self):
        """A <c-vars> default consumed as a filter argument must resolve.

        This is the exact failure mode users hit: when the default is missing
        from context it raises VariableDoesNotExist (filter args are not
        forgiving), rather than silently rendering empty.
        """
        self.create_template(
            "cotton/joined.html",
            "<c-vars sep=\"-\" :items=\"['a', 'b', 'c']\" />{{ items|join:sep }}",
        )
        self.create_template("joined_view.html", "<c-joined />", "joined/")

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/joined/")
            self.assertContains(response, "a-b-c")

    def test_distinct_components_do_not_share_cached_vars(self):
        """Two different component templates must each get their own vars.

        Guards against any cache keying that could return one component's
        vars-node list for another.
        """
        self.create_template(
            "cotton/with_default.html",
            '<c-vars greeting="hello" />{{ greeting }}',
        )
        self.create_template(
            "cotton/other_default.html",
            '<c-vars greeting="goodbye" />{{ greeting }}',
        )
        self.create_template(
            "two_components_view.html",
            "<c-with-default /> <c-other-default />",
            "two/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/two/")
            self.assertContains(response, "hello")
            self.assertContains(response, "goodbye")
