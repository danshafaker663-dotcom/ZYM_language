"""Error types shared by the ZYM interpreter."""


class ZymError(Exception):
    """Base class for errors caused by ZYM source code."""


class LexError(ZymError):
    """Raised when the lexer encounters invalid source text."""

    def __init__(
        self,
        message: str,
        *,
        filename: str,
        line: int,
        column: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return (
            f"{self.filename}:{self.line}:{self.column}: "
            f"LexError: {self.message}"
        )


class ParseError(ZymError):
    """Raised when a valid token sequence does not match ZYM grammar."""

    def __init__(
        self,
        message: str,
        *,
        filename: str,
        line: int,
        column: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return (
            f"{self.filename}:{self.line}:{self.column}: "
            f"ParseError: {self.message}"
        )


class SemanticError(ZymError):
    """Raised when valid syntax violates a static ZYM language rule."""

    def __init__(self, message: str, *, filename: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return (
            f"{self.filename}:{self.line}:{self.column}: "
            f"SemanticError: {self.message}"
        )


class ZymRuntimeError(ZymError):
    """Raised when an operation fails while a ZYM program is running."""

    def __init__(self, message: str, *, filename: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return (
            f"{self.filename}:{self.line}:{self.column}: "
            f"RuntimeError: {self.message}"
        )


class ZymFileError(ZymError):
    """Raised when a ZYM source file cannot be read."""

    def __init__(self, message: str, *, filename: str) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.filename}: FileError: {self.message}"
