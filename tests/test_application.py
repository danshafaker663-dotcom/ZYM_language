"""Subprocess smoke tests for the ZYM dungeon game application."""

from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_ROOT = Path(__file__).parents[1]
GAME_PATH = "app/dungeon_game.zym"


def run_game(user_input: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "zym", GAME_PATH],
        cwd=PROJECT_ROOT,
        input=user_input,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )


class DungeonGameSmokeTests(unittest.TestCase):
    def assert_successful_exit(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("感谢游玩，Tester！", result.stdout)

    def test_direct_exit(self) -> None:
        result = run_game("Tester\n5\n")
        self.assert_successful_exit(result)
        self.assertIn("你安全离开了地下城。", result.stdout)

    def test_status_then_exit(self) -> None:
        result = run_game("Tester\n2\n5\n")
        self.assert_successful_exit(result)
        self.assertIn("生命：30/30", result.stdout)
        self.assertIn("已探索房间：0", result.stdout)

    def test_shop_then_exit(self) -> None:
        result = run_game("Tester\n3\n3\n5\n")
        self.assert_successful_exit(result)
        self.assertIn("旅行商店", result.stdout)


if __name__ == "__main__":
    unittest.main()
