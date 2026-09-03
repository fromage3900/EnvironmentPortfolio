# Changelog

All notable changes to the Melodia live-ops pipeline are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitLab CI/CD mirror (`.gitlab-ci.yml`) with jobs for live-ops validation, LFS audit, secret scanning, and manual release preparation.
- `tools/git_mirror.py` — safe two-remote mirror helper for GitHub + GitLab with divergence checks.
- `.gitlab/merge_request_templates/default.md` — MR template aligned with Conventional Commits and live-ops impact tags.
- `scripts/git_runner.py` — centralized git utility with explicit error propagation for the daemon and release tools.
- `tools/start_overnight.ps1` / `tools/start_overnight.cmd` — one-launch overnight starters that probe Ollama and pull the recommended fleet before running the daemon.
- `tests/test_git_runner.py` and `tests/test_overnight_daemon.py` covering git-runtime state and model tier defaults.

### Changed
- `scripts/overnight_daemon.py` model tiers now default to the 2026-09-01 recommended fleet (`granite4.2:3b`, `granite4.2:8b`, `muse-glimmer:30b`) and no longer fall back to `qwen3-coder:30b`, which hangs on 12 GB VRAM.
- `tools/bootstrap_llamacpp_stack.cmd` replaced the hardcoded GGUF/llama-cpp-python path with Ollama health checks and `tools/pull_fleet.py`.
- `tools/run_first_overnight_pass.ps1` now waits for `granite4.2:3b` / `granite4.2:8b` instead of the problematic `qwen3-coder:30b`.
- `tools/bump_version.py` now uses `scripts/git_runner.py`, checks dirty state, and aborts on git errors before committing.
- `tools/git_lfs_guard.py` now verifies `git` is on PATH and the repo is valid before scanning.
- `package.json` scripts updated to remove duplicate `overnight` key and add `models:pull`, `models:worker`, `models:reasoner`, `git:mirror:*`, and `overnight:start` helpers.

### Fixed
- Duplicate `"overnight"` key in `package.json` (JSON is now valid).
- Runtime git errors in `scripts/overnight_daemon.py` are now surfaced in the `git_health` health check and propagated through the `git` lane.
- `tools/smoke_models.py` now tests the 2026-09-01 recommended fleet with a 45 s per-model timeout instead of targeting `qwen3-coder:30b` with a 900 s timeout.

## [0.2.0] - 2026-08-27

### Added
- Elite gacha live-ops CI/CD pipeline (`liveops-ci.yml`, `lfs-guard.yml`, `security.yml`).
- Automated 6-week release and hotfix branching workflows (`liveops-release.yml`, `liveops-hotfix.yml`).
- Gacha/economy JSON validators with schema and pity-math checks.
- Feature-flag validator for runtime gating.
- LFS lock guard for binary assets.
- CODEOWNERS, PR/issue templates, pre-commit hooks, and Conventional Commit enforcement.
- Initial live-ops config samples: `feature_flags.json`, `economy.json`, `banners/banner_001.json`.
- Root AI instruction files: `AGENTS.md`, `GEMINI.md`.
- `CONTACT_SHEET.md`, `MIDI_VERIFICATION_REPORT.md`, and `Docs/HERMES_GATEWAY_FIX_2026-08-27.md`.
- TouchDesigner `grandmaster_melodia` project — full TDN network export, Python scripts, and Escher Gallery renders.
- `_TouchDesigner/TP_Melusina_Profile_Spec.json` and `_TouchDesigner/deploy/osc_routing.json`.
- `obs_osc_bridge.py` — OBS Studio OSC bridge for live performance control.
- `scripts/AutoOffload-GoogleDrive.ps1` — automated disk-space watermark monitor and Google Drive offload engine.
- `tools/rclone.exe` — rclone binary (tracked via Git LFS) for cloud transfer operations.
- `.embody/project.json` — Embody externalization project config.
- LFS tracking rules for `*.tdc` (TouchDesigner cache) and `tools/rclone.exe`.
- `main` branch published to `origin`; `backup/pre-split-20260825` archived to remote.
- `origin/HEAD` corrected to point to `main`.

### Changed
- GitHub Pages deployment now builds via Vite and deploys `my-site-deploy/` artifact.
- `.gitattributes` extended with Embody/Envoy LF normalization rules (`*.py`, `*.md`, `*.tdn`, `*.json`, `*.tsv`, `*.xml`, `*.toe`, `*.tox`).
- `.gitignore` extended: scratch request files (`req*.json`, `test_*.json`, `test_output.fbx`), `_github_deploy/` output.
- `TODO.md` deduplicated — removed duplicate P0 and Workstreams A–D block; D4 item preserved.
- `README.md` updated with Helix Core/Perforce hybrid source control status.


## [0.1.0] - 2026-08-24

### Added
- Initial monorepo source-control foundation.
- Portfolio site Vite build pipeline.
- Unreal Engine 5.8 BuildGraph, static gates, and release-tag workflows (in `BS_GodFile/`).
