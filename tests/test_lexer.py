"""Unit tests for the ZYM lexer."""

import unittest

from zym.errors import LexError
from zym.lexer import Lexer
from zym.token import KEYWORDS, TokenType


def token_types(source: str) -> list[TokenType]:
    return [token.type for token in Lexer(source).scan_tokens()]


class LexerTests(unittest.TestCase):
    def test_variable_declaration(self) -> None:
        self.assertEqual(
            token_types("set age := 20."),
            [
                TokenType.SET,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.INTEGER,
                TokenType.DOT,
                TokenType.EOF,
            ],
        )

    def test_all_keywords(self) -> None:
        source = " ".join(KEYWORDS)
        actual = token_types(source)
        expected = [*KEYWORDS.values(), TokenType.EOF]
        self.assertEqual(actual, expected)

    def test_punctuation_and_operators(self) -> None:
        source = "( ) { } [ ] , . : + - * / % := -> .. == != < <= > >="
        self.assertEqual(
            token_types(source),
            [
                TokenType.LEFT_PAREN,
                TokenType.RIGHT_PAREN,
                TokenType.LEFT_BRACE,
                TokenType.RIGHT_BRACE,
                TokenType.LEFT_BRACKET,
                TokenType.RIGHT_BRACKET,
                TokenType.COMMA,
                TokenType.DOT,
                TokenType.COLON,
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.PERCENT,
                TokenType.ASSIGN,
                TokenType.ARROW,
                TokenType.RANGE,
                TokenType.EQUAL_EQUAL,
                TokenType.BANG_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.EOF,
            ],
        )

    def test_integer_literal(self) -> None:
        tokens = Lexer("12345").scan_tokens()
        self.assertEqual(tokens[0].lexeme, "12345")
        self.assertEqual(tokens[0].literal, 12345)

    def test_string_escapes(self) -> None:
        tokens = Lexer(r'"line\ncolumn\tquote\"slash\\"').scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, 'line\ncolumn\tquote"slash\\')

    def test_unicode_identifier(self) -> None:
        tokens = Lexer("set 玩家2 := 1.").scan_tokens()
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].lexeme, "玩家2")

    def test_comment_and_source_position(self) -> None:
        tokens = Lexer('# comment\noutput "ok".').scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.OUTPUT)
        self.assertEqual((tokens[0].line, tokens[0].column), (2, 1))
        self.assertEqual((tokens[1].line, tokens[1].column), (2, 8))

    def test_eof_position(self) -> None:
        eof = Lexer("output 1.\n").scan_tokens()[-1]
        self.assertEqual(eof.type, TokenType.EOF)
        self.assertEqual((eof.line, eof.column), (2, 1))

    def test_unexpected_character(self) -> None:
        with self.assertRaisesRegex(LexError, "unexpected character"):
            Lexer("@").scan_tokens()

    def test_unterminated_string(self) -> None:
        with self.assertRaisesRegex(LexError, "unterminated string literal"):
            Lexer('"missing').scan_tokens()

    def test_unknown_escape_sequence(self) -> None:
        with self.assertRaisesRegex(LexError, "unknown escape sequence"):
            Lexer(r'"bad\x"').scan_tokens()

    def test_single_equal_is_invalid(self) -> None:
        with self.assertRaisesRegex(LexError, "expected '=' after '='"):
            Lexer("=").scan_tokens()

    def test_error_contains_source_position(self) -> None:
        with self.assertRaises(LexError) as context:
            Lexer("\n@", filename="demo.zym").scan_tokens()
        self.assertEqual(
            str(context.exception),
            "demo.zym:2:1: LexError: unexpected character '@'",
        )


if __name__ == "__main__":
    unittest.main()
