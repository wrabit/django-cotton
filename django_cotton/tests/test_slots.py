from django_cotton.tests.utils import CottonTestCase
from django_cotton.tests.utils import get_compiled


class SlotTests(CottonTestCase):
    def test_named_slots_correctly_display_in_loop(self):
        self.create_template(
            "named_slot_in_loop_view.html",
            """
                {% for item in items %}
                    <c-named-slot-component>
                        <c-slot name="name">
                            item name: {{ item.name }}
                        </c-slot>
                    </c-named-slot-component>
                {% endfor %}  
            """,
            "view/",
            context={
                "items": [
                    {"name": "Item 1"},
                    {"name": "Item 2"},
                    {"name": "Item 3"},
                ]
            },
        )

        self.create_template(
            "cotton/named_slot_component.html",
            """,
            <div>
                {{ name }}
            </div>        
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "item name: Item 1")
            self.assertContains(response, "item name: Item 2")
            self.assertContains(response, "item name: Item 3")

    def test_named_slots_dont_bleed_into_sibling_components(self):
        self.create_template(
            "slot_bleed_view.html",
            """
                <c-slot-bleed id="1"> 
                    <c-slot name="named_slot">named slot 1</c-slot>
                </c-slot-bleed>
                <c-slot-bleed id="2"></c-slot-bleed>        
            """,
            "view/",
        )

        self.create_template(
            "cotton/slot_bleed.html", """named_slot {{ id }}: '{{ named_slot }}'</p>"""
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertTrue("named_slot 1: 'named slot 1'" in response.content.decode())
            self.assertTrue("named_slot 2: ''" in response.content.decode())

    def test_vars_are_converted_to_vars_frame_tags(self):
        compiled = get_compiled(
            """<c-vars var1="string with space" />
            content
            """
        )

        self.assertEqual(
            compiled,
            """{% vars var1="string with space" %}
            content
            {% endvars %}""",
        )

    def test_cvars_with_nested_quotes_in_django_filters(self):
        """Test that cvars can handle Django filters with nested quotes"""
        import datetime

        self.create_template(
            "cvars_nested_quotes_view.html",
            """
                <c-cvars-nested-quotes />
            """,
            "view/",
            context={
                "date": datetime.date(2024, 3, 15),
                "user": None,
            },
        )

        self.create_template(
            "cotton/cvars_nested_quotes.html",
            """
            <c-vars
                formatted_date="{{ date|date:"Y-m-d" }}"
                user_name="{{ user|default:"Guest" }}"
            />

            Date: {{ formatted_date }}
            User: {{ user_name }}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Date: 2024-03-15")
            self.assertContains(response, "User: Guest")

    def test_named_slot_missing(self):
        self.create_template(
            "test_empty_cvars_view.html",
            """
                <c-empty-cvars />
            """,
            "view/",
        )

        self.create_template(
            "cotton/empty_cvars.html",
            """,
            <c-vars test1="None" test2="" test3 test4=None />

            test1: '{{ test1 }}'
            test2: '{{ test2 }}'
            test3: '{{ test3 }}'
            test4: '{{ test4 }}'
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "test1: 'None'")
            self.assertContains(response, "test2: ''")
            self.assertContains(response, "test3: ''")
            self.assertContains(response, "test4: 'None'")
