import random
import re
import warnings
from html.parser import HTMLParser

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from bs4.builder._htmlparser import BeautifulSoupHTMLParser, HTMLParserTreeBuilder
from bs4.formatter import HTMLFormatter

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


class UnsortedAttributes(HTMLFormatter):
    """This keeps BS4 from re-ordering attributes"""

    def attributes(self, tag):
        for k, v in tag.attrs.items():
            yield k, v


class CottonHTMLParser(BeautifulSoupHTMLParser):
    """Extending the default HTML parser to override handle_starttag so we can preserve the intended value of the
    attribute from the developer so that we can differentiate boolean attributes and simply empty ones.
    """

    def __init__(self, tree_builder, soup, on_duplicate_attribute):
        # Initialize the parent class (HTMLParser) without additional arguments
        HTMLParser.__init__(self)
        self._first_processing_instruction = None
        self.tree_builder = tree_builder
        self.soup = soup
        self._root_tag = None  # Initialize _root_tag
        self.already_closed_empty_element = []  # Initialize this list
        self.on_duplicate_attribute = (
            on_duplicate_attribute  # You can set this according to your needs
        )
        self.IGNORE = "ignore"
        self.REPLACE = "replace"

    def handle_starttag(self, name, attrs, handle_empty_element=True):
        """Handle an opening tag, e.g. '<tag>'"""
        attr_dict = {}
        for key, value in attrs:
            # Cotton edit: We want to permit valueless / "boolean" attributes
            # if value is None:
            #     value = ''

            if key in attr_dict:
                on_dupe = self.on_duplicate_attribute
                if on_dupe == self.IGNORE:
                    pass
                elif on_dupe in (None, self.REPLACE):
                    attr_dict[key] = value
                else:
                    on_dupe(attr_dict, key, value)
            else:
                attr_dict[key] = value
        sourceline, sourcepos = self.getpos()
        tag = self.soup.handle_starttag(
            name, None, None, attr_dict, sourceline=sourceline, sourcepos=sourcepos
        )
        if tag and tag.is_empty_element and handle_empty_element:
            self.handle_endtag(name, check_already_closed=False)
            self.already_closed_empty_element.append(name)

        # Cotton edit: We do not need to validate the root element
        # if self._root_tag is None:
        #     self._root_tag_encountered(name)


