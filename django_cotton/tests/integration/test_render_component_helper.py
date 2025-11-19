from django_cotton.tests.utils import CottonTestCase
from django_cotton.utils import render_component


class TestRenderComponentHelper(CottonTestCase):
    """
    Tests for rendering Cotton components from views for HTMX responses.

    This tests the use case where you want to render a Cotton component
    directly from a view using render() or render_to_string(), which is
    common with HTMX partial updates.

    GitHub issue: https://github.com/wrabit/django-cotton/issues/179
    """

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

        # Use the render_component helper instead of render_to_string
        rendered = render_component("cotton/button_for_htmx.html", {"pk": 123})

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
            "cotton/user_card_for_htmx.html",
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

        rendered = render_component("cotton/greeting.html", name="World")

        self.assertIn("Hello, World!", rendered)
