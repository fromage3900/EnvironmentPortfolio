#!/usr/bin/env python
"""Export the Sea Above foliage kit as a self-contained glTF 2.0 .glb.

This is the "glTF 2.0 / web & portfolio delivery" piece of the emerging-3D-
architecture research notes (RESEARCH_EMERGING_3D_ARCHITECTURE.md):
- glTF is the delivery format for the Wix portfolio, not the working asset format.
- KHR_materials_variants is used for the "audio-reactive vs. calm" lookdev
  comparison that the research doc's follow-ups explicitly recommend.

Dependency-free: pure stdlib (struct/zlib). It embeds the baked BC / N / ORM /
IriMask PNGs produced by build_seaabove_foliage_textures.py directly into one
portable .glb. Every preset becomes a textured card wired to:
    baseColorTexture      <- _BC.png   (sRGB)
    metallicRoughness     <- _ORM.png  (G=Rough, B=Metal; R=AO)
    occlusionTexture      <- _ORM.png  (occlusion reads the RED channel)
    normalTexture         <- _N.png    (DirectX; glTF view uses this directly)
    emissiveTexture       <- _IriMask.png
Two material variants per preset ("Calm" and "Reactive") toggle the emissive
sub-blowout / roughness exactly like the Melodia MPC contract does at runtime.

Usage:
    python export_seaabove_glb.py --out tools/speedtree-audio/exports/seaabove.glb

Open seaabove_viewer.html in a browser to review.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import struct

PRESETS = ("KelpRibbon", "Bubbleweed", "LilyPad", "CoralFan", "DropletGrass", "SpawnGlow")
CHANNELS = ("BC", "N", "ORM", "IriMask")

FLOAT = 5126
UNSIGNED_SHORT = 5123
SCALAR = "SCALAR"
VEC2 = "VEC2"
VEC3 = "VEC3"


def _align(n: int, a: int = 4) -> int:
    return (n + a - 1) & ~(a - 1)


def build_quad_geometry(buffer: bytearray) -> list:
    """Append positions/normals/uvs/indices to `buffer`; return bufferView offsets."""
    positions = struct.pack(
        "<12f",
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5, 0.5, 0.0,
        0.5, 0.5, 0.0,
    )
    normals = struct.pack("<12f", 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1)
    uvs = struct.pack("<8f", 0, 0, 1, 0, 0, 1, 1, 1)
    indices = struct.pack("<6H", 0, 2, 1, 2, 3, 1)

    views = []
    for data in (positions, normals, uvs, indices):
        off = _align(len(buffer))
        buffer.extend(b"\x00" * (off - len(buffer)))
        buffer.extend(data)
        views.append((off, len(data)))
    return views


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", default=os.path.abspath(os.path.join(
        here, "..", "..", "toolchain", "houdini_cops", "exports", "seaabove_textures")))
    ap.add_argument("--out", default=os.path.abspath(os.path.join(here, "exports", "seaabove.glb")))
    args = ap.parse_args()

    tex_root = os.path.abspath(args.tex)
    out_path = os.path.abspath(args.out)

    buffer = bytearray()
    pos_off, pos_len = None, None
    geo_views = build_quad_geometry(buffer)
    pos_off, pos_len = geo_views[0]
    norm_off, norm_len = geo_views[1]
    uv_off, uv_len = geo_views[2]
    idx_off, idx_len = geo_views[3]

    img_views = []
    for preset in PRESETS:
        for ch in CHANNELS:
            path = os.path.join(tex_root, f"T_WA_{preset}_{ch}.png")
            if not os.path.isfile(path):
                raise SystemExit(f"missing texture {path}; run build_seaabove_foliage_textures.py first")
            data = open(path, "rb").read()
            off = _align(len(buffer))
            buffer.extend(b"\x00" * (off - len(buffer)))
            buffer.extend(data)
            img_views.append((preset, ch, off, len(data)))

    buffer_views = [
        {"buffer": 0, "byteOffset": pos_off, "byteLength": pos_len},
        {"buffer": 0, "byteOffset": norm_off, "byteLength": norm_len},
        {"buffer": 0, "byteOffset": uv_off, "byteLength": uv_len},
        {"buffer": 0, "byteOffset": idx_off, "byteLength": idx_len},
    ]
    image_ids = {}
    for (preset, ch, off, ln) in img_views:
        buffer_views.append({"buffer": 0, "byteOffset": off, "byteLength": ln})
        image_ids[(preset, ch)] = len(buffer_views) - 1

    accessors = [
        {"bufferView": 0, "byteOffset": 0, "componentType": FLOAT, "count": 4,
         "type": VEC3, "min": [-0.5, -0.5, 0.0], "max": [0.5, 0.5, 0.0]},
        {"bufferView": 1, "byteOffset": 0, "componentType": FLOAT, "count": 4, "type": VEC3},
        {"bufferView": 2, "byteOffset": 0, "componentType": FLOAT, "count": 4, "type": VEC2},
        {"bufferView": 3, "byteOffset": 0, "componentType": UNSIGNED_SHORT, "count": 6, "type": SCALAR},
    ]

    images = []
    textures = []
    for preset in PRESETS:
        for ch in CHANNELS:
            bv = image_ids[(preset, ch)]
            images.append({"bufferView": bv, "mimeType": "image/png", "name": f"T_WA_{preset}_{ch}.png"})
            textures.append({"source": len(images) - 1, "name": f"T_WA_{preset}_{ch}"})

    def tex_idx(preset: str, ch: str) -> int:
        return PRESETS.index(preset) * len(CHANNELS) + CHANNELS.index(ch)

    materials = []
    mat_idx = {}
    for preset in PRESETS:
        for variant in ("Calm", "Reactive"):
            if variant == "Calm":
                emissive = [0.10, 0.08, 0.06]
                rough_factor = 1.0
            else:
                emissive = [0.75, 0.70, 0.68]
                rough_factor = 0.85
            materials.append({
                "name": f"{preset}_{variant}",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
                    "baseColorTexture": {"index": tex_idx(preset, "BC")},
                    "metallicRoughnessTexture": {"index": tex_idx(preset, "ORM")},
                    "roughnessFactor": rough_factor,
                    "metallicFactor": 1.0,
                },
                "normalTexture": {"index": tex_idx(preset, "N")},
                "occlusionTexture": {"index": tex_idx(preset, "ORM")},
                "emissiveTexture": {"index": tex_idx(preset, "IriMask")},
                "emissiveFactor": emissive,
                "doubleSided": True,
            })
            mat_idx[(preset, variant)] = len(materials) - 1

    primitives = []
    for preset in PRESETS:
        primitives.append({
            "attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
            "indices": 3,
            "material": mat_idx[(preset, "Calm")],
            "extensions": {
                "KHR_materials_variants": {
                    "mappings": [
                        {"materials": [mat_idx[(preset, "Calm")]], "variants": [0]},
                        {"materials": [mat_idx[(preset, "Reactive")]], "variants": [1]},
                    ]
                }
            },
        })
    meshes = [{"name": "SeaAbove_FoliageCards", "primitives": primitives}]

    nodes = []
    for i, preset in enumerate(PRESETS):
        nodes.append({"name": preset, "mesh": 0, "translation": [(i - 2.5) * 1.8, 0.0, 0.0]})
    scenes = [{"name": "SeaAbove_Calm", "nodes": list(range(len(nodes)))}]

    gltf = {
        "asset": {"version": "2.0", "generator": "EnvironmentPortfolio export_seaabove_glb.py"},
        "extensionsUsed": ["KHR_materials_variants"],
        "extensions": {"KHR_materials_variants": {"variants": [
            {"name": "Calm"},
            {"name": "Reactive"},
        ]}},
        "scene": 0,
        "scenes": scenes,
        "nodes": nodes,
        "meshes": meshes,
        "materials": materials,
        "textures": textures,
        "images": images,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(buffer)}],
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_glb(out_path, gltf, buffer)
    n_assets = len(PRESETS) * len(CHANNELS)
    print(f"[GLB] wrote {out_path} ({len(buffer) / 1024 / 1024:.2f} MB, "
          f"{len(PRESETS)} presets, {n_assets} embedded textures, "
          f"{len(materials)} materials, KHR_materials_variants enabled)")


def write_glb(path: str, gltf: dict, bin_data: bytes) -> None:
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * (_align(len(json_bytes)) - len(json_bytes))
    bin_aligned = _align(len(bin_data))
    bin_data = bin_data + b"\x00" * (bin_aligned - len(bin_data))

    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I", len(json_bytes)))
        f.write(b"JSON")
        f.write(json_bytes)
        f.write(struct.pack("<I", len(bin_data)))
        f.write(b"BIN\x00")
        f.write(bin_data)


if __name__ == "__main__":
    main()