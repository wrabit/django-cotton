from django.template.loader import render_to_string

from django_cotton.tests.utils import CottonTestCase


class CvarTests(CottonTestCase):
    def test_dynamic_attributes_in_cvars(self):
        self.create_template(
            "eval_attributes_in_cvars_view.html",
            """
                <c-dynamic-attributes-cvars />        
            """,
            "view/",
        )

        self.create_template(
            "cotton/dynamic_attributes_cvars.html",
            """
                <c-vars 
                    :none="None" 
                    :number="1" 
                    :boolean_true="True" 
                    :boolean_false="False" 
                    :dict="{'key': 'value'}" 
                    :list="[1, 2, 3]" 
                    :listdict="[{'key': 'value'}]" 
                    :variable="111"             
                />
                
                {% if none is None %}
                    <p>none is None</p>
                {% endif %}
                
                {% if number == 1 %}
                    <p>number is 1</p>
                {% endif %}
                
                {% if boolean_true is True %}
                    <p>boolean_true is True</p>
                {% endif %}
                
                {% if boolean_false is False %}
                    <p>boolean_false is False</p>
                {% endif %}
                
                {% if dict.key == 'value' %}
                    <p>dict.key is 'value'</p>
                {% endif %}
                
                {% if list.0 == 1 %}
                    <p>list.0 is 1</p>
                {% endif %}
                
                {% if listdict.0.key == 'value' %}
                    <p>listdict.0.key is 'value'</p>
                {% endif %}

                {% if variable == 111 %}
                    <p>variable is 111</p>
                {% endif %}   
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, "none is None")
            self.assertContains(response, "number is 1")
            self.assertContains(response, "boolean_true is True")
            self.assertContains(response, "boolean_false is False")
            self.assertContains(response, "list.0 is 1")
            self.assertContains(response, "dict.key is 'value'")
            self.assertContains(response, "listdict.0.key is 'value'")
            self.assertContains(response, "variable is 111")

    def test_attribute_names_on_cvars_containing_hyphens_are_converted_to_underscores(
        self,
    ):
        self.create_template(
            "cotton/cvar_hyphens.html",
            """
            <c-vars x-data="{}" x-init="do_something()" />
            
            <div x-data="{{ x_data }}" x-init="{{ x_init }}"></div>
            """,
        )

        self.create_template(
            "cvar_hyphens_view.html",
            """
            <c-cvar-hyphens />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, 'x-data="{}" x-init="do_something()"')

    def test_unprocessable_dynamic_attributes_fallback_to_cvar_defaults(self):
        self.create_template(
            "cotton/unprocessable_dynamic_attribute.html",
            """
                <c-vars color="gray" />
                
                {{ color }}
            """,
        )

        self.create_template(
            "unprocessable_dynamic_attribute_view.html",
            """
                <c-unprocessable-dynamic-attribute :color="button.color" />
            """,
            "view/",
            context={},
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertTrue("gray" in response.content.decode())

    def test_empty_cvar_is_removed_from_attrs_string(self):
        self.create_template(
            "empty_cvar_view.html",
            """
                <c-empty-cvar var="im a cvar" attr="im a fallthrough" />
            """,
            "view/",
        )

        self.create_template(
            "cotton/empty_cvar.html",
            """
                <c-vars var />
                
                attr: '{{ attr }}'
                var: '{{ var }}'
                attrs: '{{ attrs }}'
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "attr: 'im a fallthrough'")
            self.assertContains(response, "var: 'im a cvar'")
            self.assertContains(response, """attrs: 'attr="im a fallthrough"'""")

    def test_attrs_do_not_contain_cvars(self):
        self.create_template(
            "cvars_test_view.html",
            """
                <c-cvars-test-component var="im a var" attr="im an attr">
                    default slot
                </c-cvars-test-component>        
            """,
            "view/",
        )

        self.create_template(
            "cotton/cvars_test_component.html",
            """
                <c-vars var="sds" prop_with_default="1" />
                
                <div>
                    {{ testy }}
                    <p>var: '{{ var }}'</p>
                    <p>attr: '{{ attr }}'</p>
                    <p>empty_var: '{{ empty_var }}'</p>
                    <p>var_with_default: '{{ var_with_default }}'</p>
                    <p>slot: '{{ slot }}'</p>
                    <p>named_slot: '{{ named_slot }}'</p>
                    <p>attrs: '{{ attrs }}'</p>
                </div>
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "attr: 'im an attr'")
            self.assertContains(response, "var: 'im a var'")
            self.assertContains(response, """attrs: 'attr="im an attr"'""")

    def test_multiline_cvar_values(self):
        self.create_template(
            "multiline_cvar_values_view.html",
            """<c-multiline-cvar-values />""",
            "view/",
        )

        self.create_template(
            "cotton/multiline_cvar_values.html",
            """
                <c-vars multiline="line1
                line2"
                 another="one" />
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertTrue(response.status_code == 200)

    def test_assigning_cvars_as_empty_strings(self):
        self.create_template(
            "empty_string_cvars_view.html",
            """<c-empty-string-cvars />""",
            "view/",
        )

        self.create_template(
            "cotton/empty_string_cvars.html",
            """
                <c-vars test="" />
                
                {% if test == "" %}got it{% endif %}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertTrue(response.status_code == 200)
            self.assertContains(response, "got it")

    def test_class_attrs_dont_come_through_as_lists(self):
        self.create_template(
            "empty_class_attrs_view.html",
            """<c-empty-class-attrs />""",
            "view/",
        )

        self.create_template(
            "cotton/empty_class_attrs.html",
            """
                <c-vars class="" />
                
                {% if class == "" %}got it{% endif %}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "got it")

    def test_cvars_with_hyphens_and_underscores(self):
        self.create_template(
            "cvars_hyphens_underscores_view.html",
            """<c-cvars-hyphens-underscores 
                overwrite-hyphenated="overwrite-hyphenated"  
                overwrite_underscored="overwrite_underscored"  
            />""",
            "view/",
        )

        self.create_template(
            "cotton/cvars_hyphens_underscores.html",
            """
                <c-vars 
                    default-hyphenated="default-hyphenated"
                    default_underscored="default_underscored"
                    overwrite-hyphenated=".."
                    overwrite_underscored=".."
                />
                
                default-hyphenated: {{ default_hyphenated }}
                default_underscored: {{ default_underscored }}
                overwrite-hyphenated: {{ overwrite_hyphenated }}
                overwrite_underscored: {{ overwrite_underscored }}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "default-hyphenated: default-hyphenated")
            self.assertContains(response, "default_underscored: default_underscored")
            self.assertContains(response, "overwrite-hyphenated: overwrite-hyphenated")
            self.assertContains(response, "overwrite_underscored: overwrite_underscored")

    def test_cvars_basics(self):
        self.create_template(
            "dynamic_cvars_basics_view.html",
            """<c-cvars-basics overwrite="overwrite" real-attribute="real" />""",
            "view/",
        )

        self.create_template(
            "cotton/cvars_basics.html",
            """
                <c-vars :unprovided="False" overwrite="default" />
                
                attrs: {{ attrs }}
                overwrite: {{ overwrite }}
                real: {{ real_attribute }} 
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, 'attrs: real-attribute="real"')
            self.assertContains(response, "overwrite: overwrite")
            self.assertContains(response, "real: real")

    def test_cvars_dynamic_defaults(self):
        self.create_template(
            "dynamic_cvars_dynamic_defaults_view.html",
            """<c-dynamic-default-cvars />""",
            "view/",
        )

        self.create_template(
            "cotton/dynamic_default_cvars.html",
            """
                <c-vars :dynamic_default="False" />
                
                {% if dynamic_default is True %}not{% endif %}
                {% if dynamic_default is False %}expected{% endif %}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertNotContains(response, "not")
            self.assertContains(response, "expected")

    def test_overwriting_cvars_dynamic_defaults(self):
        self.create_template(
            "overwriting_cvars_dynamic_defaults_view.html",
            """<c-dynamic-default-overwrite-cvars :dynamic-default="True" />""",
            "view/",
        )

        self.create_template(
            "cotton/dynamic_default_overwrite_cvars.html",
            """
                <c-vars :dynamic-default="False" />

                {% if dynamic_default is True %}expected{% endif %}
                {% if dynamic_default is False %}not{% endif %}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "expected")
            self.assertNotContains(response, "not")

    def test_incoming_dynamic_attributes_overwrite_cvars_dynamic_attributes(self):
        self.create_template(
            "attribute_priority_view.html",
            """<c-attr-priority :dynamic="True" />""",
            "view/",
        )

        self.create_template(
            "cotton/attr_priority.html",
            """
                <c-vars :dynamic="False" />
                
                {% if dynamic is True %}expected{% endif %}
                {% if dynamic is False %}not{% endif %}
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "expected")
            self.assertNotContains(response, "not")

    def test_cvars_are_processed_when_component_rendered_using_render_to_string(self):
        self.create_template(
            "cotton/direct_render.html",
            """
            <c-vars cvar="I'm all set" />
            
            {{ cvar|safe }}
            """,
        )

        rendered = render_to_string("cotton/direct_render.html")

        self.assertTrue("I'm all set" in rendered)

    def test_cvars_template_basic_types_parsing(self):
        self.create_template(
            "cotton/cvars_template_basic_types.html",
            """
            <c-vars 
                none="None" 
                number="1" 
                boolean_true="True" 
                boolean_false="False" />
                
            {% if none == "None" %}
                I am string None
            {% endif %}
            
            {% if number == "1" %}
                I am string 1
            {% endif %}
            
            {% if boolean_true == "True" %}
                I am string True
            {% endif %}
            
            {% if boolean_false == "False" %}
                I am string False
            {% endif %}
                
            """,
        )

        rendered = render_to_string("cotton/cvars_template_basic_types.html")

        self.assertTrue("I am string None" in rendered)
        self.assertTrue("I am string 1" in rendered)
        self.assertTrue("I am string True" in rendered)
        self.assertTrue("I am string False" in rendered)

    def test_dynamic_and_non_dynamic_cvars_of_the_same_name_cascade_as_one(self):
        self.create_template(
            "cotton/cvars_cascade.html",
            """
            <c-vars :action="{'do': 'it'}" />
            
            Attrs: '{{ attrs }}' <!-- Should not contain even 'action' (the non ':' dynamic version) -->
            Action: '{{ action }}'
            """,
        )

        # View template that uses the proxy component
        self.create_template(
            "cvars_cascade_view.html",
            """
            <c-cvars-cascade action="something completely different" />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            content = response.content.decode().strip()

            self.assertTrue("Attrs: ''" in content)
            self.assertTrue("Action: 'something completely different'" in content)

    def test_dynamic_cvars_can_be_overridden_by_named_slots(self):
        self.create_template(
            "cotton/cvars_named_slots.html",
            """
            <c-vars :action="{'do': 'it'}" />
            
            Action: '{{ action }}'
            """,
        )

        # View template that uses the proxy component
        self.create_template(
            "cvars_named_slots_view.html",
            """
            <c-cvars-named-slots>
                <c-slot name="action">overridden action</c-slot>
            </c-cvars-named-slots>
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            content = response.content.decode().strip()

            self.assertTrue("Action: 'overridden action'" in content)

    def test_dynamic_cvars_are_not_present_in_attrs_string(self):
        self.create_template(
            "cotton/cvars_dynamic_attrs.html",
            """
            <c-vars :disabled />

            Attrs: '{{ attrs }}'
            """,
        )

        # View template that uses the proxy component
        self.create_template(
            "cvars_dynamic_attrs_view.html",
            """
            <c-cvars-dynamic-attrs />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            content = response.content.decode().strip()

            self.assertTrue("Attrs: ''" in content)

    def test_cvars_with_trans_tag_in_defaults(self):
        """Test that c-vars defaults can handle {% trans %} template tags for i18n"""
        self.create_template(
            "cotton/cvars_trans_tag.html",
            """
            {% load i18n %}
            <c-vars label="{% trans 'Loading' %}" />

            <span class="spinner" title="{{ label }}">{{ label }}</span>
            """,
        )

        # View template that uses the component
        self.create_template(
            "cvars_trans_tag_view.html",
            """
            <c-cvars-trans-tag />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            # The trans tag should be evaluated and the translated text should appear
            self.assertContains(response, 'title="Loading"')
            self.assertContains(response, ">Loading<")

    def test_cvars_with_trans_tag_override(self):
        """Test that c-vars defaults with {% trans %} can be overridden"""
        self.create_template(
            "cotton/cvars_trans_override.html",
            """
            {% load i18n %}
            <c-vars label="{% trans 'Loading' %}" />

            <span class="spinner" title="{{ label }}">{{ label }}</span>
            """,
        )

        # View template that overrides the default
        self.create_template(
            "cvars_trans_override_view.html",
            """
            <c-cvars-trans-override label="Custom Label" />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            # The custom label should override the trans tag default
            self.assertContains(response, 'title="Custom Label"')
            self.assertContains(response, ">Custom Label<")

    def test_cvars_with_url_tag_in_defaults(self):
        """Test that c-vars defaults can handle {% url %} template tags"""
        from django.urls import path
        from django.views.generic import TemplateView

        # Create the component with url tag in c-vars default
        self.create_template(
            "cotton/cvars_url_tag.html",
            """
            <c-vars url="{% url 'test_page' %}" />

            <a href="{{ url }}" class="link">Test Link</a>
            """,
        )

        # View template that uses the component
        self.create_template(
            "cvars_url_tag_view.html",
            """
            <c-cvars-url-tag />
            """,
            "view/",
        )

        # Create a dummy template
        self.create_template(
            "test_page.html",
            """<h1>Test Page</h1>""",
        )

        # Manually register a named url pattern
        url_pattern = path(
            "test-page/", TemplateView.as_view(template_name="test_page.html"), name="test_page"
        )
        self.url_module.urlpatterns.append(url_pattern)

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            # The url tag should be evaluated and the URL should appear in the href
            self.assertContains(response, 'href="/test-page/"')
            self.assertContains(response, 'class="link"')
