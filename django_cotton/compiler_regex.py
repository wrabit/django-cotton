import re
from typing import List, Tuple


class Tag:
    tag_pattern = re.compile(
        r"<(/?)c-([^\s/>]+)((?:\s+[^\s/>\"'=<>`]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|\S+))?)*)\s*(/?)\s*>",
        re.DOTALL,
    )
    attr_pattern = re.compile(r'([^\s/>\"\'=<>`]+)(?:\s*=\s*(?:(["\'])(.*?)\2|(\S+)))?', re.DOTALL)

    def __init__(self, match: re.Match):
        self.html = match.group(0)
        self.tag_name = f"c-{match.group(2)}"
        self.attrs = match.group(3) or ""
        self.is_closing = bool(match.group(1))
        self.is_self_closing = bool(match.group(4))

    def get_template_tag(self) -> str:
        """Convert a cotton tag to a Django template tag"""
        if self.tag_name == "c-vars":
            return ""  # c-vars tags will be handled separately
        elif self.tag_name == "c-slot":
            return self._process_slot()
        elif self.tag_name.startswith("c-"):
            return self._process_component()
        else:
            return self.html

    def _process_slot(self) -> str:
        """Convert a c-slot tag to a Django template slot tag"""
        if self.is_closing:
            return "{% endslot %}"
        name_match = re.search(r'name=(["\'])(.*?)\1', self.attrs, re.DOTALL)
        if not name_match:
            raise ValueError(f"c-slot tag must have a name attribute: {self.html}")
        slot_name = name_match.group(2)
        return f"{{% slot {slot_name} %}}"

    def _process_component(self) -> str:
        """Convert a c- component tag to a Django template component tag"""
        component_name = self.tag_name[2:]
        if self.is_closing:
            return "{% endc %}"
        processed_attrs, extracted_attrs = self._process_attributes()
        opening_tag = f"{{% c {component_name}{processed_attrs} %}}"
        if self.is_self_closing:
            return f"{opening_tag}{extracted_attrs}{{% endc %}}"
        return f"{opening_tag}{extracted_attrs}"

    def _process_attributes(self) -> Tuple[str, str]:
        """Move any complex attributes to the {% attr %} tag"""
        processed_attrs = []
        extracted_attrs = []

        for match in self.attr_pattern.finditer(self.attrs):
            key, quote, value, unquoted_value = match.groups()
            if value is None and unquoted_value is None:
                processed_attrs.append(key)
            else:
                actual_value = value if value is not None else unquoted_value
                if any(s in actual_value for s in ("{{", "{%", "=", "__COTTON_IGNORE_")):
                    extracted_attrs.append(f"{{% attr {key} %}}{actual_value}{{% endattr %}}")
                else:
                    processed_attrs.append(f'{key}="{actual_value}"')

        return " " + " ".join(processed_attrs), "".join(extracted_attrs)


class CottonCompiler:
    def __init__(self):
        self.c_vars_pattern = re.compile(r"<c-vars\s([^>]*)(?:/>|>(.*?)</c-vars>)", re.DOTALL)
        self.ignore_pattern = re.compile(
            # cotton_verbatim isnt a real template tag, it's just a way to ignore <c-* tags from being compiled
            r"({%\s*cotton_verbatim\s*%}.*?{%\s*endcotton_verbatim\s*%}|"
            # Ignore both forms of comments
            r"{%\s*comment\s*%}.*?{%\s*endcomment\s*%}|{#.*?#}|"
            # Ignore django template tags and variables
            r"{{.*?}}|{%.*?%})",
            re.DOTALL,
        )
        self.cotton_verbatim_pattern = re.compile(
            r"{%\s*cotton_verbatim\s*%}(.*?){%\s*endcotton_verbatim\s*%}", re.DOTALL
        )

    def exclude_ignorables(self, html: str) -> Tuple[str, List[Tuple[str, str]]]:
        ignorables = []

        def replace_ignorable(match):
            placeholder = f"__COTTON_IGNORE_{len(ignorables)}__"
            ignorables.append((placeholder, match.group(0)))
            return placeholder

        processed_html = self.ignore_pattern.sub(replace_ignorable, html)
        return processed_html, ignorables

    def restore_ignorables(self, html: str, ignorables: List[Tuple[str, str]]) -> str:
        for placeholder, content in ignorables:
            if content.strip().startswith("{% cotton_verbatim %}"):
                # Extract content between cotton_verbatim tags, we don't want to leave these in
                match = self.cotton_verbatim_pattern.search(content)
                if match:
                    content = match.group(1)
            html = html.replace(placeholder, content)
        return html

    def get_replacements(self, html: str) -> List[Tuple[str, str]]:
        replacements = []
        for match in Tag.tag_pattern.finditer(html):
            tag = Tag(match)
            try:
                template_tag = tag.get_template_tag()
                if template_tag != tag.html:
                    replacements.append((tag.html, template_tag))
            except ValueError as e:
                # Find the line number of the error
                position = match.start()
                line_number = html[:position].count("\n") + 1
                raise ValueError(f"Error in template at line {line_number}: {str(e)}") from e

        return replacements

    def process_c_vars(self, html: str) -> Tuple[str, str]:
        """Extract c-vars content and remove c-vars tags from the html"""
        match = self.c_vars_pattern.search(html)
        if match:
            attrs = match.group(1)
            vars_content = f"{{% vars {attrs.strip()} %}}"
            html = self.c_vars_pattern.sub("", html)  # Remove all c-vars tags
            return vars_content, html
        return "", html

    def process(self, html: str) -> str:
        """Putting it all together"""
        processed_html, ignorables = self.exclude_ignorables(html)
        vars_content, processed_html = self.process_c_vars(processed_html)
        replacements = self.get_replacements(processed_html)
        for original, replacement in replacements:
            processed_html = processed_html.replace(original, replacement)
        if vars_content:
            processed_html = f"{vars_content}{processed_html}{{% endvars %}}"
        return self.restore_ignorables(processed_html, ignorables)
