# Subagent Brief — Text-Injection Wiring Deep Study (material systems)

Lane: `deep` research only. NO editor writes. NO `.uasset` mutation.
Goal: produce a canonical wiring playbook so material polish is repeatable long-term.

## Deliverable
Write `Docs/Production/TEXT_INJECTION_WIRING_PLAYBOOK_2026-08-25.md` covering:

1. **Injector inventory** — compare the three families and pick ONE recommended per use case:
   - `Tools/water_v10_text_injector.py` (guarded manifest, dry-run default, range-guarded scalars)
   - `Content/Python/wire_*.py` family (23 files; F11/F12/F13 audio-reactive wiring)
   - `Tools/_Archive/T3D_20260818/t3d_material_curve_injector.py` (dual dispatch MI vs master,
     curve read via `project_query export_asset_text`, batch `apply_toon_profile_spec`)
2. **Decision table** — for each task type (set MI scalar, author master variant, wire MPC param,
   import curve), name the single tool to use and why.
3. **Safety contract** — extract the reusable guards from water_v10_text_injector:
   `_assert_project_write_path`, dry-run default, range validation, manifest validation.
   Specify how new injectors must copy this pattern before merge.
4. **Echo pipeline integration** — where each injector sits in
   author → spec_validate → inject → compile → fingerprint → record stages
   (`Tools/echo_run.py`, `specs/echo_pipeline.json`).
5. **Anti-patterns** — document the known failure modes: silent no-op from wrong pin names,
   spaced-vs-dotted node titles, redirectors from FBX-over-existing-path, in-session delete_asset ghosts.

## Sources (start here)
- `BS_GodFile/Tools/water_v10_text_injector.py` + `water_v10_gate_audit.py`
- `BS_GodFile/Docs/WATER_V10_NATIVE_NIAGARA_SUBSTRATE_TOON_2026-08-09.md:100`
- `BS_GodFile/Content/Python/wire_audio_material_pulsation.py` (F12 canonical math)
- `BS_GodFile/Tools/_Archive/T3D_20260818/t3d_material_curve_injector.py`
- `BS_GodFile/AGENTS.md` § T3D Wiring Pipeline + defect classes
- `BS_GodFile/specs/echo_pipeline.json`, `BS_GodFile/Tools/echo_run.py`

## Constraints
- One editor instance rule applies even for read-only Monolith queries — if port 9316 has a listener,
  serialize through it; otherwise mark findings HOLD, do not launch Cmd.
- Evidence = file paths + line numbers. No prose claims without them.
