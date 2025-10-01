import hashlib

from django.template import Library, Node, TemplateSyntaxError
from django.template.base import token_kwargs, FilterExpression
from django.utils.safestring import mark_safe

from django_cotton.utils import get_cotton_data

register = Library()


class CottonStackNode(Node):
    def __init__(self, name_expr: FilterExpression, nodelist):
        self.name_expr = name_expr
        self.nodelist = nodelist

    def render(self, context):
        stack_name = str(self.name_expr.resolve(context))
        cotton_data = get_cotton_data(context)
        fallback = self.nodelist.render(context) if self.nodelist else ""

        request = context.get("request")
        middleware_active = bool(getattr(request, "_cotton_stack_middleware", False)) if request else False

        if not middleware_active:
            pushes = cotton_data.get("push_stacks", {}).get(stack_name, {})
            rendered = "".join(pushes.get("items", [])) if pushes else ""
            return mark_safe(rendered or fallback)

        # Generate unique placeholder to prevent accidental replacement
        placeholder_id = hashlib.md5(f"{id(self)}_{stack_name}".encode()).hexdigest()[:8]
        placeholder = f"__COTTON_STACK_{placeholder_id}_{stack_name}__"
        
        cotton_data.setdefault("stack_placeholders", []).append(
            {
                "placeholder": placeholder,
                "name": stack_name,
                "fallback": fallback,
            }
        )

        return placeholder


class CottonPushNode(Node):
    def __init__(self, target_expr: FilterExpression, nodelist, key_expr=None, allow_multiple=False):
        self.target_expr = target_expr
        self.key_expr = key_expr
        self.allow_multiple = allow_multiple
        self.nodelist = nodelist

    def render(self, context):
        stack_name = str(self.target_expr.resolve(context))
        cotton_data = get_cotton_data(context)

        rendered_content = self.nodelist.render(context)

        stacks = cotton_data.setdefault("push_stacks", {})
        stack = stacks.setdefault(stack_name, {"items": [], "keys": set()})

        dedupe_key = None
        if not self.allow_multiple:
            if self.key_expr is not None:
                dedupe_key = self.key_expr.resolve(context)
            else:
                dedupe_key = rendered_content.strip()

            if dedupe_key in stack["keys"]:
                return ""

            stack["keys"].add(dedupe_key)

        stack["items"].append(rendered_content)

        return ""


def cotton_stack(parser, token):
    bits = token.split_contents()[1:]
    kwargs = token_kwargs(bits, parser, support_legacy=False)

    if bits:
        raise TemplateSyntaxError("Unknown arguments provided to c-stack tag")

    if "name" not in kwargs:
        raise TemplateSyntaxError("c-stack tag requires a 'name' attribute")

    nodelist = parser.parse(("endstack",))
    parser.delete_first_token()

    name_expr = kwargs.pop("name")

    if kwargs:
        raise TemplateSyntaxError(f"Unknown keyword arguments for c-stack tag: {', '.join(kwargs.keys())}")

    return CottonStackNode(name_expr, nodelist)


def cotton_push(parser, token):
    bits = token.split_contents()[1:]
    kwargs = token_kwargs(bits, parser, support_legacy=False)
    
    # Separate flags from kwargs
    flags = []
    for bit in bits:
        if "=" not in bit and bit not in kwargs.values():
            flags.append(bit)

    if "to" not in kwargs:
        raise TemplateSyntaxError("c-push tag requires a 'to' attribute")

    if "key" in kwargs and "id" in kwargs:
        raise TemplateSyntaxError("c-push tag cannot have both 'key' and 'id' attributes")

    allow_multiple = "multiple" in flags
    if allow_multiple:
        flags.remove("multiple")

    key_expr = None
    for key_name in ("key", "id"):
        if key_name in kwargs:
            key_expr = kwargs.pop(key_name)
            break

    if flags:
        raise TemplateSyntaxError(f"Unknown arguments for c-push tag: {', '.join(sorted(flags))}")

    nodelist = parser.parse(("endpush",))
    parser.delete_first_token()

    target_expr = kwargs.pop("to")

    if kwargs:
        raise TemplateSyntaxError(f"Unknown keyword arguments for c-push tag: {', '.join(kwargs.keys())}")

    return CottonPushNode(target_expr, nodelist, key_expr=key_expr, allow_multiple=allow_multiple)
