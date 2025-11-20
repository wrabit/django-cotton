from django_cotton.tests.utils import CottonTestCase
from django_cotton import render_component
from django.test import RequestFactory


class TestRenderComponentHelper(CottonTestCase):
    """
    Tests for rendering Cotton components from views for HTMX responses.
    """

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_render_component_helper_with_static_cvars(self):
        self.create_template(
            "cotton/button_for_htmx.html",
            """
            <c-vars pk />
            <div>PK: {{ pk }}</div>
            """,
        )

        rendered = render_component(self.request, "button_for_htmx", {"pk": 123})

        self.assertIn("PK: 123", rendered)

    def test_render_component_helper_with_multiple_vars(self):
        self.create_template(
            "cotton/user_card_for_htmx.html",
            """
            <c-vars id first_name last_name />
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

        self.assertIn('id="user-42"', rendered)
        self.assertIn('href="/users/42"', rendered)
        self.assertIn("John Doe", rendered)

    def test_render_component_helper_with_kwargs(self):
        self.create_template(
            "cotton/greeting.html",
            """
            <c-vars name />
            <p>Hello, {{ name }}!</p>
            """,
        )

        rendered = render_component(self.request, "greeting", name="World")

        self.assertIn("Hello, World!", rendered)

    def test_render_component_helper_with_kwargs_and_request(self):
        from django.contrib.auth.models import User

        self.create_template(
            "cotton/user_badge.html",
            """
            <c-vars user_id username />
            <div>
                <span>{{ username }}</span>
                {% if request.user.is_authenticated %}
                    <span>(authenticated)</span>
                {% endif %}
            </div>
            """,
        )

        user = User.objects.create_user(username="testuser", password="testpass")
        self.request.user = user

        rendered = render_component(self.request, "user_badge", user_id=42, username="johndoe")

        self.assertIn("johndoe", rendered)
        self.assertIn("(authenticated)", rendered)

    def test_render_component_with_nested_components(self):
        # Create an inner component
        self.create_template(
            "cotton/inner.html",
            """
            <c-vars label />
            <span class="inner">{{ label }}</span>
            """,
        )

        self.create_template(
            "cotton/outer.html",
            """
            <c-vars title />
            <div class="outer">
                <h3>{{ title }}</h3>
                <c-inner label="Nested content" />
            </div>
            """,
        )

        rendered = render_component(self.request, "outer", title="Parent")

        self.assertIn("Parent", rendered)
        self.assertIn("Nested content", rendered)
        self.assertIn('class="outer"', rendered)
        self.assertIn('class="inner"', rendered)

    def test_render_component_attrs_excludes_cvars(self):
        self.create_template(
            "cotton/button.html",
            """
            <c-vars label />
            <button {{ attrs }} class="btn">{{ label }}</button>
            """,
        )

        rendered = render_component(
            self.request,
            "button",
            {"label": "Click me", "hx-post": "/submit", "hx-target": "#result"},
        )

        self.assertIn("Click me", rendered)

        self.assertIn('hx-post="/submit"', rendered)
        self.assertIn('hx-target="#result"', rendered)

        self.assertNotIn("label=", rendered)
