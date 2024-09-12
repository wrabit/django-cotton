from django.shortcuts import render
from django.urls import path

app_name = "example_project"


def index_view(request):
    return render(
        request,
        "index.html",
        {
            "data": "Example Project",
        },
    )


urlpatterns = [
    path("", index_view),
]
