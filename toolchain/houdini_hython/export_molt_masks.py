#!/usr/bin/env python
"""Houdini hython: bake molt-age mask + secretion flow/vector reference sequences
(IlluGen Benchmark A input). One shared procedural field -> both IlluGen textures
and Niagara flow data, per the canonical toolchain doctrine.

The field is exported as attribute-carrying .bgeo.sc frames (the attribute form
that IlluGen flow data + Niagara flow maps consume). Image baking of the scalar
field is a camera-driven COP step done in-session (see toolchain/illugen/).

Usage (headless):
    hython.exe export_molt_masks.py --out exports/molt_flow_reference
"""
from __future__ import annotations

import argparse
import os
import sys

import hou  # noqa: F401


def chain(parent: hou.Node, prev: hou.Node, node_type: str, name: str) -> hou.Node:
    """Create a SOP node in parent, wire prev's output to it, return the node."""
    n = parent.createNode(node_type, node_name=name)
    n.setInput(0, prev)
    n.moveToGoodPosition()
    return n


def build_field(obj: hou.Node) -> hou.Node:
    geo = obj.createNode("geo", node_name="molt_flow_field")
    geo.moveToGoodPosition()

    # Molt fragment surface: subdivided grid curved into a fragment-ish form
    grid = geo.createNode("grid", "molt_fragment")
    grid.parm("rows").set(120)
    grid.parm("cols").set(120)
    grid.parm("sizey").set(1.6)  # aspect

    noise = chain(geo, grid, "attribnoise::2.0", "molt_age_noise")
    noise.parm("attribs").set("molt_age")
    noise.parm("elementsize").set(0.45)

    # Flow direction: curl-ish from a second noise -> vector attribute for flow maps
    flow = chain(geo, noise, "attribnoise::2.0", "secretion_flow")
    flow.parm("attribs").set("secretion_flow_dir")
    flow.parm("attribtype").set(1)  # 1 = Vector
    flow.parm("elementsize").set(0.8)

    out = chain(geo, flow, "null", "OUT_molt_flow_field")
    out.setDisplayFlag(True)
    return out


def bake_field(out_sop: hou.Node, out_dir: str, start: int, end: int) -> None:
    """Export the molt-age/flow attribute field as attribute-carrying bgeo.sc frames."""
    os.makedirs(out_dir, exist_ok=True)
    rop = hou.node("/out").createNode("geometry", node_name="ROP_bake_molt")
    rop.parm("soppath").set(out_sop.path())
    rop.parm("sopoutput").set(
        os.path.abspath(os.path.join(out_dir, "molt_flow.$F4.bgeo.sc")).replace("\\\\", "/")
    )
    rop.parm("initsim").set(False)
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
    print(f"[export_molt_masks] exported {start}-{end} -> {out_dir}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="exports/molt_flow_reference")
    parser.add_argument("--frames", default="1-1")
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start, end = int(start_s), int(end_s or start_s)
    out = build_field(hou.node("/obj"))
    bake_field(out, args.out, start, end)
    return 0


if __name__ == "__main__":
    sys.exit(main())