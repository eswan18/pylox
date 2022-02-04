from typing import Optional

from ._token import Token
from ._expr import Expr, Binary, Grouping, Literal, Unary
# We're going to use this a lot so an alias helps.
from ._token import TokenType as TT

class LoxParseError(Exception):
    def __init__(self, token: Token, msg: str):
        self.token = token
        self.msg = msg

    def __str__(self):
        return f'Parse Error: Found {self.token} but {self.msg}'

def parse(tokens: list[Token]) -> tuple[Expr, list[LoxParseError]]:
    # Parse the whole input as an expression.
    ast, current_pos = parse_expr(tokens, 0)
    #if current_pos != len(tokens):
    #    errors.append(LoxParseError('Unable 
    return ast, errors

def parse_expr(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    return parse_equality(tokens, current_pos)

def parse_equality(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_comparison(tokens, current_pos)
    while tokens[current_pos] in (TT.BANG_EQUAL, TT.EQUAL_EQUAL):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_comparison(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_comparison(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_term(tokens, current_pos)
    while tokens[current_pos] in (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_term(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_term(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_factor(tokens, current_pos)
    while tokens[current_pos] in (TT.MINUS, TT.PLUS):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_factor(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_factor(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_unary(tokens, current_pos)
    while tokens[current_pos] in (TT.SLASH, TT.STAR):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_unary(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_unary(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    if tokens[current_pos] in (TT.BANG, TT.MINUS):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_unary(tokens, current_pos)
        return Unary(operator, right), current_pos
    else:
        return parse_primary(tokens, current_pos)

def parse_primary(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    tok = tokens[current_pos]
    if tok == TT.FALSE:
        return (Literal(False), current_pos + 1)
    elif tok == TT.TRUE:
        return (Literal(True), current_pos + 1)
    elif tok == TT.NIL:
        return (Literal(None), current_pos + 1)
    elif tok == TT.NIL:
        return (Literal(None), current_pos + 1)
    elif tok in (TT.NUMBER, TT.STRING):
        return (Literal(tok.literal), current_pos + 1)
    elif tok == TT.LEFT_PAREN:
        expr, current_pos = parse_expression(tokens, current_pos + 1)
        parent, current_pos = consume(
            tokens,
            current_pos,
            expected=TT.RIGHT_PAREN,
            msg="Expect ')' after expression."
        )
        return Grouping(expr), current_pos
    else:
        raise LoxParseError(tokens[current_pos], 'Expect expression')

def consume(tokens: list[Token], current_pos: int, expected: Token, msg: str) -> tuple[Token, int]:
    if tokens[current_pos] == Token:
        return (Token, current_pos + 1)
    else:
        raise LoxParseError(tokens[current_pos], msg)
