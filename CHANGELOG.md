# Changelog

All notable changes to the Melodia live-ops pipeline are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Elite gacha live-ops CI/CD pipeline (`liveops-ci.yml`, `lfs-guard.yml`, `security.yml`).
- Automated 6-week release and hotfix branching workflows (`liveops-release.yml`, `liveops-hotfix.yml`).
- Gacha/economy JSON validators with schema and pity-math checks.
- Feature-flag validator for runtime gating.
- LFS lock guard for binary assets.
- CODEOWNERS, PR/issue templates, pre-commit hooks, and Conventional Commit enforcement.
- Initial live-ops config samples: `feature_flags.json`, `economy.json`, `banners/banner_001.json`.

### Changed
- GitHub Pages deployment now builds via Vite and deploys `my-site-deploy/` artifact.

## [0.1.0] - 2026-08-24

### Added
- Initial monorepo source-control foundation.
- Portfolio site Vite build pipeline.
- Unreal Engine 5.8 BuildGraph, static gates, and release-tag workflows (in `BS_GodFile/`).
