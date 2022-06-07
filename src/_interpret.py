from typing import cast, Final

from ._expr import (
    Expr, Binary, Grouping, Literal, Logical, Unary, Variable, Assignment, Call
)
from ._stmt import Stmt, ExprStmt, IfStmt, PrintStmt, VarStmt, WhileStmt, BlockStmt
from ._environment import Environment
from ._errors import LoxRuntimeError
from ._token import Token
from ._lox_callable import LoxCallableProtocol, clock
# We use it a lot, so an alias helps.
from ._token import TokenType as TT


class Interpreter:

    def __init__(self):
        self.globals: Final = Environment()
        self.environment = self.globals
        # Create the built-in clock function.
        self.globals['clock'] = clock

    def interpret(self, statements: list[Stmt]) -> LoxRuntimeError | None:
        try:
            for stmt in statements:
                self.execute(stmt)
        except LoxRuntimeError as exc:
            return exc
        else:
            return None

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
            case WhileStmt(condition, body):
                should_loop = self.eval_expr(condition)
                while should_loop:
                    self.execute(body)
                    should_loop = self.eval_expr(condition)
            case BlockStmt(statements):
                self.execute_block(statements, Environment(enclosing=self.environment))
            case IfStmt():
                self.execute_if(stmt)
            case _:
                raise RuntimeError

    def execute_block(self, stmts: list[Stmt], environment: Environment) -> None:
        # Hold on to the current environment so we can reset after running the block.
        previous = self.environment
        try:
            self.environment = environment
            for stmt in stmts:
                self.execute(stmt)
        finally:
            # It's vital to reset the current environment even if we run into an error
            # in the block.
            self.environment = previous

    def execute_if(self, stmt: IfStmt) -> None:
        if is_truthy(self.eval_expr(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def eval_expr(self, expr: Expr) -> object:
        match expr:
            case Literal(value):
                return value
            case Logical():
                return self.eval_logical(expr)
            case Grouping(inner_expr):
                return self.eval_expr(inner_expr)
            case Unary():
                return self.eval_unary(expr)
            case Binary():
                return self.eval_binary(expr)
            case Call():
                return self.eval_call(expr)
            case Assignment():
                return self.eval_assignment(expr)
            case Variable(token):
                # This doesn't delegate to a function; it's simple enough to do here.
                return self.environment.get(token)
            case _:
                raise RuntimeError

    def eval_assignment(self, expr: Assignment) -> object:
        value = self.eval_expr(expr.value)
        self.environment.assign(expr.token, value)
        return value

    def eval_logical(self, expr: Logical) -> object:
        left, operator, right = expr
        left_val = self.eval_expr(left)

        if operator.token_type == TT.OR:
            if is_truthy(left_val):
                return left_val
        else:  # operator.token_type == TT.AND
            if not is_truthy(left_val):
                return left_val
        return self.eval_expr(right)

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
                # Trickier because we support numeric addition as well as string
                # concatentation.
                if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                    return cast(float, left) + cast(float, right)
                elif isinstance(left, str) and isinstance(right, str):
                    return cast(str, left) + cast(str, right)
                else:
                    raise LoxRuntimeError(
                        operator, 'Operands must be two numbers or two strings'
                    )
            case _:
                raise RuntimeError

    def eval_call(self, expr: Call) -> object:
        callee = self.eval_expr(expr)
        args = [self.eval_expr(arg) for arg in expr.arguments]
        if isinstance(callee, LoxCallableProtocol):
            function: LoxCallableProtocol = callee
        else:
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        if function.arity != len(args):
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {function.arity} arguments but got {len(args)}.",
            )
        return callee.call(interpreter=self, args=args)


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
