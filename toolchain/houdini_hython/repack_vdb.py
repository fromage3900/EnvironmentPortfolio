#!/usr/bin/env python
"""Houdini hython: repack a bgeo.sc sequence into Niagara-importable .vdb volumes.

Converts the FLIP study cache (surface SDF + velocity) from build_flip_sim.py into
single-file-per-frame .vdb that UE5.8 Niagara can import as a volume flipbook source.

Usage (headless):
    hython.exe repack_vdb.py --src exports/flip_study --dst exports/sea_above_vdb
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import hou  # noqa: F401


def chain(parent: hou.Node, prev: hou.Node, node_type: str, name: str) -> hou.Node:
    """Create a SOP node in parent, wire prev's output to it, return the node."""
    n = parent.createNode(node_type, node_name=name)
    n.setInput(0, prev)
    n.moveToGoodPosition()
    return n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="exports/flip_study")
    parser.add_argument("--dst", default="exports/sea_above_vdb")
    parser.add_argument("--frames", default="1-1")
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    args = parser.parse_args()
    start_s, _, end_s = args.frames.partition("-")
    start = args.start if args.start is not None else int(start_s)
    end = args.end if args.end is not None else int(end_s or start_s)

    os.makedirs(args.dst, exist_ok=True)
    frames = sorted(glob.glob(os.path.join(args.src, "flip_study.*.bgeo.sc")))
    if not frames:
        print(f"[repack_vdb] no bgeo.sc frames found in {args.src}", file=sys.stderr)
        return 1

    obj = hou.node("/obj")
    geo = obj.createNode("geo", node_name="vdb_repack")
    rop = hou.node("/out").createNode("geometry", node_name="ROP_vdb_repack")
    for f in frames:
        file_node = geo.createNode("file", node_name=f"load_{os.path.basename(f)[:24]}")
        file_node.parm("file").set(os.path.abspath(f).replace("\\", "/"))
        # Surface SDF + velocity grids for Niagara volume import
        vdb = chain(geo, file_node, "vdbfrompolygons", "sdf")
        frame = int(os.path.basename(f).split(".")[1])
        rop.parm("soppath").set(vdb.path())
        rop.parm("sopoutput").set(
            os.path.abspath(os.path.join(args.dst, f"sea_above_vdb.{frame:04d}.vdb")).replace("\\", "/")
        )
        rop.parm("initsim").set(False)
        hou.setFrame(frame)
        rop.parm("trange").set(1)
        ft = rop.parmTuple("f")
        if ft is not None:
            ft.set((frame, frame, 1))
        rop.render()
    rop.destroy()

    print(f"[repack_vdb] wrote {len(frames)} vdb frames -> {args.dst}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
