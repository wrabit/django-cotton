from django.shortcuts import render


# benchmarks
def compiled_cotton_test_view(request):
    return render(request, "compiled_cotton_test.html")


def native_extends_test_view(request):
    return render(request, "native_extends_test.html")


def native_include_test_view(request):
    return render(request, "native_include_test.html")
