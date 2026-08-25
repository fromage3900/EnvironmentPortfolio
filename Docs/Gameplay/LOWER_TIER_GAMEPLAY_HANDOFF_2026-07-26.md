# Lower-tier gameplay continuation handoff

This is an execution packet for DeepSeek, Cline, LingFlash, or another lower-cost coding agent. Follow it literally. Do not infer a broader redesign.

## Mission

Finish and verify one production loop in UE 5.8:

`QuillScript dialogue -> approved StartBattle(melodia_smoke_encounter) -> JRPG battle with Melusina -> typed Victory/Defeat/Fled -> QuillScript resumes once -> exploration`

The loop must preserve JRPG ownership of battle and saves.

## Project and authorities

- Production project: `C:\EnvironmentPortfolio\BS_GodFile\BS_GodFile.uproject`
- Engine: `C:\Program Files\Epic Games\UE_5.8`
- Compatibility lab: `C:\EnvironmentPortfolio\CompatibilityLabs\QuillScriptUE58`
- JRPG lab: `C:\EnvironmentPortfolio\CompatibilityLabs\TurnBasedJRPGUE58`
- Rollback authority: `C:\EnvironmentPortfolio\CompatibilityLabs\ProductionPreIntegrationBackup_2026-07-26`
- Do not trust the damaged Git object database for rollback.

## Required order

### 1. Confirm baseline before editing

1. Confirm the editor is connected to `BS_GodFile` and UE 5.8.
2. Run `CompileAllBlueprints`.
3. Confirm zero errored Blueprints.
4. Confirm no dirty packages before authoring.
5. Do not save unrelated `MI_SDF_Altar_GoldFiligree` or any existing production map.

If the baseline differs from the status document, stop and report the exact difference.

### 2. Make the C++ boundary runtime-safe

Inspect `Source/BS_GodFile/MelodiaIntegration/MelodiaNarrativeSubsystem.cpp`.

Required change: ensure `Config` resolves to `/Game/MelodiaIntegration/Config/DA_MelodiaIntegrationConfig` during `Initialize` if no explicit reference is assigned. Use a soft path or `ConstructorHelpers`/asset load appropriate to the existing module. Do not expose raw save objects, level paths, classes, controllers, or UObject lookup to QuillScript.

Required save helpers: add project-owned Blueprint-callable functions that copy the typed `FMelodiaNarrativeRecord` to/from the JRPG save object only when called by the JRPG GameInstance save/load flow. These helpers may accept a trusted save object for internal Blueprint wiring; QuillScript must never be able to call them through the notification protocol.

Build the editor target after this change. UHT must pass.

### 3. Create the project-owned Blueprint layer

Duplicate, do not mutate, these template Blueprints:

- `/Game/TurnBasedJRPGTemplate/Blueprints/Controllers/BP_JRPGPlayerController` -> `/Game/MelodiaIntegration/Blueprints/BP_MelodiaJRPGPlayerController`
- `/Game/TurnBasedJRPGTemplate/Blueprints/Controllers/BP_JRPGGameMode` -> `/Game/MelodiaIntegration/Blueprints/BP_MelodiaJRPGGameMode`
- `/Game/TurnBasedJRPGTemplate/Blueprints/Controllers/BP_JRPGGameInstance` -> `/Game/MelodiaIntegration/Blueprints/BP_MelodiaJRPGGameInstance`

Set the duplicated GameMode's PlayerController class to `BP_MelodiaJRPGPlayerController`. Set the duplicated GameInstance as the project-owned game instance only if this can be done without changing existing portfolio maps. Prefer map-local GameMode override for the integration map.

Wire the duplicated GameInstance's existing SaveGame and LoadGame events to the narrative save helpers. Preserve all original JRPG save calls and execution order. Add the narrative copy adjacent to the canonical JRPG save transaction, not as a second save system.

### 4. Create the isolated integration map

Duplicate `/Game/TurnBasedJRPGTemplate/Maps/Gameplay` to `/Game/MelodiaIntegration/Maps/MelodiaIntegrationMap`.

Set only the duplicated map's GameMode/GameInstance overrides. Do not save changes to `Gameplay`, `MainMenu`, `BattleMap`, Melodia portfolio maps, or render scenes.

Ensure the map has a valid exploration player and a deterministic, allowlisted encounter entry point. The encounter must resolve by the ID `melodia_smoke_encounter`; QuillScript must not choose a battle class, enemy class, map path, or save object.

