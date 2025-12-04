"""
Enable nested tag support for Django's template lexer to handle Cotton tags specially.

This allows template tags inside quoted attributes of {% cotton %}, {% cotton:vars %}, and {% cotton:slot %} tags to work properly.

For example:
<c-my-component label="{% trans 'Loading' %}" />
<c-vars default_text="{% blocktrans %}Hello, {{ user }}!{% endblocktrans %}" />
"""
from django.template import base as template_base


def _create_smart_tokenize(original_lexer_tokenize, original_debug_lexer_tokenize):
    """Create a smart tokenizer that handles {% cotton %} and {% cotton:vars %} tags specially."""

    # Store originals at creation time
    # We check isinstance(self, DebugLexer) to respect each engine's debug setting
    lexer_tokenize = original_lexer_tokenize
    debug_lexer_tokenize = original_debug_lexer_tokenize

    def smart_tokenize(self):
        """
        Enhanced tokenizer that treats {% cotton %} and {% cotton:vars %} tags specially.

        For Cotton tags, we parse the entire tag as one unit,
        preserving template tags inside quoted attribute values.
        For all other content, we delegate to Django's original tokenizer.
        """
        template_string = self.template_string

        # Check if there are any Cotton tags at all
        has_cotton_tags = "{% cotton " in template_string or "{%cotton " in template_string
        has_cotton_vars_tags = "{% cotton:vars " in template_string or "{%cotton:vars " in template_string
        has_cotton_slot_tags = "{% cotton:slot " in template_string or "{%cotton:slot " in template_string

        if not has_cotton_tags and not has_cotton_vars_tags and not has_cotton_slot_tags:
            # No Cotton tags - use Django's original tokenizer
            # Use DebugLexer tokenize if this is a DebugLexer instance (respects engine.debug)
            if isinstance(self, template_base.DebugLexer):
                return debug_lexer_tokenize(self)
            else:
                return lexer_tokenize(self)

        # Process Cotton tags specially
        result = []
        position = 0

        while position < len(template_string):
            # Look for the next Cotton tag ({% cotton %}, {% cotton:vars %}, or {% cotton:slot %})
            next_cotton_tag = template_string.find("{% cotton ", position)
            next_cotton_no_space = template_string.find("{%cotton ", position)
            next_cotton_vars = template_string.find("{% cotton:vars ", position)
            next_cotton_vars_no_space = template_string.find("{%cotton:vars ", position)
            next_cotton_slot = template_string.find("{% cotton:slot ", position)
            next_cotton_slot_no_space = template_string.find("{%cotton:slot ", position)

            # Find the earliest Cotton tag
            candidates = [next_cotton_tag, next_cotton_no_space, next_cotton_vars, next_cotton_vars_no_space, next_cotton_slot, next_cotton_slot_no_space]
            valid_candidates = [c for c in candidates if c != -1]

            if not valid_candidates:
                next_cotton = -1
            else:
                next_cotton = min(valid_candidates)

            if next_cotton == -1:
                # No more Cotton tags - tokenize the rest with Django's original tokenizer
                if position < len(template_string):
                    remaining = template_string[position:]
                    # Create same type of lexer to preserve debug behavior (respects engine.debug)
                    temp_lexer = self.__class__(remaining)
                    if isinstance(self, template_base.DebugLexer):
                        tokens = debug_lexer_tokenize(temp_lexer)
                    else:
                        tokens = lexer_tokenize(temp_lexer)
                    # Adjust line numbers for the tokens
                    lineno_offset = template_string[:position].count("\n")
                    for token in tokens:
                        token.lineno += lineno_offset
                    result.extend(tokens)
                break

            # Tokenize everything before the Cotton tag with Django's original tokenizer
            if next_cotton > position:
                before_cotton = template_string[position:next_cotton]
                # Create same type of lexer to preserve debug behavior (respects engine.debug)
                temp_lexer = self.__class__(before_cotton)
                if isinstance(self, template_base.DebugLexer):
                    tokens = debug_lexer_tokenize(temp_lexer)
                else:
                    tokens = lexer_tokenize(temp_lexer)
                # Adjust line numbers for the tokens
                lineno_offset = template_string[:position].count("\n")
                for token in tokens:
                    token.lineno += lineno_offset
                result.extend(tokens)

            # Now handle the Cotton tag specially
            tag_start = next_cotton
            position = next_cotton + 2  # Skip {%

            # Skip whitespace and tag name ('cotton', 'cotton:vars', or 'cotton:slot')
            while position < len(template_string) and template_string[position] in " \t\n":
                position += 1

            # Skip tag name
            if template_string[position : position + 11] == "cotton:vars":
                position += 11
            elif template_string[position : position + 11] == "cotton:slot":
                position += 11
            elif template_string[position : position + 6] == "cotton":
                position += 6

            # Now find the end %}, respecting quotes
            in_quotes = False
            quote_char = None
            # Track when we're inside Django template syntax to ignore quotes within them
            django_var_depth = 0  # Tracks {{ }} blocks
            django_tag_depth = 0  # Tracks {% %} blocks

            while position < len(template_string) - 1:
                char = template_string[position]

                # Track Django variable blocks {{ }}
                if template_string[position : position + 2] == "{{":
                    django_var_depth += 1
                    position += 2
                    continue
                elif template_string[position : position + 2] == "}}":
                    django_var_depth = max(0, django_var_depth - 1)
                    position += 2
                    continue
                
                # Track Django tag blocks {% %} (but not the outer Cotton tag we're parsing)
                # We need to be careful: we're already inside the outer {% cotton ... %} tag
                # So we only track NESTED {% %} blocks
                elif template_string[position : position + 2] == "{%":
                    django_tag_depth += 1
                    position += 2
                    continue
                elif template_string[position : position + 2] == "%}":
                    # This could be the end of the outer Cotton tag OR a nested {% %} block
                    if django_tag_depth > 0:
                        # It's closing a nested tag block
                        django_tag_depth = max(0, django_tag_depth - 1)
                        position += 2
                        continue
                    elif not in_quotes:
                        # It's the end of the outer Cotton tag
                        position += 2  # Include %}
                        break
                    else:
                        # We're in quotes, so this %} is part of the quoted value
                        position += 1
                        continue

                # Handle quotes (only when not inside Django template syntax)
                if (
                    not in_quotes
                    and char in ('"', "'")
                    and django_var_depth == 0
                    and django_tag_depth == 0
                ):
                    in_quotes = True
                    quote_char = char
                elif (
                    in_quotes
                    and char == quote_char
                    and django_var_depth == 0
                    and django_tag_depth == 0
                ):
                    # Check if escaped
                    if position > 0 and template_string[position - 1] == "\\":
                        pass  # Escaped quote, continue
                    else:
                        in_quotes = False
                        quote_char = None

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

    Called during Django initialization in AppConfig.ready().
    Patches both Lexer and DebugLexer to handle nested tags in Cotton component attributes.
    """
    # Capture originals before patching
    original_lexer_tokenize = template_base.Lexer.tokenize
    original_debug_lexer_tokenize = template_base.DebugLexer.tokenize

    # Create and apply the smart tokenizer to both Lexer and DebugLexer
    smart_tokenize = _create_smart_tokenize(original_lexer_tokenize, original_debug_lexer_tokenize)
    template_base.Lexer.tokenize = smart_tokenize
    template_base.DebugLexer.tokenize = smart_tokenize
