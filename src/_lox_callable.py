import time
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING

from ._environment import Environment

if TYPE_CHECKING:
    from ._interpret import Interpreter
    from ._stmt import FunctionStmt


@runtime_checkable
class LoxCallableProtocol(Protocol):

    arity: int

    def call(self, interpreter: 'Interpreter', args: list[object]) -> object: ...


class ClockCallable:

    def __init__(self):
        self.arity = 0

    def call(self, interpreter: Any, args: Any) -> object:
        return time.time()

    def __str__(self) -> str:
        return '<native fn>'


clock = ClockCallable()


class LoxFunction:

    def __init__(self, declaration: 'FunctionStmt'):
        self.declaration = declaration
        self.arity = len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', args: list[object]) -> object:
        env = Environment(interpreter.globals)
        for i, param in enumerate(self.declaration.params):
            env.define(param.lexeme, args[i])
        interpreter.execute_block(self.declaration.body, env)
        return None

    def __str__(self) -> str:
        return f'<fn {self.declaration.name.lexeme}>'
