# LiquiGen Spike ("flipfluids") — Benchmark E (Sea Above Hero Liquid/Atmosphere Shot)

**Tool:** JangaFX LiquiGen — **Verdict required:** ADOPT / PARK / REJECT (canonical doc: TEST)

## Setup checklist
- [ ] Record exact LiquiGen version/build in `results.md`
- [ ] Confirm license/trial export restrictions (VDB export availability, resolution caps)
- [ ] GPU budget: single 12 GB card — cap sim resolution to what LiquiGen + UE dev can share

## Benchmark E — Sea Above hero liquid shot
Goal: **5–10 second** visual sketch containing:
1. one **upward/liquid contradiction** (water rising against gravity — Sea Above principle)
2. one **atmosphere response** (mist/spray plume reacting to the impossible motion)

LiquiGen scene: hero pour/lobe of liquid climbing a surface, then breaking into spray. Keep it a
**motion sketchbook** — do not chase final look.

## Production doctrine (from canonical doc — do not violate)
```
LiquiGen     = motion sketchbook (this spike)
Houdini FLIP = deep-control / final offline sim when required  (houdini_hython/)
UE Niagara / VAT / flipbooks / caches = shipping representation
Oceanology   = runtime water authority
```

### Pass condition
A useful hero-liquid motion study built and exported in **under 30–45 minutes**, converted into a
UE-friendly representation (VDB volume -> Niagara Fluids/import, or flipbook/VAT cache).

## Export conventions
- Mesh/VDB sequence: `toolchain/liquigen/exports/sea_above_vdb/` (gitignored)
- Flipbooks for UE: `T_SeaAbove_Liquid_####` — Niagara flipbook renderer
- If VDB: convert via Houdini (`houdini_hython/repack_vdb.py`) to .vdb Niagara can import
- Runtime representation must be Oceanology/Niagara — never LiquiGen runtime

## Result template (fill in `results.md`)
```
Tool: LiquiGen
Version:
Test asset/map: Benchmark E - Sea Above 5-10s shot
Install/setup minutes:
Hands-on minutes:
Comparator: Houdini FLIP sketch + EmberGen atmosphere
What was faster:
What was worse:
Export/runtime dependency:
Stability problems:
Decision: ADOPT / PARK / REJECT
Next action:
```
