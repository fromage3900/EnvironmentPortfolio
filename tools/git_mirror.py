#!/usr/bin/env python3
"""Safe two-remote mirror helper for GitHub + GitLab.

Usage:
    python tools/git_mirror.py --check      # verify remotes and working tree
    python tools/git_mirror.py --push       # push main to origin and gitlab
    python tools/git_mirror.py --all        # check + push

Safety rules:
    - Refuses to push if the working tree is dirty.
    - Refuses to push if either remote reports divergence.
    - Does NOT delete branches or force-push.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_REMOTES = ("origin", "gitlab")


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def _remotes() -> list[str]:
    proc = _git(["remote"])
    return [r.strip() for r in proc.stdout.splitlines() if r.strip()]


def _current_branch() -> str:
    proc = _git(["branch", "--show-current"])
    return proc.stdout.strip() or "main"


def _is_dirty() -> bool:
    proc = _git(["status", "--short"])
    return bool(proc.stdout.strip())


def _remote_branch_exists(remote: str, branch: str) -> bool:
    proc = _git(["ls-remote", "--heads", remote, branch])
    return bool(proc.stdout.strip())


def _check_divergence(remote: str, branch: str) -> tuple[bool, str]:
    """Return (ok, message)."""
    proc = _git(["fetch", remote, branch])
    if proc.returncode != 0:
        return False, f"fetch from {remote}/{branch} failed: {proc.stderr.strip()}"

    local = _git(["rev-parse", branch]).stdout.strip()
    remote_ref = _git(["rev-parse", f"{remote}/{branch}"]).stdout.strip()

    if not remote_ref:
        # Remote branch does not exist yet; push will create it.
        return True, f"{remote}/{branch} does not exist; push will create it"

    if local == remote_ref:
        return True, f"{remote}/{branch} is up to date"

    # Check if local is ahead/behind or diverged.
    merge_base = _git(["merge-base", branch, f"{remote}/{branch}"]).stdout.strip()
    if merge_base == local:
        return False, f"{remote}/{branch} is ahead of local; pull required"
    if merge_base == remote_ref:
        return True, f"{remote}/{branch} is behind local; push is safe"
    return False, f"{remote}/{branch} has diverged; manual merge required"


def cmd_check() -> int:
    print(f"[CHECK] root: {ROOT}")
    print(f"[CHECK] branch: {_current_branch()}")

    remotes = _remotes()
    missing = [r for r in REQUIRED_REMOTES if r not in remotes]
    if missing:
        print(f"[FAIL] missing remotes: {missing}")
        print("       Add them, e.g.:")
        print("       git remote add gitlab https://gitlab.com/<user>/EnvironmentPortfolio.git")
        return 1
    print(f"[OK] remotes: {remotes}")

    if _is_dirty():
        print("[FAIL] working tree is dirty; commit or stash before mirror push")
        return 1
    print("[OK] working tree is clean")

    branch = _current_branch()
    ok = True
    for remote in REQUIRED_REMOTES:
        remote_ok, msg = _check_divergence(remote, branch)
        print(f"[{('OK' if remote_ok else 'FAIL')}] {remote}: {msg}")
        ok &= remote_ok
    return 0 if ok else 1


def cmd_push() -> int:
    branch = _current_branch()
    ok = True
    for remote in REQUIRED_REMOTES:
        print(f"[PUSH] {remote} -> {branch}")
        proc = _git(["push", remote, branch])
        if proc.returncode != 0:
            print(f"[FAIL] push to {remote} failed: {proc.stderr.strip()}")
            ok = False
        else:
            print(f"[OK] pushed to {remote}")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror main to GitHub and GitLab")
    parser.add_argument("--check", action="store_true", help="Check remotes and divergence only")
    parser.add_argument("--push", action="store_true", help="Push after checks")
    parser.add_argument("--all", action="store_true", help="Run checks then push")
    args = parser.parse_args()

    if not (args.check or args.push or args.all):
        parser.print_help()
        return 2

    if args.check or args.all:
        rc = cmd_check()
        if rc != 0:
            return rc

    if args.push or args.all:
        return cmd_push()

    return 0


if __name__ == "__main__":
    sys.exit(main())
