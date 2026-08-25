# Core loop handoff — Qwen / DeepSeek

## Current verified state

- Project: `C:\EnvironmentPortfolio\BS_GodFile` (UE 5.8).
- Native runtime and editor targets compile successfully.
- QuillScript is installed under `Plugins/QuillScript`.
- Imported script: `/Game/MelodiaIntegration/Narrative/MelodiaQuillSmoke`.
- Allowlist: `/Game/MelodiaIntegration/Config/DA_MelodiaIntegrationConfig`.
- Production GameInstance: `/Game/MelodiaIntegration/Blueprints/BP_MelodiaJRPGGameInstance`.
- Integration map: `/Game/MelodiaIntegration/Maps/MelodiaIntegrationMap`.
- Integration GameMode: `/Game/MelodiaIntegration/Blueprints/BP_MelodiaJRPGGameMode`.
- Canonical save object: `/Game/TurnBasedJRPGTemplate/Blueprints/Controllers/BP_JRPGSaveGame`.

## Save/load work completed

`BP_MelodiaJRPGGameInstance` now routes its existing canonical transaction through:

1. Existing save flow → `UMelodiaNarrativeSubsystem::SyncNarrativeRecordToSave` → existing `SaveGameToSlot`.
2. Existing load flow → `UMelodiaNarrativeSubsystem::RestoreNarrativeRecordFromSave` → existing JRPG load chain.

The Blueprint compiles with `0` errors and `0` warnings. Do not create another save slot or replace the JRPG save owner.

## Stable native contract

- `GetMelodiaNarrativeSubsystem(WorldContextObject)`
- `StartBattle(EncounterId)`
- `CompleteBattle(EMelodiaBattleResult)`
- `OnBattleRequested(FName EncounterId)`
- `OnBattleCompleted(FName EncounterId, EMelodiaBattleResult Result)`

Allowlisted test encounter: `melodia_smoke_encounter`.

## Remaining core-loop task

Bind exactly one `OnBattleRequested` listener in the project-owned GameInstance or integration controller. The listener must route the allowlisted ID to the existing JRPG battle-start path. The narrative subsystem must remain unaware of battle classes, maps, enemy classes, or save objects beyond its typed adapter contract.

On battle completion, call `CompleteBattle` exactly once for victory, defeat, or flee. Do not award rewards in QuillScript. QuillScript resumes through the subsystem after the typed result.

## Suggested minimal orchestration

`Melusina bed interaction → Start QuillScript smoke asset → notification battle intent → allowlisted JRPG encounter → existing JRPG battle → typed result → CompleteBattle → Quill resume → dreamstate exploration`

Use existing JRPG battle transition/custom events rather than authoring a second battle controller. Preserve the working original JRPG player controller until the duplicated controller's type mismatch is repaired.

## Relevant presentation assets

- Player: `/Game/Melodia/Characters/Melusina/BP_Melusina`
- JRPG presentation: `/Game/Experiments/MelodiaJRPG/BP_MelusinaSwordsman_Presentation`
- Enemy base: `/Game/Melodia/Enemies/BP_MelodiaEnemyBase`
- Dreamstate map: `/Game/Melodia/Levels/Opening/L_Melodia_Dreamstate`
- Bed meshes: `/Game/Melodia/Meshes/Opening/SM_MelusinaBedFrame`, `/Game/Melodia/Meshes/Opening/SM_MelusinaBedBedding`

## Stop conditions

- Do not modify portfolio/render maps.
- Do not reintroduce Conversation2D, ACFU, or MelodiaCore save ownership.
- Do not create a second save slot.
- Reject unknown encounter IDs without world mutation.
- If a Blueprint edit produces a compile error, revert that edit and report the exact node/path.
