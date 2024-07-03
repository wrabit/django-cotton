from django.shortcuts import render


def build_view(template_name):
    def view(request):
        return render(request, f"{template_name}.html")

    return view


def home(request):
    return render(request, "home.html")


def quickstart(request):
    return render(request, "quickstart.html")


def installation(request):
    return render(request, "installation.html")


def usage(request):
    return render(request, "usage.html")


def form_fields(request):
    return render(request, "form_fields.html")


def components(request):
    return render(request, "components.html")


def alpine_js(request):
    return render(request, "alpine_js.html")
