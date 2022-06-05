from enum import Enum
from dataclasses import dataclass
from typing import Optional

TOKEN_TYPES = '''
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,

    BANG, BANG_EQUAL, EQUAL, EQUAL_EQUAL,
    GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,

    IDENTIFIER, STRING, NUMBER,

    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL,
    OR, PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,

    EOF
'''
KEYWORDS = (
    'and class else false for fun if nil or print return super this true var while'
)

token_types = [t.strip() for t in TOKEN_TYPES.split(',')]
TokenType = Enum('TokenType', token_types)
keyword_map = {kwd: TokenType[kwd.upper()] for kwd in KEYWORDS.split()}


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: Optional[str]
    line_num: Optional[int]

    def __str__(self) -> str:
        return f'{self.token_type} {self.lexeme} {self.literal}'
