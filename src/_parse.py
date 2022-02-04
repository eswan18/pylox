from typing import Optional

from ._token import Token
from ._expr import Expr, Binary, Grouping, Literal, Unary
# We're going to use this a lot so an alias helps.
from ._token import TokenType as TT

class LoxParseError(Exception):
    def __init__(self, msg: str, line_num: Optional[int] = None):
        self.msg = msg
        self.line_num = line_num

    def __str__(self):
        return f'Parse Error: {self.msg} on line {self.line_num}'

def parse(tokens: list[Token]) -> tuple[Expr, list[LoxParseError]]:
    # Parse the whole input as an expression.
    ast, current_pos = parse_expr(tokens, 0)
    #if current_pos != len(tokens):
    #    errors.append(LoxParseError('Unable 
    return ast, errors

def parse_expr(tokens: list[Token], current_pos: int) -> Expr:
    return parse_equality(tokens, current_pos)

def parse_equality(tokens: list[Token], current_pos: int) -> Expr:
    expr, current_pos = parse_comparison(tokens, current_pos)
    while tokens[current_pos] in (TT.BANG_EQUAL, TT.EQUAL_EQUAL):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_comparison(tokens, current_pos)
        expr = Expr.Binary(expr, operator, right)
    return expr, current_pos

def parse_comparison(tokens: list[Token], current_pos: int) -> Expr:
    expr, current_pos = parse_term(tokens, current_pos)
    while tokens[current_pos] in (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_term(tokens, current_pos)
        expr = Expr.Binary(expr, operator, right)
    return expr, current_pos

