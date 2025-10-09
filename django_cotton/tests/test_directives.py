from django_cotton.tests.utils import CottonTestCase
from django_cotton.cotton_loader import Loader as CottonLoader

def get_parsed_directives(template_string: str) -> str:
    return CottonLoader(engine=None).directive_parser.process(template_string)

class CottonDirectivesTests(CottonTestCase):
    def test_if_directive(self):
        template = """
            <div c-if="True">
                one
            </div>
            
            <div c-if="False">
                two
            </div>
        """
        parsed = get_parsed_directives(template)
        self.assertRegex(parsed, r"{%\s*if True\s*%}")
        self.assertRegex(parsed, r"{%\s*if False\s*%}")
        
        self.create_template(
            "if_directive.html",
            template,
            "view/",
        )
       
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "one")
            self.assertNotContains(response, "two")


    def test_elif_directive(self):
        template = """
            <div c-if="False">one</div>
            <div c-elif="True">two</div>
            <div c-else>three</div>
        """
        parsed = get_parsed_directives(template)
        self.assertRegex(parsed, r"{%\s*if False\s*%}")
        self.assertRegex(parsed, r"{%\s*elif True\s*%}")
        self.assertRegex(parsed, r"{%\s*else\s*%}")
        
        self.create_template(
            "elif_directive.html",
            template,
            "view/",
        )
        
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertNotContains(response, "one")
            self.assertContains(response, "two")
            self.assertNotContains(response, "three")
            
    def test_else_directive(self):
        template = """
            <div c-if="False">one</div>
            <div c-elif="False">two</div>
            <div c-else>three</div>
        """
        parsed = get_parsed_directives(template)
        self.assertRegex(parsed, r"{%\s*if False\s*%}")
        self.assertRegex(parsed, r"{%\s*elif False\s*%}")
        self.assertRegex(parsed, r"{%\s*else\s*%}")
        
        self.create_template(
            "else_directive.html",
            template,
            "view/",
        )
        
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertNotContains(response, "one")
            self.assertNotContains(response, "two")
            self.assertContains(response, "three")
       
    def test_for_directive(self):
        template = """
            <ul c-for="number in '123'">
                <li>{{ number }}</li>
            </ul>
        """
        parsed = get_parsed_directives(template)
        self.assertRegex(parsed, r"{%\s*for number in '123'\s*%}")
        
        self.create_template(
           "for_directive.html",
            template,
            "view/",
        )
        
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<li>1</li>")
            self.assertContains(response, "<li>2</li>")
            self.assertContains(response, "<li>3</li>")
            
    def test_nested_directives(self):
        template = """
            <div c-if="True">
                <ul c-for="number in '123'">
                    <li>{{ number }}</li>
                </ul>
            </div>
        """
        parsed = get_parsed_directives(template)
        self.assertRegex(parsed, r"{%\s*if True\s*%}")
        self.assertRegex(parsed, r"{%\s*for number in '123'\s*%}")
        
        self.create_template(
           "nested_directives.html",
            template,
            "view/",
        )
        
        with self.settings(ROOT_URLCONF=self.url_conf()):
            response = self.client.get("/view/")
            self.assertContains(response, "<li>1</li>")
            self.assertContains(response, "<li>2</li>")
            self.assertContains(response, "<li>3</li>")
