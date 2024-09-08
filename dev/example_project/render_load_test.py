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
            "APP_DIRS": True,
            "OPTIONS": {
                "loaders": [
                    (
                        "django.template.loaders.cached.Loader",
                        [
                            "django_cotton.loader.CottonLoader",
                            "django.template.loaders.filesystem.Loader",
                            "django.template.loaders.app_directories.Loader",
                        ],
                    )
                ],
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
    COTTON_TEMPLATE_CACHING_ENABLED=False,
    DEBUG=False,
)

django.setup()


def template_bench(template_name, iterations=1000):
    start_time = time.time()
    for _ in range(iterations):
        render_to_string(template_name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)

    return duration, render_to_string(template_name)


def template_bench_alt(template_name, iterations=1000):
    data = list(range(1, iterations))
    start_time = time.time()
    render_to_string(template_name, context={"data": data})
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)

    return duration, render_to_string(template_name)


# warm caches
template_bench_alt("simple_native.html", iterations=1)
template_bench_alt("simple_cotton.html", iterations=1)

simple_native, _ = template_bench_alt("simple_native.html")
simple_cotton, _ = template_bench_alt("simple_cotton.html")

print("---")
print(f"Native Django {{% for %}} loop: {simple_native} ms")
print(f"Cotton {{% for %}} loop: {simple_cotton} ms")

# warm caches
template_bench("benchmarks/native_include.html", iterations=1)
template_bench("cotton/benchmarks/cotton_include.html", iterations=1)

time_native_include, _ = template_bench("benchmarks/native_include.html")
time_cotton_include, _ = template_bench("cotton/benchmarks/cotton_include.html")

print("---")
print(f"Native {{% include %}}: {time_native_include} ms")
print(f"Cotton for include: {time_cotton_include} ms")

# warm caches
template_bench("benchmarks/native_extends.html", iterations=1)
template_bench("cotton/benchmarks/cotton_compiled.html", iterations=1)
template_bench("cotton/benchmarks/cotton_extends_equivalent.html", iterations=1)

time_native_extends, _ = template_bench("benchmarks/native_extends.html")
time_compiled_cotton, _ = template_bench("cotton/benchmarks/cotton_compiled.html")
time_cotton, _ = template_bench("cotton/benchmarks/cotton_extends_equivalent.html")


print("---")
print(f"Native {{% block %}} and {{% extends %}}: {time_native_extends} ms")
print(f"Compiled Cotton Template: {time_compiled_cotton} ms")
print(f"Uncompiled Cotton Template: {time_cotton} ms")
