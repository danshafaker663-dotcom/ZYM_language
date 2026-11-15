"""Run all ZYM unit, integration, and black-box tests with one command."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).parents[1]


def run_step(label: str, script: str) -> bool:
    print(f"\n=== {label} ===", flush=True)
    result = subprocess.run(
        [sys.executable, script],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    started = time.perf_counter()
    unit_ok = run_step("UNIT AND INTEGRATION TESTS", "tests/run_tests.py")
    blackbox_ok = run_step("ZYM BLACK-BOX TESTS", "tests/run_blackbox.py")
    elapsed = time.perf_counter() - started
    successful = unit_ok and blackbox_ok

    print("\n=== ALL TESTS SUMMARY ===", flush=True)
    print(f"unit_and_integration={'PASS' if unit_ok else 'FAIL'}")
    print(f"blackbox={'PASS' if blackbox_ok else 'FAIL'}")
    print(f"elapsed_seconds={elapsed:.6f}")
    print(f"successful={successful}")
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
