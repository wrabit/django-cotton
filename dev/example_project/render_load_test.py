import time

import django
from django.conf import settings
from django.template.loader import render_to_string

# Configure Django settings
settings.configure(
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_cotton",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["example_project/templates"],
            "APP_DIRS": False,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                "builtins": [
                    "django.templatetags.static",
                ],
            },
        },
    ],
    COTTON_TEMPLATE_CACHING_ENABLED=False,
    DEBUG=False,
)

django.setup()


def template_bench(template_name, iterations=500):
    start_time = time.time()
    for _ in range(iterations):
        render_to_string(template_name)
    end_time = time.time()
    return end_time - start_time, render_to_string(template_name)


def template_bench_alt(template_name, iterations=500):
    data = list(range(1, iterations))
    start_time = time.time()
    render_to_string(template_name, context={"data": data})
    end_time = time.time()
    return end_time - start_time, render_to_string(template_name)


simple_native, _ = template_bench_alt("simple_native.html")
simple_cotton, _ = template_bench_alt("simple_cotton.html")

print(f"Native Django Template: {simple_native} seconds")
print(f"Cotton Template: {simple_cotton} seconds")

time_native_include, _ = template_bench("benchmarks/native_include.html")
time_cotton_include, _ = template_bench("cotton/benchmarks/cotton_include.html")

print(f"Native {{% include %}}: {time_native_include} seconds")
print(f"Cotton for include:: {time_cotton_include} seconds")

time_native_extends, _ = template_bench("benchmarks/native_extends.html")
time_compiled_cotton, _ = template_bench("cotton/benchmarks/cotton_compiled.html")
time_cotton, _ = template_bench("cotton/benchmarks/cotton.html")

print(f"Native {{% block %}} and {{% extends %}}: {time_native_extends} seconds")
print(f"Uncompiled Cotton Template: {time_cotton} seconds")
print(f"Compiled Cotton Template: {time_compiled_cotton} seconds")
