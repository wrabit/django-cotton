import os
import re
import hashlib
import warnings

from django.template.loaders.base import Loader as BaseLoader
from django.core.exceptions import SuspiciousFileOperation
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join
from django.template import Template
from django.core.cache import cache
from django.template import Origin
from django.conf import settings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


class Loader(BaseLoader):
    is_usable = True

    def __init__(self, engine, dirs=None):
        super().__init__(engine)
        self.cache_handler = CottonTemplateCacheHandler()
        self.dirs = dirs
        self.django_syntax_placeholders = []

    def get_template_from_string(self, template_string):
        """Create and return a Template object from a string. Used primarily for testing."""
        return Template(template_string, engine=self.engine)

    def get_contents(self, origin):
        # check if file exists, whilst getting the mtime for cache key
        try:
            mtime = os.path.getmtime(origin.name)
        except FileNotFoundError:
            raise TemplateDoesNotExist(origin)

        # check and return cached template
        cache_key = self.cache_handler.get_cache_key(origin.template_name, mtime)
        cached_content = self.cache_handler.get_cached_template(cache_key)
        if cached_content is not None:
            return cached_content

        # If not cached, process the template
        template_string = self._get_template_string(origin.name)

        # We need to provide a key to the current view or component (in this case, view) so that we can namespace
        # slot data, preventing bleeding and ensure components only clear data in their own context
        # in this case, we're top level, likely in a view so we use the view template name as the key
        component_key = (
            origin.template_name.lstrip("cotton/")
            .rstrip(".cotton.html")
            .replace("/", ".")
        )

        compiled_template = self._compile_template_from_string(
            template_string, component_key
        )

        # Cache the processed template
        self.cache_handler.cache_template(cache_key, compiled_template)

        return compiled_template

    def _replace_syntax_with_placeholders(self, content):
        """# replace {% ... %} and {{ ... }} with placeholders so they dont get touched
        or encoded by bs4. Store them to later switch them back in after transformation.
        """
        self.django_syntax_placeholders = []

        # First handle cotton_verbatim blocks, this is designed to preserve and display cotton syntax,
        # akin to the verbatim tag in Django.
        def replace_cotton_verbatim(match):
            inner_content = match.group(
                1
            )  # Get the inner content without the cotton_verbatim tags
            self.django_syntax_placeholders.append(inner_content)
            return f"__django_syntax__{len(self.django_syntax_placeholders)}__"

        # Replace cotton_verbatim blocks, capturing inner content
        content = re.sub(
            r"\{% cotton_verbatim %\}(.*?)\{% endcotton_verbatim %\}",
            replace_cotton_verbatim,
            content,
            flags=re.DOTALL,
        )

        content = re.sub(
            r"\{%.*?%\}",
            lambda x: self.django_syntax_placeholders.append(x.group(0))
            or f"__django_syntax__{len(self.django_syntax_placeholders)}__",
            content,
        )
        content = re.sub(
            r"\{\{.*?\}\}",
            lambda x: self.django_syntax_placeholders.append(x.group(0))
            or f"__django_syntax__{len(self.django_syntax_placeholders)}__",
            content,
        )

        return content

    def _replace_placeholders_with_syntax(self, content):
        """After modifying the content, replace the placeholders with the django template tags and variables."""
        for i, placeholder in enumerate(self.django_syntax_placeholders, 1):
            content = content.replace(f"__django_syntax__{i}__", placeholder)

        return content

    def _get_template_string(self, template_name):
        try:
            with open(template_name, "r") as f:
                content = f.read()
        except FileNotFoundError:
            raise TemplateDoesNotExist(template_name)

        return content

    def _compile_template_from_string(self, content, component_key):
        content = self._replace_syntax_with_placeholders(content)
        content = self._compile_cotton_to_django(content, component_key)
        content = self._replace_placeholders_with_syntax(content)
        content = self._revert_bs4_attribute_empty_attribute_fixing(content)

        return content

    def _revert_bs4_attribute_empty_attribute_fixing(self, contents):
        """Django's template parser adds ="" to empty attribute-like parts in any html-like node, i.e. <div {{ something }}> gets
        compiled to <div {{ something }}=""> Then if 'something' is holding attributes sets, the last attribute value is
        not quoted. i.e. model=test not model="test"."""
        cleaned_content = re.sub('}}=""', "}}", contents)
        return cleaned_content

    def get_dirs(self):
        return self.dirs if self.dirs is not None else self.engine.dirs

    def get_template_sources(self, template_name):
        """Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set."""
        if template_name.endswith(".cotton.html"):
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

    def _compile_cotton_to_django(self, html_content, component_key):
        """Convert cotton <c-* syntax to {%."""
        soup = BeautifulSoup(html_content, "html.parser")

        soup = self._wrap_with_cotton_props_frame(soup)
        self._transform_components(soup, component_key)

        return str(soup)

    def _transform_prop_tags(self, soup):
        c_props = soup.find_all("c-props")

        for tag in c_props:
            # Build the cotton_props tag string
            props_list = []
            for prop, value in tag.attrs.items():
                if value is None:
                    props_list.append(prop)
                else:
                    props_list.append(f'{prop}="{value}"')

            cotton_props_str = "{% cotton_props " + " ".join(props_list) + " %}"

            # Replace the <c-props> tag with the cotton_props string.
            tag.replace_with(cotton_props_str)

        return soup

    def _wrap_with_cotton_props_frame(self, soup):
        """Wrap content with {% cotton_props_frame %} to be able to govern props and attributes. In order to recognise
        props defined in a component and also have them available in the same component's context, we wrap the entire
        contents in another component: cotton_props_frame."""
        props_with_defaults = []
        c_props = soup.find("c-props")

        # parse c-props tag to extract properties and defaults
        if c_props:
            props_with_defaults = []
            for prop, value in c_props.attrs.items():
                if value is None:
                    props_with_defaults.append(f"{prop}={prop}")
                else:
                    # Assuming value is already a string that represents the default value
                    props_with_defaults.append(f'{prop}={prop}|default:"{value}"')

            c_props.decompose()

        # Construct the {% with %} opening tag
        opening = "{% cotton_props_frame " + " ".join(props_with_defaults) + " %}"
        closing = "{% endcotton_props_frame %}"

        # Convert the remaining soup back to a string and wrap it within {% with %} block
        wrapped_content = opening + str(soup).strip() + closing

        # Since we can't replace the soup object itself, we create new soup instead
        new_soup = BeautifulSoup(wrapped_content, "html.parser")

        return new_soup

    def _transform_named_slot(self, slot_tag, component_key):
        """Replace <c-slot> tags with the {% cotton_slot %} template tag"""
        # for c_slot in soup.find_all("c-slot"):
        slot_name = slot_tag.get("name", "").strip()
        inner_html = "".join(str(content) for content in slot_tag.contents)

        # Check and process any components in the slot content

        slot_soup = BeautifulSoup(inner_html, "html.parser")
        self._transform_components(slot_soup, component_key)

        cotton_slot_tag = f"{{% cotton_slot {slot_name} {component_key} %}}{str(slot_soup)}{{% end_cotton_slot %}}"

        slot_tag.replace_with(BeautifulSoup(cotton_slot_tag, "html.parser"))

    def _transform_components(self, soup, component_key):
        """Replace <c-[component path]> tags with the {% cotton_component %} template tag"""
        for tag in soup.find_all(re.compile("^c-"), recursive=True):
            if tag.name == "c-slot":
                self._transform_named_slot(tag, component_key)

                continue

            component_name = tag.name[2:]

            # Convert dot notation to path structure and replace hyphens with underscores
            path = component_name.replace(".", "/").replace("-", "_")

            # Construct the opening tag
            opening_tag = f"{{% cotton_component {'cotton/{}.cotton.html'.format(path)} {component_name} "

            for attr, value in tag.attrs.items():
                if attr == "class":
                    value = " ".join(value)
                opening_tag += ' {}="{}"'.format(attr, value)
            opening_tag += " %}"

            # Construct the closing tag
            closing_tag = "{% end_cotton_component %}"

            if tag.contents:
                tag_soup = BeautifulSoup(tag.decode_contents(), "html.parser")
                self._transform_components(tag_soup, component_name)

                # Create new content with opening tag, tag content, and closing tag
                new_content = opening_tag + str(tag_soup) + closing_tag

            else:
                # Create new content with opening tag and closing tag
                new_content = opening_tag + closing_tag

            # Replace the original tag with the new content
            new_soup = BeautifulSoup(new_content, "html.parser")
            tag.replace_with(new_soup)

        return soup


class CottonTemplateCacheHandler:
    """Handles caching of cotton templates so the html parsing is only done on first load of each view or component."""

    def __init__(self):
        self.enabled = getattr(settings, "TEMPLATE_CACHING_ENABLED", True)

    def get_cache_key(self, template_name, mtime):
        template_hash = hashlib.sha256(template_name.encode()).hexdigest()
        return f"cotton_cache_{template_hash}_{mtime}"

    def get_cached_template(self, cache_key):
        if not self.enabled:
            return None
        return cache.get(cache_key)

    def cache_template(self, cache_key, content, timeout=None):
        if self.enabled:
            cache.set(cache_key, content, timeout=timeout)
