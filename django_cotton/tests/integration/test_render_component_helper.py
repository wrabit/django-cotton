from django_cotton.tests.utils import CottonTestCase
from django_cotton.utils import render_component
from django.test import RequestFactory


class TestRenderComponentHelper(CottonTestCase):
    """
    Tests for rendering Cotton components from views for HTMX responses.

    This tests the use case where you want to render a Cotton component
    directly from a view using render() or render_to_string(), which is
    common with HTMX partial updates.

    GitHub issue: https://github.com/wrabit/django-cotton/issues/179
    """

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_render_component_helper_with_static_cvars(self):
        """
        Test the render_component() helper function.
        This should work with static c-vars (<c-vars pk="" />) by converting them
        to dynamic attributes under the hood.
        """
        self.create_template(
            "cotton/button_for_htmx.html",
            """
            <c-vars pk="" />
            <div>PK: {{ pk }}</div>
            """,
        )

        # Use the render_component helper (now requires request, like Django's render)
        rendered = render_component(self.request, "button_for_htmx", {"pk": 123})

        # This should now work even with static c-vars!
        self.assertIn("PK: 123", rendered)

    def test_render_component_helper_with_multiple_vars(self):
        """
        Test render_component() with multiple variables.
        """
        self.create_template(
            "cotton/user_card_for_htmx.html",
            """
            <c-vars id="" first_name="" last_name="" />
            <div id="user-{{ id }}">
                <a href="/users/{{ id }}">{{ first_name }} {{ last_name }}</a>
            </div>
            """,
        )

        rendered = render_component(
            self.request,
            "user_card_for_htmx",
            {
                "id": 42,
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # All variables should be replaced
        self.assertIn('id="user-42"', rendered)
        self.assertIn('href="/users/42"', rendered)
        self.assertIn("John Doe", rendered)

    def test_render_component_helper_with_kwargs(self):
        """
        Test render_component() can accept kwargs directly.
        """
        self.create_template(
            "cotton/greeting.html",
            """
            <c-vars name="" />
            <p>Hello, {{ name }}!</p>
            """,
        )

        rendered = render_component(self.request, "greeting", name="World")

        self.assertIn("Hello, World!", rendered)

    def test_render_component_helper_with_kwargs_and_request(self):
        """
        Test render_component() with kwargs and request (common HTMX pattern).
        """
        from django.contrib.auth.models import User

        self.create_template(
            "cotton/user_badge.html",
            """
            <c-vars user_id="" username="" />
            <div>
                <span>{{ username }}</span>
                {% if request.user.is_authenticated %}
                    <span>(authenticated)</span>
                {% endif %}
            </div>
            """,
        )

        # Create a real user for testing
        user = User.objects.create_user(username="testuser", password="testpass")
        self.request.user = user

        rendered = render_component(
            self.request,
            "user_badge",
            user_id=42,
            username="johndoe"
        )

        self.assertIn("johndoe", rendered)
        self.assertIn("(authenticated)", rendered)

    def test_render_component_with_nested_components(self):
        """
        Test render_component() with nested Cotton components.
        Ensures cotton_data stack is properly initialized for component nesting.
        """
        # Create an inner component
        self.create_template(
            "cotton/inner.html",
            """
            <c-vars label="" />
            <span class="inner">{{ label }}</span>
            """,
        )

        # Create an outer component that uses the inner component
        self.create_template(
            "cotton/outer.html",
            """
            <c-vars title="" />
            <div class="outer">
                <h3>{{ title }}</h3>
                <c-inner label="Nested content" />
            </div>
            """,
        )

        rendered = render_component(self.request, "outer", title="Parent")

        # Both outer and inner should be rendered correctly
        self.assertIn("Parent", rendered)
        self.assertIn("Nested content", rendered)
        self.assertIn('class="outer"', rendered)
        self.assertIn('class="inner"', rendered)
