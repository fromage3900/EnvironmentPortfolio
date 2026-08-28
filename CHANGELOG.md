# Changelog

All notable changes to the Melodia live-ops pipeline are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
