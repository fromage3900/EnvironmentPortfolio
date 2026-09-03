import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from git_runner import git_run, git_status, git_log_summary, git_remotes, is_git_repo


class TestGitRunner(unittest.TestCase):
    """Unit tests for the centralized git runner utility."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self._run(["git", "init"])
        self._run(["git", "config", "user.email", "test@melodia.dev"])
        self._run(["git", "config", "user.name", "Test Runner"])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=self.cwd, capture_output=True, text=True, check=False)

    def _commit(self, msg: str = "test commit") -> None:
        marker = self.cwd / f"marker-{msg.replace(' ', '-')}.txt"
        marker.write_text("x", encoding="utf-8")
        self._run(["git", "add", str(marker)])
        self._run(["git", "commit", "-m", msg])

    def test_is_git_repo_true(self) -> None:
        self.assertTrue(is_git_repo(self.cwd))

    def test_is_git_repo_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(is_git_repo(d))

    def test_git_status_clean(self) -> None:
        status = git_status(self.cwd)
        self.assertTrue(status["ok"], status)
        self.assertEqual(status["dirty_count"], 0)
        self.assertEqual(status["dirty_files"], [])
        self.assertIsNone(status["error"])

    def test_git_status_dirty(self) -> None:
        (self.cwd / "dirty.txt").write_text("dirty", encoding="utf-8")
        status = git_status(self.cwd)
        self.assertTrue(status["ok"], status)
        self.assertEqual(status["dirty_count"], 1)
        self.assertTrue(any("dirty.txt" in f for f in status["dirty_files"]))

    def test_git_log_summary_empty(self) -> None:
        summary = git_log_summary(count=5, cwd=self.cwd)
        self.assertTrue(summary["ok"], summary)
        self.assertEqual(summary["lines"], [])

    def test_git_log_summary_commits(self) -> None:
        self._commit("first")
        self._commit("second")
        summary = git_log_summary(count=5, cwd=self.cwd)
        self.assertTrue(summary["ok"], summary)
        self.assertEqual(len(summary["lines"]), 2)
        self.assertTrue(all(len(l) > 0 and " " in l for l in summary["lines"]))

    def test_git_remotes(self) -> None:
        self._run(["git", "remote", "add", "origin", "https://example.com/repo.git"])
        remotes = git_remotes(self.cwd)
        self.assertTrue(remotes["ok"], remotes)
        self.assertEqual(remotes["remotes"], ["origin"])

    def test_git_run_failure(self) -> None:
        proc = git_run(["not-a-real-git-subcommand"], cwd=self.cwd)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
