#!/usr/bin/env python
"""Houdini hython: build a FLIP liquid motion study (LiquiGen Benchmark E reference).

Builds a FLIP tank with a "climbing ramp" collider that sketches the Sea Above
upward/liquid-contradiction motion, then caches bgeo.sc surfaces + VDB volumes.

Usage (headless):
    hython.exe build_flip_sim.py --frames 1-120 --out exports/flip_study

Authoring-only. Outputs under toolchain/houdini_hython/exports/ (gitignored).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import hou  # noqa: F401  (hython provides this)

import sys as _sys
if _sys.argv and any(a == "--list-flip-types" for a in _sys.argv):
    cat = hou.nodeType(hou.sopNodeTypeCategory(), "box").category()
    names = sorted(cat.nodeTypes().keys())
    print([n for n in names if "flip" in n or "fluid" in n])
    sys.exit(0)



def build_network(obj: hou.Node, res: int = 0) -> hou.Node:
    """Create /obj/flip_study geometry network: tank + ramp + FLIP sim + output cache."""
    geo = obj.createNode("geo", node_name="flip_study")
    geo.moveToGoodPosition()

    # Upward-contradiction ramp: liquid climbs a slanted surface
    ramp = geo.createNode("box", node_name="climbing_ramp")
    ramp.parm("sizex").set(8.0)
    ramp.parm("sizey").set(0.6)
    ramp.parm("sizez").set(3.0)
    ramp.parm("tx").set(0.0)
    ramp.parm("ty").set(1.0)
    ramp.parm("rz").set(-28.0)  # slanted so flow must climb

    transform = geo.createNode("xform", "ramp_world")
    transform.setInput(0, ramp)
    transform.parm("ty").set(1.5)

    # SOP-level FLIP workflow (H19.5+/22): flipcontainer handles source+solver wiring
    # and generates its own fluid block; the ramp comes in as a collider on input 1.
    flip = geo.createNode("flipcontainer", node_name="flip_study_sim")
    flip.setInput(0, transform)
    flip.moveToGoodPosition()

    out = geo.createNode("null", "OUT_flip_study")
    out.setInput(0, flip)
    out.setDisplayFlag(True)
    if res:
        # Best-effort resolution override across known parm names (container/solver variants)
        for node in (flip,):
            for child in (node, *node.children()):
                for parm in ("resolution", "res", "gridres", "divsize", "particlesep"):
                    p = child.parm(parm)
                    if p is not None:
                        try:
                            p.set(round(4.0 / res, 4) if parm == "particlesep" else res)
                        except Exception:
                            pass
        print(f"[build_flip_sim] resolution override -> {res}", flush=True)
    return out


def cache_output(out_node: hou.Node, out_dir: str, start: int, end: int) -> None:
    os.makedirs(out_dir, exist_ok=True)
    rop_parent = hou.node("/out") or out_node.parent()
    rop = rop_parent.createNode("geometry", "ROP_cache_flip")
    try:
        rop.setNextInput(out_node)
    except Exception:
        pass
    try:
        rop.parm("soppath").set(out_node.path())
    except Exception:
        pass
    rop.parm("sopoutput").set(os.path.abspath(os.path.join(out_dir, "flip_study.$F4.bgeo.sc")).replace("\\", "/"))
    rop.parm("initsim").set(True)
    rop.parm("trange").set(1)
    ft = rop.parmTuple("f")
    if ft is not None:
        ft.deleteAllKeyframes()
        try:
            ft.setExpression("")
        except Exception:
            pass
        ft.set((start, end, 1))
    rop.render()
    print(f"[build_flip_sim] cached {start}-{end} -> {out_dir}", flush=True)
    # Content gate (2026-08-31): ROP exit 0 is NOT a pass. Empty-fluid frames are
    # ~1-10 KB (see FINDINGS_FLIP_HEADLESS_2026-08-31.md); real fluid is far larger.
    cached = sorted(Path(out_dir).glob("*.bgeo.sc"))
    min_bytes = 48000
    small = [f for f in cached if f.stat().st_size < min_bytes]
    if small:
        print(f"[build_flip_sim] CONTENT GATE FAIL: {len(small)}/{len(cached)} frames "
              f"under {min_bytes} B — sim produced no fluid. The flipcontainer macro's "
              f"sim network is UI-only; author the sim in the UI (HIP/HDA) or use a "
              f"full source contract. See FINDINGS_FLIP_HEADLESS_2026-08-31.md.",
              flush=True)
        return 1  # non-zero so callers/lanes treat this as a failure


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", default="1-120")
    parser.add_argument("--out", default="exports/flip_study")
    parser.add_argument("--res", type=int, default=0, help="best-effort sim resolution override (0 = defaults)")
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start, end = int(start_s), int(end_s or start_s)

    obj = hou.node("/obj")
    hou.setFps(24)
    out = build_network(obj, res=args.res)
    return cache_output(out, args.out, start, end)


if __name__ == "__main__":
    sys.exit(main())
