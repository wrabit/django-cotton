from django.shortcuts import render


def build_view(template_name):
    def view(request):
        return render(request, f"{template_name}.cotton.html")

    return view


def home(request):
    return render(request, "home.cotton.html")


def quickstart(request):
    return render(request, "quickstart.cotton.html")


def installation(request):
    return render(request, "installation.cotton.html")


def usage(request):
    return render(request, "usage.cotton.html")


def form_fields(request):
    return render(request, "form_fields.cotton.html")


def components(request):
    return render(request, "components.cotton.html")


def alpine_js(request):
    return render(request, "alpine_js.cotton.html")
