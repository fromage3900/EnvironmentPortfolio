"""Generate the missing SeaAbove foliage FBX placeholders as a family of assets.

Uses a tiny dependency-free ASCII FBX writer so the meshes are real files that
build_seaabove_kit.py can import, even without SpeedTree Modeler installed. The
geometries are simple stand-ins (sphere, disks, fan grid, crossed cards, hex
sprite) that carry correct normals, UVs, and a single material slot.

Assets created (besides the existing ST_Kelp_Ribbon_Tall):
    ST_Bubbleweed_Bush
    ST_LilyPad_Carousel
    ST_Coral_Fan_A, ST_Coral_Fan_B, ST_Coral_Fan_C
    ST_Droplet_Grass_Card
    ST_SpawnGlow_Mote

Usage:
    python tools/speedtree-audio/generate_seaabove_fbx_family.py
"""
from __future__ import annotations

import math
import os
from typing import Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_ROOT = os.path.join(REPO, "Imports", "SeaAboveFoliage")


def write_ascii_fbx(path: str, mesh_name: str, vertices: list[float], normals: list[float],
                    uvs: list[float], indices: list[int], material_name: str = "SeaAbove") -> None:
    """Write a minimal valid FBX 7.4 ASCII file with one mesh + one material."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def f_list(seq):
        return ", ".join(f"{v:.6f}" for v in seq)

    def i_list(seq):
        return ", ".join(str(v) for v in seq)

    poly_idx = []
    for i in range(0, len(indices), 3):
        a, b, c = indices[i], indices[i + 1], indices[i + 2]
        poly_idx.extend([a, b, -(c + 1)])

    lines = []
    lines.append("; FBX 7.4.0 project file")
    lines.append("; ----------------------------------------------------")
    lines.append("")
    lines.append("FBXHeaderExtension:  {")
    lines.append("    FBXHeaderVersion: 1003")
    lines.append("    FBXVersion: 7400")
    lines.append("    CreationTimeStamp:  {")
    lines.append("        Version: 1000")
    lines.append("        Year: 2026")
    lines.append("        Month: 9")
    lines.append("        Day: 2")
    lines.append("        Hour: 0")
    lines.append("        Minute: 0")
    lines.append("        Second: 0")
    lines.append("        Millisecond: 0")
    lines.append("    }")
    lines.append(f'    Creator: "EnvironmentPortfolio/{mesh_name}"')
    lines.append("}")
    lines.append("")
    lines.append("GlobalSettings:  {")
    lines.append("    Version: 1000")
    lines.append("    Properties70:  {")
    lines.append('        P: "UpAxis", "int", "Integer", "",1')
    lines.append('        P: "UpAxisSign", "int", "Integer", "",1')
    lines.append('        P: "FrontAxis", "int", "Integer", "",2')
    lines.append('        P: "FrontAxisSign", "int", "Integer", "",1')
    lines.append('        P: "CoordSystem", "int", "Integer", "",0')
    lines.append('        P: "OriginalUpAxis", "int", "Integer", "",-1')
    lines.append('        P: "OriginalUpAxisSign", "int", "Integer", "",1')
    lines.append('        P: "UnitScaleFactor", "double", "Number", "",1')
    lines.append('        P: "OriginalUnitScaleFactor", "double", "Number", "",1')
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.append("Documents:  {")
    lines.append("    Count: 1")
    lines.append('    Document: 1000000000, "Scene", "Scene" {')
    lines.append("        Properties70:  {")
    lines.append('            P: "SourceObject", "object", "", ""')
    lines.append('            P: "ActiveAnimStackName", "KString", "", "", ""')
    lines.append("        }")
    lines.append("        RootNode: 0")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.append("References:  {")
    lines.append("}")
    lines.append("")
    lines.append("Definitions:  {")
    lines.append("    Version: 100")
    lines.append("    Count: 4")
    lines.append('    ObjectType: "GlobalSettings" {')
    lines.append("        Count: 1")
    lines.append("    }")
    lines.append('    ObjectType: "Model" {')
    lines.append("        Count: 1")
    lines.append("    }")
    lines.append('    ObjectType: "Geometry" {')
    lines.append("        Count: 1")
    lines.append("    }")
    lines.append('    ObjectType: "Material" {')
    lines.append("        Count: 1")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.append("Objects:  {")
    lines.append(f'    Geometry: 2000000000, "Geometry::{mesh_name}", "Mesh" {{')
    lines.append(f"        Vertices: *{len(vertices)} {{")
    lines.append(f"            a: {f_list(vertices)}")
    lines.append("        }")
    lines.append(f"        PolygonVertexIndex: *{len(poly_idx)} {{")
    lines.append(f"            a: {i_list(poly_idx)}")
    lines.append("        }")
    lines.append("        GeometryVersion: 124")
    lines.append("        LayerElementNormal: 0 {")
    lines.append("            Version: 101")
    lines.append('            Name: ""')
    lines.append('            MappingInformationType: "ByPolygonVertex"')
    lines.append('            ReferenceInformationType: "Direct"')
    lines.append(f"            Normals: *{len(normals)} {{")
    lines.append(f"                a: {f_list(normals)}")
    lines.append("            }")
    lines.append("        }")
    lines.append("        LayerElementUV: 0 {")
    lines.append("            Version: 101")
    lines.append('            Name: "UVMap"')
    lines.append('            MappingInformationType: "ByPolygonVertex"')
    lines.append('            ReferenceInformationType: "Direct"')
    lines.append(f"            UV: *{len(uvs)} {{")
    lines.append(f"                a: {f_list(uvs)}")
    lines.append("            }")
    lines.append("            LayerElementMaterial: 0 {")
    lines.append("                Version: 101")
    lines.append('                Name: ""')
    lines.append('                MappingInformationType: "AllSame"')
    lines.append('                ReferenceInformationType: "IndexToDirect"')
    lines.append("                Materials: *1 {")
    lines.append("                    a: 0")
    lines.append("                }")
    lines.append("            }")
    lines.append("        }")
    lines.append("        Layer: 0 {")
    lines.append("            Version: 100")
    lines.append("            LayerElement:  {")
    lines.append('                Type: "LayerElementNormal"')
    lines.append("                TypedIndex: 0")
    lines.append("            }")
    lines.append("            LayerElement:  {")
    lines.append('                Type: "LayerElementUV"')
    lines.append("                TypedIndex: 0")
    lines.append("            }")
    lines.append("            LayerElement:  {")
    lines.append('                Type: "LayerElementMaterial"')
    lines.append("                TypedIndex: 0")
    lines.append("            }")
    lines.append("        }")
    lines.append("    }")
    lines.append(f'    Model: 1000000000, "Model::{mesh_name}", "Mesh" {{')
    lines.append("        Version: 232")
    lines.append("        Properties70:  {")
    lines.append('            P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0')
    lines.append('            P: "Lcl Rotation", "Lcl Rotation", "", "A",0,0,0')
    lines.append('            P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1')
    lines.append('            P: "Visibility", "Visibility", "", "A",1')
    lines.append("        }")
    lines.append('        Shading: Y')
    lines.append('        Culling: "CullingOff"')
    lines.append("    }")
    lines.append(f'    Material: 3000000000, "Material::{material_name}", "" {{')
    lines.append("        Version: 102")
    lines.append('        ShadingModel: "lambert"')
    lines.append("        MultiLayer: 0")
    lines.append("        Properties70:  {")
    lines.append('            P: "AmbientColor", "Color", "", "A",0.2,0.2,0.2')
    lines.append('            P: "DiffuseColor", "Color", "", "A",0.8,0.8,0.8')
    lines.append('            P: "SpecularColor", "Color", "", "A",0.2,0.2,0.2')
    lines.append('            P: "SpecularFactor", "double", "Number", "",0.2')
    lines.append('            P: "ShininessExponent", "double", "Number", "",20')
    lines.append("        }")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.append("Connections:  {")
    lines.append('    C: "OO",1000000000,2000000000')
    lines.append('    C: "OO",3000000000,1000000000,0')
    lines.append("}")
    lines.append("")
    lines.append("Takes:  {")
    lines.append('    Current: ""')
    lines.append("}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")





# ---- mesh generators --------------------------------------------------------


def _tri_fan(center: int, ring: list[int]) -> list[int]:
    """Return triangle indices for a disk centered at `center` with ring indices."""
    idx = []
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        idx.extend([center, ring[i], ring[j]])
    return idx



def make_uv_sphere(rings: int = 8, segments: int = 16,
                   scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)) -> Tuple[list[float], list[float], list[float], list[int]]:
    vertices, normals, uvs, indices = [], [], [], []
    for i in range(rings + 1):
        t = math.pi * i / rings
        for j in range(segments):
            p = 2.0 * math.pi * j / segments
            x = math.sin(t) * math.cos(p) * scale[0]
            y = math.cos(t) * scale[1]
            z = math.sin(t) * math.sin(p) * scale[2]
            vertices.extend([x, y, z])
            nx, ny, nz = x / scale[0], y / scale[1], z / scale[2]
            length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            normals.extend([nx / length, ny / length, nz / length])
            uvs.extend([j / segments, i / rings])
    seg = segments
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j
            b = (i + 1) * seg + j
            c = (i + 1) * seg + (j + 1) % seg
            d = i * seg + (j + 1) % seg
            indices.extend([a, b, c])
            indices.extend([a, c, d])
    return vertices, normals, uvs, indices


def make_bubbleweed_bush() -> Tuple[list[float], list[float], list[float], list[int]]:
    return make_uv_sphere(rings=8, segments=16, scale=(0.6, 0.75, 0.6))


def make_lilypad_carousel(n_pads: int = 5, segments: int = 16) -> Tuple[list[float], list[float], list[float], list[int]]:
    vertices, normals, uvs, indices = [], [], [], []
    radius = 0.45
    for i in range(n_pads):
        angle = 2.0 * math.pi * i / n_pads
        cx = 1.1 * math.cos(angle)
        cz = 1.1 * math.sin(angle)
        base = len(vertices) // 3
        vertices.extend([cx, 0.0, cz])
        normals.extend([0.0, 1.0, 0.0])
        uvs.extend([0.5, 0.5])
        ring = []
        for j in range(segments):
            a = 2.0 * math.pi * j / segments
            x = cx + radius * math.cos(a)
            z = cz + radius * math.sin(a)
            vertices.extend([x, 0.0, z])
            normals.extend([0.0, 1.0, 0.0])
            uvs.extend([0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)])
            ring.append(base + 1 + j)
        indices.extend(_tri_fan(base, ring))
    return vertices, normals, uvs, indices


def make_coral_fan(width: float = 1.0, height: float = 1.2, curvature: float = 0.35,
                   cols: int = 8, rows: int = 8) -> Tuple[list[float], list[float], list[float], list[int]]:
    vertices, normals, uvs, indices = [], [], [], []
    for r in range(rows + 1):
        v = r / rows
        y = (1.0 - v) * height
        for c in range(cols + 1):
            u = c / cols
            theta = math.pi * (u - 0.5)
            arc = width * 0.5
            x = arc * math.sin(theta)
            z = curvature * math.cos(theta) - curvature
            vertices.extend([x, y, z])
            uvs.extend([u, v])
            tx = arc * math.cos(theta)
            ty = 0.0
            tz = -curvature * math.sin(theta)
            vx = 0.0
            vy = -height
            vz = 0.0
            nx = ty * vz - tz * vy
            ny = tz * vx - tx * vz
            nz = tx * vy - ty * vx
            length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            normals.extend([nx / length, ny / length, nz / length])
    for r in range(rows):
        for c in range(cols):
            a = r * (cols + 1) + c
            b = (r + 1) * (cols + 1) + c
            d = r * (cols + 1) + c + 1
            e = (r + 1) * (cols + 1) + c + 1
            indices.extend([a, b, d])
            indices.extend([b, e, d])
    return vertices, normals, uvs, indices
def make_droplet_grass_card() -> Tuple[list[float], list[float], list[float], list[int]]:
    vertices, normals, uvs, indices = [], [], [], []
    hw, hh = 0.3, 0.8
    quads = [
        [(-hw, -hh, 0.0), (hw, -hh, 0.0), (-hw, hh, 0.0), (hw, hh, 0.0)],
        [(0.0, -hh, -hw), (0.0, -hh, hw), (0.0, hh, -hw), (0.0, hh, hw)],
    ]
    for quad in quads:
        base = len(vertices) // 3
        for p, uv in zip(quad, [(0, 0), (1, 0), (0, 1), (1, 1)]):
            vertices.extend(p)
            nx = 1.0 if p[2] == 0.0 else 0.0
            nz = 1.0 if p[0] == 0.0 else 0.0
            normals.extend([nx, 0.0, nz])
            uvs.extend(uv)
        indices.extend([base, base + 1, base + 2])
        indices.extend([base + 1, base + 3, base + 2])
    return vertices, normals, uvs, indices


def make_spawnglow_mote(segments: int = 6) -> Tuple[list[float], list[float], list[float], list[int]]:
    vertices, normals, uvs, indices = [], [], [], []
    base = 0
    vertices.extend([0.0, 0.0, 0.0])
    normals.extend([0.0, 1.0, 0.0])
    uvs.extend([0.5, 0.5])
    ring = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        x = 0.2 * math.cos(a)
        z = 0.2 * math.sin(a)
        vertices.extend([x, 0.0, z])
        normals.extend([0.0, 1.0, 0.0])
        uvs.extend([0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)])
        ring.append(base + 1 + i)
    indices.extend(_tri_fan(base, ring))
    return vertices, normals, uvs, indices


ASSETS = [
    ("ST_Bubbleweed_Bush", make_bubbleweed_bush),
    ("ST_LilyPad_Carousel", make_lilypad_carousel),
    ("ST_Coral_Fan_A", lambda: make_coral_fan(width=0.9, height=1.0, curvature=0.25)),
    ("ST_Coral_Fan_B", lambda: make_coral_fan(width=1.2, height=1.4, curvature=0.40)),
    ("ST_Coral_Fan_C", lambda: make_coral_fan(width=1.5, height=1.1, curvature=0.55)),
    ("ST_Droplet_Grass_Card", make_droplet_grass_card),
    ("ST_SpawnGlow_Mote", make_spawnglow_mote),
]


def main() -> None:
    for asset_name, builder in ASSETS:
        verts, norms, uvs, idx = builder()
        out_dir = os.path.join(OUT_ROOT, asset_name)
        out_path = os.path.join(out_dir, f"{asset_name}.fbx")
        write_ascii_fbx(out_path, asset_name, verts, norms, uvs, idx)
        print(f"[FBX] {asset_name}: {len(verts) // 3} verts, {len(idx) // 3} tris -> {out_path}")
    print(f"[FBX] SeaAbove family complete in {OUT_ROOT}")


if __name__ == "__main__":
    main()

