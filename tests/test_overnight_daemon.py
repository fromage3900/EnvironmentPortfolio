import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from overnight_daemon import repo_status, repo_dirty, QWEN_MODEL_CHAIN, PING_MODELS, WORKER_MODELS, REASONER_MODELS


class TestOvernightDaemonGit(unittest.TestCase):
    """Tests for the overnight daemon's git-runtime hardening."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        import subprocess as sp
        sp.run(["git", "init"], cwd=self.cwd, check=True)
        sp.run(["git", "config", "user.email", "test@melodia.dev"], cwd=self.cwd, check=True)
        sp.run(["git", "config", "user.name", "Test Runner"], cwd=self.cwd, check=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_repo_status_not_a_repo(self) -> None:
        # Use a non-repo directory; the function should report ok=False.
        import overnight_daemon as od
        original_root = od.ROOT
        try:
            od.ROOT = Path(self.cwd) / "not_a_repo"
            status = od.repo_status()
            self.assertFalse(status["ok"], status)
            self.assertIn("not a git repository", status["error"].lower())
        finally:
            od.ROOT = original_root

    def test_qwen_model_chain_excludes_problematic_qwen30b(self) -> None:
        # The 2026-09-01 research showed qwen3-coder:30b hangs on 12 GB VRAM.
        self.assertNotIn("qwen3-coder:30b", QWEN_MODEL_CHAIN)
        self.assertNotIn("qwen3-coder:30b", PING_MODELS)
        self.assertNotIn("qwen3-coder:30b", WORKER_MODELS)

    def test_reasoner_tier_still_available(self) -> None:
        self.assertIn("muse-glimmer:30b", REASONER_MODELS)

    def test_worker_tier_prefers_granite(self) -> None:
        self.assertEqual(WORKER_MODELS[0], "granite4.2:8b")


if __name__ == "__main__":
    unittest.main()
