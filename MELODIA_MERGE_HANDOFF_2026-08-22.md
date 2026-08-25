# G: → C: Merge — Paused Handoff (2026-08-22)

## Status: PAUSED — blocked by Unreal Editor (PID 41204) holding file locks

The merge of `gdrive/main` into C: main is **not complete**. It was paused by user request
("Don't close it — pause the merge and I'll resume later"). **Unreal Editor is running and
locks the .uasset files**, so git can neither delete/replace them (merge) nor revert the
partial merge (reset --hard) until it is closed.

## Repository state (verified 02:44 AM)

- Repo: `C:\EnvironmentPortfolio\BS_GodFile`
- HEAD: `c2736d24` (`docs+assets: P0 handoff, pawn deprecation tags, Claireon B1 ratified`)
- Branch: `main` (ahead of `origin/main` by 2)
- Merge: **never committed, no MERGE_HEAD** — the merge failed mid-checkout 3 times
- Working tree: **51 dirty entries** from the last partial merge attempt (cannot be reset
  while Unreal Editor holds `ABP_Melusina_Current.uasset` and the material .uasset files)
- Safety branch: `safety/pre-g-sync-20260821` at `54c4064d` (C:'s pre-merge HEAD)

## Resolved blockers (do NOT redo)

1. **LFS object `1834db4`** (MI_IridescentRock.uasset) — copied from G: to C:, SHA-256 verified.
2. **LFS object `15b1f00`** (Grass.uasset) — present after full LFS store robocopy.
3. **LFS object `72665cb`** (Mud.uasset) — copied from G: to C:, SHA-256 verified.
4. Full LFS object store robocopy: `G:\...\.git\lfs\objects` → `C:\...\.git\lfs\objects` (done).
5. Read-only attribute cleared on all `Content\**\*.uasset` files on C:.
6. NOTE: `git lfs fetch --all` reported **3 corrupt historical objects** on G: (checksum
   mismatches: b5bdxxx, bfecaxx, 6e669xx). These are NOT referenced by gdrive/main's current
   tree, so they do not block the merge. They should be pruned/re-fetched on G: eventually.

## Backups of C:-side files (safe to lose from tree — merge restores G: versions)

Directory: `C:\EnvironmentPortfolio\_merge_backup_20260822\`

- `MelodiaIntegrationConfig.cpp` (38 B)
- `MelodiaNarrativeSaveGame.h` (1072 B)
- `MelodiaWaterAnimNotify.cpp` (3435 B)
- `MelodiaWaterAnimNotify.h` (4480 B)
- `MelodiaWaterInteractionTypes.h` (C:-side local enums — proven real work, not merge damage)

The 12 untracked files that block the merge (setup_convergence_demo.py, CONVERGENCE_STATUS,
CORE_PERSONA_LOOP_HANDOFF, MELODIA_WATERHAIR_PHASE1_SESSION, MODEL_RECOMMENDATIONS_3D_VFX,
MelodiaIntegrationConfig.cpp, MelodiaNarrativeSaveGame.h, MelodiaWaterAnimNotify.*,
MelodiaWaterVFXContract.*, MelodiaWaterVFXContractTests.cpp) were byte-identical to
gdrive/main (8) or backed-up (4). They re-materialize after each failed merge; safe to remove
with `git clean -f <path>` before each merge attempt.

## Resume procedure (when Unreal Editor is closed)

```bash
cd C:\EnvironmentPortfolio\BS_GodFile
# 1. Verify needed LFS objects still present
dir .git\lfs\objects\18\34\1834[……]  REM MI_IridescentRock
dir .git\lfs\objects\15\b1\15b[……]   REM Grass
dir .git\lfs\objects\72\66\72665[……] REM Mud

# 2. Reset partial merge, remove untracked blockers
git reset --hard HEAD
git clean -f Content/Python/setup_convergence_demo.py Docs/CONVERGENCE_STATUS_2026-08-21.md Docs/Handoffs/CORE_PERSONA_LOOP_HANDOFF_2026-08-17.md Docs/MELODIA_WATERHAIR_PHASE1_SESSION_2026-08-20.md Docs/MODEL_RECOMMENDATIONS_3D_VFX_SCREENSHOT_2026-08-20.md Source/BS_GodFile/MelodiaIntegration/MelodiaIntegrationConfig.cpp Source/BS_GodFile/MelodiaIntegration/MelodiaNarrativeSaveGame.h Source/BS_GodFile/MelodiaIntegration/MelodiaWaterAnimNotify.cpp Source/BS_GodFile/MelodiaIntegration/MelodiaWaterAnimNotify.h Source/BS_GodFile/MelodiaIntegration/MelodiaWaterVFXContract.cpp Source/BS_GodFile/MelodiaIntegration/MelodiaWaterVFXContract.h Source/BS_GodFile/MelodiaIntegration/Tests/MelodiaWaterVFXContractTests.cpp

# 3. Merge
git merge gdrive/main -m "merge(gdrive): sync G: main into C:"

# 4. Verify — spot-check the G:-only content
git status                # expect: clean (or only pre-existing untracked)
git log --graph --oneline -3   # expect: merge commit on top of c2736d24
# The merged commits bring over: UIBridgeSubsystem two-writer merge (orchestra gate #3),
# Claude-on-G' gitignore, wardrobe/music bridge setup, UE Python compat fix,
# material archive + SDF duple removal.