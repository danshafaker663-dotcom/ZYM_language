"""Token definitions for the ZYM programming language."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """All token types recognized by the ZYM lexer."""

    # Single-character punctuation.
    LEFT_PAREN = auto()       # (
    RIGHT_PAREN = auto()      # )
    LEFT_BRACE = auto()       # {
    RIGHT_BRACE = auto()      # }
    LEFT_BRACKET = auto()     # [
    RIGHT_BRACKET = auto()    # ]
    COMMA = auto()            # ,
    DOT = auto()              # .
    COLON = auto()            # :

    # Arithmetic operators.
    PLUS = auto()             # +
    MINUS = auto()            # -
    STAR = auto()             # *
    SLASH = auto()            # /
    PERCENT = auto()          # %

    # Assignment, range, arrow, and comparison operators.
    ASSIGN = auto()           # :=
    ARROW = auto()            # ->
    RANGE = auto()            # ..
    EQUAL_EQUAL = auto()      # ==
    BANG_EQUAL = auto()       # !=
    LESS = auto()             # <
    LESS_EQUAL = auto()       # <=
    GREATER = auto()          # >
    GREATER_EQUAL = auto()    # >=

    # Literals and identifiers.
    IDENTIFIER = auto()
    INTEGER = auto()
    STRING = auto()

    # Keywords.
    SET = auto()
    OUTPUT = auto()
    INPUT = auto()
    WHEN = auto()
    OTHERWISE = auto()
    WHILE = auto()
    LOOP = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    DECLARE = auto()
    MAKE_FUNCTION = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "set": TokenType.SET,
    "output": TokenType.OUTPUT,
    "input": TokenType.INPUT,
    "when": TokenType.WHEN,
    "otherwise": TokenType.OTHERWISE,
    "while": TokenType.WHILE,
    "loop": TokenType.LOOP,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "declare": TokenType.DECLARE,
    "makeFunction": TokenType.MAKE_FUNCTION,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


@dataclass(frozen=True)
class Token:
    """A token together with its original text and source position."""

    type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int

    def __str__(self) -> str:
        """Return a stable representation useful for debugging and tests."""

        return (
            f"Token(type={self.type.name}, "
            f"lexeme={self.lexeme!r}, "
            f"literal={self.literal!r}, "
            f"line={self.line}, "
            f"column={self.column})"
        )
