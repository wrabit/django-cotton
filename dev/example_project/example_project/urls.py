from django.shortcuts import render
from django.urls import path

app_name = "example_project"


def index_view(request):
    return render(
        request,
        "index.html",
        {
            "view_context": "I'm from view context",
        },
    )


urlpatterns = [path("", index_view)]
