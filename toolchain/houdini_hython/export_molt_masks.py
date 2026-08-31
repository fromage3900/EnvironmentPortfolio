#!/usr/bin/env python
"""Houdini hython: bake molt-age mask + secretion flow/vector reference sequences
(IlluGen Benchmark A input). One shared procedural field -> both IlluGen textures
and Niagara flow data, per the canonical toolchain doctrine.

Usage (headless):
    hython.exe export_molt_masks.py --out exports/molt_flow_reference
"""
from __future__ import annotations

import argparse
import os
import sys

import hou  # noqa: F401


def build_field(obj: hou.Node) -> hou.Node:
    geo = obj.createNode("geo", node_name="molt_flow_field")
    geo.moveToGoodPosition()

    # Molt fragment surface: subdivided grid curved into a fragment-ish form
    grid = geo.createNode("grid", "molt_fragment")
    grid.parm("rows").set(120)
    grid.parm("cols").set(120)
    grid.parm("sizey").set(1.6)  # aspect

    noise = grid.createOutputNodeAndConnect("attribnoise::2.0", "molt_age_noise")
    noise.parm("attribs").set("molt_age")
    noise.parm("elementsize").set(0.45)

    # Flow direction: curl-ish from a second noise -> vector attribute for flow maps
    flow = noise.createOutputNodeAndConnect("attribnoise::2.0", "secretion_flow")
    flow.parm("attribs").set("secretion_flow_dir")
    flow.parm("valuetype").set(1)  # vector
    flow.parm("elementsize").set(0.8)

    out = flow.createOutputNodeAndConnect("null", "OUT_molt_flow_field")
    out.setDisplayFlag(True)
    return out


def bake_cops(out_sop: hou.Node, out_dir: str, start: int, end: int) -> None:
    """Render molt_age + flow direction to image sequences via COP2 net on geometry UVs."""
    os.makedirs(out_dir, exist_ok=True)
    img_dir = os.path.abspath(out_dir).replace("\\", "/")
    copnet = hou.node("/obj").createNode("copnet", "molt_copnet")
    gci = copnet.createNode("geometry", "in_molt_field")
    gci.parm("soppath").set(out_sop.path())

    # Bake via attribute-from-map style render: use "file" ROP equivalent (cops render)
    null = gci.createOutputNodeAndConnect("null", "out_bake")
    rop = copnet.createNode("rop_cop2", "ROP_bake_molt")
    rop.setNextInput(null)
    for name, chan in (("molt_age", "C"), ("secretion_flow_dir", "N")):
        rop.parm(f"chanscope").set(chan)
    rop.parm("output").set(f"{img_dir}/molt_$F4.exr")
    rop.parm("trange").set(1)
    rop.parmTuple("f").set((start, end, 1))
    rop.render(frame_range=(start, end))
    print(f"[export_molt_masks] baked {start}-{end} -> {img_dir}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="exports/molt_flow_reference")
    parser.add_argument("--frames", default="1-1")
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start, end = int(start_s), int(end_s or start_s)
    out = build_field(hou.node("/obj"))
    bake_cops(out, args.out, start, end)
    return 0


if __name__ == "__main__":
    sys.exit(main())
