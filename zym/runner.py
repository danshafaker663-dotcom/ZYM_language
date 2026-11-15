"""Public helpers for parsing and running ZYM source code."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from zym.ast_nodes import Program
from zym.errors import ZymFileError
from zym.interpreter import Interpreter
from zym.lexer import Lexer
from zym.parser import Parser


def parse_source(source: str, filename: str = "<source>") -> Program:
    """Convert ZYM source text into an AST without executing it."""

    tokens = Lexer(source, filename).scan_tokens()
    return Parser(tokens, filename).parse()


def run_source(
    source: str,
    *,
    filename: str = "<source>",
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> Interpreter:
    """Parse and execute source text, returning the completed interpreter."""

    program = parse_source(source, filename)
    interpreter = Interpreter(
        filename=filename,
        input_stream=input_stream,
        output_stream=output_stream,
    )
    interpreter.interpret(program)
    return interpreter


def read_source_file(path: str | Path) -> tuple[str, str]:
    """Read one UTF-8 ZYM file and return its text and display filename."""

    source_path = Path(path)
    display_name = str(source_path)
    try:
        source = source_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ZymFileError("file does not exist", filename=display_name) from error
    except UnicodeDecodeError as error:
        raise ZymFileError("file is not valid UTF-8", filename=display_name) from error
    except OSError as error:
        message = error.strerror or str(error)
        raise ZymFileError(message, filename=display_name) from error
    return source, display_name


def parse_file(path: str | Path) -> Program:
    """Read and parse one UTF-8 ZYM file."""

    source, filename = read_source_file(path)
    return parse_source(source, filename)


def run_file(
    path: str | Path,
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> Interpreter:
    """Read, parse, and execute one UTF-8 ZYM file."""

    source, filename = read_source_file(path)
    return run_source(
        source,
        filename=filename,
        input_stream=input_stream,
        output_stream=output_stream,
    )
