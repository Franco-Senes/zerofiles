import re
import datetime

class ZeroFile:
    def __init__(self, data, metadata=None):
        self.data = data
        self.metadata = metadata or {}

    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def __contains__(self, item):
        return item in self.data
    def __repr__(self):
        return f"ZeroFile(data={repr(self.data)}, metadata={repr(self.metadata)})"

class Token:
    def __init__(self, type_, value, line, column, quote_char=None):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
        self.quote_char = quote_char

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"

# Converts something raw to a list of tokens.
def tokenize(source_code):
    tokens = []
    line = 1
    column = 1
    i = 0
    n = len(source_code)

    while i < n:
        c = source_code[i]
        # newlines
        if c == '\n':
            line += 1
            column = 1
            i += 1
            continue
        if c == '\r':
            i += 1
            continue

        # whitespace
        if c.isspace():
            column += 1
            i += 1
            continue

        # single-line comments you can use # or //
        if c == '#' or (c == '/' and i + 1 < n and source_code[i+1] == '/'):
            start_i = i
            while i < n and source_code[i] != '\n':
                i += 1
            comment_text = source_code[start_i:i]
            tokens.append(Token('COMMENT', comment_text, line, column))
            continue

        # now multi line comments you start it with /* and end it with */
        # nice right?
        if c == '/' and i + 1 < n and source_code[i+1] == '*':
            start_line = line
            start_col = column
            start_i = i
            i += 2
            column += 2
            closed = False
            while i < n:
                if source_code[i] == '*' and i + 1 < n and source_code[i+1] == '/':
                    i += 2
                    column += 2
                    closed = True
                    break
                elif source_code[i] == '\n':
                    line += 1
                    column = 1
                    i += 1
                else:
                    column += 1
                    i += 1
            # If the comments isnt closed throw an error
            if not closed:
                raise SyntaxError(f"Unterminated block comment starting at line {start_line}, column {start_col}")
            comment_text = source_code[start_i:i]
            tokens.append(Token('COMMENT', comment_text, start_line, start_col))
            continue

        # single character tokens
        # this part is messy af
        if c == '{':
            tokens.append(Token('LBRACE', '{', line, column))
            i += 1
            column += 1
            continue
        if c == '}':
            tokens.append(Token('RBRACE', '}', line, column))
            i += 1
            column += 1
            continue
        if c == '[':
            tokens.append(Token('LBRACKET', '[', line, column))
            i += 1
            column += 1
            continue
        if c == ']':
            tokens.append(Token('RBRACKET', ']', line, column))
            i += 1
            column += 1
            continue
        if c == ':':
            tokens.append(Token('COLON', ':', line, column))
            i += 1
            column += 1
            continue
        if c == ',':
            tokens.append(Token('COMMA', ',', line, column))
            i += 1
            column += 1
            continue

        # double quoted strings
        if c == '"':
            start_line = line
            start_col = column
            val = []
            i += 1
            column += 1
            closed = False
            while i < n:
                char = source_code[i]
                if char == '"':
                    i += 1
                    column += 1
                    closed = True
                    break
                elif char == '\\':
                    if i + 1 >= n:
                        raise SyntaxError(f"Unterminated string escape at EOF (string started at line {start_line}, col {start_col})")
                    esc = source_code[i+1]
                    # Another section of messy code ✌️💔
                    if esc == 'n': val.append('\n')# Ctrl + c
                    elif esc == 't': val.append('\t') # Ctrl + v
                    elif esc == 'r': val.append('\r') # Ctrl + v
                    elif esc == '\\': val.append('\\') # Ctrl + v
                    elif esc == '"': val.append('"') # Ctrl + v
                    elif esc == "'": val.append("'") # Ctrl + v
                    else: val.append(esc)
                    i += 2
                    column += 2
                elif char == '\n':
                    line += 1
                    column = 1
                    val.append('\n')
                    i += 1
                else:
                    val.append(char)
                    i += 1
                    column += 1
            if not closed:
                raise SyntaxError(f"Unterminated double-quoted string starting at line {start_line}, col {start_col}")
            tokens.append(Token('STRING', "".join(val), start_line, start_col, quote_char='"'))
            continue

        # Single quoted strings
        if c == "'":
            start_line = line
            start_col = column
            val = []
            i += 1
            column += 1
            closed = False
            while i < n:
                char = source_code[i]
                if char == "'":
                    i += 1
                    column += 1
                    closed = True
                    break
                elif char == '\\':
                    if i + 1 >= n:
                        raise SyntaxError(f"Unterminated string escape at EOF (string started at line {start_line}, col {start_col})")
                    esc = source_code[i+1]
                    # Another Another section of messy code ✌️💔
                    if esc == 'n': val.append('\n')
                    elif esc == 't': val.append('\t')
                    elif esc == 'r': val.append('\r')
                    elif esc == '\\': val.append('\\')
                    elif esc == '"': val.append('"')
                    elif esc == "'": val.append("'")
                    else: val.append(esc)
                    i += 2
                    column += 2
                elif char == '\n':
                    line += 1
                    column = 1
                    val.append('\n')
                    i += 1
                else:
                    val.append(char)
                    i += 1
                    column += 1
            if not closed:
                raise SyntaxError(f"Unterminated single-quoted string starting at line {start_line}, col {start_col}")
            tokens.append(Token('STRING', "".join(val), start_line, start_col, quote_char="'"))
            continue

        # words or stuff like (numbers identifiers booleans, null)
        if c.isalnum() or c in '_-+.':
            start_line = line
            start_col = column
            start_i = i
            while i < n and (source_code[i].isalnum() or source_code[i] in '_-+.'):
                i += 1
                column += 1
            word = source_code[start_i:i]

            word_lower = word.lower()
            # Another Another Another section of messy code ✌️💔
            # Why dont i fix it?
            # I am just too lazy for this 🥀
            if word_lower == 'true':
                tokens.append(Token('BOOLEAN', True, start_line, start_col))
            elif word_lower == 'false':
                tokens.append(Token('BOOLEAN', False, start_line, start_col))
            elif word == 'None' or word_lower == 'null':
                tokens.append(Token('NULL', None, start_line, start_col))
            else:
                # try to parse as a number
                has_digit = any(char.isdigit() for char in word)
                parsed_as_number = False
                if has_digit:
                    try:
                        if '.' not in word and 'e' not in word_lower:
                            val = int(word)
                            tokens.append(Token('NUMBER', val, start_line, start_col))
                            parsed_as_number = True
                        else:
                            val = float(word)
                            tokens.append(Token('NUMBER', val, start_line, start_col))
                            parsed_as_number = True
                    except ValueError:
                        pass
                if not parsed_as_number:
                    # fallback to identifier
                    tokens.append(Token('IDENTIFIER', word, start_line, start_col))
            continue

        raise SyntaxError(f"Unexpected character {repr(c)} at line {line}, column {column}")

    tokens.append(Token('EOF', None, line, column))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
            self.pos += 1
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    def consume(self, expected_type=None):
        tok = self.peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type is not None and tok.type != expected_type:
            raise SyntaxError(f"Expected token of type {expected_type}, got {tok.type} ({repr(tok.value)}) at line {tok.line}, column {tok.column}")
        self.pos += 1
        return tok
    def parse(self):
        val = self.parse_value()
        tok = self.peek()
        if tok and tok.type != 'EOF':
            raise SyntaxError(f"Unexpected extra token {tok.type} at line {tok.line}, column {tok.column}")
        return val
    def parse_value(self):
        tok = self.peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")

        # Another Another Another Another section of messy code ✌️💔
        # yup again
        if tok.type == 'LBRACE':
            return self.parse_object()
        elif tok.type == 'LBRACKET':
            return self.parse_array()
        elif tok.type == 'STRING':
            self.consume()
            return tok.value
        elif tok.type == 'NUMBER':
            self.consume()
            return tok.value
        elif tok.type == 'BOOLEAN':
            self.consume()
            return tok.value
        elif tok.type == 'NULL':
            self.consume()
            return tok.value
        else:
            raise SyntaxError(f"Unexpected value starting with token {tok.type} ({repr(tok.value)}) at line {tok.line}, column {tok.column}")
    def parse_object(self):
        self.consume('LBRACE')
        obj = {}

        tok = self.peek()
        if tok and tok.type == 'RBRACE':
            self.consume('RBRACE')
            return obj

        while True:
            key_tok = self.peek()
            if key_tok is None:
                raise SyntaxError("Unexpected EOF while parsing object")
            if key_tok.type not in ('STRING', 'IDENTIFIER'):
                raise SyntaxError(f"Expected string or identifier for object key, got {key_tok.type} at line {key_tok.line}, column {key_tok.column}")
            self.consume()
            key = key_tok.value

            self.consume('COLON')
            val = self.parse_value()
            obj[key] = val

            next_tok = self.peek()
            if next_tok is None:
                raise SyntaxError("Unexpected EOF while parsing object")
            if next_tok.type == 'COMMA':
                self.consume('COMMA')
            elif next_tok.type == 'RBRACE':
                self.consume('RBRACE')
                break
            else:
                raise SyntaxError(f"Expected ',' or '}}' after object property, got {next_tok.type} at line {next_tok.line}, column {next_tok.column}")
        return obj

    def parse_array(self):
        self.consume('LBRACKET')
        arr = []

        tok = self.peek()
        if tok and tok.type == 'RBRACKET':
            self.consume('RBRACKET')
            return arr

        while True:
            val = self.parse_value()
            arr.append(val)

            next_tok = self.peek()
            if next_tok is None:
                raise SyntaxError("Unexpected EOF while parsing array")

            if next_tok.type == 'COMMA':
                self.consume('COMMA')
                after_comma = self.peek()
                if after_comma and after_comma.type == 'RBRACKET':
                    self.consume('RBRACKET')
                    break
            elif next_tok.type == 'RBRACKET':
                self.consume('RBRACKET')
                break
            else:
                raise SyntaxError(f"Expected ',' or ']' after array element, got {next_tok.type} at line {next_tok.line}, column {next_tok.column}")
        return arr

