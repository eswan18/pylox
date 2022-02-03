from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any

class LoxScanError(Exception):
    def __init__(self, msg: str, line_num: Optional[int] = None):
        self.msg = msg
        self.line_num = line_num

    def __str__(self):
        return f'{self.msg} on line {self.line_num}'

TOKEN_TYPES = '''
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,

    BANG, BANG_EQUAL, EQUAL, EQUAL_EQUAL, GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,

    IDENTIFIER, STRING, NUMBER,

    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR, PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,

    EOF
'''
KEYWORDS = 'and class else false for fun if nil or print return super this true var while'

token_types = [t.strip() for t in TOKEN_TYPES.split(',')]
TokenType = Enum('TokenType', token_types)
kwd_map = {kwd: TokenType[kwd.upper()] for kwd in KEYWORDS.split()}


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: Optional[str]
    line_num: Optional[int]

    def __str__(self) -> str:
        return f'{self.token_type} {self.lexeme} {self.literal}'


def get_tokens(source: str) -> list[Token]:
    line_num = 1
    current_pos = 0
    tokens = []
    errors = []
    while current_pos < len(source):
        start_pos = current_pos
        try:
            (next_token, next_pos, n_newlines) = _scan_token(source, current_pos)
        except LoxScanError as exc:
            # The scan function doesn't know the line number so we have to provide it.
            exc.line_num = line_num
            errors.append(exc)
            # Advance to the next token and keep going, to find all errors in one go.
            current_pos += 1
            line_num += n_newlines
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
    # We need to track not only where we started, but how far into the string we are.
    current_pos = start_pos
    token_type: Optional[Token] = None
    token_value: Any = None

    n_newlines = 0

    # Shift to get the next character.
    c = source[current_pos]
    current_pos += 1


    if c == '(': token_type = TokenType.LEFT_PAREN
    elif c == ')': token_type = TokenType.RIGHT_PAREN
    elif c == '{': token_type = TokenType.LEFT_BRACE
    elif c == '}': token_type = TokenType.RIGHT_BRACE
    elif c == ',': token_type = TokenType.COMMA
    elif c == '.': token_type = TokenType.DOT
    elif c == '-': token_type = TokenType.MINUS
    elif c == '+': token_type = TokenType.PLUS
    elif c == ';': token_type = TokenType.SEMICOLON
    elif c == '*': token_type = TokenType.STAR
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
            raise LoxScanError('Unterminated string')
        current_pos += 1
        token_type = TokenType.STRING
        # The string is bookended by quotes, which shouldn't be included in its value.
        token_value = source[start_pos + 1 : current_pos - 1]
    else:
        if c.isdigit():
            token_type = _parse_number()
        elif c.isalpha():
            token_type = _parse_identifier()
        else:
            raise LoxScanError('Unexpected character')

    if token_type is not None:
        token = Token(token_type, source[start_pos:current_pos], token_value, None)
    else:
        token = None
    return (token, current_pos, n_newlines)

