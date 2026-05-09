import re
from typing import List, Tuple

from django.conf import settings


def get_cotton_tag_prefix() -> str:
    return getattr(settings, "COTTON_TAG_PREFIX", "c")


class Tag:
    attr_pattern = re.compile(r'([^\s/>\"\'=<>`]+)(?:\s*=\s*(?:(["\'])(.*?)\2|(\S+)))?', re.DOTALL)

    def __init__(self, match: re.Match, prefix: str = "c"):
        self.prefix = prefix
        self.html = match.group(0)
        self.tag_name = f"{prefix}-{match.group(2)}"
        self.attrs = match.group(3) or ""
        self.is_closing = bool(match.group(1))
        self.is_self_closing = bool(match.group(4))

    def get_template_tag(self) -> str:
        if self.tag_name == f"{self.prefix}-vars":
            return ""
        elif self.tag_name == f"{self.prefix}-slot":
            return self._process_slot()
        elif self.tag_name.startswith(f"{self.prefix}-"):
            return self._process_component()
        else:
            return self.html

    def _process_slot(self) -> str:
        if self.is_closing:
            return "{% endcotton:slot %}"
        name_match = re.search(r'name=(["\'])(.*?)\1', self.attrs, re.DOTALL)
        if not name_match:
            raise ValueError(f"{self.prefix}-slot tag must have a name attribute: {self.html}")
        slot_name = name_match.group(2)
        return f"{{% cotton:slot {slot_name} %}}"

    def _process_component(self) -> str:
        component_name = self.tag_name[len(self.prefix) + 1:]
        if self.is_closing:
            return "{% endcotton %}"
        processed_attrs, extracted_attrs = self._process_attributes()
        opening_tag = f"{{% cotton {component_name}{processed_attrs} %}}"
        if self.is_self_closing:
            return f"{opening_tag}{extracted_attrs}{{% endcotton %}}"
        return f"{opening_tag}{extracted_attrs}"

    def _process_attributes(self) -> Tuple[str, str]:
        processed_attrs = []
        extracted_attrs = []

        for match in self.attr_pattern.finditer(self.attrs):
            key, quote, value, unquoted_value = match.groups()
            if value is None and unquoted_value is None:
                processed_attrs.append(key)
            elif value is not None:
                quote_char = quote if quote else '"'
                processed_attrs.append(f'{key}={quote_char}{value}{quote_char}')
            else:
                processed_attrs.append(f'{key}={unquoted_value}')

        attrs_str = " ".join(processed_attrs)
        return " " + attrs_str if attrs_str else "", "".join(extracted_attrs)


def _build_tag_pattern(prefix: str) -> re.Pattern:
    escaped = re.escape(prefix)
    return re.compile(
        rf"<(/?){escaped}-([^\s/>]+)((?:\s+[^\s/>\"'=<>`]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|\S+))?)*)\s*(/?)\s*>",
        re.DOTALL,
    )


def _build_c_vars_pattern(prefix: str) -> re.Pattern:
    escaped = re.escape(prefix)
    return re.compile(
        rf"<{escaped}-vars\s([^>]*)(?:/>|>(.*?)</{escaped}-vars>)", re.DOTALL
    )


class CottonCompiler:
    _ignore_pattern = re.compile(
        r"({%\s*verbatim(?:\s+\w+)?\s*%}.*?{%\s*endverbatim(?:\s+\w+)?\s*%}|"
        r"{%\s*cotton:verbatim\s*%}.*?{%\s*endcotton:verbatim\s*%}|"
        r"{%\s*comment\s*%}.*?{%\s*endcomment\s*%}|{#.*?#}|"
        r"{{.*?}}|{%.*?%})",
        re.DOTALL,
    )
    _cotton_verbatim_pattern = re.compile(
        r"{%\s*cotton:verbatim\s*%}(.*?){%\s*endcotton:verbatim\s*%}", re.DOTALL
    )

    def __init__(self):
        self._prefix = None
        self._tag_pattern = None
        self._c_vars_pattern = None
        self._sync_prefix()

    def _sync_prefix(self):
        current_prefix = get_cotton_tag_prefix()
        if self._prefix != current_prefix:
            self._prefix = current_prefix
            self._tag_pattern = _build_tag_pattern(self._prefix)
            self._c_vars_pattern = _build_c_vars_pattern(self._prefix)

    @property
    def prefix(self):
        return self._prefix

    def exclude_ignorables(self, html: str) -> Tuple[str, List[Tuple[str, str]]]:
        ignorables = []

        def replace_ignorable(match):
            placeholder = f"__COTTON_IGNORE_{len(ignorables)}__"
            ignorables.append((placeholder, match.group(0)))
            return placeholder

        processed_html = self._ignore_pattern.sub(replace_ignorable, html)
        return processed_html, ignorables

    def restore_ignorables(self, html: str, ignorables: List[Tuple[str, str]]) -> str:
        for placeholder, content in ignorables:
            if content.strip().startswith("{% cotton:verbatim %}"):
                match = self._cotton_verbatim_pattern.search(content)
                if match:
                    content = match.group(1)
            html = html.replace(placeholder, content)
        return html

    def get_replacements(self, html: str) -> List[Tuple[str, str]]:
        replacements = []
        for match in self._tag_pattern.finditer(html):
            tag = Tag(match, self._prefix)
            try:
                template_tag = tag.get_template_tag()
                if template_tag != tag.html:
                    replacements.append((tag.html, template_tag))
            except ValueError as e:
                position = match.start()
                line_number = html[:position].count("\n") + 1
                raise ValueError(f"Error in template at line {line_number}: {str(e)}") from e

        return replacements

    def process_c_vars(self, html: str) -> Tuple[str, str]:
        matches = list(self._c_vars_pattern.finditer(html))

        if len(matches) > 1:
            raise ValueError(
                f"Multiple {self._prefix}-vars tags found in component template. "
                f"Only one {self._prefix}-vars tag is allowed per template."
            )

        match = matches[0] if matches else None
        if match:
            attrs = match.group(1)
            vars_content = f"{{% cotton:vars {attrs.strip()} %}}"
            html = self._c_vars_pattern.sub("", html)
            return vars_content, html

        return "", html

    def process(self, html: str) -> str:
        self._sync_prefix()
        processed_html, ignorables = self.exclude_ignorables(html)
        vars_content, processed_html = self.process_c_vars(processed_html)
        replacements = self.get_replacements(processed_html)
        for original, replacement in replacements:
            processed_html = processed_html.replace(original, replacement)
        if vars_content:
            processed_html = f"{vars_content}{processed_html}"
        return self.restore_ignorables(processed_html, ignorables)
