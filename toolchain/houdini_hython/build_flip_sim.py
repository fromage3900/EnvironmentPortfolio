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
    print(f"[build_flip_sim] CONTENT GATE PASS: {len(cached)} frames all >= {min_bytes} B", flush=True)
    return 0


def load_hip_and_find_output(hip_path: str, out_hint: str = "") -> hou.Node:
    """Load a UI-authored HIP and locate the sim's output node.

    Search order: exact out_hint path -> node named OUT_flip_study -> the display
    node of any /obj geometry containing a flip/fluid sim.
    """
    hou.hipFile.load(hip_path, suppress_save_prompt=True, ignore_load_warnings=True)
    print(f"[build_flip_sim] loaded HIP: {hip_path}", flush=True)

    if out_hint:
        node = hou.node(out_hint)
        if node is None:
            raise SystemExit(f"[build_flip_sim] --out-node {out_hint} not found in HIP")
        return node

    node = hou.node("/obj/flip_study/OUT_flip_study")
    if node is not None:
        return node

    for geo in hou.node("/obj").children():
        if not isinstance(geo, hou.ObjNode):
            continue
        for child in geo.children():
            name = child.name().lower()
            if name.startswith("out_") or "flip" in name or "fluid" in name:
                if child.isDisplayFlagSet():
                    return child
    # last resort: first geo's display node
    for geo in hou.node("/obj").children():
        if isinstance(geo, hou.ObjNode):
            disp = geo.displayNode()
            if disp is not None:
                print(f"[build_flip_sim] falling back to display node {disp.path()}", flush=True)
                return disp
    raise SystemExit("[build_flip_sim] no output node found in HIP — pass --out-node /obj/geo/node")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", default="1-120")
    parser.add_argument("--out", default="exports/flip_study")
    parser.add_argument("--res", type=int, default=0, help="best-effort sim resolution override (0 = defaults)")
    parser.add_argument("--hip", default="",
                        help="UI-authored HIP to load instead of building a network "
                             "(the flipcontainer macro is inert headless — see "
                             "FINDINGS_FLIP_HEADLESS_2026-08-31.md and UI_SESSION_GUIDE.md)")
    parser.add_argument("--out-node", default="", dest="out_node",
                        help="explicit SOP path to cache when using --hip")
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start, end = int(start_s), int(end_s or start_s)

    hou.setFps(24)
    if args.hip:
        out = load_hip_and_find_output(args.hip, args.out_node)
    else:
        out = build_network(hou.node("/obj"), res=args.res)
    return cache_output(out, args.out, start, end)


if __name__ == "__main__":
    sys.exit(main())
