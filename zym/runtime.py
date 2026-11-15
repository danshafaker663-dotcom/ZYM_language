"""Runtime data structures used by the ZYM tree-walking interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zym.errors import SemanticError, ZymRuntimeError
from zym.token import Token


class Environment:
    """One lexical scope linked to an optional enclosing scope."""

    def __init__(
        self,
        enclosing: Environment | None = None,
        *,
        filename: str | None = None,
    ) -> None:
        self.enclosing = enclosing
        self.filename = filename or (
            enclosing.filename if enclosing is not None else "<source>"
        )
        self._values: dict[str, Any] = {}

    def define(self, name: Token, value: Any) -> None:
        """Create a variable in this scope, rejecting duplicate declarations."""

        if name.lexeme in self._values:
            raise SemanticError(
                f"name '{name.lexeme}' is already declared in this scope",
                filename=self.filename,
                line=name.line,
                column=name.column,
            )
        self._values[name.lexeme] = value

    def define_builtin(self, name: str, value: Any) -> None:
        """Install an interpreter-provided name in the global environment."""

        if name in self._values:
            raise ValueError(f"duplicate builtin name: {name}")
        self._values[name] = value

    def get(self, name: Token) -> Any:
        """Look up a name from the nearest lexical scope outwards."""

        if name.lexeme in self._values:
            return self._values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise ZymRuntimeError(
            f"undefined name '{name.lexeme}'",
            filename=self.filename,
            line=name.line,
            column=name.column,
        )

    def assign(self, name: Token, value: Any) -> None:
        """Update the nearest existing binding for a name."""

        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise ZymRuntimeError(
            f"undefined name '{name.lexeme}'",
            filename=self.filename,
            line=name.line,
            column=name.column,
        )


@dataclass(frozen=True)
class StructureType:
    """A declared structure name and its fixed field order."""

    name: str
    fields: tuple[str, ...]
    filename: str = "<source>"

    def create(self, values: dict[str, Any], token: Token) -> StructureInstance:
        """Validate field names and create one mutable structure instance."""

        expected = set(self.fields)
        actual = set(values)
        missing = [field for field in self.fields if field not in actual]
        unknown = [field for field in values if field not in expected]

        if missing:
            raise ZymRuntimeError(
                f"missing field(s) for {self.name}: {', '.join(missing)}",
                filename=self.filename,
                line=token.line,
                column=token.column,
            )
        if unknown:
            raise ZymRuntimeError(
                f"unknown field(s) for {self.name}: {', '.join(unknown)}",
                filename=self.filename,
                line=token.line,
                column=token.column,
            )

        ordered_values = {field: values[field] for field in self.fields}
        return StructureInstance(self, ordered_values)


@dataclass
class StructureInstance:
    """A mutable value created from a StructureType."""

    structure_type: StructureType
    values: dict[str, Any]

    def get(self, name: Token) -> Any:
        if name.lexeme not in self.values:
            self._field_error(name)
        return self.values[name.lexeme]

    def set(self, name: Token, value: Any) -> None:
        if name.lexeme not in self.values:
            self._field_error(name)
        self.values[name.lexeme] = value

    def _field_error(self, name: Token) -> None:
        raise ZymRuntimeError(
            f"{self.structure_type.name} has no field '{name.lexeme}'",
            filename=self.structure_type.filename,
            line=name.line,
            column=name.column,
        )
