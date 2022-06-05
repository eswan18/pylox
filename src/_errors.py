from __future__ import annotations

from ._token import Token, TokenType


class LoxError(Exception):
    def __init__(self, return_code: int):
        self.return_code = return_code


class LoxParseError(Exception):
    def __init__(self, token: Token, msg: str):
        self.token = token
        self.msg = msg

    def __str__(self):
        if self.token.token_type == TokenType.EOF:
            location = 'EOF'
        else:
            location = f"'{self.token.lexeme}'"
        return f"[line {self.token.line_num}] Parse Error at {location}. {self.msg}"


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, msg: str):
        self.token = token
        self.msg = msg

    def __str__(self):
        return f'{self.msg}\n[line {self.token.line_num}]'
