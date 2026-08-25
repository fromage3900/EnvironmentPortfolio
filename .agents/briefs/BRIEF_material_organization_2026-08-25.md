# Subagent Brief — Material System Long-Term Organization

Lane: `audit` then `author`. Read-only first pass; writes only metadata (Groups, SortPriority)
and manifests. Never touches graph topology.

## Deliverables
1. `Saved/Audit/material_org_baseline.json` — census of every master/function/instance under:
   - `/Game/EnvSandbox/Materials/{Masters,Functions,Instances,Landscape,Niagara}`
   - `/Game/Melodia/_PROJECT/04_Materials/**`
   - `/Game/ZenForestTest_MusicalGlam/**` (if present)
   Fields per asset: path, class, parent (MI→Master), param count, Group assignments, drift flags.
2. **Duplicate/orphan report** — flag:
   - duplicate short names (`M_Master_Toon_Universal_Inst` exists in 2 locations today),
   - MIs with missing parents,
   - masters with zero instances (candidate archive),
   - params outside any Group (`organize_masters.py` misses).
3. **Target taxonomy** — propose folder+Group scheme consistent with
   `master_column_scheme.py`; keep `ZenForestTest_MusicalGlam` isolated as glam-pass pattern.
4. **Migration script skeleton** — `organize_material_folders_v2.py` following
   `organize_masters.py` template: metadata-only, dry-run default, per-batch save with
   `list_dirty_packages` verification.

## Sources
- `BS_GodFile/Content/Python/master_column_scheme.py` (single source of truth for Groups)
- `BS_GodFile/Content/Python/organize_masters.py`, `organize_universal_instances.py`
- `BS_GodFile/Content/Python/material_family_manifest.py` / `_full.py`
- `BS_GodFile/Content/Python/audit_material_parameters.py`, `audit_mi_master_integrity_disk.py`
- Known drift: `PROJECT.md static_gates FAIL` — `M_Master_Simple_Universal` 25→26 nodes,
  `M_Master_Toon_Landscape_HeightBlend` 290→304 nodes (see `Docs/ORCHESTRA_CONVERGENCE_2026-08-20.md`)

## Constraints
- P0 guardrail: no new subsystems; this lane is organization only.
- Editor work serializes through one holder; if editor closed, deliver disk-level census +
  migration skeleton and mark live verification HOLD.
- Baselines that drifted must be reconciled via the existing gate, never waived
  (P0 plan Step 1).
