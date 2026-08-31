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

import hou  # noqa: F401  (hython provides this)


def build_network(obj: hou.Node) -> hou.Node:
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

    transform = ramp.createOutputNodeAndConnect("xform", "ramp_world")
    transform.parm("ty").set(1.5)

    # FLIP tank source: block of water at ramp base
    tank = geo.createNode("box", node_name="water_source")
    tank.parm("sizex").set(6.0)
    tank.parm("sizey").set(2.0)
    tank.parm("sizez").set(4.0)
    tank.parm("ty").set(-0.5)

    merge = geo.createNode("merge", "sim_inputs")
    merge.setNextInput(transform)
    merge.setNextInput(tank)

    # Auto-generate FLIP network from the merge (tank + colliders workflow)
    shelf = hou.shelves.shelfTool() if hasattr(hou, "shelves") else None
    # Use the "Auto-generate FLIP" equivalent: fluidcontainer via FLIP configure is UI-side;
    # headless-safe: build the container network via the 'flipsolver' HDA directly.
    try:
        flip = geo.createNode("fluidcontainer::2.0", node_name="flip_study_sim")
    except hou.OperationFailed:
        flip = geo.createNode("fluidcontainer", node_name="flip_study_sim")
    flip.setNextInput(merge)
    flip.moveToGoodPosition()

    out = flip.createOutputNodeAndConnect("null", "OUT_flip_study")
    out.setDisplayFlag(True)
    return out


def cache_output(out_node: hou.Node, out_dir: str, start: int, end: int) -> None:
    os.makedirs(out_dir, exist_ok=True)
    rop = out_node.parent().createNode("geometry", "ROP_cache_flip")
    rop.setNextInput(out_node)
    rop.parm("sopoutput").set(os.path.abspath(os.path.join(out_dir, "flip_study.$F4.bgeo.sc")).replace("\\", "/"))
    rop.parm("trange").set(1)  # frame range
    rop.parmTuple("f").set((start, end, 1))
    rop.parm("initsim").set(True)
    rop.render()
    print(f"[build_flip_sim] cached {start}-{end} -> {out_dir}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", default="1-120")
    parser.add_argument("--out", default="exports/flip_study")
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start, end = int(start_s), int(end_s or start_s)

    obj = hou.node("/obj")
    out = build_network(obj)
    hou.setFps(24)
    cache_output(out, args.out, start, end)
    return 0


if __name__ == "__main__":
    sys.exit(main())
