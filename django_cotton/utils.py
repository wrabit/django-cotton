import ast

from bs4.builder._htmlparser import BeautifulSoupHTMLParser, HTMLParserTreeBuilder
from html.parser import HTMLParser


def eval_string(value):
    """
    Evaluate a string representation of a constant, list, or dictionary to the actual Python object.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def ensure_quoted(value):
    if isinstance(value, str):
        if value.startswith('{"') and value.endswith("}"):
            return f"'{value}'"  # use single quotes for json-like strings
        elif value.startswith('"') and value.endswith('"'):
            return value  # already quoted
    return f'"{value}"'  # default to double quotes


def get_cotton_data(context):
    if "cotton_data" not in context:
        context["cotton_data"] = {"stack": [], "vars": {}}
    return context["cotton_data"]


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