def extract_metadata(source_code):
    metadata = {}
    lines = source_code.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1

    metadata_pattern = re.compile(r'^\s*(?:#|//)\s*@([a-zA-Z0-9_-]+)\s*:\s*(.*)$')
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        match = metadata_pattern.match(line)
        if match:
            key = match.group(1).strip()
            val = match.group(2).strip()
            metadata[key] = val
            i += 1
        else:
            break
    return metadata
def loads(text):
    # parses a string to .zr format.
    metadata = extract_metadata(text)
    tokens = tokenize(text)
    parser = Parser(tokens)
    data = parser.parse()
    return ZeroFile(data, metadata)
def load(filepath_or_fp):
    # Loads and parses the .zr files
    # if you are curious .zr meants zerofiles so yeah
    if isinstance(filepath_or_fp, str):
        with open(filepath_or_fp, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = filepath_or_fp.read()
    return loads(content)

def serialize_compact(val):
    if val is None:
        return "null"
    # Another Another Another Another Another section of messy code ✌️💔 yuh
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, str):
        escaped = val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
        return f'"{escaped}"'
    elif isinstance(val, dict):
        if not val:
            return "{}"
        parts = []
        for k, v in val.items():
            if isinstance(k, str) and k and re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', k):
                key_str = k
            else:
                escaped_k = str(k).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
                key_str = f'"{escaped_k}"'
            parts.append(f"{key_str}:{serialize_compact(v)}")
        return "{" + ",".join(parts) + "}"
    elif isinstance(val, (list, tuple)):
        if not val:
            return "[]"
        parts = [serialize_compact(item) for item in val]
        return "[" + ",".join(parts) + "]"
    else:
        escaped = str(val).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
        return f'"{escaped}"'

