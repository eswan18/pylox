'Statement classes for the AST.'

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ._token import Token, TokenType
from ._expr import Expr

class Stmt(ABC):
    ...

@dataclass
class ExprStmt(Stmt):
    expression: Expr

@dataclass
class PrintStmt(Stmt):
    expression: Expr

@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]

@dataclass
class VarStmt(Stmt):
    token: Token
    initializer: Optional[Expr]
