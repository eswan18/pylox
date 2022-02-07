from typing import Optional, cast

from ._expr import Expr, Binary, Grouping, Literal, Unary, Variable, Assignment
from ._stmt import Stmt, ExprStmt, PrintStmt, VarStmt
from ._environment import Environment
from ._errors import LoxRuntimeError
from ._token import Token
# We use it a lot, so an alias helps.
from ._token import TokenType as TT

class Interpreter:

    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: list[Stmt]) -> Optional[LoxRuntimeError]:
        try:
            for stmt in statements:
                self.execute(stmt)
        except LoxRuntimeError as exc:
            return exc

    def execute(self, stmt: Stmt) -> None:
        match stmt:
            case ExprStmt(expr):
                self.eval_expr(expr)
            case PrintStmt(expr):
                result = self.eval_expr(expr)
                print(stringify(result))
            case VarStmt(token, initializer):
                value = self.eval_expr(initializer) if initializer is not None else None
                self.environment.define(token.lexeme, value)
            case _:
                raise RuntimeError

    def eval_expr(self, expr: Expr) -> object:
        match expr:
            case Literal(value):
                return value
            case Grouping(inner_expr):
                return self.eval_expr(inner_expr)
            case Unary():
                return self.eval_unary(expr)
            case Binary():
                return self.eval_binary(expr)
            case Assignment():
                return self.eval_assignment(expr)
            case Variable(token):
                # Note that this doesn't delegate to a function; simple enough to do here.
                return self.environment.get(token)
            case _:
                raise RuntimeError

    def eval_assignment(self, expr: Assignment) -> object:
        value = self.eval_expr(expr.value)
        self.environment.assign(expr.token, value)
        return value

    def eval_unary(self, expr: Unary) -> object:
        operator, raw_right = expr
        right = self.eval_expr(raw_right)

        match operator.token_type:
            case TT.BANG:
                return not is_truthy(right)
            case TT.MINUS:
                check_operands_are_numbers(operator, right)
                return -cast(float, right)
            case _:
                raise RuntimeError

    def eval_binary(self, expr: Binary) -> object:
        raw_left, operator, raw_right = expr
        left = self.eval_expr(raw_left)
        right = self.eval_expr(raw_right)
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
