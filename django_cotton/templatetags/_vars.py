from typing import List

from django.template.base import (
    Variable,
    VariableDoesNotExist,
    Node,
)

from django_cotton.templatetags import DynamicAttr, UnprocessableDynamicAttr, Attrs
from django_cotton.utils import get_cotton_data


class CottonVarsNode(Node):
    def __init__(self, var_dict, empty_vars: List, nodelist):
        self.var_dict = var_dict
        self.empty_vars = empty_vars
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)

        if cotton_data["stack"]:
            current_component = cotton_data["stack"][-1]
            attrs = current_component["attrs"]
        else:
            attrs = Attrs({})

        vars = {}

        for key, value in self.var_dict.items():
            if key not in attrs.exclude_unprocessable():
                if key.startswith(":"):
                    try:
                        vars[key[1:]] = DynamicAttr(value, is_cvar=True).resolve(context)
                    except UnprocessableDynamicAttr:
                        pass
                else:
                    attrs[key] = value
            attrs.exclude_from_string_output(key)

        # Process cvars without values
        for empty_var in self.empty_vars:
            attrs.exclude_from_string_output(empty_var)

        with context.push({**vars, **attrs.make_attrs_accessible(), "attrs": attrs}):
            output = self.nodelist.render(context)

        return output


def cotton_cvars(parser, token):
    bits = token.split_contents()[1:]
    var_dict = {}
    empty_vars = []
    for bit in bits:
        try:
            key, value = bit.split("=")
            var_dict[key] = value.strip("\"'")
        except ValueError:
            empty_vars.append(bit)

    nodelist = parser.parse(("endvars",))
    parser.delete_first_token()

    return CottonVarsNode(var_dict, empty_vars, nodelist)
