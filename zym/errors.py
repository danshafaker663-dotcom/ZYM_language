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
