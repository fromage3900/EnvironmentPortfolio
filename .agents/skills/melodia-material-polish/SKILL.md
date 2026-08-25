# Skill: Melodia Material System Polish & Organization

Long-term material-system maintenance lane for `BS_GodFile` (UE 5.8, Substrate + Lumen).
Owner: you. Lane class: `asset_qa` / `author`. Never rebuilds masters — organizes, audits,
injects via guarded tools only.

## Authority map

| Layer | Owner | Path |
|---|---|---|
| MPC musical time | `UMelodiaAudioReactivePresentationSubsystem` (only writer) | `Source/BS_GodFile/MelodiaIntegration/MelodiaAudioReactivePresentationSubsystem.cpp:167` |
| MPC asset | `MPC_Melodia_Palette` | `/Game/Melodia/_PROJECT/04_Materials/MPC_Melodia_Palette` |
| NPC twin (Niagara) | same subsystem mirrors every tick | `/Game/EnvSandbox/VFX/MPC/NPC_Melodia_Palette` |
| Toon master | `M_Master_Toon_Universal` | `/Game/EnvSandbox/Materials/Masters/` |
| Water master | `M_Water_Master_Grand_v10` | `/Game/EnvSandbox/Water/v10/` |
| Glam isolation folder | one per beauty pass | `/Game/ZenForestTest_MusicalGlam/` |
| Beat math | `BeatPulse = cos^2(BeatPhase * PI)` — ON beat, derivative 0 at wrap | never re-implement locally |

## Guarded injection workflow (text-injection wiring)

1. **Never mutate a master graph in place.** Duplicate to a spec-driven variant first
   (`Tools/_Archive/T3D_20260818/t3d_material_curve_injector.py --spec ...`) or author
   into an isolated folder (`ZenForestTest_MusicalGlam/`).
2. **Dry-run → apply.** Use the `water_v10_text_injector.py` pattern:
   validate manifest → range-guarded scalars (`ToonLightBands[1,8]`, etc.) →
   `_assert_project_write_path` (`/Game/` only) → apply → save.
3. **Monolith routes for reads:** `blueprint_query get_cdo_properties/get_graph_data`,
   `material_query get_instance_parameters`, `project_query export_asset_text + grep_pattern`.
   NEVER `editor_query run_python` on `Content/TurnBasedJRPGTemplate/Blueprints/Skills/`
   (D_DamageType enum kills editor, PyWrapperTypeRegistry.cpp:2641).
4. **After any param addition:** run organizer (`Content/Python/organize_masters.py`,
   `master_column_scheme.py` Group+SortPriority) then audit
   (`audit_material_parameters.py`, `audit_material_instance_aaa.py`).
5. **Evidence:** write JSON to `Saved/Audit/<lane>.json`; a claim is done only with a ledger row.

## Headless vs editor matrix

| Task | Mode |
|---|---|
| Audit ini/disk alphas | plain `python` — CI safe |
| Author mats/presets/instances | `UnrealEditor-Cmd -ExecutePythonScript -unattended -nullRHI -NOSOUND -DisablePlugins=Monolith`, editor CLOSED |
| MRQ preset creation | Cmd `-nullRHI` OK (`setup_mrq_presets.py` pattern) |
| PNG capture / hero stills | Cmd **without** `-nullRHI` (RHI), sleep 12-15s init + 8s settle |
| PIE smoke | live editor + Monolith :9316 (`pie_smoke_runner.py`) — NOT headless |
| Packaging | `deploy/package_game.ps1` / BuildGraph `RunUAT.bat`, editor closed |

## Long-term organization rules

- One folder per beauty pass; never scatter into `Melodia/_PROJECT`.
- Masters: `EnvSandbox/Materials/Masters/`; functions: `Functions/`; instances under
  `Instances/<Family>/`. Landscape height-blend stays separate.
- Manifest before MRQ/package: `material_family_manifest.py` →
  `Saved/Portfolio/Materials/material_family_manifest.json`.
- Water family loop: manifest → `audit_water_v10_completion.py` →
  `water_v10_gate_audit.py` (disk-level, no editor).
- LFS: `.uasset/.umap/.png/.exr lockable filter=lfs`; `git lfs locks` before editing umaps.
- Bans: no `git clean -fd`, no `git checkout -- .`, no `delete_asset` on uncreated assets,
  no second BPM source, no parallel HUD/combat authority.
