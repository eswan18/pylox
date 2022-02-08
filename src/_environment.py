from __future__ import annotations

from ._token import Token
from ._errors import LoxRuntimeError

class Environment:

    def __init__(self, enclosing: Environment = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, token: Token) -> object:
        name = token.lexeme
        if name in self.values:
            # If the variable is in this environment, return its value.
            return self.values[token.lexeme]
        elif self.enclosing is not None:
            # If this environment is enclosed by another, check that one (and its parents).
            return self.enclosing.get(token)
        else:
            raise LoxRuntimeError(token, f"Undefined variable '{name}'.")
    
    def assign(self, token: Token, value: object) -> None:
        name = token.lexeme
        if name in self.values:
            # If the variable is in this environment, update it here.
            self.values[name] = value
        elif self.enclosing is not None:
            # If this environment is enclosed by another, check that one (and its parents).
            self.enclosing.assign(token, value)
        else:
            raise LoxRuntimeError(token, "Undefined variable '{name}'.")
