from django.shortcuts import render

# benchmark tests


def compiled_cotton_test_view(request):
    return render(request, "compiled_cotton_test.html")


def cotton_test_view(request):
    return render(request, "cotton_test.cotton.html")


def native_extends_test_view(request):
    return render(request, "native_extends_test.html")


def native_include_test_view(request):
    return render(request, "native_include_test.html")


# Django tests


def attribute_merging_test_view(request):
    return render(request, "attribute_merging_test.cotton.html")


def attribute_passing_test_view(request):
    return render(request, "attribute_passing_test.cotton.html")


def django_syntax_decoding_test_view(request):
    return render(request, "django_syntax_decoding_test.cotton.html")


def variable_parsing_test_view(request):
    return render(
        request, "variable_parsing_test.cotton.html", {"variable": "some-class"}
    )