def serialize_val(val, indent_sz, current_indent):
    return serialize_compact(val)

def dumps(data, metadata=None, indent=4):
    # serialize a python object to a zr file string.
    if isinstance(data,ZeroFile):
        if metadata is None:
            metadata =  data.metadata
        data = data.data

    meta = {}
    if metadata is not None:
        meta.update(metadata)

    if 'date' not in meta:
        meta['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'version' not in meta:
        meta['version'] = '1.0'

    header_lines = []
    for k, v in meta.items():
        header_lines.append(f"# @{k}: {v}")
    if indent is None or indent <= 0:
        body = serialize_compact(data)
    else:
        body = serialize_val(data, indent, current_indent=0)

    if header_lines:
        return "\n".join(header_lines) + "\n\n" + body
    return body

def dump(data, filepath_or_fp, metadata=None, indent=4):
    ## serializes a python object and writes it to a file.

    content = dumps(data, metadata, indent)
    if isinstance(filepath_or_fp, str):
        with open(filepath_or_fp, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        filepath_or_fp.write(content)

#Ast and formatter class

class ASTNode:
    def __init__(self, leading_comments=None, trailing_comment=None, line=None):
        self.leading_comments = leading_comments or []
        self.trailing_comment = trailing_comment
        self.line = line

    def to_python(self):
        raise NotImplementedError()

    def to_zr(self, indent_sz=4, current_indent=0, inline=False):
        raise NotImplementedError()

class LiteralNode(ASTNode):
    def __init__(self, value, is_string=False, raw_token_type=None, quote_char=None, leading_comments=None, trailing_comment=None, line=None):
        super().__init__(leading_comments, trailing_comment, line)
        self.value = value
        self.is_string = is_string
        self.raw_token_type = raw_token_type
        self.quote_char = quote_char

    def to_python(self):
        return self.value

    def to_zr(self, indent_sz=4, current_indent=0, inline=False):
        indent_str = "" if inline else (" " * current_indent)
        res = format_comments(self.leading_comments, " " * current_indent)
        if self.leading_comments:
            res += " " * current_indent
        else:
            res += indent_str

        # Another Another Another Another Another Another section of messy code ✌️💔 yuh yuh
        if self.value is None:
            res += "null"
        elif isinstance(self.value, bool):
            res += "true" if self.value else "false"
        elif isinstance(self.value, (int, float)):
            res += str(self.value)
        elif self.is_string:
            escaped = self.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
            res += f'"{escaped}"'
        else:
            res += str(self.value)
        return res

class ArrayNode(ASTNode):
    def __init__(self, elements, leading_comments=None, trailing_comment=None, line=None):
        super().__init__(leading_comments, trailing_comment, line)
        self.elements = elements

    def to_python(self):
        return  [elem.to_python() for elem in self.elements]
    def to_zr(self, indent_sz=4, current_indent=0, inline=False):
        indent_str = "" if inline else (" " * current_indent)
        res = format_comments(self.leading_comments, " " * current_indent)
        if self.leading_comments:
            res += " " * current_indent
        else:
            res += indent_str

        if not self.elements:
            res += "[]"
            return res
        res += "[\n"
        for elem in self.elements:
            elem_str = elem.to_zr(indent_sz, current_indent + indent_sz)
            res += elem_str
            res += ","
            if elem.trailing_comment:
                res += " " + elem.trailing_comment
            res += "\n"
        res += (" " * current_indent + "]")
        return res

class PropertyNode(ASTNode):
    def __init__(self, key, value, leading_comments=None, trailing_comment=None, line=None, key_token_type=None, key_quote_char=None):
        super().__init__(leading_comments, trailing_comment, line)
        self.key = key
        self.value = value
        self.key_token_type = key_token_type
        self.key_quote_char = key_quote_char

class ObjectNode(ASTNode):
    def __init__(self, properties, leading_comments=None, trailing_comment=None, line=None):
        super().__init__(leading_comments, trailing_comment, line)
        self.properties = properties

    def to_python(self):
        return  {prop.key: prop.value.to_python() for prop in self.properties}

    def to_zr(self, indent_sz=4, current_indent=0, inline=False):
        indent_str = "" if inline else (" " * current_indent)
        res = format_comments(self.leading_comments, " " * current_indent)
        if self.leading_comments:
            res += " " * current_indent
        else:
            res += indent_str

        if not self.properties:
            res += "{}"
            return res

        res += "{\n"
        for prop in self.properties:
            res += format_comments(prop.leading_comments, " " * (current_indent + indent_sz))
            k = prop.key
            if isinstance(k, str) and re.match('^[a-zA-Z_][a-zA-Z0-9_-]*$', k):
                key_str = k
            else:
                # Another Another Another Another Another Another Another section of messy code ✌️💔 yuh yuh yuh
                escaped_k = str(k).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
                key_str = f'"{escaped_k}"'

            if prop.value.leading_comments:
                val_str = prop.value.to_zr(indent_sz, current_indent + indent_sz)
                res += f'{" " * (current_indent + indent_sz)}{key_str}:\n{val_str}'
            else:
                val_str = prop.value.to_zr(indent_sz, current_indent + indent_sz, inline=True)
                res += f'{" " * (current_indent + indent_sz)}{key_str}: {val_str}'

            res += ","
            if prop.trailing_comment:
                res += " " + prop.trailing_comment
            res += "\n"

        res += (" " * current_indent) + "}"
        return res

def format_comments(comments, indent_Str):
    lines = []
    for c in comments:
        lines.append(f"{indent_Str}{c}")
    if lines:
        return "\n".join(lines) + "\n"
    return ""

class ASTparser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.pending_comments = [] # me dieron ganas de visitar el salar de uyuni

    def skip_comments(self): # otro dia sera o este año 👀
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
            self.pending_comments.append(self.tokens[self.pos].value)
            self.pos += 1

    def peek_non_comment(self):
        self.skip_comments()
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume_non_comment(self, expected_type=None):
        tok = self.peek_non_comment()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type is not None and tok.type != expected_type:
            raise SyntaxError(f"Expected token of type {expected_type}, got {tok.type} at line {tok.line}, col {tok.column}")
        self.pos += 1
        return tok

    def parse(self):
        val = self.parse_value()
        tok = self.peek_non_comment()
        if tok and tok.type != 'EOF':
            raise SyntaxError(f"Unexpected extra token {tok.type} at line {tok.line}, col {tok.column}")
        return val

    def parse_value(self):
        self.skip_comments()
        leading = self.pending_comments
        self.pending_comments = []

        tok = self.peek_non_comment()
        if tok is None:
            raise SyntaxError("Unexpected end of input")

        if tok.type == 'LBRACE':
            val = self.parse_object(leading)
        elif tok.type == 'LBRACKET':
            val = self.parse_array(leading)
        elif tok.type in ('STRING', 'NUMBER', 'BOOLEAN', 'NULL'):
            self.consume_non_comment()
            val = LiteralNode(
                tok.value,
                is_string=(tok.type == 'STRING'),
                raw_token_type=tok.type,
                quote_char=tok.quote_char,
                leading_comments=leading,
                line=tok.line
            )
        else:
            raise SyntaxError(f"Unexpected token {tok.type} at line {tok.line}, col {tok.column}")

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
            comment_tok = self.tokens[self.pos]
            if comment_tok.line == tok.line:
                val.trailing_comment = comment_tok.value
                self.pos += 1
        return val

    def parse_object(self, leading_comments):
        brace_tok = self.consume_non_comment('LBRACE')
        # ima take a water break im kinda tired
        # 12:44 am -  friday june 5
        # finished break 13:10 - friday june
        #huh good morning 11:03 saturday june 6
        properties = []

        tok = self.peek_non_comment()
        if tok and tok.type == 'RBRACE':
            self.consume_non_comment('RBRACE')
            return ObjectNode(properties, leading_comments, line=brace_tok.line)

        while True:
            self.skip_comments()
            prop_leading = self.pending_comments
            self.pending_comments = []

            key_tok = self.peek_non_comment()

            if key_tok is None:
                raise SyntaxError("Unexpected EOF while parsing object")
            if key_tok.type not in ('STRING', 'IDENTIFIER'):
                raise SyntaxError(f"Expected string or identifier key, got {key_tok.type} at line {key_tok.line}")
            self.consume_non_comment()
            key = key_tok.value

            self.consume_non_comment('COLON')
            val = self.parse_value()

            prop = PropertyNode(
                key,
                val,
                prop_leading,
                key_token_type=key_tok.type,
                key_quote_char=key_tok.quote_char,
                line=key_tok.line
            )

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
                comment_tok = self.tokens[self.pos]
                if comment_tok.line == key_tok.line or comment_tok.line == self.tokens[self.pos-1].line:
                    prop.trailing_comment = comment_tok.value
                    self.pos += 1

            properties.append(prop)

            next_tok = self.peek_non_comment()
            if next_tok is None:
                raise SyntaxError("Unexpected EOF while parsing object")

            if next_tok.type == 'COMMA':
                self.consume_non_comment('COMMA')
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
                    comment_tok = self.tokens[self.pos]
                    if comment_tok.line == next_tok.line:
                        prop.trailing_comment = comment_tok.value
                        self.pos += 1

                after_comma = self.peek_non_comment()
                if after_comma and after_comma.type == 'RBRACE':
                    self.consume_non_comment('RBRACE')
                    break
            elif next_tok.type == 'RBRACE':
                self.consume_non_comment('RBRACE')
                break
            else:
                raise SyntaxError(f"Expected ',' or '}}', got {next_tok.type} at line {next_tok.line}")
        return ObjectNode(properties, leading_comments, line=brace_tok.line)

    def parse_array(self, leading_comments):
        bracket_tok = self.consume_non_comment('LBRACKET')
        elements = []

        tok = self.peek_non_comment()
        if tok and tok.type == 'RBRACKET':
            self.consume_non_comment('RBRACKET')
            return ArrayNode(elements, leading_comments, line=bracket_tok.line)

        while True:
            val = self.parse_value()
            elements.append(val)

            next_tok = self.peek_non_comment()
            if next_tok is None:
                raise SyntaxError("Unexpected EOF while parsing array")

            if next_tok.type == 'COMMA':
                self.consume_non_comment('COMMA')
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'COMMENT':
                    comment_tok = self.tokens[self.pos]
                    if comment_tok.line == next_tok.line:
                        val.trailing_comment = comment_tok.value
                        self.pos += 1

                after_comma = self.peek_non_comment()
                if after_comma and after_comma.type == 'RBRACKET':
                    self.consume_non_comment('RBRACKET')
                    break
            elif next_tok.type == 'RBRACKET':
                self.consume_non_comment('RBRACKET')
                break
            else:
                raise SyntaxError(f"Expected ',' or ']', got {next_tok.type} at line {next_tok.line}")
        return ArrayNode(elements, leading_comments, line=bracket_tok.line)

def format_zr(text, indent=4):
    # formats a zerofiles string maintaining all comments and formating stuff beautifully (;

    metadata = extract_metadata(text)

    # strip metadata lines from the start to prevent duplication in comments
    lines = text.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    metadata_pattern = re.compile(r'^\s*(?:#|//)\s*@([a-zA-Z0-9_-]+)\s*:\s*(.*)$')
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if metadata_pattern.match(line):
            i += 1
        else:
            break
    remaining_text = "\n".join(lines[i:])

    tokens = tokenize(remaining_text)
    parser = ASTparser(tokens)
    ast = parser.parse()

    body = ast.to_zr(indent, current_indent=0)

    header_lines = []
    if metadata:
        for k, v in metadata.items():
            header_lines.append(f"# @{k}: {v}")
    if header_lines:
        return  "\n".join(header_lines) + "\n\n" + body
    return body

def lint_zr(text):
    #lints a zerofile for style and syntax
    #returns a list of issue dictionaries or an empty list if clean

    issues = []
    try:
        tokens = tokenize(text)
        parser = ASTparser(tokens)
        ast = parser.parse()

        def walk(node):
            if isinstance(node, ObjectNode):
                for prop in node.properties:
                    # rule 1 that quoted key is a valid identifier
                    if prop.key_token_type == 'STRING':
                        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', prop.key):
                            issues.append({
                                'type': 'warning',
                                'message': f"Key '{prop.key}' is quoted but is a valid identifier. Can be unquoted: {prop.key}.",
                                'line': prop.value.line
                            })
                    # rule 2 single quotes used for keys
                    if prop.key_quote_char == "'":
                        issues.append({
                            'type': 'warning',
                            'message': f"Single quotes used for key '{prop.key}'. Prefer unquoted or double quotes.",
                            'line': prop.value.line
                        })
                    walk(prop.value)

            elif isinstance(node, ArrayNode):
                for elem in node.elements:
                    walk(elem)
            elif isinstance(node, LiteralNode):
                # rule 3 single quotes used for string values
                if node.raw_token_type == 'STRING' and node.quote_char == "'":
                    issues.append({
                        'type': 'warning',
                        'message': f"Single quotes used for string value '{node.value}'. Prefer double quotes.",
                        'line': node.line
                    })

        walk(ast)

    except SyntaxError as e:
        # Standard SyntaxError doesn't always populate lineno/offset directly in custom cases
        # We try to extract them if they are stored
        line = getattr(e, 'lineno', None)
        # Parse error message to see if we can find "line X"
        if line is None:
            match = re.search(r'line (\d+)', str(e))
            if match:
                line = int(match.group(1))

        column = getattr(e, 'offset', None)
        if column is None:
            match = re.search(r'column (\d+)', str(e))
            if match:
                column = int(match.group(1))

        issues.append({
            'type': 'error',
            'message': str(e),
            'line': line,
            'column': column
        })
    return issues