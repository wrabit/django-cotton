from django import forms
from django_cotton.tests.utils import CottonTestCase


class FieldComponentTests(CottonTestCase):
    """Integration tests for the ui/field component error handling"""

    def test_field_uses_form_from_context(self):
        """Field component should use form from context when :form not provided"""
        # Create form with validation errors
        class TestForm(forms.Form):
            email = forms.EmailField()

        form = TestForm(data={"email": "invalid-email"})
        form.is_valid()  # Trigger validation

        # Create view template that uses field with error
        self.create_template(
            "form_context_view.html",
            """
            <c-ui.input
                name="email"
                label="Email Address"
                error="email"
            />
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Enter a valid email")

    def test_field_uses_explicit_form(self):
        """Field component should use explicit :form when provided"""
        # Create form with errors
        class TestForm(forms.Form):
            username = forms.CharField(min_length=5)

        form = TestForm(data={"username": "ab"})
        form.is_valid()

        # Create view with explicit form parameter
        self.create_template(
            "explicit_form_view.html",
            """
            <c-ui.input
                name="username"
                label="Username"
                :form="my_form"
                error="username"
            />
            """,
            "view/",
            context={"my_form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "at least 5 characters")

    def test_field_with_valid_form_shows_no_error(self):
        """Field should not render error when form field is valid"""
        # Create valid form (no errors)
        class TestForm(forms.Form):
            email = forms.EmailField()

        form = TestForm(data={"email": "valid@example.com"})
        form.is_valid()

        self.create_template(
            "valid_form_view.html",
            """
            <c-ui.input
                name="email"
                label="Email"
                error="email"
            />
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should not contain error styling
            self.assertNotContains(response, "text-red")
            self.assertNotContains(response, "Enter a valid email")

    def test_field_error_with_select_component(self):
        """Field error handling should work with select component"""
        class TestForm(forms.Form):
            country = forms.ChoiceField(choices=[("us", "USA"), ("uk", "UK")])

        form = TestForm(data={})  # Empty data
        form.is_valid()

        self.create_template(
            "select_error_view.html",
            """
            <c-ui.select
                name="country"
                label="Country"
                error="country"
            >
                <c-ui.select.option value="us">United States</c-ui.select.option>
                <c-ui.select.option value="uk">United Kingdom</c-ui.select.option>
            </c-ui.select>
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "This field is required")

    def test_field_error_with_textarea_component(self):
        """Field error handling should work with textarea component"""
        class TestForm(forms.Form):
            message = forms.CharField(min_length=10)

        form = TestForm(data={"message": "short"})
        form.is_valid()

        self.create_template(
            "textarea_error_view.html",
            """
            <c-ui.textarea
                name="message"
                label="Message"
                error="message"
            />
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "at least 10 characters")

    def test_multiple_fields_same_form(self):
        """Multiple fields should all use the same form from context"""
        class TestForm(forms.Form):
            email = forms.EmailField()
            password = forms.CharField(min_length=8)

        form = TestForm(data={"email": "bad", "password": "short"})
        form.is_valid()

        self.create_template(
            "multiple_fields_view.html",
            """
            <c-ui.input
                name="email"
                label="Email"
                error="email"
            />
            <c-ui.input
                name="password"
                label="Password"
                type="password"
                error="password"
            />
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Enter a valid email")
            self.assertContains(response, "at least 8 characters")

    def test_field_error_overrides_context_form(self):
        """Explicit :form should override form from context"""
        class Form1(forms.Form):
            email = forms.EmailField()

        class Form2(forms.Form):
            email = forms.EmailField()

        form1 = Form1(data={"email": "bad1"})
        form1.is_valid()

        form2 = Form2(data={"email": "bad2"})
        form2.is_valid()

        self.create_template(
            "override_form_view.html",
            """
            <c-ui.input
                name="email"
                label="Email"
                :form="form2"
                error="email"
            />
            """,
            "view/",
            context={"form": form1, "form2": form2},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            # Should use form2 (explicit), not form (context)
            self.assertContains(response, "Enter a valid email")

    def test_checkbox_group_with_form_errors(self):
        """Checkbox group should show form errors when error prop provided"""

        class TestForm(forms.Form):
            features = forms.MultipleChoiceField(
                choices=[("feature1", "Feature 1"), ("feature2", "Feature 2")],
                required=True,
            )

        form = TestForm(data={})  # Empty data - no features selected
        form.is_valid()

        self.create_template(
            "checkbox_error_view.html",
            """
            <c-ui.checkbox.group
                name="features"
                label="Select Features"
                error="features"
            >
                <c-ui.checkbox value="feature1" label="Feature 1" />
                <c-ui.checkbox value="feature2" label="Feature 2" />
            </c-ui.checkbox.group>
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "This field is required")

    def test_radio_group_with_form_errors(self):
        """Radio group should show form errors when error prop provided"""

        class TestForm(forms.Form):
            size = forms.ChoiceField(
                choices=[("small", "Small"), ("medium", "Medium"), ("large", "Large")],
                required=True,
            )

        form = TestForm(data={})  # Empty data - no size selected
        form.is_valid()

        self.create_template(
            "radio_error_view.html",
            """
            <c-ui.radio.group
                name="size"
                label="Select Size"
                error="size"
            >
                <c-ui.radio value="small" label="Small" />
                <c-ui.radio value="medium" label="Medium" />
                <c-ui.radio value="large" label="Large" />
            </c-ui.radio.group>
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "This field is required")

    def test_checkbox_group_with_description_and_badge(self):
        """Checkbox group should render description and badge through field"""

        class TestForm(forms.Form):
            permissions = forms.MultipleChoiceField(
                choices=[("read", "Read"), ("write", "Write")],
                required=False,
            )

        form = TestForm(data={})
        form.is_valid()

        self.create_template(
            "checkbox_description_view.html",
            """
            <c-ui.checkbox.group
                name="permissions"
                label="Permissions"
                description="Select user permissions"
                badge="Optional"
            >
                <c-ui.checkbox value="read" label="Read" />
                <c-ui.checkbox value="write" label="Write" />
            </c-ui.checkbox.group>
            """,
            "view/",
            context={"form": form},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "Select user permissions")
            self.assertContains(response, "Optional")

    def test_radio_group_explicit_form_override(self):
        """Radio group explicit :form should override context form"""

        class Form1(forms.Form):
            plan = forms.ChoiceField(choices=[("free", "Free"), ("pro", "Pro")])

        class Form2(forms.Form):
            plan = forms.ChoiceField(choices=[("free", "Free"), ("pro", "Pro")])

        form1 = Form1(data={})
        form1.is_valid()

        form2 = Form2(data={})
        form2.is_valid()

        self.create_template(
            "radio_override_form_view.html",
            """
            <c-ui.radio.group
                name="plan"
                label="Select Plan"
                :form="form2"
                error="plan"
            >
                <c-ui.radio value="free" label="Free" />
                <c-ui.radio value="pro" label="Pro" />
            </c-ui.radio.group>
            """,
            "view/",
            context={"form": form1, "form2": form2},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "This field is required")
