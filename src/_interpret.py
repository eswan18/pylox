from typing import Optional, cast

from ._expr import Expr, Binary, Grouping, Literal, Unary
from ._errors import LoxRuntimeError
from ._token import Token
# We use it a lot, so an alias helps.
from ._token import TokenType as TT

def interpret(expr: Expr) -> Optional[LoxRuntimeError]:
    try:
        value = eval_expr(expr)
        print(stringify(value))
    except LoxRuntimeError as exc:
        return exc

def eval_expr(expr: Expr) -> object:
    # From simplest to most complex.
    match expr:
        case Literal(value):
            return value
        case Grouping(inner_expr):
            return eval_expr(inner_expr)
        case Unary():
            return eval_unary(expr)
        case Binary():
            return eval_binary(expr)
        case _:
            raise RuntimeError

def eval_unary(expr: Unary) -> object:
    operator, raw_right = expr
    right = eval_expr(raw_right)

    match operator.token_type:
        case TT.BANG:
            return not is_truthy(right)
        case TT.MINUS:
            check_operands_are_numbers(operator, right)
            return -cast(float, right)
        case _:
            raise RuntimeError

def eval_binary(expr: Binary) -> object:
    raw_left, operator, raw_right = expr
    left = eval_expr(raw_left)
    right = eval_expr(raw_right)
    match operator.token_type:
        case TT.BANG_EQUAL:
            return not (left == right)
        case TT.EQUAL_EQUAL:
            return left == right
        case TT.GREATER:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) > cast(float, right)
        case TT.GREATER_EQUAL:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) >= cast(float, right)
        case TT.LESS:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) < cast(float, right)
        case TT.LESS_EQUAL:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) >= cast(float, right)
        case TT.MINUS:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) - cast(float, right)
        case TT.SLASH:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) / cast(float, right)
        case TT.STAR:
            check_operands_are_numbers(operator, left, right)
            return cast(float, left) * cast(float, right)
        case TT.PLUS:
            # Trickier because we support numeric addition as well as string concatentation.
            if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                return cast(float, left) + cast(float, right)
            elif isinstance(left, str) and isinstance(right, str):
                return cast(str, left) + cast(str, right)
            else:
                raise LoxRuntimeError(operator, 'Operands must be two numbers or two strings')
        case _:
            raise RuntimeError

def check_operands_are_numbers(operator: Token, *operands: object) -> None:
    if not all(isinstance(op, (float, int)) for op in operands):
        if len(operands) > 1:
            msg = 'Operands must be numbers.'
        else:
            msg = 'Operand must be a number.'
        raise LoxRuntimeError(operator, msg)

def is_truthy(thing: object) -> bool:
    if thing is None:
        return False
    if isinstance(thing, bool):
        return thing
    else:
        return True

def stringify(thing: object) -> str:
    if thing is None:
        return 'nil'
    if isinstance(thing, bool):
        # Lox doesn't capitalize True/False but Python does.
        return str(thing).lower()
    if isinstance(thing, (float, int)):
        text = str(thing)
        if text.endswith('.0'):
            text = text[:-2]
        return text
    return str(thing)
