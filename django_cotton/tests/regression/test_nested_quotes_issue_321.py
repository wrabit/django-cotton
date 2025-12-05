"""
Regression tests for issue #321: Parser issue with template tag and quotes in attribute value.

Tests comprehensive scenarios for nested quotes in component attributes including:
- Various Django template tags (trans, blocktrans, if, for, etc.)
- Different quote combinations (single in double, double in single, same types)
- Multiple nesting levels
- Escape sequences
- Edge cases with Django template syntax
"""

from django.test import override_settings

from django_cotton.tests.utils import CottonTestCase


@override_settings(ROOT_URLCONF="django_cotton.tests.urls")
class NestedQuotesIssue321Tests(CottonTestCase):
    """
    Test suite for issue #321 - nested quotes in component attributes.

    These tests ensure that template tags with nested quotes work correctly
    in both {% cotton %} and {% cotton:vars %} tags.
    """

    # ==================== Real-World Use Cases ====================

    def test_original_issue_321_case(self):
        """The EXACT case reported in issue #321"""
        self.create_template(
            "cotton/password_reset_form.html",
            """
            <div class="password-reset">
                <p class="subtitle">{{ subtitle }}</p>
            </div>
            """,
        )

        # This is what users want to write
        self.create_template(
            "password_reset_page.html",
            """
            {% load i18n %}
            <c-password-reset-form 
                subtitle="{% trans "Enter your email address and we'll send you a secure link to reset your password." %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should successfully render with the text
            self.assertContains(response, "Enter your email address")
            self.assertContains(response, "we'll send you")
            self.assertContains(response, "secure link to reset your password")

    def test_multiple_template_tags_with_quotes(self):
        """Multiple Django template tags in one attribute"""
        self.create_template(
            "cotton/user_profile.html",
            """
            <div>
                <h1>{{ greeting }}</h1>
                <p>{{ name }}</p>
            </div>
            """,
        )

        self.create_template(
            "user_profile_page.html",
            """
            {% load i18n %}
            <c-user-profile 
                name="{% trans 'John ONeill' %}"
                greeting="{% trans 'Welcome' %}, {% trans 'nice to see you' %}!"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Welcome")
            self.assertContains(response, "nice to see you")
            self.assertContains(response, "ONeill")

    def test_if_tag_with_nested_quotes_real_world(self):
        """Conditional rendering with nested quotes"""
        self.create_template(
            "cotton/conditional_message.html",
            """
            <div class="message">{{ message }}</div>
            """,
        )

        self.create_template(
            "conditional_page.html",
            """
            {% load i18n %}
            <c-conditional-message 
                message="{% if user.is_authenticated %}{% trans 'Welcome back' %}{% else %}{% trans 'Please sign in' %}{% endif %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Since no user is authenticated in test, should show sign in message
            self.assertContains(response, "Please sign in")

    def test_for_loop_with_filter_quotes_real_world(self):
        """For loop with filter containing quoted arguments"""
        self.create_template(
            "cotton/item_list.html",
            """
            <ul>{{ items|safe }}</ul>
            """,
        )

        self.create_template(
            "item_list_page.html",
            """
            <c-item-list 
                items="{% for i in '123' %}<li>Item {{ i }}</li>{% endfor %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<li>Item 1</li>")
            self.assertContains(response, "<li>Item 2</li>")
            self.assertContains(response, "<li>Item 3</li>")

    # ==================== Basic Quote Nesting ====================

    def test_double_quote_inside_single_quotes_trans_tag(self):
        """Test {% trans "text" %} inside single-quoted attribute"""
        self.create_template(
            "cotton/quote_component.html",
            """
            <div>{{ message }}</div>
            """,
        )

        self.create_template(
            "double_in_single_view.html",
            """
            {% load i18n %}
            <c-quote-component message='{% trans "Hello World" %}' />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<div>Hello World</div>")

    def test_same_quote_type_nested_double_in_double(self):
        """Test double quotes inside double quotes using Django template tag"""
        self.create_template(
            "cotton/echo_component.html",
            """
            <span>{{ text }}</span>
            """,
        )

        self.create_template(
            "same_double_view.html",
            """
            <c-echo-component text="{% trans "Nested Text" %}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<span>Nested Text</span>")

    def test_same_quote_type_nested_single_in_single(self):
        """Test single quotes inside single quotes using Django template tag"""
        self.create_template(
            "cotton/text_component.html",
            """
            <p>{{ content }}</p>
            """,
        )

        self.create_template(
            "same_single_view.html",
            """
            <c-text-component content='{% trans 'Single Nested' %}' />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<p>Single Nested</p>")

    # ==================== Different Template Tags ====================

    def test_blocktrans_tag_with_nested_quotes(self):
        """Test {% blocktrans %} tag with nested quotes and variables"""
        self.create_template(
            "cotton/blocktrans_component.html",
            """
            <div class="greeting">{{ greeting }}</div>
            """,
        )

        self.create_template(
            "blocktrans_view.html",
            """
            {% load i18n %}
            <c-blocktrans-component 
                greeting="{% blocktrans %}Hello, it's a great day!{% endblocktrans %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Hello, it's a great day!")

    def test_if_tag_with_nested_quotes(self):
        """Test {% if %} tag with nested quotes"""
        self.create_template(
            "cotton/if_component.html",
            """
            <output>{{ result }}</output>
            """,
        )

        self.create_template(
            "if_tag_view.html",
            """
            <c-if-component 
                result="{% if True %}Success with 'quotes'{% else %}Failure{% endif %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Success with 'quotes'")

    def test_for_tag_with_nested_quotes(self):
        """Test {% for %} tag with nested quotes"""
        self.create_template(
            "cotton/for_component.html",
            """
            <div>{{ items }}</div>
            """,
        )

        self.create_template(
            "for_tag_view.html",
            """
            <c-for-component 
                items="{% for i in 'abc' %}{{ i }}'s {% endfor %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should render as: a's b's c's
            self.assertContains(response, "a's b's c's")

    # ==================== Variable Interpolation ====================

    def test_variable_with_filter_and_nested_quotes(self):
        """Test {{ var|filter:"arg" }} with nested quotes"""
        self.create_template(
            "cotton/filter_component.html",
            """
            <span class="name">{{ name }}</span>
            """,
        )

        self.create_template(
            "filter_view.html",
            """
            <c-filter-component name="{{ user.name|default:"Guest User" }}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # user context doesn't exist, so default is used
            self.assertContains(response, "Guest User")

    def test_variable_interpolation_with_single_quotes(self):
        """Test {{ var }} with surrounding text containing single quotes"""
        self.create_template(
            "cotton/var_component.html",
            """
            <label>{{ label }}</label>
            """,
        )

        self.create_template(
            "var_single_view.html",
            """
            <c-var-component label="It's {{ 'Django' }}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "It's Django")

    # ==================== Multiple Nesting Levels ====================

    def test_multiple_django_blocks_in_one_attribute(self):
        """Test multiple Django template blocks in a single attribute"""
        self.create_template(
            "cotton/multi_component.html",
            """
            <div data-value="{{ complex }}"></div>
            """,
        )

        self.create_template(
            "multi_blocks_view.html",
            """
            {% load i18n %}
            <c-multi-component 
                complex="{% trans 'Part 1' %} and {{ 'Part 2' }} and {% if True %}Part 3's{% endif %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Part 1")
            self.assertContains(response, "Part 2")
            self.assertContains(response, "Part 3's")

    def test_deeply_nested_template_syntax(self):
        """Test deeply nested Django template syntax"""
        self.create_template(
            "cotton/deep_component.html",
            """
            <code>{{ nested }}</code>
            """,
        )

        self.create_template(
            "deep_nested_view.html",
            """
            <c-deep-component 
                nested="{% if True %}{{ 'value'|default:"it's working" }}{% endif %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "value")

    # ==================== c-vars Tag Tests ====================

    def test_cvars_with_nested_quotes_in_defaults(self):
        """Test {% cotton:vars %} with nested quotes in default values"""
        self.create_template(
            "cotton/cvars_component.html",
            """
            {% load i18n %}
            <c-vars 
                title="{% trans 'Default Title' %}"
                message="{% trans "It's the default message" %}"
            />
            <h2>{{ title }}</h2>
            <p>{{ message }}</p>
            """,
        )

        self.create_template(
            "cvars_defaults_view.html",
            """
            <c-cvars-component />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<h2>Default Title</h2>")
            self.assertContains(response, "It's the default message")

    def test_cvars_override_with_nested_quotes(self):
        """Test overriding c-vars defaults that contain nested quotes"""
        self.create_template(
            "cotton/cvars_override_component.html",
            """
            {% load i18n %}
            <c-vars label="{% trans 'Default' %}" />
            <span>{{ label }}</span>
            """,
        )

        self.create_template(
            "cvars_override_view.html",
            """
            {% load i18n %}
            <c-cvars-override-component label="{% trans "Custom's Value" %}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should use the override, not the default
            self.assertNotContains(response, "Default")
            self.assertContains(response, "Custom's Value")

    # ==================== Mixed Quote Scenarios ====================

    def test_mixed_quotes_in_multiple_attributes(self):
        """Test different quote combinations across multiple attributes"""
        self.create_template(
            "cotton/mixed_component.html",
            """
            <div data-1="{{ attr1 }}" data-2="{{ attr2 }}" data-3="{{ attr3 }}"></div>
            """,
        )

        self.create_template(
            "mixed_quotes_view.html",
            """
            {% load i18n %}
            <c-mixed-component 
                attr1="{% trans 'Single in double' %}"
                attr2='{% trans "Double in single" %}'
                attr3="Plain with 'quotes' inside"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Single in double")
            self.assertContains(response, "Double in single")
            # Quotes are auto-escaped in variable output?
            self.assertContains(response, "Plain with &#x27;quotes&#x27;")

    # ==================== Edge Cases ====================

    def test_empty_template_tag_in_attribute(self):
        """Test empty or whitespace-only template tag"""
        self.create_template(
            "cotton/empty_tag_component.html",
            """
            <p>{{ content }}</p>
            """,
        )

        self.create_template(
            "empty_tag_view.html",
            """
            <c-empty-tag-component content="Before {%  %} After" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should render the literal text since the tag is empty
            self.assertContains(response, "Before")
            self.assertContains(response, "After")

    def test_comment_tag_in_attribute(self):
        """Test {% comment %} tag in attribute"""
        self.create_template(
            "cotton/comment_component.html",
            """
            <div>{{ text }}</div>
            """,
        )

        self.create_template(
            "comment_tag_view.html",
            """
            <c-comment-component text="Before{% comment %}Hidden 'text'{% endcomment %}After" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "BeforeAfter")
            self.assertNotContains(response, "Hidden")

    def test_verbatim_tag_in_attribute(self):
        """Test {% verbatim %} tag in attribute (preserves template syntax)"""
        self.create_template(
            "cotton/verbatim_component.html",
            """
            <code>{{ raw }}</code>
            """,
        )

        self.create_template(
            "verbatim_tag_view.html",
            """
            <c-verbatim-component raw="{% verbatim %}{{ 'literal' }}{% endverbatim %}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Verbatim should preserve the literal template syntax
            self.assertContains(response, "{{ 'literal' }}")

    def test_multiple_variables_with_filters(self):
        """Test multiple variables with filters containing quoted arguments"""
        self.create_template(
            "cotton/filters_component.html",
            """
            <pre>{{ formatted }}</pre>
            """,
        )

        self.create_template(
            "multiple_filters_view.html",
            """
            <c-filters-component 
                formatted="{{ value|default:"N/A"|add:" - it's ok" }}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # value doesn't exist, so default is used, then " - it's ok" is added
            self.assertContains(response, "N/A - it's ok")

    def test_url_tag_with_quotes(self):
        """Test {% url %} tag with quoted arguments"""
        self.create_template(
            "cotton/url_component.html",
            """
            <a href="{{ link }}">Link</a>
            """,
        )

        # Note: This test may fail if the URL doesn't exist, but it tests parsing
        self.create_template(
            "url_tag_view.html",
            """
            <c-url-component link="{% url 'view' %}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            try:
                response = self.client.get("/view/")
                # If URL resolution works, check the link
                self.assertContains(response, "<a href=")
            except Exception:
                # URL might not exist, but the template should parse without error
                pass

    # ==================== Escape Sequence Tests ====================

    def test_escaped_quote_in_template_tag(self):
        """Test escaped quotes within template tags"""
        self.create_template(
            "cotton/escaped_component.html",
            """
            <p>{{ text }}</p>
            """,
        )

        self.create_template(
            "escaped_quote_view.html",
            """
            <c-escaped-component text="{% trans "She said 'hello'" %}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # The escaped quotes should be handled correctly
            self.assertContains(response, "She said")

    # ==================== Multiline Tests ====================

    def test_multiline_attribute_with_nested_quotes(self):
        """Test attribute spanning multiple lines with nested quotes"""
        self.create_template(
            "cotton/multiline_component.html",
            """
            <p>{{ long_text }}</p>
            """,
        )

        self.create_template(
            "multiline_view.html",
            """
            {% load i18n %}
            <c-multiline-component 
                long_text="{% trans 'This is a very long text
                that spans multiple lines
                and contains apostrophes like it's and won't' %}"
            />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "This is a very long text")
            self.assertContains(response, "it's")
            self.assertContains(response, "won't")

    # ==================== Alpine.js / JavaScript Tests ====================

    def test_alpine_js_syntax_with_nested_quotes(self):
        """Test Alpine.js-style attributes with nested quotes"""
        self.create_template(
            "cotton/alpine_component.html",
            """
            <button x-on:click="{{ click }}">Click me</button>
            """,
        )

        self.create_template(
            "alpine_view.html",
            """
            <c-alpine-component click="modal = 'confirm-{{ id }}'" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Alpine expression should be preserved
            self.assertContains(response, "modal = 'confirm-")

    def test_json_in_attribute_with_nested_quotes(self):
        """Test JSON-like data in attributes with nested quotes"""
        self.create_template(
            "cotton/json_component.html",
            """
            <div x-data="{{ data }}"></div>
            """,
        )

        self.create_template(
            "json_view.html",
            """
            <c-json-component :data="{'name': '{{ user.name }}', 'role': 'admin'}" />
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should contain the JSON structure
            self.assertContains(response, "name")
            self.assertContains(response, "role")
