#!/usr/bin/env python3
"""LFS lock guard.

Pre-commit / CI helper that ensures any modified lockable binary file is
locked by the current Git user before it is committed.

In CI (GITHUB_ACTIONS set) the lock check is skipped because CI cannot hold
LFS locks; instead it verifies that LFS pointers are present for tracked files.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from git_runner import git_run, is_git_repo

GITATTRS = ROOT / ".gitattributes"


def _git(args: list[str]) -> str:
    return git_run(args, cwd=ROOT, check=False).stdout.strip()


def _lockable_patterns() -> list[str]:
    """Return glob-ish patterns from .gitattributes that are marked lockable."""
    if not GITATTRS.exists():
        return []
    patterns: list[str] = []
    for line in GITATTRS.read_text(encoding="utf-8").splitlines():
        if "lockable" in line and line.strip().startswith("*."):
            # e.g. "*.uasset filter=lfs ... lockable" -> "*.uasset"
            parts = line.split()
            if parts and parts[0].startswith("*."):
                patterns.append(parts[0][2:])  # strip leading *.
    return patterns


def _changed_files() -> list[pathlib.Path]:
    """Return files changed in the working tree (staged + unstaged)."""
    files: set[str] = set()
    for diff_arg in ("--cached", ""):
        cmd = ["git", "diff", "--name-only"] + ([diff_arg] if diff_arg else [])
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        if result.stdout:
            files.update(result.stdout.splitlines())
    # Also include unmerged/untracked binary-looking files? Keep it simple.
    return [ROOT / f for f in files if f]


def _is_lockable(path: pathlib.Path, patterns: list[str]) -> bool:
    return any(path.name.endswith(p) for p in patterns)


def main() -> int:
    if shutil.which("git") is None:
        print("::error::git executable not found on PATH")
        return 1

    if not is_git_repo(ROOT):
        print("::warning::Not inside a git repository; skipping LFS lock guard")
        return 0

    if not (ROOT / ".git").is_dir():
        print("::warning::Not inside a git repository; skipping LFS lock guard")
        return 0

    patterns = _lockable_patterns()
    if not patterns:
        print("::warning::No lockable patterns found in .gitattributes")
        return 0

    changed = _changed_files()
    touched_binaries = [p for p in changed if _is_lockable(p, patterns)]

    if not touched_binaries:
        print("[OK] No lockable binaries modified")
        return 0

    # CI mode: just verify LFS pointers exist for tracked files.
    if os.environ.get("GITHUB_ACTIONS") == "true":
        tracked = _git(["ls-files"] + [str(p.relative_to(ROOT)) for p in touched_binaries]).splitlines()
        missing_lfs: list[str] = []
        for rel in tracked:
            full = ROOT / rel
            if not full.exists():
                continue
            first = full.read_bytes()[:7]
            if first != b"version":
                # Not an LFS pointer; could be a small text file or mis-tracked binary.
                missing_lfs.append(rel)
        if missing_lfs:
            print("::error::Tracked binary files are not stored as LFS pointers:")
            for f in missing_lfs:
                print(f"  - {f}")
            return 1
        print(f"[OK] CI LFS pointer check passed for {len(touched_binaries)} binary file(s)")
        return 0

    # Local mode: ensure current user holds the lock.
    locks_raw = _git(["lfs", "locks"])
    locked_by_me: set[str] = set()
    for line in locks_raw.splitlines():
        # Format: <path>	<id> [<user>] or similar depending on git-lfs version.
        if "\t" in line:
            locked_path = line.split("\t")[0].strip()
            locked_by_me.add(locked_path.replace("\\", "/"))

    failures: list[str] = []
    for path in touched_binaries:
        rel = path.relative_to(ROOT).as_posix()
        if rel not in locked_by_me:
            failures.append(rel)

    if failures:
        print("::error::You modified lockable binary files without holding the LFS lock:")
        for f in failures:
            print(f"  - {f}")
        print("\nRun:  git lfs lock <path>")
        return 1

    print(f"[OK] LFS lock guard passed for {len(touched_binaries)} binary file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
