from typing import Optional

from ._token import Token
from ._expr import Expr, Binary, Grouping, Literal, Unary
from ._stmt import Stmt, ExprStmt, PrintStmt
from ._errors import LoxParseError
# We're going to use this a lot so an alias helps.
from ._token import TokenType as TT

def parse(tokens: list[Token]) -> tuple[list[Stmt], list[LoxParseError]]:
    current_pos = 0
    stmts: list[Stmt] = []
    errors: list[LoxParseError] = []
    while tokens[current_pos].token_type != TT.EOF:
        try:
            stmt, current_pos = parse_stmt(tokens, current_pos)
        except LoxParseError as exc:
            errors.append(exc)
        else:
            stmts.append(stmt)
    return stmts, errors

def parse_stmt(tokens: list[Token], current_pos: int) -> tuple[Stmt, int]:
    if tokens[current_pos].token_type == TT.PRINT:
        # Consume the PRINT token.
        current_pos += 1
        return parse_print_stmt(tokens, current_pos)
    else:
        return parse_expr_stmt(tokens, current_pos)

def parse_expr_stmt(tokens: list[Token], current_pos: int) -> tuple[Stmt, int]:
    expr, current_pos = parse_expression(tokens, current_pos)
    _, current_pos = consume(tokens, current_pos, TT.SEMICOLON, "Expect ';' after expression.")
    return ExprStmt(expr), current_pos

def parse_print_stmt(tokens: list[Token], current_pos: int) -> tuple[Stmt, int]:
    expr, current_pos = parse_expression(tokens, current_pos)
    _, current_pos = consume(tokens, current_pos, TT.SEMICOLON, "Expect ';' after value.")
    return PrintStmt(expr), current_pos

def parse_expression(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    return parse_equality(tokens, current_pos)

def parse_equality(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_comparison(tokens, current_pos)
    while tokens[current_pos].token_type in (TT.BANG_EQUAL, TT.EQUAL_EQUAL):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_comparison(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_comparison(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_term(tokens, current_pos)
    tok_types = (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL)
    while tokens[current_pos].token_type in tok_types:
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_term(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_term(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_factor(tokens, current_pos)
    while tokens[current_pos].token_type in (TT.MINUS, TT.PLUS):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_factor(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_factor(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    expr, current_pos = parse_unary(tokens, current_pos)
    while tokens[current_pos].token_type in (TT.SLASH, TT.STAR):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_unary(tokens, current_pos)
        expr = Binary(expr, operator, right)
    return expr, current_pos

def parse_unary(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    if tokens[current_pos].token_type in (TT.BANG, TT.MINUS):
        operator = tokens[current_pos]
        current_pos += 1
        right, current_pos = parse_unary(tokens, current_pos)
        return Unary(operator, right), current_pos
    else:
        return parse_primary(tokens, current_pos)

def parse_primary(tokens: list[Token], current_pos: int) -> tuple[Expr, int]:
    token = tokens[current_pos]
    if token.token_type == TT.FALSE:
        return (Literal(False), current_pos + 1)
    elif token.token_type == TT.TRUE:
        return (Literal(True), current_pos + 1)
    elif token.token_type == TT.NIL:
        return (Literal(None), current_pos + 1)
    elif token.token_type == TT.NIL:
        return (Literal(None), current_pos + 1)
    elif token.token_type in (TT.NUMBER, TT.STRING):
        return (Literal(token.literal), current_pos + 1)
    elif token.token_type == TT.LEFT_PAREN:
        expr, current_pos = parse_expression(tokens, current_pos + 1)
        paren, current_pos = consume(
            tokens,
            current_pos,
            expected=TT.RIGHT_PAREN,
            msg="Expect ')' after expression."
        )
        return Grouping(expr), current_pos
    else:
        raise LoxParseError(token, 'Expect expression.')

def consume(tokens: list[Token], current_pos: int, expected: Token, msg: str) -> tuple[Token, int]:
    if tokens[current_pos].token_type == expected:
        return (expected, current_pos + 1)
    else:
        raise LoxParseError(tokens[current_pos], msg)
