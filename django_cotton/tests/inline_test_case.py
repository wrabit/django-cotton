import os
import sys
import shutil
import tempfile

from django.core.cache import cache
from django.urls import path
from django.test import override_settings
from django.views.generic import TemplateView
from django.conf import settings
from django.test import TestCase


class DynamicURLModule:
    def __init__(self):
        self.urlpatterns = []

    def __call__(self):
        return self.urlpatterns


class CottonInlineTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set tmp dir and register a url module for our tmp files
        cls.temp_dir = tempfile.mkdtemp()
        cls.url_module = DynamicURLModule()
        cls.url_module_name = f"dynamic_urls_{cls.__name__}"
        sys.modules[cls.url_module_name] = cls.url_module

        # Register our temp directory as a TEMPLATES path
        cls.new_templates_setting = settings.TEMPLATES.copy()
        cls.new_templates_setting[0]["DIRS"] = [
            cls.temp_dir
        ] + cls.new_templates_setting[0]["DIRS"]

        # Apply the setting
        cls.templates_override = override_settings(TEMPLATES=cls.new_templates_setting)
        cls.templates_override.enable()

    @classmethod
    def tearDownClass(cls):
        """Remove temporary directory and clean up modules"""
        cls.templates_override.disable()
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        del sys.modules[cls.url_module_name]
        super().tearDownClass()

    def tearDown(self):
        """Clear cache between tests so that we can use the same file names for simplicity"""
        cache.clear()

    def create_template(self, name, content):
        """Create a template file in the temporary directory and return the path"""
        path = os.path.join(self.temp_dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    def make_view(self, template_name):
        """Make a view that renders the given template"""
        return TemplateView.as_view(template_name=template_name)

    def register_url(self, url, view):
        """Register a URL pattern and returns path"""
        url_pattern = path(url, view)
        self.url_module.urlpatterns.append(url_pattern)
        return url_pattern

    def setUp(self):
        super().setUp()
        self.url_module.urlpatterns = []

    def get_url_conf(self):
        return self.url_module_name
