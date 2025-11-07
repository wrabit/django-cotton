"""
Enable nested tag support for Django's template lexer to handle Cotton tags specially.

This allows template tags inside quoted attributes of {% c %} and {% vars %} tags to work properly.

For example: 
<c-my-component label="{% trans 'Loading' %}" />
<c-vars default_text="{% blocktrans %}Hello, {{ user }}!{% endblocktrans %}" %}" />
"""
from django.template import base as template_base


# Store the original tokenize method
_original_tokenize = None
_support_enabled = False


def _create_smart_tokenize():
    """Create a smart tokenizer that handles {% c %} and {% vars %} tags specially."""

    # Store original at creation time
    original_tokenize = template_base.Lexer.tokenize

    def smart_tokenize(self):
        """
        Enhanced tokenizer that treats {% c %} and {% vars %} tags specially.

        For Cotton tags, we parse the entire tag as one unit,
        preserving template tags inside quoted attribute values.
        For all other content, we delegate to Django's original tokenizer.
        """
        template_string = self.template_string

        # Check if there are any Cotton tags at all
        has_c_tags = "{% c " in template_string or "{%c " in template_string
        has_vars_tags = "{% vars " in template_string or "{%vars " in template_string

        if not has_c_tags and not has_vars_tags:
            # No Cotton tags - use Django's original tokenizer
            return original_tokenize(self)

        # Process Cotton tags specially
        result = []
        position = 0

        while position < len(template_string):
            # Look for the next Cotton tag ({% c %} or {% vars %})
            next_c = template_string.find("{% c ", position)
            next_c_no_space = template_string.find("{%c ", position)
            next_vars = template_string.find("{% vars ", position)
            next_vars_no_space = template_string.find("{%vars ", position)

            # Find the earliest Cotton tag
            candidates = [next_c, next_c_no_space, next_vars, next_vars_no_space]
            valid_candidates = [c for c in candidates if c != -1]

            if not valid_candidates:
                next_cotton = -1
            else:
                next_cotton = min(valid_candidates)

            if next_cotton == -1:
                # No more Cotton tags - tokenize the rest with Django's original tokenizer
                if position < len(template_string):
                    remaining = template_string[position:]
                    temp_lexer = template_base.Lexer(remaining)
                    tokens = original_tokenize(temp_lexer)
                    # Adjust line numbers for the tokens
                    lineno_offset = template_string[:position].count("\n")
                    for token in tokens:
                        token.lineno += lineno_offset
                    result.extend(tokens)
                break

            # Tokenize everything before the Cotton tag with Django's original tokenizer
            if next_cotton > position:
                before_cotton = template_string[position:next_cotton]
                temp_lexer = template_base.Lexer(before_cotton)
                tokens = original_tokenize(temp_lexer)
                # Adjust line numbers for the tokens
                lineno_offset = template_string[:position].count("\n")
                for token in tokens:
                    token.lineno += lineno_offset
                result.extend(tokens)

            # Now handle the Cotton tag specially
            tag_start = next_cotton
            position = next_cotton + 2  # Skip {%

            # Skip whitespace and tag name ('c' or 'vars')
            while position < len(template_string) and template_string[position] in " \t\n":
                position += 1

            # Skip tag name
            if template_string[position : position + 4] == "vars":
                position += 4
            elif template_string[position] == "c":
                position += 1

            # Now find the end %}, respecting quotes
            in_quotes = False
            quote_char = None

            while position < len(template_string) - 1:
                char = template_string[position]

                # Handle quotes
                if not in_quotes and char in ('"', "'"):
                    in_quotes = True
                    quote_char = char
                elif in_quotes and char == quote_char:
                    # Check if escaped
                    if position > 0 and template_string[position - 1] == "\\":
                        pass  # Escaped quote, continue
                    else:
                        in_quotes = False
                        quote_char = None

                # Look for %} only when not in quotes
                elif not in_quotes and template_string[position : position + 2] == "%}":
                    position += 2  # Include %}
                    break

                position += 1
            else:
                # Reached end without finding %}
                position = len(template_string)

            # Create token for the entire Cotton tag
            token_string = template_string[tag_start:position]
            if token_string:
                lineno = template_string[:tag_start].count("\n") + 1
                result.append(self.create_token(token_string, None, lineno, True))

        return result

    return smart_tokenize


def enable_nested_tag_support():
    """
    Enable nested tag support for Django's template lexer.

    This should be called early in Django's initialization,
    typically in an app's AppConfig.ready() method.
    """
    global _original_tokenize, _support_enabled

    if _support_enabled:
        return  # Already enabled

    # Store original
    _original_tokenize = template_base.Lexer.tokenize

    # Enable nested tag support for Lexer and DebugLexer
    smart_tokenize = _create_smart_tokenize()
    template_base.Lexer.tokenize = smart_tokenize
    template_base.DebugLexer.tokenize = smart_tokenize
    _support_enabled = True


def disable_nested_tag_support():
    """
    Disable nested tag support and restore the original Django lexer behavior.
    """
    global _original_tokenize, _support_enabled

    if not _support_enabled or not _original_tokenize:
        return

    template_base.Lexer.tokenize = _original_tokenize
    _support_enabled = False
