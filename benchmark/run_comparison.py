"""Compare end-to-end ZYM and Python prime-sieve performance."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
ZYM_SOURCE = ROOT / "benchmark" / "prime_sieve.zym"
PYTHON_SOURCE = ROOT / "benchmark" / "prime_sieve.py"
RESULTS_DIRECTORY = ROOT / "benchmark" / "results"
RAW_CSV = RESULTS_DIRECTORY / "runtime_comparison.csv"
SUMMARY_LOG = RESULTS_DIRECTORY / "runtime_comparison.log"


class Measurement(NamedTuple):
    size: int
    implementation: str
    repeat: int
    seconds: float
    stdout: str


def command_for(implementation: str) -> list[str]:
    if implementation == "zym":
        return [sys.executable, "-m", "zym", str(ZYM_SOURCE)]
    if implementation == "python":
        return [sys.executable, str(PYTHON_SOURCE)]
    raise ValueError(f"unknown implementation: {implementation}")


def run_once(implementation: str, size: int) -> tuple[float, str]:
    started = time.perf_counter()
    result = subprocess.run(
        command_for(implementation),
        cwd=ROOT,
        input=f"{size}\n",
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    elapsed = time.perf_counter() - started
    if result.returncode != 0:
        raise RuntimeError(
            f"{implementation} failed for size {size} with exit code "
            f"{result.returncode}: {result.stderr}"
        )
    if result.stderr:
        raise RuntimeError(
            f"{implementation} wrote unexpected stderr for size {size}: "
            f"{result.stderr}"
        )
    return elapsed, result.stdout


def git_value(*arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *arguments],
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip()


def verify_outputs(sizes: list[int]) -> dict[int, str]:
    expected: dict[int, str] = {}
    for size in sizes:
        _, python_output = run_once("python", size)
        _, zym_output = run_once("zym", size)
        if zym_output != python_output:
            raise RuntimeError(
                f"output mismatch for size {size}: "
                f"ZYM={zym_output!r}, Python={python_output!r}"
            )
        expected[size] = python_output
    return expected


def collect_measurements(
    sizes: list[int],
    repeats: int,
    warmups: int,
) -> list[Measurement]:
    measurements: list[Measurement] = []
    for size in sizes:
        for _ in range(warmups):
            run_once("python", size)
            run_once("zym", size)

        for repeat in range(1, repeats + 1):
            order = ("python", "zym") if repeat % 2 else ("zym", "python")
            for implementation in order:
                seconds, stdout = run_once(implementation, size)
                measurements.append(
                    Measurement(size, implementation, repeat, seconds, stdout)
                )
                print(
                    f"size={size} implementation={implementation} "
                    f"repeat={repeat} seconds={seconds:.6f}",
                    flush=True,
                )
    return measurements


def write_csv(measurements: list[Measurement], timestamp: str) -> None:
    RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with RAW_CSV.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["timestamp", "size", "implementation", "repeat", "seconds", "stdout"]
        )
        for measurement in measurements:
            writer.writerow(
                [
                    timestamp,
                    measurement.size,
                    measurement.implementation,
                    measurement.repeat,
                    f"{measurement.seconds:.9f}",
                    measurement.stdout.replace("\n", "|"),
                ]
            )


def build_summary(
    measurements: list[Measurement],
    sizes: list[int],
    repeats: int,
    warmups: int,
    timestamp: str,
) -> str:
    dirty = str(bool(git_value("status", "--porcelain"))).lower()
    lines = [
        "ZYM VS PYTHON PRIME-SIEVE PERFORMANCE",
        f"timestamp={timestamp}",
        f"git_commit={git_value('rev-parse', 'HEAD')}",
        f"git_dirty={dirty}",
        f"python={platform.python_version()}",
        f"platform={platform.platform()}",
        f"sizes={','.join(str(size) for size in sizes)}",
        f"warmups_per_size={warmups}",
        f"repeats_per_size={repeats}",
        "timing_scope=end-to-end subprocess wall time",
        "output_verified=true",
        "",
        "size,zym_median_seconds,python_median_seconds,slowdown_ratio",
    ]
    for size in sizes:
        values: dict[str, list[float]] = {"zym": [], "python": []}
        for measurement in measurements:
            if measurement.size == size:
                values[measurement.implementation].append(measurement.seconds)
        zym_median = statistics.median(values["zym"])
        python_median = statistics.median(values["python"])
        ratio = zym_median / python_median
        lines.append(
            f"{size},{zym_median:.6f},{python_median:.6f},{ratio:.2f}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 3000, 6000])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=1)
    arguments = parser.parse_args()

    if any(size < 2 for size in arguments.sizes):
        parser.error("all sizes must be at least 2")
    if arguments.repeats <= 0 or arguments.warmups < 0:
        parser.error("repeats must be positive and warmups cannot be negative")
    if len(set(arguments.sizes)) != len(arguments.sizes):
        parser.error("sizes must be unique")

    print("Verifying equivalent outputs...", flush=True)
    expected = verify_outputs(arguments.sizes)
    for size, output in expected.items():
        print(f"size={size} output={output.strip().replace(chr(10), ',')}")

    measurements = collect_measurements(
        arguments.sizes,
        arguments.repeats,
        arguments.warmups,
    )
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    write_csv(measurements, timestamp)
    summary = build_summary(
        measurements,
        arguments.sizes,
        arguments.repeats,
        arguments.warmups,
        timestamp,
    )
    SUMMARY_LOG.write_text(summary, encoding="utf-8")
    print("\n" + summary, end="")
    print(f"raw_csv={RAW_CSV.relative_to(ROOT)}")
    print(f"summary_log={SUMMARY_LOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
