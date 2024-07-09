from django.shortcuts import render

# benchmark tests


def compiled_cotton_test_view(request):
    return render(request, "compiled_cotton_test.html")


def cotton_test_view(request):
    return render(request, "cotton_test.html")


def native_extends_test_view(request):
    return render(request, "native_extends_test.html")


def native_include_test_view(request):
    return render(request, "native_include_test.html")


# Django tests


def attribute_merging_test_view(request):
    return render(request, "attribute_merging_test.html")


def attribute_passing_test_view(request):
    return render(request, "attribute_passing_test.html")


def django_syntax_decoding_test_view(request):
    return render(request, "django_syntax_decoding_test.html")


def variable_parsing_test_view(request):
    return render(request, "variable_parsing_test.html", {"variable": "some-class"})


def valueless_attributes_test_view(request):
    return render(request, "valueless_attributes_test_view.html")


def eval_vars_test_view(request):
    return render(request, "eval_vars_test_view.html")


def eval_attributes_test_view(request):
    return render(request, "eval_attributes_test_view.html")
