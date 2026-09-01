# Houdini UI Session Guide — author the Sea Above FLIP tank (one-time, ~10 min)

**Why a UI session:** the `flipcontainer` macro only builds its simulation network
interactively; headless `createNode()` yields an inert scaffold (full diagnosis in
`FINDINGS_FLIP_HEADLESS_2026-08-31.md`). Everything downstream (content gate,
`repack_vdb.py`, `oneclick_seaabove.py`) is already built and waiting for real frames.

## In Houdini (any 22.x)

1. **New scene**, `File > Save As...` → `toolchain/houdini_hython/sea_above_tank.hip`
2. In `/obj`, `Tab > Fluid Tanks` shelf tab → click **Tank Fill** (creates a
   `particlefluidtank` SOP inside a geo, or place a `particlefluidtank` node).
   Set parms:
   - **Size** x=8 y=4 z=6, **Water Level** 0.5
3. `Tab > Particle Fluids` → **Emit from Surface/Geometry** or drag a **FLIP Solver**
   (SOP-level `flipsolver`) into the same geo and wire: `tank -> flipsolver` input 1.
4. Collider — the climbing ramp:
   - `box` (sizex=8, sizey=0.6, sizez=3, ty=1.0, rz=-28), then `transform` ty=1.5
   - `vdbfrompolygons` (distancename `collision`, voxelsize 0.1) → `name` = `collision`
   - wire into the **flipsolver's collision input** (input 2 on the shelf network,
     or use a `flipcollide`/static-object path inside the solver if prompted)
5. Press **Play** on the playbar ~48 frames. You should SEE water sloshing up the
   ramp. If not, don't save — fix the wiring in the UI first.
6. Add a `null` named exactly **`OUT_flip_study`** at the end, display flag ON.
7. **Save** the HIP.

## Then hand off to the (already-built) headless chain

```cmd
hython build_flip_sim.py --hip sea_above_tank.hip --frames 1-48 --out exports\sea_above_vdb
```

The script loads the HIP, finds `OUT_flip_study`, caches via ROP, and enforces the
**content gate** (fails loudly if frames are still empty — 48 KB threshold).

Then continue with the existing pipeline:

```cmd
hython repack_vdb.py --src exports\flip_study\bgeo --dst exports\sea_above_vdb
```
…and in UE: `oneclick_seaabove.run()` (see `Content/_PROJECT/VFX/README_SeaAbove.md`).

## Notes
- `--res N` is ignored in `--hip` mode; set resolution in the UI (SOLVER tab >
  Particle Separation) before saving.
- The content gate is the source of truth: "sim looks fine in viewport" + gate
  pass = done; gate fail = don't proceed to repack/UE.
