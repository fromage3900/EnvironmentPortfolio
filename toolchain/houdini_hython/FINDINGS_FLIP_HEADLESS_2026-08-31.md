# FINDINGS — headless FLIP sim produces empty fluid (2026-08-31)

**Context:** Today's planned test was "repack VDB → UE import" for the Sea Above
volume-flipbook. Validation *before* import caught a showstopper: the entire cached
sim chain contains **no fluid**.

## What we found

| Stage | Result | Verdict |
|---|---|---|
| `prod_flip/flip_study.*.bgeo.sc` (24 frames) | 7 VDB prims/frame, **zero fluid**, sizes ~4.5 KB, byte-similar across frames | ❌ no sim content |
| `prod_vdb/sea_above_vdb.*.vdb` (24 frames) | valid SDF grids but **809 bytes each = no active voxels** | ❌ empty volumes |
| `repack_vdb.py` plumbing | works correctly (bgeo → SDF → .vdb) | ✅ plumbing OK |
| UE import path (`README_SeaAbove.md`) | untested — **correctly blocked** by empty data | ⛔ do not import |

**Root cause:** the SOP `flipcontainer` macro's internal simulation network is only
built interactively by the UI. When created via `createNode()` in headless hython it
generates only inert scaffolding grids (`source`, `sink`, `vel`, `pressure`, …) — no
fluid ever cooks, regardless of frame. The earlier "validate and repair" pass
(6b7194f) verified frame ranges and ROP wiring but not **sim content**, because
"ROP completed" ≠ "fluid exists".

## What works (verified today)

- `particlefluidtank` SOP headless: real fill, **4,591 particles** at defaults. ✅
- SOP `flipsolver` explicit wiring headless: got past domain validation with
  - input 0 = `merge(particlefluidtank, surface VDB named "surface", vel VDB named "vel")`
  - input 1 = domain box + detail attrs `gridscale`, `particlesep` (from tank),
    **plus string-array detail attr `volumenames` = ["surface","vel","collision"]**
    (required by the solver's `error1/enable2` validation)
  - input 2 = collision VDB named "collision"
- The dopnet cooks at frame 1 but frame 24+ fails inside `FLIP_DATA` →
  `SETTINGS/rest_dual` attrib lookup — the internal macro chain still references
  flipcontainer-only settings. **Remaining gap.**

## Recommended fix path (next session)

1. **Preferred:** build the sim in the Houdini UI once, save the HIP or a `.hda`,
   and drive it headless via `hou.hipFile.load()` + ROP. This matches the canonical
   doctrine (Houdini = authoritative authoring) and stops fighting macro internals.
2. **Alternative (pure headless):** replace the SOP-macro approach with a DOP-level
   `dopnet` (`flipobject` + `flipsolver` + `flipsource` DOPs), which is fully
   scriptable and documented.
3. **Add a content gate** to `cache_output()` / `lane_hython` (see daemon): after
   caching, re-open one frame and assert `points > N` or VDB active-voxel count > 0.
   "ROP exit 0" must never again count as a pass. Wire this into the daemon
   `hython` lane ledger entry as `"content_ok": bool`.

## Test artifacts

- `probe_flip.py` (this dir) — full diagnostic/repro chain, kept for the fix session.
- Daemon health lane re-verified green today: `ok=true`, ping on `granite4.2:3b`,
  all 5 models detected.

## Nikk-lens note (portfolio view)

The Infinity-Nikki-lens goal for Sea Above is a **reactive hero liquid** moment
(audio-reactive plume response, rhythm-hit splashes using the existing grade-halo /
sparkle alpha library). None of that is buildable until the sim emits real fluid —
so today's blocker removal is the gate for the whole portfolio piece.
