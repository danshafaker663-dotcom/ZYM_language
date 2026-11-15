"""Recursive-descent parser for the ZYM programming language."""

from __future__ import annotations

from zym.ast_nodes import (
    ArrayLiteral,
    Assignment,
    Binary,
    Block,
    BreakStatement,
    Call,
    ContinueStatement,
    Expr,
    ExpressionStatement,
    FieldAccess,
    FunctionDeclaration,
    Grouping,
    IfStatement,
    IndexAccess,
    InputStatement,
    Literal,
    Logical,
    LoopStatement,
    OutputStatement,
    Program,
    ReturnStatement,
    Stmt,
    StructureDeclaration,
    StructureField,
    StructureLiteral,
    Unary,
    Variable,
    VariableDeclaration,
    WhileStatement,
)
from zym.errors import ParseError
from zym.token import Token, TokenType


class Parser:
    """Convert a token sequence into a ZYM abstract syntax tree."""

    def __init__(
        self,
        tokens: list[Token],
        filename: str = "<source>",
    ) -> None:
        self.tokens = tokens
        self.filename = filename
        self.current = 0

    def parse(self) -> Program:
        """Parse an entire source file."""

        declarations: list[Stmt] = []
        while not self._is_at_end():
            declarations.append(self._declaration())
        return Program(tuple(declarations))

    def _declaration(self) -> Stmt:
        if self._match(TokenType.DECLARE):
            return self._structure_declaration(self._previous())
        if self._match(TokenType.MAKE_FUNCTION):
            return self._function_declaration(self._previous())
        return self._statement()

    def _structure_declaration(self, keyword: Token) -> StructureDeclaration:
        name = self._consume(
            TokenType.IDENTIFIER,
            "expected structure name after 'declare'",
        )
        self._consume(TokenType.LEFT_BRACE, "expected '{' after structure name")

        fields = [
            self._consume(
                TokenType.IDENTIFIER,
                "expected at least one structure field",
            )
        ]
        while self._match(TokenType.COMMA):
            if self._check(TokenType.RIGHT_BRACE):
                break
            fields.append(
                self._consume(TokenType.IDENTIFIER, "expected field name")
            )

        self._consume(TokenType.RIGHT_BRACE, "expected '}' after structure fields")
        self._consume(TokenType.DOT, "expected '.' after structure declaration")
        return StructureDeclaration(keyword, name, tuple(fields))

    def _function_declaration(self, keyword: Token) -> FunctionDeclaration:
        name = self._consume(
            TokenType.IDENTIFIER,
            "expected function name after 'makeFunction'",
        )
        self._consume(TokenType.LEFT_PAREN, "expected '(' after function name")

        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            parameters.append(
                self._consume(TokenType.IDENTIFIER, "expected parameter name")
            )
            while self._match(TokenType.COMMA):
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "expected parameter name")
                )

        self._consume(TokenType.RIGHT_PAREN, "expected ')' after parameters")
        body = self._consume_block("expected '{' before function body")
        return FunctionDeclaration(keyword, name, tuple(parameters), body)

    def _statement(self) -> Stmt:
        if self._match(TokenType.SET):
            return self._variable_declaration(self._previous())
        if self._match(TokenType.OUTPUT):
            return self._output_statement(self._previous())
        if self._match(TokenType.INPUT):
            return self._input_statement(self._previous())
        if self._match(TokenType.WHEN):
            return self._if_statement(self._previous())
        if self._match(TokenType.WHILE):
            return self._while_statement(self._previous())
        if self._match(TokenType.LOOP):
            return self._loop_statement(self._previous())
        if self._match(TokenType.BREAK):
            keyword = self._previous()
            self._consume(TokenType.DOT, "expected '.' after 'break'")
            return BreakStatement(keyword)
        if self._match(TokenType.CONTINUE):
            keyword = self._previous()
            self._consume(TokenType.DOT, "expected '.' after 'continue'")
            return ContinueStatement(keyword)
        if self._match(TokenType.RETURN):
            return self._return_statement(self._previous())
        if self._match(TokenType.LEFT_BRACE):
            return self._finish_block(self._previous())

        expression = self._expression()
        if self._match(TokenType.ASSIGN):
            operator = self._previous()
            if not isinstance(expression, (Variable, IndexAccess, FieldAccess)):
                raise self._error(operator, "invalid assignment target")
            value = self._expression()
            self._consume(TokenType.DOT, "expected '.' after assignment")
            return Assignment(expression, operator, value)

        self._consume(TokenType.DOT, "expected '.' after expression")
        return ExpressionStatement(expression)

    def _variable_declaration(self, keyword: Token) -> VariableDeclaration:
        name = self._consume(
            TokenType.IDENTIFIER,
            "expected variable name after 'set'",
        )
        self._consume(TokenType.ASSIGN, "expected ':=' after variable name")
        initializer = self._expression()
        self._consume(TokenType.DOT, "expected '.' after variable declaration")
        return VariableDeclaration(keyword, name, initializer)

    def _output_statement(self, keyword: Token) -> OutputStatement:
        expression = self._expression()
        self._consume(TokenType.DOT, "expected '.' after output value")
        return OutputStatement(keyword, expression)

    def _input_statement(self, keyword: Token) -> InputStatement:
        prompt = self._expression()
        self._consume(TokenType.ARROW, "expected '->' after input prompt")
        name = self._consume(
            TokenType.IDENTIFIER,
            "expected variable name after '->'",
        )
        self._consume(TokenType.DOT, "expected '.' after input statement")
        return InputStatement(keyword, prompt, name)

    def _if_statement(self, keyword: Token) -> IfStatement:
        condition = self._expression()
        then_branch = self._consume_block("expected '{' after when condition")

        else_branch: Stmt | None = None
        if self._match(TokenType.OTHERWISE):
            if self._match(TokenType.WHEN):
                else_branch = self._if_statement(self._previous())
            else:
                else_branch = self._consume_block(
                    "expected '{' after 'otherwise'"
                )

        return IfStatement(keyword, condition, then_branch, else_branch)

    def _while_statement(self, keyword: Token) -> WhileStatement:
        condition = self._expression()
        body = self._consume_block("expected '{' after while condition")
        return WhileStatement(keyword, condition, body)

    def _loop_statement(self, keyword: Token) -> LoopStatement:
        variable = self._consume(
            TokenType.IDENTIFIER,
            "expected loop variable after 'loop'",
        )
        self._consume(TokenType.IN, "expected 'in' after loop variable")
        start = self._expression()
        self._consume(TokenType.RANGE, "expected '..' in loop range")
        end = self._expression()
        body = self._consume_block("expected '{' after loop range")
        return LoopStatement(keyword, variable, start, end, body)

    def _return_statement(self, keyword: Token) -> ReturnStatement:
        value = None if self._check(TokenType.DOT) else self._expression()
        self._consume(TokenType.DOT, "expected '.' after return value")
        return ReturnStatement(keyword, value)

    def _consume_block(self, message: str) -> Block:
        brace = self._consume(TokenType.LEFT_BRACE, message)
        return self._finish_block(brace)

    def _finish_block(self, brace: Token) -> Block:
        declarations: list[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            declarations.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "expected '}' after block")
        return Block(brace, tuple(declarations))

    def _expression(self) -> Expr:
        return self._logic_or()

    def _logic_or(self) -> Expr:
        expression = self._logic_and()
        while self._match(TokenType.OR):
            operator = self._previous()
            expression = Logical(expression, operator, self._logic_and())
        return expression

    def _logic_and(self) -> Expr:
        expression = self._equality()
        while self._match(TokenType.AND):
            operator = self._previous()
            expression = Logical(expression, operator, self._equality())
        return expression

    def _equality(self) -> Expr:
        expression = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self._previous()
            expression = Binary(expression, operator, self._comparison())
        return expression

    def _comparison(self) -> Expr:
        expression = self._term()
        while self._match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operator = self._previous()
            expression = Binary(expression, operator, self._term())
        return expression

    def _term(self) -> Expr:
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            expression = Binary(expression, operator, self._factor())
        return expression

    def _factor(self) -> Expr:
        expression = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            expression = Binary(expression, operator, self._unary())
        return expression

    def _unary(self) -> Expr:
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._previous()
            return Unary(operator, self._unary())
        return self._postfix()

    def _postfix(self) -> Expr:
        expression = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expression = self._finish_call(expression, self._previous())
            elif self._match(TokenType.LEFT_BRACKET):
                bracket = self._previous()
                index = self._expression()
                self._consume(TokenType.RIGHT_BRACKET, "expected ']' after index")
                expression = IndexAccess(expression, bracket, index)
            elif self._check(TokenType.DOT) and self._check_at(
                1, TokenType.IDENTIFIER
            ):
                self._advance()
                name = self._consume(
                    TokenType.IDENTIFIER,
                    "expected field name after '.'",
                )
                expression = FieldAccess(expression, name)
            else:
                break

        return expression

    def _finish_call(self, callee: Expr, paren: Token) -> Call:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                arguments.append(self._expression())

        self._consume(TokenType.RIGHT_PAREN, "expected ')' after arguments")
        return Call(callee, paren, tuple(arguments))

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(self._previous(), False)
        if self._match(TokenType.TRUE):
            return Literal(self._previous(), True)
        if self._match(TokenType.NULL):
            return Literal(self._previous(), None)
        if self._match(TokenType.INTEGER, TokenType.STRING):
            token = self._previous()
            return Literal(token, token.literal)
        if self._match(TokenType.LEFT_BRACKET):
            return self._array_literal(self._previous())
        if self._match(TokenType.IDENTIFIER):
            name = self._previous()
            if self._looks_like_structure_literal():
                return self._structure_literal(name)
            return Variable(name)
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "expected ')' after expression")
            return Grouping(expression)

        raise self._error(self._peek(), "expected expression")

    def _array_literal(self, bracket: Token) -> ArrayLiteral:
        elements: list[Expr] = []
        if not self._check(TokenType.RIGHT_BRACKET):
            elements.append(self._expression())
            while self._match(TokenType.COMMA):
                elements.append(self._expression())

        self._consume(TokenType.RIGHT_BRACKET, "expected ']' after array values")
        return ArrayLiteral(bracket, tuple(elements))

    def _looks_like_structure_literal(self) -> bool:
        return (
            self._check(TokenType.LEFT_BRACE)
            and self._check_at(1, TokenType.IDENTIFIER)
            and self._check_at(2, TokenType.COLON)
        )

    def _structure_literal(self, name: Token) -> StructureLiteral:
        self._consume(TokenType.LEFT_BRACE, "expected '{' after structure name")

        fields: list[StructureField] = []
        while True:
            field_name = self._consume(
                TokenType.IDENTIFIER,
                "expected structure field name",
            )
            self._consume(TokenType.COLON, "expected ':' after field name")
            fields.append(StructureField(field_name, self._expression()))
            if not self._match(TokenType.COMMA):
                break
            if self._check(TokenType.RIGHT_BRACE):
                break

        self._consume(TokenType.RIGHT_BRACE, "expected '}' after field values")
        return StructureLiteral(name, tuple(fields))

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type is TokenType.EOF
        return self._peek().type is token_type

    def _check_at(self, offset: int, token_type: TokenType) -> bool:
        index = self.current + offset
        if index >= len(self.tokens):
            return False
        return self.tokens[index].type is token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type is TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, token: Token, message: str) -> ParseError:
        return ParseError(
            message,
            filename=self.filename,
            line=token.line,
            column=token.column,
        )
