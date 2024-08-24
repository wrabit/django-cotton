"""
django-cotton

App configuration to set up the cotton loader and builtins automatically.
"""

from contextlib import suppress

import django.contrib.admin
import django.template
from django.apps import AppConfig
from django.conf import settings


def wrap_loaders(name):
    for template_config in settings.TEMPLATES:
        engine_name = template_config.get("NAME")
        if not engine_name:
            engine_name = template_config["BACKEND"].split(".")[-2]
        if engine_name == name:
            loaders = template_config.setdefault("OPTIONS", {}).get("loaders", [])

            loaders_already_configured = (
                loaders
                and isinstance(loaders, (list, tuple))
                and isinstance(loaders[0], (tuple, list))
                and loaders[0][0] == "django.template.loaders.cached.Loader"
                and "django_cotton.cotton_loader.Loader" in loaders[0][1]
            )

            if not loaders_already_configured:
                template_config.pop("APP_DIRS", None)
                default_loaders = [
                    "django_cotton.cotton_loader.Loader",
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ]
                cached_loaders = [("django.template.loaders.cached.Loader", default_loaders)]
                template_config["OPTIONS"]["loaders"] = cached_loaders

            options = template_config.setdefault("OPTIONS", {})
            builtins = options.setdefault("builtins", [])
            builtins_already_configured = (
                builtins and "django_cotton.templatetags.cotton" in builtins
            )
            if not builtins_already_configured:
                template_config["OPTIONS"]["builtins"].insert(
                    0, "django_cotton.templatetags.cotton"
                )

            break

    # Force re-evaluation of settings.TEMPLATES because EngineHandler caches it.
    with suppress(AttributeError):
        del django.template.engines.templates
        django.template.engines._engines = {}


class LoaderAppConfig(AppConfig):
    """
    This, the default configuration, does the automatic setup of a partials loader.
    """

    name = "django_cotton"
    default = True

    def ready(self):
        wrap_loaders("django")


class SimpleAppConfig(AppConfig):
    """
    This, the non-default configuration, allows the user to opt-out of the automatic configuration. They just need to
    add "django_cotton.apps.SimpleAppConfig" to INSTALLED_APPS instead of "django_cotton".
    """

    name = "django_cotton"
