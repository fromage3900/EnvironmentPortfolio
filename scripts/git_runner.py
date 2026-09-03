#!/usr/bin/env python3
"""Centralized git runner with explicit error propagation.

No exceptions swallowed; every call returns a structured result.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


def git_run(
    args: list[str],
    cwd: Path | str | None = None,
    timeout: float = 30.0,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run git with explicit error handling."""
    if shutil.which("git") is None:
        raise RuntimeError("git executable not found on PATH")
    cwd = Path(cwd or ".").resolve()
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )
    return proc


def is_git_repo(cwd: Path | str | None = None) -> bool:
    try:
        proc = git_run(["rev-parse", "--is-inside-work-tree"], cwd=cwd, timeout=10)
        return proc.returncode == 0 and proc.stdout.strip() == "true"
    except Exception:
        return False


def git_status(cwd: Path | str | None = None) -> dict[str, Any]:
    """Return structured git status."""
    result: dict[str, Any] = {
        "ok": False,
        "dirty_count": -1,
        "dirty_files": [],
        "error": None,
    }
    if not is_git_repo(cwd):
        result["error"] = "not a git repository"
        return result
    try:
        proc = git_run(["status", "--short"], cwd=cwd, timeout=30)
        if proc.returncode != 0:
            result["error"] = f"git status failed: {proc.stderr.strip()}"
            return result
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        result["ok"] = True
        result["dirty_count"] = len(lines)
        result["dirty_files"] = lines
    except Exception as exc:
        result["error"] = f"git status exception: {exc}"
    return result


def git_log_summary(count: int = 25, cwd: Path | str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": False, "lines": [], "error": None}
    if not is_git_repo(cwd):
        result["error"] = "not a git repository"
        return result
    try:
        proc = git_run(["log", "--oneline", f"-{count}"], cwd=cwd, timeout=30)
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            # An empty repo is not a failure; just no commits yet.
            if "does not have any commits yet" in stderr:
                result["ok"] = True
                return result
            result["error"] = f"git log failed: {stderr}"
            return result
        result["ok"] = True
        result["lines"] = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
    except Exception as exc:
        result["error"] = f"git log exception: {exc}"
    return result


def git_remotes(cwd: Path | str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": False, "remotes": [], "error": None}
    if not is_git_repo(cwd):
        result["error"] = "not a git repository"
        return result
    try:
        proc = git_run(["remote"], cwd=cwd, timeout=10)
        if proc.returncode != 0:
            result["error"] = f"git remote failed: {proc.stderr.strip()}"
            return result
        result["ok"] = True
        result["remotes"] = [r.strip() for r in proc.stdout.splitlines() if r.strip()]
    except Exception as exc:
        result["error"] = f"git remote exception: {exc}"
    return result
