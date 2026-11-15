"""Unit tests for the ZYM recursive-descent parser."""

import unittest
from pathlib import Path

from zym.ast_nodes import (
    Assignment,
    Binary,
    Call,
    FieldAccess,
    IfStatement,
    IndexAccess,
    InputStatement,
    Literal,
    LoopStatement,
    OutputStatement,
    StructureDeclaration,
    StructureLiteral,
    VariableDeclaration,
    WhileStatement,
)
from zym.errors import ParseError
from zym.lexer import Lexer
from zym.parser import Parser
from zym.token import TokenType


def parse(source: str, filename: str = "<test>"):
    tokens = Lexer(source, filename).scan_tokens()
    return Parser(tokens, filename).parse()


class ParserTests(unittest.TestCase):
    def test_operator_precedence(self) -> None:
        program = parse("set result := 1 + 2 * 3.")
        declaration = program.declarations[0]

        self.assertIsInstance(declaration, VariableDeclaration)
        self.assertIsInstance(declaration.initializer, Binary)
        self.assertEqual(declaration.initializer.operator.type, TokenType.PLUS)
        self.assertIsInstance(declaration.initializer.right, Binary)
        self.assertEqual(
            declaration.initializer.right.operator.type,
            TokenType.STAR,
        )

    def test_structure_declaration_and_literal(self) -> None:
        program = parse(
            """
            declare Student { name, score }.
            set student := Student { name: "A", score: 95 }.
            """
        )

        declaration = program.declarations[0]
        variable = program.declarations[1]
        self.assertIsInstance(declaration, StructureDeclaration)
        self.assertEqual([field.lexeme for field in declaration.fields], ["name", "score"])
        self.assertIsInstance(variable.initializer, StructureLiteral)
        self.assertEqual(len(variable.initializer.fields), 2)

    def test_postfix_expression_chain(self) -> None:
        program = parse("output get(items[0].name).")
        statement = program.declarations[0]

        self.assertIsInstance(statement, OutputStatement)
        self.assertIsInstance(statement.expression, Call)
        argument = statement.expression.arguments[0]
        self.assertIsInstance(argument, FieldAccess)
        self.assertIsInstance(argument.object, IndexAccess)

    def test_control_flow_and_assignment(self) -> None:
        program = parse(
            """
            input "count: " -> raw.
            set count := toInt(raw).
            loop i in 0..count {
                output i.
            }
            while count > 0 {
                count := count - 1.
            }
            """
        )

        self.assertIsInstance(program.declarations[0], InputStatement)
        self.assertIsInstance(program.declarations[2], LoopStatement)
        while_statement = program.declarations[3]
        self.assertIsInstance(while_statement, WhileStatement)
        self.assertIsInstance(while_statement.body.declarations[0], Assignment)

    def test_otherwise_when_is_nested_if(self) -> None:
        program = parse(
            """
            when score >= 90 {
                output "A".
            } otherwise when score >= 60 {
                output "B".
            } otherwise {
                output "C".
            }
            """
        )
        statement = program.declarations[0]

        self.assertIsInstance(statement, IfStatement)
        self.assertIsInstance(statement.else_branch, IfStatement)
        self.assertIsNotNone(statement.else_branch.else_branch)

    def test_boolean_null_and_array_literals(self) -> None:
        program = parse("set values := [true, false, null, 3].")
        array = program.declarations[0].initializer

        self.assertEqual(
            [element.value for element in array.elements],
            [True, False, None, 3],
        )
        self.assertTrue(all(isinstance(element, Literal) for element in array.elements))

    def test_complete_syntax_tour(self) -> None:
        path = Path("examples/syntax_tour.zym")
        source = path.read_text(encoding="utf-8")
        program = Parser(
            Lexer(source, str(path)).scan_tokens(),
            str(path),
        ).parse()

        self.assertEqual(len(program.declarations), 8)

    def test_missing_statement_dot_reports_position(self) -> None:
        with self.assertRaises(ParseError) as context:
            parse("output 1", "demo.zym")

        self.assertEqual(
            str(context.exception),
            "demo.zym:1:9: ParseError: expected '.' after output value",
        )

    def test_invalid_assignment_target(self) -> None:
        with self.assertRaisesRegex(ParseError, "invalid assignment target"):
            parse("(1 + 2) := 3.")

    def test_empty_structure_declaration_is_rejected(self) -> None:
        with self.assertRaisesRegex(ParseError, "at least one structure field"):
            parse("declare Empty {}.")


if __name__ == "__main__":
    unittest.main()
