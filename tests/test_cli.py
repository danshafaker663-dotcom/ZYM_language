"""Black-box process tests for the ZYM command-line interface."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).parents[1]


def run_cli(*arguments: str, input_text: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "zym", *arguments],
        cwd=PROJECT_ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_version(self) -> None:
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ZYM 0.1.0\n")
        self.assertEqual(result.stderr, "")

    def test_run_shorthand_executes_syntax_tour(self) -> None:
        result = run_cli("examples/syntax_tour.zym")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "学生：小明\n总分：259\n平均分：86\n等级：通过\n",
        )
        self.assertEqual(result.stderr, "")

    def test_check_command_parses_without_running(self) -> None:
        result = run_cli("check", "examples/syntax_tour.zym")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Syntax OK: examples/syntax_tour.zym\n")

    def test_root_launcher_is_compatible(self) -> None:
        result = subprocess.run(
            [sys.executable, "zym.py", "--version"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ZYM 0.1.0\n")

    def test_error_categories_have_documented_exit_codes(self) -> None:
        cases = (
            ("output @.", 2, "LexError"),
            ("output 1", 3, "ParseError"),
            ("break.", 4, "SemanticError"),
            ("output 1 / 0.", 5, "RuntimeError"),
        )
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            for index, (source, exit_code, error_name) in enumerate(cases):
                with self.subTest(error=error_name):
                    path = Path(temporary_directory) / f"error_{index}.zym"
                    path.write_text(source, encoding="utf-8")
                    result = run_cli(str(path))
                    self.assertEqual(result.returncode, exit_code)
                    self.assertEqual(result.stdout, "")
                    self.assertIn(error_name, result.stderr)

    def test_missing_file_returns_file_error_exit_code(self) -> None:
        result = run_cli("missing_file_for_cli_test.zym")
        self.assertEqual(result.returncode, 6)
        self.assertEqual(result.stdout, "")
        self.assertIn("FileError: file does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
