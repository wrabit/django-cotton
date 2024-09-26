from django_cotton.tests.utils import CottonTestCase, get_compiled


class CompileTests(CottonTestCase):
    def test_compile(self):
        compiled = get_compiled(
            """
            <c-render-basic>
                Default!
                <c-slot nam="named">Named!</c-slot>
            </c-render-basic>            
            """
        )

        print(compiled)

        self.assertTrue(True)

    def test_basic(self):
        self.create_template(
            "cotton/render_basic.html",
            """<div>
                default: {{ slot }}
                named: {{ named }}
            </div>""",
        )

        self.create_template(
            "view.html",
            """<c-render-basic>
                Default!
                <c-slot name="named">Named!</c-slot>
            </c-render>""",
            "view/",
        )

        # Override URLconf
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "default: Default!")
            self.assertContains(response, "named: Named!")
