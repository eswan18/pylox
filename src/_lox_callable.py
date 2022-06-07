import time
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from ._interpret import Interpreter


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
