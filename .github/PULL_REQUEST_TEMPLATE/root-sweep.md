Title: Canonicalize project root to C:\EnvironmentPortfolio — safe sweep

Summary

This PR standardizes references to the project root by replacing occurrences of
`G:/EnvironmentPortfolio` (or `G:\EnvironmentPortfolio`) with
`C:/EnvironmentPortfolio` across a whitelisted set of file types.

Files changed
- This PR includes only the changes proposed by `tools/safe_root_sweep.py` when
  run as a dry-run and then applied with `--apply`.

Checklist (reviewers)
- [ ] Verify the JSON report: `tools/g_root_report.json` and `tools/diffs.patch`.
- [ ] Confirm backups exist under `tools/g_root_backups/` and inspect randomly.
- [ ] Run CI / unit tests locally (if available) — ensure no regressions.
- [ ] Confirm no secrets were committed; rotate any keys found in `.mcp.json`.
- [ ] Ensure `deploy/mcp_git.py` and other MCP configs point at the canonical root.
- [ ] Confirm `git status` was clean before apply and only intended files changed.

How to review
1. Run the scan locally:

```bash
python tools/safe_root_sweep.py --old "G:/EnvironmentPortfolio" --new "C:/EnvironmentPortfolio" --extensions ".py,.ps1,.json,.md" --out tools/g_root_report.json --diffs tools/diffs.patch
```

2. Inspect `tools/diffs.patch` for unexpected edits.
3. If OK, apply with:

```bash
python tools/safe_root_sweep.py --old "G:/EnvironmentPortfolio" --new "C:/EnvironmentPortfolio" --extensions ".py,.ps1,.json,.md" --apply --backup-dir tools/g_root_backups
```

4. Verify backups in `tools/g_root_backups/` and run local tests.

Notes
- This sweep intentionally excludes binary assets and large generated manifests.
- If you prefer `G:` as canonical, do not merge this PR; instead prepare the inverse sweep.
