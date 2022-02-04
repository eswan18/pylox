'Expression classes for the AST.'

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ._token import Token, TokenType

class Expr(ABC):
    ...

    @abstractmethod
    def __str__(self):
        ...

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __str__(self):
        return f'({self.operator.lexeme} {self.left} {self.right})'

@dataclass
class Grouping(Expr):
    expression: Expr

    def __str__(self):
        return f'(group {self.expression})'

@dataclass
class Literal(Expr):
    value: Any

    def __str__(self):
        if self.value is None:
            return "nil"
        else:
            return str(self.value)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def __str__(self):
        return f'({self.operator.lexeme} {self.right})'

if __name__ == "__main__":
    print(
        Binary(
            Unary(
                Token(TokenType.MINUS, '-', None, 1),
                Literal(123),
            ),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(Literal(45.56)),
        )
    )
