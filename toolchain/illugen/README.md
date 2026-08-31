# IlluGen Spike — Benchmark A (P2 Molt Material Family)

**Tool:** JangaFX IlluGen — **Verdict required:** ADOPT / PARK / REJECT (canonical doc: TEST NOW, no shipping dependency until proven)

## Setup checklist
- [ ] Record exact IlluGen version/build in `results.md` before first use
- [ ] Confirm license/trial export restrictions (resolution caps, watermarks) before committing outputs
- [ ] Create output dirs: `toolchain/illugen/exports/` (gitignored for heavy assets)

## Benchmark A — P2 Molt Material Family
One procedural molt fragment, matched states, driven from the Houdini anatomy mask:

```
Dormant -> Hydrated -> Reactive -> Crystallized -> Spent
```

### IlluGen target outputs (per state)
1. **Basecolor/flipbook sequence** — pigment migration breakup (Hydrated -> Reactive)
2. **Flow map** — secretion direction field (use Houdini-exported vector mask as reference frame, `houdini_hython/exports/molt_flow_reference/`)
3. **Distortion map** — crystallization surface breakup (Reactive -> Crystallized)
4. **Emissive mask family** — spent-glow decay (Spent)

### Pass condition
Production-useful animated flow/distortion texture family built **faster** than the equivalent
Houdini-COP/Substance workflow, exporting clean, UE-importable assets (PNG/TGA flipbooks + flowmaps).

### Reject if
- Asset round-tripping is awkward
- Animated outputs become an opaque runtime dependency
- It duplicates Substance/Houdini work without a meaningful speedup

## UE import conventions
- Flipbooks: `T_Molt_<state>_<map>` suffix, `FLIP_Molt_<state>` flipbook material, sRGB off for masks/flow
- Flow maps: UnpackNormal in UE material; store magnitude in alpha
- All outputs authoring-only/baked; no runtime IlluGen dependency

## Result template (fill in `results.md`)
```
Tool: IlluGen
Version:
Test asset/map: Benchmark A - P2 Molt fragment
Install/setup minutes:
Hands-on minutes:
Comparator: Houdini COP + Substance equivalent
What was faster:
What was worse:
Export/runtime dependency:
Stability problems:
Decision: ADOPT / PARK / REJECT
Next action:
```
