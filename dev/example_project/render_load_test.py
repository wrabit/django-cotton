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
                "loaders": [
                    "django_cotton.cotton_loader.Loader",
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
                "builtins": [
                    "django.templatetags.static",
                    "django_cotton.templatetags.cotton",
                ],
            },
        },
    ],
    # Toggle this to turn caching on and off
    COTTON_TEMPLATE_CACHING_ENABLED=True,
)

django.setup()


def benchmark_template_rendering(template_name, iterations=1000):
    start_time = time.time()
    for _ in range(iterations):
        render_to_string(template_name)
    end_time = time.time()
    return end_time - start_time, render_to_string(template_name)


# Benchmarking each template
time_native_extends, output_native_extends = benchmark_template_rendering(
    "cotton/benchmarks/native_extends.html"
)
time_compiled_cotton, output_compiled_cotton = benchmark_template_rendering(
    "cotton/benchmarks/cotton_compiled.html"
)
time_cotton, output_cotton = benchmark_template_rendering(
    "cotton/benchmarks/cotton.html"
)

# Output results
print(f"Native Django Template using extend: {time_native_extends} seconds")
print(f"Compiled Cotton Template: {time_compiled_cotton} seconds")
print(f"Cotton Template: {time_cotton} seconds")
