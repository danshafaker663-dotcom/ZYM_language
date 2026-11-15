"""Run the complete Python test suite and write a reproducible test log."""

from __future__ import annotations

import io
import platform
import subprocess
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"
LATEST_LOG = RESULTS_DIR / "latest_test.log"


class Tee:
    """Write unittest output to the terminal and an in-memory buffer."""

    def __init__(self, *streams: TextIO) -> None:
        self.streams = streams

    def write(self, text: str) -> int:
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def current_git_commit() -> str:
    """Return the checked-out commit without making the test depend on Git."""

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
    """Report whether tracked or untracked files differ from HEAD."""

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


def main() -> int:
    """Discover tests, run them, print a summary, and save the same evidence."""

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    suite = unittest.defaultTestLoader.discover(
        str(TESTS_DIR),
        pattern="test_*.py",
    )

    captured = io.StringIO()
    stream = Tee(sys.stdout, captured)
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    elapsed = time.perf_counter() - start

    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    expected_failures = len(result.expectedFailures)
    unexpected_successes = len(result.unexpectedSuccesses)
    passed = (
        result.testsRun
        - failures
        - errors
        - skipped
        - expected_failures
        - unexpected_successes
    )

    summary = (
        "\nZYM TEST SUMMARY\n"
        f"total={result.testsRun}\n"
        f"passed={passed}\n"
        f"failures={failures}\n"
        f"errors={errors}\n"
        f"skipped={skipped}\n"
        f"elapsed_seconds={elapsed:.6f}\n"
        f"successful={result.wasSuccessful()}\n"
    )
    print(summary, end="")

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    header = (
        "ZYM AUTOMATED TEST LOG\n"
        f"timestamp={timestamp}\n"
        f"git_commit={current_git_commit()}\n"
        f"git_dirty={git_worktree_is_dirty()}\n"
        f"python={platform.python_version()}\n"
        f"platform={platform.platform()}\n"
        f"command={Path(sys.executable).name} tests/run_tests.py\n\n"
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_LOG.write_text(
        header + captured.getvalue() + summary,
        encoding="utf-8",
    )
    print(f"test_log={LATEST_LOG.relative_to(ROOT)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