### 5. Import the smoke script under `/Game`

Source: `C:\EnvironmentPortfolio\CompatibilityLabs\QuillScriptUE58\TestScripts\MelodiaQuillSmoke.qsc`

Import/copy it as a QuillScript asset under:

`/Game/MelodiaIntegration/Narrative/MelodiaQuillSmoke`

Do not leave the production script under `/Engine`. Preserve the script source and keep its commands within the stable notification contract. If the script needs a battle command, use the exact stable notification form already implemented by the subsystem:

`melodia:battle:melodia_smoke_encounter`

Do not invent a new command syntax without updating the C++ parser and adding a focused test.

### 6. Wire the authored loop

At the integration map's narrative trigger/interpreter:

1. Start `MelodiaQuillSmoke`.
2. QuillScript sends the battle notification.
3. `UMelodiaNarrativeSubsystem::StartBattle` validates the ID, marks the pending encounter, stops the active interpreter, and emits `OnBattleRequested` once.
4. The project-owned JRPG layer consumes `OnBattleRequested` and invokes the existing JRPG encounter transition. It must use the existing party/turn/save machinery.
5. Register exactly one battle-result listener for the active request.
6. On victory, defeat, or flee, call `CompleteBattle` exactly once with the corresponding `EMelodiaBattleResult`.
7. `CompleteBattle` must clear the pending encounter, broadcast the typed result once, resume the interpreter once, and return to exploration.
8. Apply `melodia_battle_won` and `melodia_smoke_reward` only through allowlisted, deduplicated paths. Do not award on both battle result and dialogue resume.

The existing lab already proved that Melusina appears in battle, attacks, and victory returns to exploration. Reuse that proven presentation setup; do not change locomotion or replace the JRPG skill system.

## Failure handling requirements

The integration must fail safely for:

- unknown encounter ID;
- duplicate battle completion callback;
- duplicate reward or quest completion;
- missing QuillScript runtime/interpreter;
- incompatible narrative record version;
- direct/bare BattleMap launch without a valid JRPG handoff.

Safe failure means no world mutation, no duplicate widget/delegate/reward, and a clear log/delegate signal.

## Verification matrix

Record exact evidence, not “looks good.”

1. Editor: zero Blueprint compile errors.
2. Map: MainMenu, Gameplay, BattleMap still load; integration map initializes.
3. Runtime: Melusina is visible in battle, uses the 4.5-second notify once, damages once, and releases the turn once.
4. Results: victory, defeat, and flee each produce one typed result and return to exploration.
5. Repetition: two sequential battles produce no duplicate callbacks, widgets, delegates, or rewards.
6. Save: save/load preserves party, quests, inventory, removed battles, and narrative flags/checkpoint/consumed IDs.
7. Quill independence: JRPG save loads when no QuillScript is active.
8. Security boundary: unknown notification/identifier produces rejection and no world mutation.
9. Package: Development package launches the integration map and completes the authored loop without editor-only dependencies or missing packages.

## Stop conditions

Stop and report instead of improvising if any of these occur:

- a task requires editing an existing portfolio/Melodia map;
- the JRPG save authority would be replaced by QuillScript;
- a new plugin, Conversation2D, ACFU, or MelodiaCore gameplay authority is proposed;
- a Blueprint edit cannot be verified through compile/runtime evidence;
- a package or asset path differs from this handoff;
- Git is suggested as rollback authority.

## Clarifications for current handoff questions

- The allowlist self-resolution exists in `Source/BS_GodFile/MelodiaIntegration/MelodiaNarrativeSubsystem.cpp` and loads `/Game/MelodiaIntegration/Config/DA_MelodiaIntegrationConfig.DA_MelodiaIntegrationConfig` when `Config` is unset.
- `BP_MelodiaJRPGGameInstance` derives from native `/Script/Engine.GameInstance`.
- The narrative helper is the project-owned `UMelodiaNarrativeSubsystem`. The duplicated GameInstance should call it during the existing JRPG save/load transaction. Do not move canonical authority to MelodiaCore or QuillScript.

## Handoff report format

Return:

1. Files/assets changed, with exact paths.
2. Build result and compiler/UHT errors.
3. Blueprint compile count.
4. Runtime test results for each result path.
5. Save/load test results.
6. Development-package result.
7. Remaining blockers, if any.

Never claim the loop is complete from static graph inspection alone.
