'Statement classes for the AST.'

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ._token import Token
from ._expr import Expr


class Stmt(ABC):
    ...


@dataclass
class ExprStmt(Stmt):
    expression: Expr


@dataclass
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None = None


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


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt
