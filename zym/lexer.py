"""Lexical analysis for the ZYM programming language."""

from __future__ import annotations

from zym.errors import LexError
from zym.token import KEYWORDS, Token, TokenType


class Lexer:
    """Convert ZYM source text into a sequence of tokens."""

    def __init__(self, source: str, filename: str = "<source>") -> None:
        self.source = source
        self.filename = filename
        self.tokens: list[Token] = []

        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def scan_tokens(self) -> list[Token]:
        """Scan all tokens and append one final EOF token."""

        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(
            Token(
                TokenType.EOF,
                "",
                None,
                self.line,
                self.column,
            )
        )
        return self.tokens

    def _scan_token(self) -> None:
        char = self._advance()

        single_character_tokens = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            "[": TokenType.LEFT_BRACKET,
            "]": TokenType.RIGHT_BRACKET,
            ",": TokenType.COMMA,
            "+": TokenType.PLUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
        }

        token_type = single_character_tokens.get(char)
        if token_type is not None:
            self._add_token(token_type)
            return

        if char == ".":
            self._add_token(
                TokenType.RANGE if self._match(".") else TokenType.DOT
            )
        elif char == ":":
            self._add_token(
                TokenType.ASSIGN if self._match("=") else TokenType.COLON
            )
        elif char == "-":
            self._add_token(
                TokenType.ARROW if self._match(">") else TokenType.MINUS
            )
        elif char == "=":
            if not self._match("="):
                self._raise_error("expected '=' after '='")
            self._add_token(TokenType.EQUAL_EQUAL)
        elif char == "!":
            if not self._match("="):
                self._raise_error("expected '=' after '!'")
            self._add_token(TokenType.BANG_EQUAL)
        elif char == "<":
            self._add_token(
                TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            )
        elif char == ">":
            self._add_token(
                TokenType.GREATER_EQUAL
                if self._match("=")
                else TokenType.GREATER
            )
        elif char in {" ", "\r", "\t", "\n"}:
            return
        elif char == "#":
            self._skip_comment()
        elif char == '"':
            self._scan_string()
        elif char.isdigit():
            self._scan_integer()
        elif self._is_identifier_start(char):
            self._scan_identifier()
        else:
            self._raise_error(f"unexpected character {char!r}")

    def _scan_integer(self) -> None:
        while self._peek().isdigit():
            self._advance()

        text = self.source[self.start : self.current]
        self._add_token(TokenType.INTEGER, int(text))

    def _scan_identifier(self) -> None:
        while self._is_identifier_part(self._peek()):
            self._advance()

        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _scan_string(self) -> None:
        value: list[str] = []

        while not self._is_at_end():
            char = self._advance()

            if char == '"':
                self._add_token(TokenType.STRING, "".join(value))
                return

            if char == "\n":
                self._raise_error(
                    "unterminated string literal",
                    line=self.start_line,
                    column=self.start_column,
                )

            if char != "\\":
                value.append(char)
                continue

            if self._is_at_end():
                self._raise_error(
                    "unterminated escape sequence",
                    line=self.start_line,
                    column=self.start_column,
                )

            escape = self._advance()
            escape_values = {
                "n": "\n",
                "t": "\t",
                '"': '"',
                "\\": "\\",
            }
            if escape not in escape_values:
                self._raise_error(f"unknown escape sequence '\\{escape}'")
            value.append(escape_values[escape])

        self._raise_error(
            "unterminated string literal",
            line=self.start_line,
            column=self.start_column,
        )

    def _skip_comment(self) -> None:
        while self._peek() not in {"\n", "\0"}:
            self._advance()

    def _add_token(self, token_type: TokenType, literal: object = None) -> None:
        lexeme = self.source[self.start : self.current]
        self.tokens.append(
            Token(
                token_type,
                lexeme,
                literal,
                self.start_line,
                self.start_column,
            )
        )

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self._advance()
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char == "_" or char.isalpha()

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return char == "_" or char.isalnum()

    def _raise_error(
        self,
        message: str,
        *,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        raise LexError(
            message,
            filename=self.filename,
            line=self.start_line if line is None else line,
            column=self.start_column if column is None else column,
        )
