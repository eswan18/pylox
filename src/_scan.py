from typing import Any

from ._token import Token, TokenType, keyword_map


class LoxScanError(Exception):
    def __init__(self, msg: str, line_num: int | None = None):
        self.msg = msg
        self.line_num = line_num

    def __str__(self):
        return f'[line {self.line_num}] Scan Error: {self.msg}'


def scan(source: str) -> tuple[list[Token], list[LoxScanError]]:
    line_num = 1
    current_pos = 0
    tokens = []
    errors = []
    while current_pos < len(source):
        try:
            (next_token, next_pos, n_newlines) = _scan_token(source, current_pos)
        except LoxScanError as exc:
            # The scan function doesn't know the line number so we have to provide it.
            exc.line_num = line_num
            errors.append(exc)
            if source[current_pos] == '\n':
                line_num += 1
            # Advance to the next token and keep going, to find all errors in one go.
            current_pos += 1
            continue
        if next_token is not None:
            next_token.line_num = line_num
            tokens.append(next_token)
        line_num += n_newlines
        # Restart processing starting at the end of the token we found.
        current_pos = next_pos

    eof_token = Token(TokenType.EOF, '', None, line_num)
    tokens.append(eof_token)
    return tokens, errors


def _scan_token(source: str, start_pos: int) -> tuple[Token, int, int]:
    '''
    Scan the next token.

    Returns
    -------
    next_token: Token
        The next token found.
    next_position: int
        The position from which scanning should resume
    n_newlines: int
        The number of newlines found in the process of scanning this token.
    '''
    # We need to track not only where we started, but how far into the string we are.
    current_pos = start_pos
    token_type: Token | None = None
    token_value: Any = None

    n_newlines = 0

    # Shift to get the next character.
    c = source[current_pos]
    current_pos += 1

    if c == '(':
        token_type = TokenType.LEFT_PAREN
    elif c == ')':
        token_type = TokenType.RIGHT_PAREN
    elif c == '{':
        token_type = TokenType.LEFT_BRACE
    elif c == '}':
        token_type = TokenType.RIGHT_BRACE
    elif c == ',':
        token_type = TokenType.COMMA
    elif c == '.':
        token_type = TokenType.DOT
    elif c == '-':
        token_type = TokenType.MINUS
    elif c == '+':
        token_type = TokenType.PLUS
    elif c == ';':
        token_type = TokenType.SEMICOLON
    elif c == '*':
        token_type = TokenType.STAR
    elif c == '!':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            token_type = TokenType.BANG_EQUAL
        else:
            token_type = TokenType.BANG
    elif c == '=':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            token_type = TokenType.EQUAL_EQUAL
        else:
            token_type = TokenType.EQUAL
    elif c == '<':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            token_type = TokenType.LESS_EQUAL
        else:
            token_type = TokenType.LESS
    elif c == '>':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            token_type = TokenType.GREATER_EQUAL
        else:
            token_type = TokenType.GREATER
    elif c == '/':
        if current_pos < len(source) and source[current_pos] == '/':
            # A comment goes until the end of the line.
            while current_pos < len(source) and source[current_pos] != '\n':
                current_pos += 1
            token_type = None
        else:
            token_type = TokenType.SLASH
    elif c in (' ', '\r', '\t'):
        token_type = None
    elif c == '\n':
        # Return early, signaling that we need to increment the line counter.
        return (None, current_pos, 1)
    elif c == '"':
        while current_pos < len(source) and source[current_pos] != '"':
            if source[current_pos] == '\n':
                n_newlines += 1
            current_pos += 1
        if current_pos == len(source):
            raise LoxScanError('Unterminated string.')
        current_pos += 1
        token_type = TokenType.STRING
        # The string is bookended by quotes, which shouldn't be included in its value.
        token_value = source[start_pos + 1 : current_pos - 1]  # noqa
    else:
        if c.isdigit():
            while current_pos < len(source) and source[current_pos].isdigit():
                current_pos += 1
            # We may encounter a decimal number.
            if current_pos < len(source) and source[current_pos] == '.':
                if current_pos + 1 < len(source) and source[current_pos + 1].isdigit():
                    current_pos += 1
                    # Look over the numbers following the decimal.
                    while current_pos < len(source) and source[current_pos].isdigit():
                        current_pos += 1
            token_type = TokenType.NUMBER
            token_value = float(source[start_pos:current_pos])
        elif c.isalpha():
            # Identifiers and keywords.
            while (
                current_pos < len(source) and
                (source[current_pos].isdigit() or source[current_pos].isalpha())
            ):
                current_pos += 1
            text = source[start_pos:current_pos]
            # Names that aren't keywords must be identifiers.
            token_type = keyword_map.get(text, TokenType.IDENTIFIER)
        else:
            raise LoxScanError('Unexpected character.')

    if token_type is not None:
        token = Token(token_type, source[start_pos:current_pos], token_value, None)
    else:
        token = None
    return (token, current_pos, n_newlines)
