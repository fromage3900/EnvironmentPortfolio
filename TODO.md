# Collaborator Environment & Git Source Control — Implementation TODO

## Handoff checkpoint — 2026-08-09

- [x] Identify active nested repositories and keep recovery/temp checkouts out of the commit path.
- [x] Establish isolated commit batches for docs, source/tools, authored content, and VRM4U.
- [x] Add the cross-PC handoff at `BS_GodFile/Docs/Handoffs/PROJECT_HANDOFF_2026-08-09.md`.
- [x] Complete local batch commits and record hashes in the handoff.
- [x] Mirror matching content from `C:\EnvironmentPortfolio` to `G:\EnvironmentPortfolio`.
- [ ] Upload the approved full project archive to Google Drive folder `EnvironmentPortfolio-2026-08-09` using a direct Drive client or authenticated browser; the connector timed out on 500 MiB chunks.
- [ ] Verify the GitHub recovery branch `codex/full-project-snapshot-20260809` after LFS publication; do not force-push.

Status: Local cross-PC handoff is committed; C:→G: refresh and Google Drive archive upload are in progress; remote reconciliation remains pending (2026-08-09)

## Phase 0 — Git Reconciliation (P0)
Live status override (2026-08-09): C: to G: refresh is verified; six Drive handoff documents are
verified; the full Drive archive and GitHub recovery-ref verification remain pending.

- [x] Commit late BS_GodFile source and documentation changes in isolated batches
- [ ] Fetch origin/main
- [ ] Merge/rebase local 4 commits onto origin/main
- [ ] Attempt push (may be network-blocked)

## Workstream A — Git Infrastructure
- [x] A1: Remove broken `my-site-clean` gitlink from index
- [x] A2: Remove broken `_github_deploy` gitlink from index
- [x] A3: Create `BS_GodFile/.githooks/` (pre-commit, pre-push, post-checkout)
- [x] A4: Enable `core.hooksPath`
- [x] A5: Fix `unreal_build.yml` stale G:\ path → C:\EnvironmentPortfolio\

## Workstream B — Collaborator Documentation
- [x] B1: Rewrite `COLLABORATOR_SETUP.md` with Tier 1/2/3 onboarding
- [x] B2: Update `CONTRIBUTING.md` with `collab/[role]/[feature]` naming
- [x] B3: Link asset naming conventions to PIPELINE.md

## Workstream C — Validation & Automation
- [ ] C1: Fix `collaborator_onboarding.sh` path bugs (BS_GodFile/ prefix)
- [ ] C2: Enhance `validate_setup.ps1` — tier detection, Blender 5.1→5.2
- [ ] C3: Create `deploy/recover_orphans.py` scaffold

## Workstream D — Documentation Sync
- [ ] D1: Update `_ROADBLOCKS_2026-07-31.md` — mark git recovered, add 2026-08-05 state
- [ ] D2: Fix root `README.md` mojibake
- [ ] D3: Fix `Docs/QUEUE.md` C9 contradiction
- [ ] D4: Update `_DECISION_LOG.md`

## Workstream E — Website Deploy (separate my-site repo)
- [ ] E1: Add GitHub Pages deploy workflow to `my-site-deploy/` repo
- [ ] E2: Verify Pages config (user confirmation)

## Workstream F — 0.1% Workflow Automation (NEW)
- [x] F1: Create `deploy/verify_critical_workflows.sh` — one-command runner for rare-but-critical gates
- [x] F2: Add git hooks for LFS/size validation (pre-commit)

## Workstream G — Substrate Pipeline Conversion (NEW)
- [ ] G1: Convert newly imported and downloaded JRPG, rhythm, and Cathedral assets to utilize the Substrate pipeline.
