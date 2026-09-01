# Sea Above Niagara Volume Flipbook — Niagara Liquid Volume System

Ingests the Houdini `repack_vdb.py` output (`sea_above_vdb.####.vdb`) as a **volume
flipbook** for the Sea Above upward-liquid Benchmark E study, per the canonical
doctrine:

```
LiquiGen  = motion sketchbook (Houdini flip_study reference here)
Niagara   = shipping volume-flipbook representation
```

## Assets created
- `VFX/Niagara/NS_SeaAbove_VolumeFlipbook` — Niagara System (volume renderer + flipbook)
- `VFX/Materials/M_SeaAbove_VDB_Volume` — Volume material (density from VDB, emissive tint)
- `VFX/Textures/T_SeaAbove_VDB_####` — flipbook texture group (populated by UE import)

## Import wiring (one-click, once real VDBs exist)

> Prereq: the sim must pass the **content gate** (`build_flip_sim.py` / `lane_hython`
> now fail loudly on empty fluid — see
> `toolchain/houdini_hython/FINDINGS_FLIP_HEADLESS_2026-08-31.md`).

Run `toolchain/ue/oneclick_seaabove.py` inside the UE Editor Python console:

```py
import sys; sys.path.append(r"C:\EnvironmentPortfolio\toolchain\ue")
import oneclick_seaabove
oneclick_seaabove.run()   # edit VDB_SOURCE at the top if needed
```

It does, in order:
1. **Imports** `exports/sea_above_vdb/*.vdb` as `T_SeaAbove_VDB` (tries the
   OpenVDB/VolumeTexture factories; falls back to the manual import below if the
   build has none).
2. **Builds** `M_SeaAbove_VDB_Volume` (Domain=Volume, VT RGB→Emissive, R→Opacity).
3. **Creates** the `NS_SeaAbove_VolumeFlipbook` skeleton and logs the 2-minute
   manual Niagara wiring checklist (emitter graphs aren't scriptable in 5.8).

### Manual fallback (only if no VDB factory in the build)
1. **File → Import → Volume Sequence** on `exports/sea_above_vdb/sea_above_vdb.####.vdb`:
   - **Volume Format**: OpenVDB · **Import Type**: Volume Flipbook
   - **Asset Name**: `T_SeaAbove_VDB` · **Texture Group**: `VFX` (sRGB off, no mips)
2. Re-run `oneclick_seaabove.run()` — it will reuse the imported texture.

## Assets created
- `VFX/Niagara/NS_SeaAbove_VolumeFlipbook` — Niagara System (volume renderer + flipbook)
- `VFX/Materials/M_SeaAbove_VDB_Volume` — Volume material (density from VDB, emissive tint)
- `VFX/Textures/T_SeaAbove_VDB` — flipbook texture (populated by the UE import)

### Audio-reactive hook (Nikki lens)
`M_SeaAbove_VDB_Volume` exposes an `AudioLevel` scalar (added in step 4 of the
logged checklist) intended to be driven from MetaSounds — plume brightness/mist
responds to the track, matching the rhythm-UI grade-halo language elsewhere in
the portfolio.

This keeps the Sea Above upward-liquid contradiction as a UE-runtime-representable
volume with the atmosphere response baked as temperature channel.