from enum import Enum
from dataclasses import dataclass

class LoxScanError(Exception):
    def __init__(msg: str, line_num: int):
        self.msg = msg
        self.line_num = line_num

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
    literal: str
    line_num: int

    def __str__(self) -> str:
        return f'{self.token_type} {self.lexeme} {self.literal}'


def get_tokens(source: str) -> list[Token]:
    line_num = 1
    current_pos = 0
    tokens = []
    while current_pos < len(source):
        start_pos = current_pos
        (next_token, next_pos, is_newline) = _scan_token(source, current_pos)
        if is_newline:
            line_num += 1
        if next_token is not None:
            tokens.append(next_token)
        current_pos = next_pos


def _scan_token(source: str, start_pos: int) -> tuple[Token, int, bool]:
    # We need to track not only where we started, but how far into the string we are.
    current_pos = start_pos
    tok: Optional[Token] = None

    # Shift to get the next character.
    c = source[current_pos]
    current_pos += 1

    if c == '(': tok = LEFT_PAREN
    elif c == ')': tok = RIGHT_PAREN
    elif c == '{': tok = LEFT_BRACE
    elif c == '}': tok = RIGHT_BRACE
    elif c == ',': tok = COMMA
    elif c == '.': tok = DOT
    elif c == '-': tok = MINUS
    elif c == '+': tok = PLUS
    elif c == ';': tok = SEMICOLON
    elif c == '*': tok = STAR
    elif c == '!':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            tok = BANG_EQUAL
        else:
            tok = BANG
    elif c == '=':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            tok = EQUAL_EQUAL
        else:
            tok = EQUAL
    elif c == '<':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            tok = LESS_EQUAL
        else:
            tok = LESS
    elif c == '>':
        if current_pos < len(source) and source[current_pos] == '=':
            current_pos += 1
            tok = GREATER_EQUAL
        else:
            tok = GREATER
    elif c == '/':
        if current_pos < len(source) and source[current_pos] == '/':
            # A comment goes until the end of the line.
            while current_pos < len(source) and source[current_pos] != '\n':
                current_pos += 1
            tok = None
        else:
            tok = SLASH
    elif c in (' ', '\r', '\t'):
        tok = None
    elif c == '\n':
        # Return early, signaling that we need to increment the line counter.
        return (None, current_pos, True)  
    elif c == '"':
        tok = _parse_string()
    else:
        if c.isdigit():
            _parse_number()
        elif c.isalpha():
            _parse_identifier()
        else:
            raise LoxScanError('Unexpected character', line_num)

    return (tok, current_pos, False)

