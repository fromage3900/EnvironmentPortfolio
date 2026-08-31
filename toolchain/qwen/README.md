# Qwen — Toolchain Spike Briefs

The overnight daemon (`scripts/overnight_daemon.py`, lane **`toolchain`**) uses local Qwen
(Ollama, fallback chain `qwen3-coder:30b → qwen2.5:14b → qwen3:8b`) to author spike material
for the emerging-toolchain evaluations.

- **Canonical research:** `BS_GodFile/Docs/Research/EMERGING_3D_RENDERING_TOOLCHAIN_RESEARCH_2026-08-30.md`
- **Spike plan:** `BS_GodFile/Docs/Research/TOOLCHAIN_INTEGRATION_SPIKE_PLAN_2026-08-31.md`
- **Model output goes to:** `generated/overnight/toolchain/` (daemon safety gate: writes only
  under `generated/overnight/` and `logs/overnight/`)

## Brief rotation
| Brief | Feeds |
| --- | --- |
| `illugen_molt_family` | Benchmark A — IlluGen setup steps for the P2 molt texture family |
| `liquigen_sea_above` | Benchmark E — LiquiGen "flipfluids" upward-liquid motion sketch |
| `hython_flip_pipeline` | `toolchain/houdini_hython/build_flip_sim.py` headless FLIP review |
| `ue_intake_checklist` | UE 5.8 intake of baked flipbooks / flowmaps / VDB→Niagara volumes |

## Run it
```powershell
python scripts\overnight_daemon.py --lanes toolchain --once
# or full pass:
python scripts\overnight_daemon.py --once
```

Human-owned checklists the lane feeds: `toolchain/illugen/`, `toolchain/liquigen/`,
`toolchain/houdini_hython/`. Heavy exports stay in `*/exports/` (gitignored).
