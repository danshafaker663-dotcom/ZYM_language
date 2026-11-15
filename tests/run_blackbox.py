"""Run ZYM programs as black-box subprocess test cases."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


PROJECT_ROOT = Path(__file__).parents[1]
MANIFEST_PATH = PROJECT_ROOT / "tests" / "blackbox" / "manifest.json"
LOG_PATH = PROJECT_ROOT / "tests" / "results" / "latest_blackbox.log"


def load_cases() -> list[dict[str, Any]]:
    with MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
        data = json.load(manifest_file)
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError("black-box manifest must contain a 'cases' list")
    return cases


def run_case(case: dict[str, Any]) -> tuple[bool, str, float]:
    source = PROJECT_ROOT / case["source"]
    command = [sys.executable, "-m", "zym", str(source)]
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        input=case.get("stdin", ""),
        text=True,
        capture_output=True,
        timeout=case.get("timeout_seconds", 10),
        check=False,
    )
    elapsed = time.perf_counter() - started

    problems: list[str] = []
    expected_code = case.get("exit_code", 0)
    if result.returncode != expected_code:
        problems.append(
            f"exit code: expected {expected_code}, actual {result.returncode}"
        )

    expected_stdout = case.get("stdout", "")
    if result.stdout != expected_stdout:
        problems.append(
            f"stdout: expected {expected_stdout!r}, actual {result.stdout!r}"
        )

    stderr_fragments = case.get("stderr_contains", [])
    if not stderr_fragments:
        expected_stderr = case.get("stderr", "")
        if result.stderr != expected_stderr:
            problems.append(
                f"stderr: expected {expected_stderr!r}, actual {result.stderr!r}"
            )
    for fragment in stderr_fragments:
        if fragment not in result.stderr:
            problems.append(
                f"stderr does not contain {fragment!r}: actual {result.stderr!r}"
            )

    if problems:
        return False, "\n    ".join(problems), elapsed
    return True, "", elapsed


def main() -> int:
    cases = load_cases()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "ZYM BLACK-BOX TEST LOG",
        f"python={sys.version.split()[0]}",
        f"cases={len(cases)}",
        "",
    ]
    passed = 0
    started = time.perf_counter()

    for case in cases:
        try:
            successful, detail, elapsed = run_case(case)
        except subprocess.TimeoutExpired:
            successful = False
            detail = f"process exceeded {case.get('timeout_seconds', 10)} seconds"
            elapsed = float(case.get("timeout_seconds", 10))

        status = "PASS" if successful else "FAIL"
        print(f"[{status}] {case['id']} ({elapsed:.4f}s)")
        lines.append(f"[{status}] {case['id']} ({elapsed:.6f}s)")
        if successful:
            passed += 1
        else:
            print(f"    {detail}")
            lines.append(f"    {detail}")

    elapsed_total = time.perf_counter() - started
    failed = len(cases) - passed
    summary = [
        "",
        "ZYM BLACK-BOX SUMMARY",
        f"total={len(cases)}",
        f"passed={passed}",
        f"failed={failed}",
        f"elapsed_seconds={elapsed_total:.6f}",
        f"successful={failed == 0}",
    ]
    for line in summary:
        print(line)
    lines.extend(summary)
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"blackbox_log={LOG_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
