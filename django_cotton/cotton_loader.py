import hashlib
import os
from functools import lru_cache

from django.conf import settings
from django.template.loaders.base import Loader as BaseLoader
from django.core.exceptions import SuspiciousFileOperation
from django.template import TemplateDoesNotExist, Origin
from django.utils._os import safe_join
from django.template import Template
from django.apps import apps

from django_cotton.compiler_regex import CottonCompiler


class Loader(BaseLoader):
    def __init__(self, engine, dirs=None):
        super().__init__(engine)
        self.cotton_compiler = CottonCompiler()
        self.cache_handler = CottonTemplateCacheHandler()
        self.dirs = dirs

    def get_contents(self, origin):
        cache_key = self.cache_handler.get_cache_key(origin)
        cached_content = self.cache_handler.get_cached_template(cache_key)

        if cached_content is not None:
            return cached_content

        template_string = self._get_template_string(origin.name)

        if "<c-" not in template_string and "{% cotton_verbatim" not in template_string:
            compiled = template_string
        else:
            compiled = self.cotton_compiler.process(template_string)

        self.cache_handler.cache_template(cache_key, compiled)

        return compiled

    def get_template_from_string(self, template_string):
        """Create and return a Template object from a string. Used primarily for testing."""
        return Template(template_string, engine=self.engine)

    def _get_template_string(self, template_name):
        try:
            with open(template_name, "r", encoding=self.engine.file_charset) as f:
                return f.read()
        except FileNotFoundError:
            raise TemplateDoesNotExist(template_name)

    @lru_cache(maxsize=None)
    def get_dirs(self):
        """Retrieves possible locations of cotton directory"""
        dirs = list(self.dirs or self.engine.dirs)

        # Include any included installed app directories, e.g. project/app1/templates
        for app_config in apps.get_app_configs():
            template_dir = os.path.join(app_config.path, "templates")
            if os.path.isdir(template_dir):
                dirs.append(template_dir)

        # Check project root templates, e.g. project/templates
        base_dir = getattr(settings, "COTTON_BASE_DIR", None)
        if base_dir is None:
            base_dir = getattr(settings, "BASE_DIR", None)

        if base_dir is not None:
            root_template_dir = os.path.join(base_dir, "templates")
            if os.path.isdir(root_template_dir):
                dirs.append(root_template_dir)

        return dirs

    def reset(self):
        """Empty the template cache."""
        self.cache_handler.reset()

    def get_template_sources(self, template_name):
        """Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set."""
        for template_dir in self.get_dirs():
            try:
                name = safe_join(template_dir, template_name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                continue

            yield Origin(
                name=name,
                template_name=template_name,
                loader=self,
            )


class CottonTemplateCacheHandler:
    """This mimics the simple template caching mechanism in Django's cached.Loader which acts a decent fallback when
    the user has not configured the cache loader manually.

    TODO: implement cache warming functionality e.g. to be used at deployment
    """

    def __init__(self):
        self.template_cache = {}

    def get_cached_template(self, cache_key):
        return self.template_cache.get(cache_key)

    def cache_template(self, cache_key, compiled_template):
        self.template_cache[cache_key] = compiled_template

    def get_cache_key(self, origin):
        try:
            cache_key = self.generate_hash([origin.name, str(os.path.getmtime(origin.name))])
        except FileNotFoundError:
            raise TemplateDoesNotExist(origin)

        return cache_key

    def generate_hash(self, values):
        return hashlib.sha1("|".join(values).encode()).hexdigest()

    def reset(self):
        self.template_cache.clear()
