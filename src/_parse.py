from ._token import Token
from ._expr import Expr, Binary, Grouping, Literal, Logical, Unary, Variable, Assignment
from ._stmt import Stmt, ExprStmt, IfStmt, PrintStmt, WhileStmt, VarStmt, BlockStmt
from ._errors import LoxParseError
# We're going to use this a lot so an alias helps.
from ._token import TokenType as TT


class Parser:

    def __init__(self):
        self.errors: list[LoxParseError] = []

    def parse(
        self,
        tokens: list[Token],
    ) -> list[Stmt]:
        current_pos = 0
        stmts: list[Stmt] = []
        while tokens[current_pos].token_type != TT.EOF:
            try:
                stmt, current_pos = self.parse_declaration(tokens, current_pos)
            except LoxParseError as exc:
                self.errors.append(exc)
                current_pos = self.synchronize(tokens, current_pos+1)
            else:
                stmts.append(stmt)
        return stmts

    def parse_declaration(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[Stmt, int]:
        if tokens[current_pos].token_type == TT.VAR:
            # Consume the VAR token.
            current_pos += 1
            return self.parse_var_declaration(tokens, current_pos)
        else:
            return self.parse_stmt(tokens, current_pos)

    def parse_var_declaration(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[Stmt, int]:
        name_token, current_pos = self.consume(
            tokens,
            current_pos,
            TT.IDENTIFIER,
            "Expect variable name.",
        )
        initializer = None
        if tokens[current_pos].token_type == TT.EQUAL:
            # Consume the EQUAL token.
            current_pos += 1
            initializer, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.SEMICOLON,
            "Expect ';' after variable declaration.",
        )
        return VarStmt(name_token, initializer), current_pos

    def parse_while_stmt(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[WhileStmt, int]:
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.LEFT_PAREN,
            "Expect '(' after 'while'.",
        )
        condition, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.RIGHT_PAREN,
            "Expect ')' after while condition.",
        )
        body, current_pos = self.parse_stmt(tokens, current_pos)
        return WhileStmt(condition, body), current_pos

    def parse_stmt(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Stmt, int]:
        if tokens[current_pos].token_type == TT.IF:
            # Consume the IF token.
            current_pos += 1
            return self.parse_if_stmt(tokens, current_pos)
        elif tokens[current_pos].token_type == TT.PRINT:
            # Consume the PRINT token.
            current_pos += 1
            return self.parse_print_stmt(tokens, current_pos)
        elif tokens[current_pos].token_type == TT.WHILE:
            # Consume the left brace token.
            current_pos += 1
            return self.parse_while_stmt(tokens, current_pos)
        elif tokens[current_pos].token_type == TT.LEFT_BRACE:
            # Consume the left brace token.
            current_pos += 1
            block, current_pos = self.parse_block(tokens, current_pos)
            return BlockStmt(block), current_pos
        elif tokens[current_pos].token_type == TT.FOR:
            # Consume the for token.
            current_pos += 1
            return self.parse_for_stmt(tokens, current_pos)
        else:
            return self.parse_expr_stmt(tokens, current_pos)

    def parse_for_stmt(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[Stmt, int]:
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.LEFT_PAREN,
            "Expect '(' after 'for'.",
        )
        initializer: Stmt | None
        if tokens[current_pos].token_type == TT.SEMICOLON:
            # Consume the semicolon
            current_pos += 1
            initializer = None
        elif tokens[current_pos].token_type == TT.VAR:
            # Consume the var keyword
            current_pos += 1
            initializer, current_pos = self.parse_var_declaration(tokens, current_pos)
        else:
            initializer, current_pos = self.parse_expr_stmt(tokens, current_pos)

        condition: Expr | None = None
        if tokens[current_pos].token_type != TT.SEMICOLON:
            condition, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.SEMICOLON,
            "Expect ';' after loop condition."
        )

        increment: Expr | None = None
        if tokens[current_pos].token_type != TT.RIGHT_PAREN:
            increment, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.RIGHT_PAREN,
            "Expect ')' after for clauses."
        )

        body, current_pos = self.parse_stmt(tokens, current_pos)

        # Desugar
        if increment:
            body = BlockStmt([body, ExprStmt(increment)])
        if condition is not None:
            body = WhileStmt(condition, body)
        else:
            body = WhileStmt(Literal(True), body)
        if initializer:
            body = BlockStmt([initializer, body])
        return body, current_pos

    def parse_if_stmt(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[IfStmt, int]:
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.LEFT_PAREN,
            "Expect '(' after 'if'.",
        )
        condition, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.RIGHT_PAREN,
            "Expect ')' after if condition."
        )
        then_stmt, current_pos = self.parse_stmt(tokens, current_pos)
        else_stmt = None
        if tokens[current_pos].token_type == TT.ELSE:
            # Consume the ELSE token.
            current_pos += 1
            else_stmt, current_pos = self.parse_stmt(tokens, current_pos)
        return IfStmt(condition, then_stmt, else_stmt), current_pos

    def parse_expr_stmt(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Stmt, int]:
        expr, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.SEMICOLON,
            "Expect ';' after expression.",
        )
        return ExprStmt(expr), current_pos

    def parse_block(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[list[Stmt], int]:
        stmts: list[Stmt] = []

        while tokens[current_pos].token_type not in (TT.RIGHT_BRACE, TT.EOF):
            declaration, current_pos = self.parse_declaration(tokens, current_pos)
            stmts.append(declaration)

        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.RIGHT_BRACE,
            "Expect '}' after block."
        )
        return stmts, current_pos

    def parse_print_stmt(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Stmt, int]:
        expr, current_pos = self.parse_expression(tokens, current_pos)
        _, current_pos = self.consume(
            tokens,
            current_pos,
            TT.SEMICOLON,
            "Expect ';' after value.",
        )
        return PrintStmt(expr), current_pos

    def parse_expression(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        return self.parse_assignment(tokens, current_pos)

    def parse_assignment(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_or(tokens, current_pos)
        if tokens[current_pos].token_type == TT.EQUAL:
            # If this is indeed an assignment.
            equals_pos = current_pos
            current_pos += 1
            value, current_pos = self.parse_assignment(tokens, current_pos)
            # Only certain things are valid l-values.
            if isinstance(expr, Variable):
                return Assignment(expr.token, value), current_pos
            else:
                # Note that we don't *raise* errors in parsing, halting immediately;
                # instead we finish parsing everything and display all the errors we
                # find at once.
                self.errors.append(
                    LoxParseError(tokens[equals_pos], "Invalid assignment target.")
                )
                return expr, current_pos
        else:
            # If this is not an assignment expression.
            return expr, current_pos

    def parse_or(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_and(tokens, current_pos)
        while tokens[current_pos].token_type == TT.OR:
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_and(tokens, current_pos)
            expr = Logical(expr, operator, right)
        return expr, current_pos

    def parse_and(
        self,
        tokens: list[Token],
        current_pos: int,
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_equality(tokens, current_pos)
        while tokens[current_pos].token_type == TT.AND:
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_equality(tokens, current_pos)
            expr = Logical(expr, operator, right)
        return expr, current_pos

    def parse_equality(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_comparison(tokens, current_pos)
        while tokens[current_pos].token_type in (TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_comparison(tokens, current_pos)
            expr = Binary(expr, operator, right)
        return expr, current_pos

    def parse_comparison(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_term(tokens, current_pos)
        tok_types = (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL)
        while tokens[current_pos].token_type in tok_types:
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_term(tokens, current_pos)
            expr = Binary(expr, operator, right)
        return expr, current_pos

    def parse_term(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_factor(tokens, current_pos)
        while tokens[current_pos].token_type in (TT.MINUS, TT.PLUS):
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_factor(tokens, current_pos)
            expr = Binary(expr, operator, right)
        return expr, current_pos

    def parse_factor(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        expr, current_pos = self.parse_unary(tokens, current_pos)
        while tokens[current_pos].token_type in (TT.SLASH, TT.STAR):
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_unary(tokens, current_pos)
            expr = Binary(expr, operator, right)
        return expr, current_pos

    def parse_unary(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        if tokens[current_pos].token_type in (TT.BANG, TT.MINUS):
            operator = tokens[current_pos]
            current_pos += 1
            right, current_pos = self.parse_unary(tokens, current_pos)
            return Unary(operator, right), current_pos
        else:
            return self.parse_primary(tokens, current_pos)

    def parse_primary(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> tuple[Expr, int]:
        token = tokens[current_pos]
        if token.token_type == TT.FALSE:
            return (Literal(False), current_pos + 1)
        elif token.token_type == TT.TRUE:
            return (Literal(True), current_pos + 1)
        elif token.token_type == TT.NIL:
            return (Literal(None), current_pos + 1)
        elif token.token_type == TT.IDENTIFIER:
            return (Variable(tokens[current_pos]), current_pos + 1)
        elif token.token_type in (TT.NUMBER, TT.STRING):
            return (Literal(token.literal), current_pos + 1)
        elif token.token_type == TT.LEFT_PAREN:
            expr, current_pos = self.parse_expression(tokens, current_pos + 1)
            paren, current_pos = self.consume(
                tokens,
                current_pos,
                TT.RIGHT_PAREN,
                "Expect ')' after expression.",
            )
            return Grouping(expr), current_pos
        else:
            raise LoxParseError(token, 'Expect expression.')

    def consume(
        self,
        tokens: list[Token],
        current_pos: int,
        expected: TT,
        msg: str
    ) -> tuple[Token, int]:
        if tokens[current_pos].token_type == expected:
            return (tokens[current_pos], current_pos + 1)
        else:
            raise LoxParseError(tokens[current_pos], msg)

    def synchronize(
        self,
        tokens: list[Token],
        current_pos: int
    ) -> int:
        # If we're already at the end of the input, no need to synchronize.
        if tokens[current_pos].token_type == TT.EOF:
            return current_pos

        current_pos += 1
        # These tokens generally begin statements. The interpreter should resync if it
        # hits one.
        resync_tokens = (
            TT.CLASS, TT.FUN, TT.VAR, TT.FOR, TT.IF, TT.WHILE, TT.PRINT, TT.RETURN
        )
        while tokens[current_pos].token_type != TT.EOF:
            if tokens[current_pos-1] == TT.SEMICOLON:
                return current_pos
            if tokens[current_pos].token_type in resync_tokens:
                return current_pos
            current_pos += 1
        return current_pos
