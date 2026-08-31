# Houdini 22 — hython headless integration

Headless Houdini tooling for the LiquiGen ("flipfluids") and IlluGen spikes. `hython` is Houdini's
Python interpreter; these scripts build and cook networks without opening the UI.

## Locate hython
Typical: `C:\Program Files\Side Effects Software\Houdini 22.x.yyy\bin\hython.exe`.
Run `where_hython.cmd` to auto-detect and print the path.

## Scripts

### `build_flip_sim.py` — FLIP liquid motion study (feeds LiquiGen Benchmark E)
```cmd
hython.exe build_flip_sim.py --frames 1-120 --res 96 --out exports\flip_study\bgeo
```
Builds a FLIP tank with a slanted "climbing ramp" collider (sketches the upward/contradiction
motion), using the SOP-level `flipcontainer` macro (H19.5+/22) with the ramp wired into its
collider input. Caches a `bgeo.sc` surface + velocity sequence for LiquiGen reference and
UE/Niagara conversion. `--res` does a best-effort particle-separation/resolution override.

### `export_molt_masks.py` — anatomy masks + flow reference (feeds IlluGen Benchmark A)
```cmd
hython.exe export_molt_masks.py --frames 1-24 --out exports\molt_flow_reference
```
Generates the shared procedural field (molt-age scalar + secretion flow/vector attribute) from a
single grid, baked as attribute-carrying `.bgeo.sc` frames — the "one shared procedural rule"
that feeds both IlluGen textures and (Niagara) flow data. (Optional camera-driven COP image
bake of the scalar field is done in-session; see `toolchain/illugen/`.)

### `repack_vdb.py` — convert LiquiGen/Houdini caches to Niagara-importable .vdb
```cmd
hython.exe repack_vdb.py --src exports\flip_study\bgeo --dst exports\sea_above_vdb
```
Loads each `flip_study.$F4.bgeo.sc` frame, converts to SDF via `vdbfrompolygons`, and writes a
single `.vdb` per frame for UE5.8 Niagara volume-flipbook import.

## Rules (canonical doc)
- Houdini is **authoritative** for physical/procedural fields; IlluGen/LiquiGen are sketch layers.
- Everything here is authoring-only; outputs are baked UE-native representations.
- Keep sim caches under `exports/` (gitignored); commit only the scripts + settings.