class CottonHTMLTreeBuilder(HTMLParserTreeBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handle_duplicate_attributes = kwargs.get("on_duplicate_attribute", None)
        self.parser_class = CottonHTMLParser

    def feed(self, markup):
        parser = self.parser_class(self, self.soup, self.handle_duplicate_attributes)
        parser.feed(markup)
        parser.close()


class CottonBs4Compiler:
    DJANGO_SYNTAX_PLACEHOLDER_PREFIX = "__django_syntax__"
    COTTON_VERBATIM_PATTERN = re.compile(
        r"\{% cotton_verbatim %\}(.*?)\{% endcotton_verbatim %\}", re.DOTALL
    )
    DJANGO_TAG_PATTERN = re.compile(r"(\s?)(\{%.*?%\})(\s?)")
    DJANGO_VAR_PATTERN = re.compile(r"(\s?)(\{\{.*?\}\})(\s?)")
    HTML_ENTITY_PATTERN = re.compile(r"&[a-zA-Z]+;|&#[0-9]+;|&#x[a-fA-F0-9]+;")

    def __init__(self):
        self.django_syntax_placeholders = []
        self.html_entity_placeholders = []

    def process(self, content: str):
        processors = [
            self._replace_syntax_with_placeholders,
            self._replace_html_entities_with_placeholders,
            self._compile_cotton_to_django,
            self._replace_placeholders_with_syntax,
            self._replace_placeholders_with_html_entities,
            self._remove_duplicate_attribute_markers,
        ]

        for processor in processors:
            # noinspection PyArgumentList
            content = processor(content)

        return content

    def _replace_html_entities_with_placeholders(self, content):
        """Replace HTML entities with placeholders so they dont get touched by BS4"""

        def replace_entity(match):
            entity = match.group(0)
            self.html_entity_placeholders.append(entity)
            return f"__HTML_ENTITY_{len(self.html_entity_placeholders) - 1}__"

        return self.HTML_ENTITY_PATTERN.sub(replace_entity, content)

    def _replace_placeholders_with_html_entities(self, content: str):
        for i, entity in enumerate(self.html_entity_placeholders):
            content = content.replace(f"__HTML_ENTITY_{i}__", entity)
        return content

    def _replace_syntax_with_placeholders(self, content: str):
        """Replace {% ... %} and {{ ... }} with placeholders so they dont get touched
        or encoded by bs4. We will replace them back after bs4 has done its job."""
        self.django_syntax_placeholders = []

        def replace_pattern(pattern, replacement_func):
            return pattern.sub(replacement_func, content)

        def replace_cotton_verbatim(match):
            """{% cotton_verbatim %} protects the content through the bs4 parsing process when we want to actually print
            cotton syntax in <pre> blocks."""
            inner_content = match.group(1)
            self.django_syntax_placeholders.append({"type": "verbatim", "content": inner_content})
            return (
                f"{self.DJANGO_SYNTAX_PLACEHOLDER_PREFIX}{len(self.django_syntax_placeholders)}__"
            )

        def replace_django_syntax(match):
            """Store if the match had at least one space on the left or right side of the syntax so we can restore it later"""
            left_space, syntax, right_space = match.groups()
            self.django_syntax_placeholders.append(
                {
                    "type": "django",
                    "content": syntax,
                    "left_space": bool(left_space),
                    "right_space": bool(right_space),
                }
            )
            return (
                f" {self.DJANGO_SYNTAX_PLACEHOLDER_PREFIX}{len(self.django_syntax_placeholders)}__ "
            )

        # Replace cotton_verbatim blocks
        content = replace_pattern(self.COTTON_VERBATIM_PATTERN, replace_cotton_verbatim)

        # Replace {% ... %}
        content = replace_pattern(self.DJANGO_TAG_PATTERN, replace_django_syntax)

        # Replace {{ ... }}
        content = replace_pattern(self.DJANGO_VAR_PATTERN, replace_django_syntax)

        return content

    def _compile_cotton_to_django(self, content: str):
        """Convert cotton <c-* syntax to {%."""
        soup = self._make_soup(content)

        if cvars_el := soup.find("c-vars"):
            soup = self._wrap_with_cotton_vars_frame(soup, cvars_el)

        self._transform_components(soup)

        return str(soup.encode(formatter=UnsortedAttributes()).decode("utf-8"))

    def _replace_placeholders_with_syntax(self, content: str):
        """Replace placeholders with original syntax."""
        for i, placeholder in enumerate(self.django_syntax_placeholders, 1):
            if placeholder["type"] == "verbatim":
                placeholder_pattern = f"{self.DJANGO_SYNTAX_PLACEHOLDER_PREFIX}{i}__"
                content = content.replace(placeholder_pattern, placeholder["content"])
            else:
                """
                Construct the regex pattern based on original whitespace. This is to avoid unnecessary whitespace
                changes in the output that can lead to unintended tag type mutations,
                i.e. <div{% expr %}></div> --> <div__placeholder></div__placeholder> --> <div{% expr %}></div{% expr %}>
                """
                left_group = r"( ?)" if not placeholder["left_space"] else ""
                right_group = r"( ?)" if not placeholder["right_space"] else ""
                placeholder_pattern = (
                    f"{left_group}{self.DJANGO_SYNTAX_PLACEHOLDER_PREFIX}{i}__{right_group}"
                )

                content = re.sub(placeholder_pattern, placeholder["content"], content)

        return content

    def _remove_duplicate_attribute_markers(self, content: str):
        return re.sub(r"__COTTON_DUPE_ATTR__[0-9A-F]{5}", "", content, flags=re.IGNORECASE)

    def _wrap_with_cotton_vars_frame(self, soup, cvars_el):
        """If the user has defined a <c-vars> tag, wrap content with {% cotton_vars_frame %} to be able to create and
        govern vars and attributes. To be able to defined new vars within a component and also have them available in the
        same component's context, we wrap the entire contents in another component: cotton_vars_frame. Only when <c-vars>
        is present."""

        cvars_attrs = []
        for k, v in cvars_el.attrs.items():
            if v is None:
                cvars_attrs.append(k)
            else:
                if k == "class":
                    v = " ".join(v)
                cvars_attrs.append(f'{k}="{v}"')

        cvars_el.decompose()
        opening = f"{{% vars {' '.join(cvars_attrs)} %}}"
        opening = opening.replace("\n", "")
        closing = "{% endvars %}"

        # Convert the remaining soup back to a string and wrap it within {% with %} block
        wrapped_content = (
            opening
            + str(soup.encode(formatter=UnsortedAttributes()).decode("utf-8")).strip()
            + closing
        )
        new_soup = self._make_soup(wrapped_content)
        return new_soup

    def _transform_components(self, soup):
        """Replace <c-[component path]> tags with the {% cotton_component %} template tag"""
        for tag in soup.find_all(re.compile("^c-"), recursive=True):
            if tag.name == "c-slot":
                self._transform_named_slot(tag)

                continue

            component_key = tag.name[2:]
            opening_tag = f"{{% c {component_key} "

            # Store attributes that contain template expressions, they are when we use '{{' or '{%' in the value of an attribute
            complex_attrs = []

            # Build the attributes
            for key, value in tag.attrs.items():
                # value might be None
                if value is None:
                    opening_tag += f" {key}"
                    continue

                # BS4 stores class values as a list, so we need to join them back into a string
                if key == "class":
                    value = " ".join(value)

                # Django templates tags cannot have {{ or {% expressions in their attribute values
                # Neither can they have new lines, let's treat them both as "expression attrs"
                if self.DJANGO_SYNTAX_PLACEHOLDER_PREFIX in value or "\n" in value or "=" in value:
                    complex_attrs.append((key, value))
                    continue

                opening_tag += ' {}="{}"'.format(key, value)
            opening_tag += " %}"

            component_tag = opening_tag

            if complex_attrs:
                for key, value in complex_attrs:
                    component_tag += f"{{% attr {key} %}}{value}{{% endattr %}}"

            if tag.contents:
                tag_soup = self._make_soup(tag.decode_contents(formatter=UnsortedAttributes()))
                self._transform_components(tag_soup)
                component_tag += str(
                    tag_soup.encode(formatter=UnsortedAttributes()).decode("utf-8")
                    # tag_soup.decode_contents(formatter=UnsortedAttributes())
                )

            component_tag += "{% endc %}"

            # Replace the original tag with the compiled django syntax
            new_soup = self._make_soup(component_tag)
            tag.replace_with(new_soup)

        return soup

    def _transform_named_slot(self, slot_tag):
        """Compile <c-slot> to {% slot %}"""
        slot_name = slot_tag.get("name", "").strip()
        inner_html = slot_tag.decode_contents(formatter=UnsortedAttributes())

        # Check and process any components in the slot content
        slot_soup = self._make_soup(inner_html)
        self._transform_components(slot_soup)

        cotton_slot_tag = f"{{% slot {slot_name} %}}{str(slot_soup.encode(formatter=UnsortedAttributes()).decode('utf-8'))}{{% endslot %}}"

        slot_tag.replace_with(self._make_soup(cotton_slot_tag))

    def _make_soup(self, content):
        return BeautifulSoup(
            content,
            "html.parser",
            builder=CottonHTMLTreeBuilder(on_duplicate_attribute=handle_duplicate_attributes),
        )


def handle_duplicate_attributes(tag_attrs, key, value):
    """BS4 cleans html and removes duplicate attributes. This would be fine if our target was html, but actually
    we're targeting Django Template Language. This contains expressions to govern content including attributes of
    any XML-like tag. It's perfectly fine to expect duplicate attributes per tag in DTL:

    <a href="#" {% if something %} class="this" {% else %} class="that" {% endif %}>Hello</a>

    The solution here is to make duplicate attribute keys unique across that tag so BS4 will not attempt to merge or
    replace existing. Then in post processing we'll remove the unique mask.

    Todo - This could be simplified with a custom formatter
    """
    key_id = "".join(random.choice("0123456789ABCDEF") for i in range(5))
    key = f"{key}__COTTON_DUPE_ATTR__{key_id}"
    tag_attrs[key] = value
