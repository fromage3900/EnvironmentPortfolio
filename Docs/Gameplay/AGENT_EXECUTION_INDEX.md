# Gameplay agent execution index

Use this as the low-cost entry point for future agents.

## Read first

1. `C:\EnvironmentPortfolio\BS_GodFile\AGENTS.md`
2. `Docs/Gameplay/JRPG_QUILLSCRIPT_EXECUTION_STATUS_2026-07-26.md`
3. `Docs/Gameplay/LOWER_TIER_GAMEPLAY_HANDOFF_2026-07-26.md`

## Current evidence snapshot

- `BS_GodFile` is the active UE 5.8 project.
- QuillScript is installed under `BS_GodFile/Plugins/QuillScript`.
- The project C++ boundary is present and the runtime config self-resolution is in source.
- The project-owned integration assets exist under `/Game/MelodiaIntegration`.
- The JRPG save Blueprint has the versioned narrative record field.
- The smoke script is now imported and saved as `/Game/MelodiaIntegration/Narrative/MelodiaQuillSmoke` (`QuillscriptAsset`).
- `MelodiaIntegrationMap` now uses `BP_MelodiaJRPGGameMode`; the GameMode is currently pinned to the original working `BP_JRPGPlayerController` because the duplicated controller has two inherited type-mismatch errors. Do not switch it back until that duplicate is repaired.
- `Config/DefaultEngine.ini` now selects `BP_MelodiaJRPGGameInstance` as the project GameInstance, allowing the native narrative subsystem to coexist with the JRPG save transaction in the production project. Existing default/render maps were not changed.
- Native save bridge declarations/implementation now exist in `MelodiaNarrativeSubsystem` (`SyncNarrativeRecordToSave` / `RestoreNarrativeRecordFromSave`). Compile verification is pending because the editor Live Coding session closed and the standalone build is waiting on Unreal's build mutex; do not wire Blueprint nodes until the module build is confirmed.
- The editor currently reports zero dirty packages.
- The complete authored loop remains unverified.

## Do not spend credits on

- broad web research;
- redesigning MelodiaCore;
- ACFU or Conversation2D integration;
- locomotion/UI polish;
- changing portfolio/render maps;
- repeated full rebuilds when a static path or editor compile check is sufficient.

## Handoff output requirement

Every agent must report exact changed paths, compile status, runtime evidence, save/load evidence, and unresolved blockers. “Looks good” is not an acceptance result.
