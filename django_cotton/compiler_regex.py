import re
from typing import List, Tuple, Optional
from html.parser import HTMLParser


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
        """
        Extract c-vars content and remove c-vars tags from the html.
        Raises ValueError if more than one c-vars tag is found.
        """
        # Find all matches of c-vars tags
        matches = list(self.c_vars_pattern.finditer(html))

        if len(matches) > 1:
            raise ValueError(
                "Multiple c-vars tags found in component template. Only one c-vars tag is allowed per template."
            )

        # Process single c-vars tag if present
        match = matches[0] if matches else None
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


class CottonDirectiveParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.available_directives = ["c-if", "c-elif", "c-else", "c-for"]
        self.result = []
        self.directive_blocks = []
        
    def has_directive(self, attrs: dict) -> Tuple[bool, Optional[str]]:
        """
        Check if a single directive is present in the element.
        Raises ValueError if more than one directive is found.
        """
        directives = [directive for directive in self.available_directives if directive in attrs]
        
        if (len(directives) > 1):
            raise ValueError(
                "Multiple cotton directives found in the same element. Only one directive is allowed per HTML element."
            )
            
        return (True, directives[0]) if directives else (False, None)
    
    def build_tag(self, tag: str, attrs: List[Tuple[str, Optional[str]]], self_closing=False) -> str:
        """Build an HTML start tag (or self-closing tag) from the given tag name and attributes."""
        parts = [f"<{tag}"]
        for k, v in attrs:
            parts.append(f' {k}="{v}"')
        parts.append("/>" if self_closing else ">")
        return "".join(parts)
    
    def adjust_conditional_directive(self, directive):
        """
        Removes the closing {% endif %} from the previous block to allow continuation 
        with 'elif' or 'else'. Raises a ValueError if the conditional structure is invalid
        (i.e., 'c-elif' or 'c-else' not immediately following a valid 'c-if' or 'c-elif').
        """
        error = ValueError(
            f"An element with the '{directive}' directive must follow an element "
            "with a 'c-if' or 'c-elif' directive. Ensure that conditional directives "
            "follow the correct structure."
        )
        
        if len(self.directive_blocks) > 1:
            buffer = self.directive_blocks[-2]['buffer']
        else:
            buffer = self.result
        
        if len(buffer) >= 1 and buffer[-1] == "{% endif %}":
            buffer.pop()
        elif len(buffer) >= 2 and buffer[-2] == "{% endif %}":
            buffer.pop(-2) 
        else:
            raise error

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        """Handles opening tags, detects directives, and manages directive block buffering."""
        attrs_dict = dict(attrs)
        has_directive, directive = self.has_directive(attrs_dict)
        
        if has_directive:
            clean_attrs = [(k, v) for k, v in attrs if k not in self.available_directives]
            tag_with_attrs = self.build_tag(tag, clean_attrs)
            directive_block = {
                "directive": directive,
                "directive_value": attrs_dict[directive],
                "stack": [tag],
                "buffer": [tag_with_attrs]
            }
            self.directive_blocks.append(directive_block)
            
            if directive == "c-elif" or directive == "c-else":
                self.adjust_conditional_directive(directive)
                
        elif self.directive_blocks:
            tag_with_attrs = self.build_tag(tag, attrs)
            current_block = self.directive_blocks[-1]
            current_block["buffer"].append(tag_with_attrs)
            current_block["stack"].append(tag)
        else:
            self.result.append(self.build_tag(tag, attrs))

    def handle_endtag(self, tag: str):
        """Handles closing tags and finalizes directive blocks if applicable."""
        if self.directive_blocks:
            current_block = self.directive_blocks[-1]
            current_block["buffer"].append(f"</{tag}>")
            current_block["stack"].pop()

            if not current_block["stack"]:
                block_content = "".join(current_block["buffer"])
                directive = current_block["directive"].replace("c-", "")
                closing = "if" if directive in ["elif", "else"] else directive
                value = current_block["directive_value"] or ""
                
                rendered = [
                    f"{{% {directive} {value} %}}".strip(),
                    block_content,
                    f"{{% end{closing} %}}"
                ]
                
                if len(self.directive_blocks) > 1:
                    self.directive_blocks[-2]["buffer"].extend(rendered)
                else:
                    self.result.extend(rendered)

                self.directive_blocks.pop()
        else:
            self.result.append(f"</{tag}>")

    def handle_data(self, data: str):
        """Handles raw text content inside or outside directive blocks."""
        if self.directive_blocks:
            self.directive_blocks[-1]["buffer"].append(data)
        else:
            self.result.append(data)

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        """Handles self-closing tags and buffers them appropriately."""
        tag_with_attrs = self.build_tag(tag, attrs, self_closing=True)
        
        if self.directive_blocks:
            self.directive_blocks[-1]["buffer"].append(tag_with_attrs)
        else:
            self.result.append(tag_with_attrs)

    def process(self, html: str) -> str:
        """Parses the input HTML and returns the transformed output with directives rendered."""
        if not any(f'{directive}=' in html for directive in self.available_directives):
            return html

        self.feed(html)
        final_result = "".join(self.result)
        self.result = [] # reset for reuse
        return final_result