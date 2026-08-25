# SYNC AUDIT — C / F / G EnvironmentPortfolio — 2026-08-24

## Executive Summary
- **C: is primary and authoritative** — newest commit 7122a391 (2026-08-24), 10975 tracked files, 61 dirty, 38.3GB free
- **G: is close ancestor, safely fast-forwardable** — commit 762d8d2f (2026-08-21), 11131 tracked (+158 vs C), diff only 181/337 files
- **F: is stale divergent fork — DO NOT AUTO-SYNC** — commit 089fea71 (2026-07-30) on branch codex/integration-gameplay-loop-20260718, main 521982ff, 13123 tracked (+2150 vs C), diff 5690/7838 vs C (only 5285 common) — 52% overlap, heavily contaminated with ._site_aside_untracked, 86419_Zbrush pack, .ai/.continue configs
- **Top-level Wix site is UNVERSIONED on all drives** — no .git at C/G/F top (only BS_GodFile is git). Risk of total loss.
- **No cloud sync active** for EnvironmentPortfolio — OneDrive running but not syncing these folders, no Syncthing/FreeFileSync detected.
- **F: drive critical** — 28.7GB free (1.5%) same as C was pre-cleanup.

## Git Details

| Location | HEAD | Date | Branch | Tracked | Dirty | Remotes |
|----------|------|------|--------|---------|-------|---------|
| C:\ BS_GodFile | 7122a391 | 2026-08-24 | main | 10975 | 61 | gdrive->G, origin MelodiaMelusinaV2, legacy-melodia |
| G:\ BS_GodFile | 762d8d2f | 2026-08-21 | main | 11131 | ~? (timeout) | origin MelodiaMelusinaV2, legacy-melodia |
| F:\ BS_GodFile | 089fea71 | 2026-07-30 | codex/integration... | 13123 | ? | origin environment-portfolio.git, outer_repo G:/.git |

- C 7122a391 descends from 529967d4 -> 762d8d2f? merge-base check says G NOT ancestor of new 7122a391 — indicates C has rebased or rewritten history since last gdrive push. Need \git fetch gdrive\ + compare.
- C vs G: Only in C 181 (unified SDF masters, MI_Universal_Default etc), Only in G 337 (_Archive/Candidates_Archive etc) — C has pruned archive candidates, G retains them.
- C vs F: Only in C 5690, Only in F 7838 — massive divergence, not a simple ahead/behind.
- F's outer_repo is G:/EnvironmentPortfolio/.git which does not exist as active top-level git (only .git.backup.mirror) — broken.

## File-Level Freshness
- C: 2026-08-24 01:07 Tools\BlenderAddons\melodia_studio\walkable_world.py (today)
- G: 2026-08-24 01:06 Saved\Logs\BS_GodFile.log (today, but only logs)
- F: timeout scanning — but git date 2026-07-30 proves stale.

## Disk Health
- C: 38.3GB free 4.0% — safe for now, will drop 7GB when Intermediate rebuilds
- F: 28.7GB free 1.5% — CRITICAL, contains 1.8TB used (Archive, Backups, EnvironmentPortfolio etc)
- G: 359.7GB free 38.6% — healthy, holds \Archive 16.31GB

## Safe Sync Plan (Requested: check for all synchs first — no destructive sync done yet)

### 1. Backup before any sync
- Archive F:\EnvironmentPortfolio to G:\Archive\F_EnvironmentPortfolio_20260824\ (robocopy /J, verify lengths) — F is 25 days stale and contaminated, preserve before any delete.
- Archive G:\EnvironmentPortfolio\BS_GodFile to G:\Archive\G_BS_GodFile_pre_sync_20260824\ (or ensure gdrive remote is backup).

### 2. Commit dirty on C before push
- C has 61 dirty files (MI_Ornament_GoldTrim, MI_Master_Toon_Landscape..., ABP_Melusina_Current, DT_MelodySlime_Skills.json etc) — stash or commit before pushing to G to avoid losing WIP.
- Command: \git -C C:\EnvironmentPortfolio\BS_GodFile status\ -> review, then \git commit -m "chore(sync): pre-sync checkpoint 2026-08-24"\ or \git stash\.

### 3. Sync C -> G (fast-forward, safe)
- Since C is intended primary, and G diff is small, update G to match C:
  \git -C C:\EnvironmentPortfolio\BS_GodFile fetch gdrive\
  \git -C C:\EnvironmentPortfolio\BS_GodFile push gdrive main\  (will either fast-forward or be rejected if non-fast-forward — then use \--force-with-lease\ only after confirming C is desired).
- Alternative: on G, \git pull\ from C's gdrive remote.

### 4. DO NOT sync F automatically
- F's 7838 unique files and 5690 missing vs C means merging would create massive conflicts and bring back pruned _Archive candidates plus junk like 86419_Zbrush pack.
- After archiving F to G:\Archive, either keep F read-only or delete F:\EnvironmentPortfolio\BS_GodFile\.git to prevent accidental commits, or re-clone F from C:
  \obocopy C:\EnvironmentPortfolio\BS_GodFile F:\EnvironmentPortfolio\BS_GodFile /MIR /XD .git Intermediate DerivedDataCache Saved\  (exclude regenerable).

### 5. Wix top-level versioning
- Top-level EnvironmentPortfolio has no .git on any drive — Wix site (wix/, my-site*, etc) is unversioned and at risk. Recommend \git init\ at C:\EnvironmentPortfolio for Wix, or ensure F's environment-portfolio.git remote is not used.

### 6. F: drive relief
- F: is 98.5% used — move F:\Archive, F:\Backups, F:\C_Drive_Offload to G: or external. Do not use F for new UE backups.

## Commands to Run (Dry-Run First)
\\\powershell
# 1. Dry-run archive F
robocopy F:\EnvironmentPortfolio G:\Archive\F_EnvironmentPortfolio_20260824 /E /J /L /NFL /NDL /XJ
# 2. Check G sync status
git -C C:\EnvironmentPortfolio\BS_GodFile fetch gdrive; git -C C:\EnvironmentPortfolio\BS_GodFile log --oneline --graph --all -10
# 3. Verify C dirty before push
git -C C:\EnvironmentPortfolio\BS_GodFile status --short | Select -First 20
\\\

No destructive sync has been executed in this audit — all findings are read-only.
