"""Command-line interface for the ZYM interpreter."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from zym import __version__
from zym.errors import (
    LexError,
    ParseError,
    SemanticError,
    ZymFileError,
    ZymRuntimeError,
)
from zym.runner import parse_file, run_file


EXIT_SUCCESS = 0
EXIT_LEX_ERROR = 2
EXIT_PARSE_ERROR = 3
EXIT_SEMANTIC_ERROR = 4
EXIT_RUNTIME_ERROR = 5
EXIT_FILE_ERROR = 6


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zym",
        description="Run or check a ZYM source file.",
        epilog=(
            "Examples: python -m zym program.zym | "
            "python -m zym check program.zym"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ZYM {__version__}",
    )
    parser.add_argument(
        "command_or_file",
        nargs="?",
        help="run, check, or a .zym file (shorthand for run)",
    )
    parser.add_argument("source", nargs="?", help="path to a UTF-8 .zym file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = _argument_parser()
    arguments = parser.parse_args(argv)
    first = arguments.command_or_file

    if first is None:
        parser.print_help()
        return EXIT_SUCCESS

    if first in {"run", "check"}:
        command = first
        if arguments.source is None:
            parser.error(f"the {command} command requires a source file")
        source_path = arguments.source
    else:
        if arguments.source is not None:
            parser.error("use 'zym run FILE', 'zym check FILE', or 'zym FILE'")
        command = "run"
        source_path = first

    try:
        if command == "check":
            parse_file(source_path)
            print(f"Syntax OK: {source_path}")
        else:
            run_file(
                source_path,
                input_stream=sys.stdin,
                output_stream=sys.stdout,
            )
        return EXIT_SUCCESS
    except LexError as error:
        print(error, file=sys.stderr)
        return EXIT_LEX_ERROR
    except ParseError as error:
        print(error, file=sys.stderr)
        return EXIT_PARSE_ERROR
    except SemanticError as error:
        print(error, file=sys.stderr)
        return EXIT_SEMANTIC_ERROR
    except ZymRuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    except ZymFileError as error:
        print(error, file=sys.stderr)
        return EXIT_FILE_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
