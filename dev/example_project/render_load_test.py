import time
from django.template.loader import render_to_string
from statistics import mean


def configure_django():
    from django.conf import settings

    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django_cotton.apps.SimpleAppConfig",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": ["example_project/templates"],
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django_cotton.cotton_loader.Loader",
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                    "builtins": [
                        "django_cotton.templatetags.cotton",
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
        DEBUG=False,
    )

    import django

    django.setup()


def template_bench(template_name, iterations=5000):
    start_time = time.time()
    for _ in range(iterations):
        render_to_string(template_name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)
    return duration


def template_bench_data_loop(template_name, iterations=5000):
    data = list(range(1, iterations))
    start_time = time.time()
    render_to_string(template_name, context={"data": data})
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)
    return duration


def run_benchmark(bench_func, template_name, iterations=5000, runs=5):
    # Warm up
    bench_func(template_name, iterations=1)

    results = []
    for _ in range(runs):
        result = bench_func(template_name, iterations)
        results.append(result)

    return mean(results)


def main():
    configure_django()

    runs = 5
    iterations = 5000

    print(f"Running benchmarks with {runs} runs, {iterations} iterations each")

    simple_native = run_benchmark(
        template_bench_data_loop, "simple_native.html", iterations, runs
    )
    simple_cotton = run_benchmark(
        template_bench_data_loop, "simple_cotton.html", iterations, runs
    )

    print("---")
    print(f"Native Django {{% for %}} loop: {simple_native:.2f} ms")
    print(f"Cotton {{% for %}} loop: {simple_cotton:.2f} ms")

    time_native_include = run_benchmark(
        template_bench, "benchmarks/native_include.html", iterations, runs
    )
    time_cotton_include = run_benchmark(
        template_bench, "cotton/benchmarks/cotton_include.html", iterations, runs
    )

    print("---")
    print(f"Native {{% include %}}: {time_native_include:.2f} ms")
    print(f"Cotton for include: {time_cotton_include:.2f} ms")

    time_native_extends = run_benchmark(
        template_bench, "benchmarks/native_extends.html", iterations, runs
    )
    time_compiled_cotton = run_benchmark(
        template_bench, "cotton/benchmarks/cotton_compiled.html", iterations, runs
    )
    time_cotton = run_benchmark(
        template_bench,
        "cotton/benchmarks/cotton_extends_equivalent.html",
        iterations,
        runs,
    )

    print("---")
    print(f"Native {{% block %}} and {{% extends %}}: {time_native_extends:.2f} ms")
    print(f"Compiled Cotton Template: {time_compiled_cotton:.2f} ms")
    print(f"Uncompiled Cotton Template: {time_cotton:.2f} ms")


if __name__ == "__main__":
    main()
