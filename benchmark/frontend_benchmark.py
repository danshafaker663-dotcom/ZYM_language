"""Measure the current performance of the ZYM lexer and parser."""

from __future__ import annotations

import argparse
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "examples" / "syntax_tour.zym"
DEFAULT_OUTPUT = ROOT / "benchmark" / "results" / "frontend_latest.log"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zym.lexer import Lexer
from zym.parser import Parser


def current_git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return completed.stdout.strip()


def git_worktree_is_dirty() -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return str(bool(completed.stdout.strip())).lower()


def parse_once(source: str, filename: str) -> tuple[int, int]:
    tokens = Lexer(source, filename).scan_tokens()
    program = Parser(tokens, filename).parse()
    return len(tokens), len(program.declarations)


def benchmark_round(source: str, filename: str, iterations: int) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        parse_once(source, filename)
    return time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--rounds", type=int, default=7)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.iterations <= 0 or args.rounds <= 0:
        parser.error("iterations and rounds must be positive")

    source_path = args.source.resolve()
    source = source_path.read_text(encoding="utf-8")
    filename = str(source_path)
    token_count, declaration_count = parse_once(source, filename)

    for _ in range(100):
        parse_once(source, filename)

    round_seconds = [
        benchmark_round(source, filename, args.iterations)
        for _ in range(args.rounds)
    ]
    per_parse_ms = [
        seconds * 1000 / args.iterations for seconds in round_seconds
    ]
    median_ms = statistics.median(per_parse_ms)
    parses_per_second = 1000 / median_ms

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "ZYM FRONTEND PERFORMANCE BASELINE",
        f"timestamp={timestamp}",
        f"git_commit={current_git_commit()}",
        f"git_dirty={git_worktree_is_dirty()}",
        f"python={platform.python_version()}",
        f"platform={platform.platform()}",
        f"source={source_path}",
        f"source_characters={len(source)}",
        f"tokens_per_parse={token_count}",
        f"declarations_per_parse={declaration_count}",
        f"warmup_iterations=100",
        f"rounds={args.rounds}",
        f"iterations_per_round={args.iterations}",
        "round_seconds=" + ",".join(f"{value:.6f}" for value in round_seconds),
        f"minimum_ms_per_parse={min(per_parse_ms):.6f}",
        f"median_ms_per_parse={median_ms:.6f}",
        f"maximum_ms_per_parse={max(per_parse_ms):.6f}",
        f"median_parses_per_second={parses_per_second:.2f}",
    ]
    report = "\n".join(lines) + "\n"

    print(report, end="")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"benchmark_log={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
