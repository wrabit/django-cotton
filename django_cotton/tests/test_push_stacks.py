from django_cotton.tests.utils import CottonTestCase


class PushStackTests(CottonTestCase):
    def test_push_content_deduplicated(self):
        self.create_template(
            "cotton/push_component.html",
            """
                <div class=\"widget\">{{ slot }}</div>
                <c-push to=\"head\">
                    <script src=\"/static/push.js\"></script>
                </c-push>
            """,
        )

        self.create_template(
            "push_view.html",
            """
                <html>
                    <head>
                        <c-stack name=\"head\" />
                    </head>
                    <body>
                        <c-push-component>One</c-push-component>
                        <c-push-component>Two</c-push-component>
                    </body>
                </html>
            """,
            "view/",
        )

        with self.settings(
            ROOT_URLCONF=self.url_conf(),
            MIDDLEWARE=["django_cotton.middleware.CottonStackMiddleware"],
        ):
            response = self.client.get("/view/")

        html = response.content.decode()
        snippet = '<script src="/static/push.js"></script>'

        self.assertIn(snippet, html)
        self.assertEqual(html.count(snippet), 1)
        self.assertNotIn("__COTTON_STACK__", html)

    def test_push_multiple_allows_duplicates(self):
        self.create_template(
            "cotton/push_multi.html",
            """
                <div class=\"widget\">{{ slot }}</div>
                <c-push to=\"head\" multiple>
                    <script src=\"/static/push-multi.js\"></script>
                </c-push>
            """,
        )

        self.create_template(
            "push_multi_view.html",
            """
                <html>
                    <head>
                        <c-stack name=\"head\" />
                    </head>
                    <body>
                        <c-push-multi>One</c-push-multi>
                        <c-push-multi>Two</c-push-multi>
                    </body>
                </html>
            """,
            "view-multi/",
        )

        with self.settings(
            ROOT_URLCONF=self.url_conf(),
            MIDDLEWARE=["django_cotton.middleware.CottonStackMiddleware"],
        ):
            response = self.client.get("/view-multi/")

        html = response.content.decode()
        snippet = '<script src="/static/push-multi.js"></script>'

        self.assertEqual(html.count(snippet), 2)

    def test_stack_fallback_used_when_no_push(self):
        self.create_template(
            "fallback_view.html",
            """
                <html>
                    <head>
                        <c-stack name=\"foot\">
                            <meta name=\"robots\" content=\"noindex\" />
                        </c-stack>
                    </head>
                    <body>Empty</body>
                </html>
            """,
            "fallback/",
        )

        with self.settings(
            ROOT_URLCONF=self.url_conf(),
            MIDDLEWARE=["django_cotton.middleware.CottonStackMiddleware"],
        ):
            response = self.client.get("/fallback/")

        html = response.content.decode()

        self.assertIn('<meta name="robots" content="noindex" />', html)

    def test_push_deduplicates_using_key(self):
        self.create_template(
            "cotton/push_keyed.html",
            """
                <div>{{ slot }}</div>
                <c-push to=\"head\" key=\"lib\">
                    <script>init('{{ slot|slugify }}')</script>
                </c-push>
            """,
        )

        self.create_template(
            "push_key_view.html",
            """
                <html>
                    <head>
                        <c-stack name=\"head\" />
                    </head>
                    <body>
                        <c-push-keyed>Alpha One</c-push-keyed>
                        <c-push-keyed>Beta Two</c-push-keyed>
                    </body>
                </html>
            """,
            "view-key/",
        )

        with self.settings(
            ROOT_URLCONF=self.url_conf(),
            MIDDLEWARE=["django_cotton.middleware.CottonStackMiddleware"],
        ):
            response = self.client.get("/view-key/")

        html = response.content.decode()

        self.assertIn("init('alpha-one')", html)
        self.assertNotIn("init('beta-two')", html)
