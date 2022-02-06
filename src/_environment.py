from ._token import Token
from ._errors import LoxRuntimeError

class Environment:

    def __init__(self):
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, token: Token) -> object:
        if token.lexeme in self.values:
            return self.values[token.lexeme]
        else:
            raise LoxRuntimeError(token, f"Undefined variable '{token.lexeme}'.")
