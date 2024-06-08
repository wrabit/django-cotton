from django.apps import AppConfig
from django.conf import settings
from django.template import engines

# fmt: off
class CottonConfig(AppConfig):
    name = "django_cotton"
    verbose_name = "Cotton"

    def ready(self):
        self._modify_templates_settings()
        self._add_builtin_template_tag()

    def _modify_templates_settings(self):
        modified = False
        for template in settings.TEMPLATES:
            if not template.get("APP_DIRS", True):
                # If APP_DIRS is explicitly set to False, we assume the user
                # has a custom setup and do not modify the settings and provide tutorial instead.
                continue

            # Example modification: Set APP_DIRS to False
            template["APP_DIRS"] = False

            # Add your custom template loader
            if "OPTIONS" not in template:
                template["OPTIONS"] = {}
            if "loaders" not in template["OPTIONS"]:
                template["OPTIONS"]["loaders"] = []

            # Add django_cotton loader
            if "django_cotton.cotton_loader.Loader" not in template["OPTIONS"]["loaders"]:
                template["OPTIONS"]["loaders"].insert(
                    0, "django_cotton.cotton_loader.Loader"
                )

            # Ensure default loaders are present, then add your custom loader
            if "django.template.loaders.filesystem.Loader" not in template["OPTIONS"]["loaders"]:
                template["OPTIONS"]["loaders"].append(
                    "django.template.loaders.filesystem.Loader"
                )
            if "django.template.loaders.app_directories.Loader" not in template["OPTIONS"]["loaders"]:
                template["OPTIONS"]["loaders"].append(
                    "django.template.loaders.app_directories.Loader"
                )

            # Specify TEMPLATE_DIRS if necessary
            # template['DIRS'] += ['path/to/your/templates']

            modified = True

        if modified:
            print("TEMPLATES setting modified by Django Cotton.")

    def _add_builtin_template_tag(self):
        """Add a custom template tag to the built-ins."""
        builtins = engines["django"].engine.builtins
        custom_tag_lib = "django_cotton.templatetags.cotton"
        if custom_tag_lib not in builtins:
            builtins.append(custom_tag_lib)
