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
    
    def assign(self, token: Token, value: object) -> None:
        name = token.lexeme
        if name in self.values:
            self.values[name] = value
        else:
            raise LoxRuntimeError(token, "Undefined variable '{name}'.")
