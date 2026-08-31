# Houdini 22 — hython headless integration

Headless Houdini tooling for the LiquiGen ("flipfluids") and IlluGen spikes. `hython` is Houdini's
Python interpreter; these scripts build and cook networks without opening the UI.

## Locate hython
Typical: `C:\Program Files\Side Effects Software\Houdini 22.x.yyy\bin\hython.exe`.
Run `where_hython.cmd` to auto-detect and print the path.

## Scripts

### `build_flip_sim.py` — FLIP liquid motion study (feeds LiquiGen Benchmark E)
```cmd
hython.exe build_flip_sim.py --frames 1-120 --out exports\flip_study\bgeo
```
Builds a FLIP tank + source collider (a "climbing ramp" to sketch the upward/contradiction motion),
caches surface bgeo.sc sequences and VDB volumes for LiquiGen reference and UE/Niagara conversion.

### `export_molt_masks.py` — anatomy masks + flow reference (feeds IlluGen Benchmark A)
```cmd
hython.exe export_molt_masks.py --out exports\molt_flow_reference
```
Generates the shared procedural field (molt-age mask + secretion flow/vector field) baked as
COP-ready image sequences — the "one shared procedural rule" that feeds both IlluGen textures and
(Niagara) flow data, per the canonical doctrine.

### `repack_vdb.py` — convert LiquiGen/Houdini caches to Niagara-importable .vdb
```cmd
hython.exe repack_vdb.py --src exports\flip_study\bgeo --dst exports\sea_above_vdb
```

## Rules (canonical doc)
- Houdini is **authoritative** for physical/procedural fields; IlluGen/LiquiGen are sketch layers.
- Everything here is authoring-only; outputs are baked UE-native representations.
- Keep sim caches under `exports/` (gitignored); commit only the scripts + settings.
