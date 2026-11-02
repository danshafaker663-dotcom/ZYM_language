"""Unit tests for ZYM abstract syntax tree nodes."""

import unittest
from dataclasses import FrozenInstanceError

from zym.ast_nodes import (
    Binary,
    Block,
    FunctionDeclaration,
    IfStatement,
    Literal,
    Program,
    ReturnStatement,
    Variable,
    VariableDeclaration,
)
from zym.token import Token, TokenType


def token(token_type: TokenType, lexeme: str) -> Token:
    return Token(token_type, lexeme, None, 1, 1)


class AstNodeTests(unittest.TestCase):
    def test_binary_expression_tree(self) -> None:
        expression = Binary(
            Literal(token(TokenType.INTEGER, "1"), 1),
            token(TokenType.PLUS, "+"),
            Literal(token(TokenType.INTEGER, "2"), 2),
        )

        self.assertEqual(expression.left.value, 1)
        self.assertEqual(expression.operator.type, TokenType.PLUS)
        self.assertEqual(expression.right.value, 2)

    def test_variable_declaration(self) -> None:
        declaration = VariableDeclaration(
            token(TokenType.SET, "set"),
            token(TokenType.IDENTIFIER, "answer"),
            Literal(token(TokenType.INTEGER, "42"), 42),
        )

        self.assertEqual(declaration.name.lexeme, "answer")
        self.assertEqual(declaration.initializer.value, 42)

    def test_function_declaration(self) -> None:
        return_statement = ReturnStatement(
            token(TokenType.RETURN, "return"),
            Variable(token(TokenType.IDENTIFIER, "value")),
        )
        body = Block(
            token(TokenType.LEFT_BRACE, "{"),
            (return_statement,),
        )
        function = FunctionDeclaration(
            token(TokenType.MAKE_FUNCTION, "makeFunction"),
            token(TokenType.IDENTIFIER, "identity"),
            (token(TokenType.IDENTIFIER, "value"),),
            body,
        )

        self.assertEqual(function.name.lexeme, "identity")
        self.assertEqual(len(function.parameters), 1)
        self.assertIs(function.body.declarations[0], return_statement)

    def test_otherwise_when_uses_nested_if_node(self) -> None:
        empty_block = Block(token(TokenType.LEFT_BRACE, "{"), ())
        nested = IfStatement(
            token(TokenType.WHEN, "when"),
            Literal(token(TokenType.FALSE, "false"), False),
            empty_block,
            None,
        )
        outer = IfStatement(
            token(TokenType.WHEN, "when"),
            Literal(token(TokenType.TRUE, "true"), True),
            empty_block,
            nested,
        )

        self.assertIs(outer.else_branch, nested)

    def test_program_contains_declarations(self) -> None:
        declaration = VariableDeclaration(
            token(TokenType.SET, "set"),
            token(TokenType.IDENTIFIER, "value"),
            Literal(token(TokenType.NULL, "null"), None),
        )
        program = Program((declaration,))

        self.assertEqual(program.declarations, (declaration,))

    def test_nodes_are_immutable(self) -> None:
        literal = Literal(token(TokenType.INTEGER, "1"), 1)

        with self.assertRaises(FrozenInstanceError):
            literal.value = 2  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
