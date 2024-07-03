from django.views.generic import TemplateView
from . import views
from django.urls import path

app_name = "django_cotton"


class NamedSlotInLoop(TemplateView):
    template_name = "named_slot_in_loop.html"

    def get_context_data(self, **kwargs):
        return {
            "items": [
                {"name": "Item 1"},
                {"name": "Item 2"},
                {"name": "Item 3"},
            ]
        }


urlpatterns = [
    path("parent", TemplateView.as_view(template_name="parent_test.html")),
    path("child", TemplateView.as_view(template_name="child_test.html")),
    path(
        "self-closing",
        TemplateView.as_view(template_name="self_closing_test.html"),
    ),
    path("include", TemplateView.as_view(template_name="cotton_include.html")),
    path("playground", TemplateView.as_view(template_name="playground.html")),
    path("tag", TemplateView.as_view(template_name="tag.html")),
    path("named-slot-in-loop", NamedSlotInLoop.as_view()),
    path("test/compiled-cotton", views.compiled_cotton_test_view),
    path("test/cotton", views.cotton_test_view),
    path("test/native-extends", views.native_extends_test_view),
    path("test/native-include", views.native_include_test_view),
    path("test/valueless-attributes", views.valueless_attributes_test_view),
    path("attribute-merging", views.attribute_merging_test_view),
    path("attribute-passing", views.attribute_passing_test_view),
    path("django-syntax-decoding", views.django_syntax_decoding_test_view),
    path(
        "string-with-spaces",
        TemplateView.as_view(template_name="string_with_spaces.html"),
    ),
    path("vars-test", TemplateView.as_view(template_name="vars_test.html")),
    path("variable-parsing", views.variable_parsing_test_view),
    path("test/eval-vars", views.eval_vars_test_view),
    path("test/eval-attributes", views.eval_attributes_test_view),
    path(
        "test/native-tags-in-attributes",
        TemplateView.as_view(template_name="native_tags_in_attributes_view.html"),
    ),
]
