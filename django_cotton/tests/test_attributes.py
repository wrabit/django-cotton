from django_cotton.tests.utils import CottonTestCase
from django_cotton.tests.utils import get_compiled


class AttributeHandlingTests(CottonTestCase):
    def test_dynamic_attributes_on_components(self):
        self.create_template(
            "eval_attributes_on_component_view.html",
            """
                <c-dynamic-attributes-component
                        :none="None"
                        :number="1"
                        :boolean_true="True"
                        :boolean_false="False"
                        :dict="{'key': 'value'}"
                        :list="[1, 2, 3]"
                        :listdict="[{'key': 'value'}]"
                        :variable="variable"
                        :template_string_lit="{'dummy': {{ dummy }}}"
                />        
            """,
            "view/",
            context={"variable": 111, "dummy": 222},
        )

        self.create_template(
            "cotton/dynamic_attributes_component.html",
            """
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
                
                HHH{{ template_string_lit }}HHH
                
                {% if template_string_lit.dummy == 222 %}
                    <p>template_string_lit.dummy is 222</p>
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
            self.assertContains(response, "template_string_lit.dummy is 222")

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

    def test_we_can_govern_whole_attributes_in_html_elements(self):
        self.create_template(
            "cotton/attribute_govern.html",
            """
            <div {% if something %} class="first" {% else %} class="second" {% endif %}><div>
            """,
        )

        self.create_template(
            "attribute_govern_view.html",
            """
            <c-attribute-govern :something="False" />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, 'class="second"')
            self.assertNotContains(response, 'class="first"')

    def test_attribute_names_on_component_containing_hyphens_are_converted_to_underscores(
        self,
    ):
        self.create_template(
            "cotton/hyphens.html",
            """
            <div x-data="{{ x_data }}" x-init="{{ x_init }}"></div>
            """,
        )

        self.create_template(
            "hyphens_view.html",
            """
            <c-hyphens x-data="{}" x-init="do_something()" />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, 'x-data="{}" x-init="do_something()"')

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

    def test_equals_in_attribute_values(self):
        self.create_template(
            "cotton/equals.html",
            """
            <div {{ attrs }}><div>
            """,
        )

        self.create_template(
            "equals_view.html",
            """
            <c-equals
              @click="this=test"
            />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, '@click="this=test"')

    def test_spaces_are_maintained_around_expressions_inside_attributes(self):
        self.create_template(
            "maintain_spaces_in_attributes_view.html",
            """
            <div some_attribute_{{ id }}_something="true"></div>
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, "some_attribute__something")

    def test_boolean_attributes(self):
        self.create_template(
            "cotton/boolean_attribute.html",
            """
                {% if is_something is True %}
                    It's True
                {% endif %}
            """,
        )

        self.create_template(
            "boolean_attribute_view.html",
            """
                <c-boolean-attribute is_something />
            """,
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "It's True")

    def test_attributes_without_colons_are_not_evaluated(self):
        self.create_template(
            "cotton/static_attrs.html",
            """
                {% if something == "1,234" %}
                    All good
                {% endif %}
                
                {% if something == "(1, 234)" %}
                    "1,234" was evaluated as a tuple
                {% endif %}
            """,
        )

        self.create_template(
            "static_attrs_view.html",
            """
                <c-static-attrs something="{{ something }}" />
            """,
            "view/",
            context={"something": "1,234"},
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "All good")

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

    def test_attribute_merging(self):
        self.create_template(
            "cotton/merges_attributes.html",
            """
            <div {{ attrs|merge:'class:form-group another-class-with:colon' }}></div>
            """,
        )

        self.create_template(
            "attribute_merging_view.html",
            """
            <c-merges-attributes class="extra-class" silica:model="test" another="test">ss</c-merges-attributes>        
            """,
            "view/",
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, 'class="form-group another-class-with:colon extra-class"')

    def test_attributes_can_contain_django_native_tags(self):
        self.create_template(
            "native_tags_in_attributes_view.html",
            """                                
                <c-native-tags-in-attributes
                    attr1="Hello {{ name }}"
                    attr2="{{ test|default:"none" }}"
                    attr3="{% if 1 == 1 %}cowabonga!{% endif %}"
                >
                    <c-slot name="named">test</c-slot>
                </c-native-tags-in-attributes>
            """,
            "view/",
            context={"name": "Will", "test": "world"},
        )

        self.create_template(
            "cotton/native_tags_in_attributes.html",
            """
                Attribute 1 says: '{{ attr1 }}'
                Attribute 2 says: '{{ attr2 }}'
                Attribute 3 says: '{{ attr3 }}'
                attrs tag is: '{{ attrs }}'            
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")

            self.assertContains(response, "Attribute 1 says: 'Hello Will'")
            self.assertContains(response, "Attribute 2 says: 'world'")
            self.assertContains(response, "Attribute 3 says: 'cowabonga!'")

            self.assertContains(
                response,
                """attrs tag is: 'attr1="Hello Will" attr2="world" attr3="cowabonga!"'""",
            )

    def test_strings_with_spaces_can_be_passed(self):
        self.create_template(
            "string_with_spaces_view.html",
            """
                <c-string-test var="string with space" attr="I have spaces">
                    <c-slot name="named_slot">
                        named_slot with spaces
                    </c-slot>
                </c-string-test>            
            """,
            "view/",
        )

        self.create_template(
            "cotton/string_test.html",
            """
                <c-vars var default_var="default var" />
                
                slot: '{{ slot }}'
                attr: '{{ attr }}'
                var: '{{ var }}'
                default_var: '{{ default_var }}'
                named_slot: '{{ named_slot }}'
                attrs: '{{ attrs }}'
            """,
        )

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

    def test_attribute_passing(self):
        self.create_template(
            "attribute_passing_view.html",
            """
                <c-attribute-passing attribute_1="hello" and-another="woo1" thirdForLuck="yes" />       
            """,
            "view/",
        )
        self.create_template("cotton/attribute_passing.html", """<div {{ attrs }}></div>""")

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(
                response, '<div attribute_1="hello" and-another="woo1" thirdforluck="yes">'
            )

    def test_loader_preserves_duplicate_attributes(self):
        compiled = get_compiled("""<a href="#" class="test" class="test2">hello</a>""")

        self.assertEquals(
            compiled,
            """<a href="#" class="test" class="test2">hello</a>""",
        )

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
                line2" />
            """,
        )

        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertTrue(response.status_code == 200)
