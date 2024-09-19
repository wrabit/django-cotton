from django.shortcuts import render


# function to convert snake_case to Title Case
def snake_to_title(snake_str):
    return snake_str.replace("_", " ").title()


def build_view(template_name, title=None):
    title = title or f"{snake_to_title(template_name)} - Django Cotton"

    def view(request):
        return render(request, f"{template_name}.html", {"meta_title": title})

    return view


# HTMX snippet
# def home(request):
#     template = "home.html"
#     if request.META.get("HTTP_HX_REQUEST"):
#         print("htmx!")
#         template = f"{template}#table"
#
#     return render(request, template)
