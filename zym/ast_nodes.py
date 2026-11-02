"""Abstract syntax tree node definitions for ZYM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zym.token import Token


class Node:
    """Base class for every AST node."""


class Expr(Node):
    """Base class for expression nodes that produce a value."""


class Stmt(Node):
    """Base class for statement and declaration nodes."""


@dataclass(frozen=True)
class Program(Node):
    """The root node of one parsed ZYM source file."""

    declarations: tuple[Stmt, ...]


# Expression nodes


@dataclass(frozen=True)
class Literal(Expr):
    """An integer, string, Boolean, or null literal."""

    token: Token
    value: Any


@dataclass(frozen=True)
class Variable(Expr):
    """A reference to a variable by name."""

    name: Token


@dataclass(frozen=True)
class Grouping(Expr):
    """A parenthesized expression."""

    expression: Expr


@dataclass(frozen=True)
class Unary(Expr):
    """A prefix unary operation such as -value or not value."""

    operator: Token
    operand: Expr


@dataclass(frozen=True)
class Binary(Expr):
    """A binary arithmetic, comparison, or equality operation."""

    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Logical(Expr):
    """A short-circuiting and/or expression."""

    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class ArrayLiteral(Expr):
    """An array literal such as [1, 2, 3]."""

    bracket: Token
    elements: tuple[Expr, ...]


@dataclass(frozen=True)
class StructureField(Node):
    """One named value inside a structure literal."""

    name: Token
    value: Expr


@dataclass(frozen=True)
class StructureLiteral(Expr):
    """A structure instance expression such as Student { name: value }."""

    name: Token
    fields: tuple[StructureField, ...]


@dataclass(frozen=True)
class IndexAccess(Expr):
    """Array indexing such as values[index]."""

    collection: Expr
    bracket: Token
    index: Expr


@dataclass(frozen=True)
class FieldAccess(Expr):
    """Structure field access such as student.name."""

    object: Expr
    name: Token


@dataclass(frozen=True)
class Call(Expr):
    """A function call expression."""

    callee: Expr
    paren: Token
    arguments: tuple[Expr, ...]


# Statement and declaration nodes


@dataclass(frozen=True)
class Block(Stmt):
    """A brace-delimited sequence of declarations and statements."""

    brace: Token
    declarations: tuple[Stmt, ...]


@dataclass(frozen=True)
class ExpressionStatement(Stmt):
    """An expression evaluated for its side effects."""

    expression: Expr


@dataclass(frozen=True)
class VariableDeclaration(Stmt):
    """A variable declaration introduced by set."""

    keyword: Token
    name: Token
    initializer: Expr


@dataclass(frozen=True)
class Assignment(Stmt):
    """Assignment to a variable, array element, or structure field."""

    target: Expr
    operator: Token
    value: Expr


@dataclass(frozen=True)
class OutputStatement(Stmt):
    """Write one expression value to standard output."""

    keyword: Token
    expression: Expr


@dataclass(frozen=True)
class InputStatement(Stmt):
    """Read one line from standard input into a new variable."""

    keyword: Token
    prompt: Expr
    name: Token


@dataclass(frozen=True)
class IfStatement(Stmt):
    """A when/otherwise conditional statement."""

    keyword: Token
    condition: Expr
    then_branch: Block
    else_branch: Stmt | None


@dataclass(frozen=True)
class WhileStatement(Stmt):
    """A condition-controlled while loop."""

    keyword: Token
    condition: Expr
    body: Block


@dataclass(frozen=True)
class LoopStatement(Stmt):
    """An integer range loop introduced by loop."""

    keyword: Token
    variable: Token
    start: Expr
    end: Expr
    body: Block


@dataclass(frozen=True)
class BreakStatement(Stmt):
    """Exit the nearest enclosing loop."""

    keyword: Token


@dataclass(frozen=True)
class ContinueStatement(Stmt):
    """Continue with the next iteration of the nearest loop."""

    keyword: Token


@dataclass(frozen=True)
class ReturnStatement(Stmt):
    """Return an optional value from the current function."""

    keyword: Token
    value: Expr | None


@dataclass(frozen=True)
class StructureDeclaration(Stmt):
    """Declare a structure type and its fixed field names."""

    keyword: Token
    name: Token
    fields: tuple[Token, ...]


@dataclass(frozen=True)
class FunctionDeclaration(Stmt):
    """Declare a named function with parameters and a body."""

    keyword: Token
    name: Token
    parameters: tuple[Token, ...]
    body: Block
