import hashlib
import re

from django.template import TemplateSyntaxError
from django.template.base import Node, TokenType
from django.utils.safestring import mark_safe

from django_cotton import portals
from django_cotton.utils import get_cotton_data

_ATTR_RE = re.compile(r'(\w+)(?:=(["\'])(.*?)\2)?')
_END_TAG = "endcotton:portal"


def cotton_portal(parser, token):
    """{% cotton:portal name="head" %}                       destination
    {% cotton:portal to="head" [multiple] %}...{% endcotton:portal %}   source
    """
    parts = token.contents.split(None, 1)
    attr_string = parts[1] if len(parts) > 1 else ""
    attrs = {m.group(1): m.group(3) if m.group(3) is not None else True for m in _ATTR_RE.finditer(attr_string)}

    if "to" in attrs:
        before = list(parser.tokens)
        nodelist = parser.parse((_END_TAG,))
        block = _block_id(before[len(parser.tokens):])
        parser.delete_first_token()
        return PortalSourceNode(attrs["to"], nodelist, block=block, multiple=attrs.get("multiple") is True)

    if "name" in attrs:
        # Allow the explicit closing form `<c-portal name="x"></c-portal>`.
        if (
            parser.tokens
            and parser.tokens[0].token_type == TokenType.BLOCK
            and parser.tokens[0].contents.strip() == _END_TAG
        ):
            parser.delete_first_token()
        return PortalDestinationNode(attrs["name"])

    raise TemplateSyntaxError('c-portal needs either name="..." (destination) or to="..." (source)')


def _block_id(tokens) -> str:
    """Identify a push block by its source: the tokens between the tags, with
    whitespace normalised so indentation differences don't split an id. The
    same block in two components gets the same id, which is what lets them
    share a slot."""
    source = "\n".join(f"{t.token_type.value}:{' '.join(t.contents.split())}" for t in tokens)
    return hashlib.sha1(source.encode()).hexdigest()[:10]


class PortalDestinationNode(Node):
    def __init__(self, name):
        self.name = name

    def render(self, context):
        # Make sure the render has a collector even if no component ever runs,
        # so the root template knows there is something to resolve.
        get_cotton_data(context)
        return mark_safe(portals.marker(self.name))


class PortalSourceNode(Node):
    def __init__(self, to, nodelist, block=None, multiple=False):
        self.to = to
        self.nodelist = nodelist
        self.block = block  # derived from the block's source at parse time
        self.multiple = multiple

    def render(self, context):
        cotton_data = get_cotton_data(context)
        # One render per block per page unless `multiple`. The claim comes before
        # rendering the body so later instances skip the work entirely.
        if not self.multiple and self.block and not portals.claim(cotton_data, self.to, self.block):
            return ""
        portals.push(cotton_data, self.to, self.nodelist.render(context))
        return ""
