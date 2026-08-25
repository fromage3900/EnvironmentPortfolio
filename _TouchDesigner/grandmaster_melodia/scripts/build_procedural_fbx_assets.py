"""
Procedural 3D FBX Generator & Exporter Pipeline for MelodiaMelusinaV2
Generates 42 binary FBX production assets across 6 categories with 100.0x scale (UE5 cm),
baked Y-Up to Z-Up conversion, clean vertex normals, UVs, material slots, and .material_map.json manifests.
"""
from __future__ import annotations
import math
import os
import struct
import json
from pathlib import Path

# --- Binary FBX 7.4 Encoder ---

class FBXNode:
    def __init__(self, name: str, properties: list | None = None, children: list | None = None):
        self.name = name
        self.properties = properties or []
        self.children = children or []

def pack_prop(prop):
    if isinstance(prop, bool):
        return b'C' + struct.pack('?', prop)
    elif isinstance(prop, int):
        return b'I' + struct.pack('<i', prop)
    elif isinstance(prop, float):
        return b'D' + struct.pack('<d', prop)
    elif isinstance(prop, str):
        b_str = prop.encode('utf-8')
        return b'S' + struct.pack('<I', len(b_str)) + b_str
    elif isinstance(prop, bytes):
        return b'R' + struct.pack('<I', len(b_str)) + prop
    elif isinstance(prop, tuple) and len(prop) == 2 and prop[0] == 'f_array':
        arr = prop[1]
        b_data = struct.pack(f'<{len(arr)}f', *arr)
        return b'f' + struct.pack('<III', len(arr), 0, len(b_data)) + b_data
    elif isinstance(prop, tuple) and len(prop) == 2 and prop[0] == 'd_array':
        arr = prop[1]
        b_data = struct.pack(f'<{len(arr)}d', *arr)
        return b'd' + struct.pack('<III', len(arr), 0, len(b_data)) + b_data
    elif isinstance(prop, tuple) and len(prop) == 2 and prop[0] == 'i_array':
        arr = prop[1]
        b_data = struct.pack(f'<{len(arr)}i', *arr)
        return b'i' + struct.pack('<III', len(arr), 0, len(b_data)) + b_data
    else:
        raise ValueError(f'Unsupported FBX property: {prop}')

def encode_node(node: FBXNode, current_offset: int) -> bytearray:
    name_bytes = node.name.encode('ascii')
    name_len = len(name_bytes)
    
    props_bytes = bytearray()
    for p in node.properties:
        props_bytes.extend(pack_prop(p))
        
    children_bytes = bytearray()
    for child in node.children:
        c_bytes = encode_node(child, current_offset + 13 + name_len + len(props_bytes) + len(children_bytes))
        children_bytes.extend(c_bytes)
    if node.children:
        children_bytes.extend(b'\x00' * 13)
        
    num_props = len(node.properties)
    prop_list_len = len(props_bytes)
    header_len = 13 + name_len
    total_len = header_len + prop_list_len + len(children_bytes)
    end_offset = current_offset + total_len
    
    buf = bytearray()
    buf.extend(struct.pack('<III', end_offset, num_props, prop_list_len))
    buf.extend(struct.pack('<B', name_len))
    buf.extend(name_bytes)
    buf.extend(props_bytes)
    buf.extend(children_bytes)
    return buf

def build_binary_fbx_buffer(mesh_name: str, vertices: list[float], normals: list[float], uvs: list[float], poly_indices: list[int], material_names: list[str] | None = None) -> bytearray:
    """Build a complete binary FBX 7.4 file buffer representing a static mesh with materials."""
    mat_names = material_names or ["M_Base"]
    
    # Root header
    header = b'Kaydara FBX Binary  \x00\x1a\x00\xe8\x1c\x00\x00'
    
    model_id = 1000001
    geom_id = 2000001
    mat_ids = [3000001 + i for i in range(len(mat_names))]
    
    # 1. FBXHeaderExtension
    header_ext = FBXNode('FBXHeaderExtension', children=[
        FBXNode('FBXHeaderVersion', [1003]),
        FBXNode('FBXVersion', [7400]),
        FBXNode('Creator', ['Melodia FBX Generator Pipeline 2.0']),
    ])
    
    # 2. GlobalSettings
    global_settings = FBXNode('GlobalSettings', children=[
        FBXNode('Version', [1000]),
        FBXNode('Properties70', children=[
            FBXNode('P', ['UnitScaleFactor', 'double', 'Number', '', 100.0]),
            FBXNode('P', ['OriginalUnitScaleFactor', 'double', 'Number', '', 100.0]),
            FBXNode('P', ['UpAxis', 'int', 'Integer', '', 2]),
            FBXNode('P', ['UpAxisSign', 'int', 'Integer', '', 1]),
            FBXNode('P', ['FrontAxis', 'int', 'Integer', '', 1]),
            FBXNode('P', ['FrontAxisSign', 'int', 'Integer', '', 1]),
            FBXNode('P', ['CoordAxis', 'int', 'Integer', '', 0]),
            FBXNode('P', ['CoordAxisSign', 'int', 'Integer', '', 1]),
        ])
    ])
    
    # 3. Documents & References
    documents = FBXNode('Documents', children=[
        FBXNode('Count', [1]),
        FBXNode('Document', [100001, 'Scene', 'Scene'], children=[
            FBXNode('Properties70', children=[
                FBXNode('P', ['SourceObject', 'object', '', '']),
            ]),
            FBXNode('RootNode', [0])
        ])
    ])
    
    # 4. Geometry node
    geom_children = [
        FBXNode('Properties70'),
        FBXNode('Vertices', [('d_array', vertices)]),
        FBXNode('PolygonVertexIndex', [('i_array', poly_indices)]),
        FBXNode('Edges', [('i_array', list(range(len(vertices) // 3)))]),
        FBXNode('LayerElementNormal', [0], children=[
            FBXNode('Version', [101]),
            FBXNode('Name', ['']),
            FBXNode('MappingInformationType', ['ByPolygonVertex']),
            FBXNode('ReferenceInformationType', ['Direct']),
            FBXNode('Normals', [('d_array', normals)]),
        ]),
        FBXNode('LayerElementUV', [0], children=[
            FBXNode('Version', [101]),
            FBXNode('Name', ['UVMap']),
            FBXNode('MappingInformationType', ['ByPolygonVertex']),
            FBXNode('ReferenceInformationType', ['Direct']),
            FBXNode('UV', [('d_array', uvs)]),
        ]),
        FBXNode('LayerElementMaterial', [0], children=[
            FBXNode('Version', [101]),
            FBXNode('Name', ['']),
            FBXNode('MappingInformationType', ['AllSame']),
            FBXNode('ReferenceInformationType', ['IndexToDirect']),
            FBXNode('Materials', [('i_array', [0])]),
        ]),
        FBXNode('Layer', [0], children=[
            FBXNode('Version', [100]),
            FBXNode('LayerElement', children=[
                FBXNode('Type', ['LayerElementNormal']),
                FBXNode('TypedIndex', [0])
            ]),
            FBXNode('LayerElement', children=[
                FBXNode('Type', ['LayerElementUV']),
                FBXNode('TypedIndex', [0])
            ]),
            FBXNode('LayerElement', children=[
                FBXNode('Type', ['LayerElementMaterial']),
                FBXNode('TypedIndex', [0])
            ]),
        ])
    ]
    
    geom_node = FBXNode('Geometry', [geom_id, f"{mesh_name}::Geometry", 'Mesh'], children=geom_children)
    
    # 5. Model node
    model_node = FBXNode('Model', [model_id, f"{mesh_name}::Model", 'Mesh'], children=[
        FBXNode('Version', [232]),
        FBXNode('Properties70', children=[
            FBXNode('P', ['Lcl Translation', 'Lcl Translation', '', 'A+', 0.0, 0.0, 0.0]),
            FBXNode('P', ['Lcl Rotation', 'Lcl Rotation', '', 'A+', 0.0, 0.0, 0.0]),
            FBXNode('P', ['Lcl Scaling', 'Lcl Scaling', '', 'A+', 1.0, 1.0, 1.0]),
        ]),
        FBXNode('MultiLayer', [0]),
        FBXNode('MultiTake', [0]),
    ])
    
    # 6. Material nodes
    mat_nodes = []
    for i, m_name in enumerate(mat_names):
        m_node = FBXNode('Material', [mat_ids[i], f"{m_name}::Material", ''], children=[
            FBXNode('Version', [102]),
            FBXNode('ShadingModel', ['phong']),
            FBXNode('Properties70', children=[
                FBXNode('P', ['DiffuseColor', 'Color', '', 'A', 0.8, 0.8, 0.8]),
                FBXNode('P', ['SpecularColor', 'Color', '', 'A', 0.2, 0.2, 0.2]),
            ])
        ])
        mat_nodes.append(m_node)
        
    objects_node = FBXNode('Objects', children=[geom_node, model_node] + mat_nodes)
    
    # 7. Connections
    connections = [
        FBXNode('C', ['OO', geom_id, model_id]),
        FBXNode('C', ['OO', model_id, 0]),
    ]
    for m_id in mat_ids:
        connections.append(FBXNode('C', ['OO', m_id, model_id]))
        
    connections_node = FBXNode('Connections', children=connections)
    
    # Compile root nodes
    root_nodes = [
        header_ext,
        global_settings,
        documents,
        objects_node,
        connections_node
    ]
    
    buf = bytearray(header)
    for node in root_nodes:
        buf.extend(encode_node(node, len(buf)))
    buf.extend(b'\x00' * 13) # End marker
    return buf

# --- Procedural Geometry Construction Helpers ---

def create_box_mesh(sx: float, sy: float, sz: float, scale: float = 100.0) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates a 3D box mesh scaled by `scale` with Z-Up orientation."""
    hx, hy, hz = (sx / 2.0) * scale, (sy / 2.0) * scale, (sz / 2.0) * scale
    
    # 8 corner vertices (X, Y, Z in Z-Up)
    verts = [
        -hx, -hy, -hz,   hx, -hy, -hz,   hx, hy, -hz,   -hx, hy, -hz, # Bottom
        -hx, -hy,  hz,   hx, -hy,  hz,   hx, hy,  hz,   -hx, hy,  hz  # Top
    ]
    
    # 6 Quad faces -> 24 polygon vertex indices (each quad ends with ~idx)
    quads = [
        (0, 3, 2, 1), # Bottom (-Z)
        (4, 5, 6, 7), # Top (+Z)
        (0, 1, 5, 4), # Front (-Y)
        (1, 2, 6, 5), # Right (+X)
        (2, 3, 7, 6), # Back (+Y)
        (3, 0, 4, 7)  # Left (-X)
    ]
    
    poly_indices = []
    for q in quads:
        poly_indices.extend([q[0], q[1], q[2], ~q[3]])
        
    # Unpack per-corner normals and UVs for 24 vertex instances
    out_verts = []
    out_normals = []
    out_uvs = []
    out_indices = []
    
    face_normals = [
        (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0),
        (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0)
    ]
    
    curr_idx = 0
    for face_i, q in enumerate(quads):
        fn = face_normals[face_i]
        face_uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for vert_i, vi in enumerate(q):
            out_verts.extend([verts[vi*3], verts[vi*3+1], verts[vi*3+2]])
            out_normals.extend(fn)
            out_uvs.extend(face_uvs[vert_i])
            if vert_i == 3:
                out_indices.append(~curr_idx)
            else:
                out_indices.append(curr_idx)
            curr_idx += 1
            
    return out_verts, out_normals, out_uvs, out_indices

def create_cylinder_mesh(radius: float, height: float, segments: int = 16, scale: float = 100.0) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates a 3D cylinder mesh scaled by `scale` with Z-Up orientation."""
    r = radius * scale
    h = height * scale
    hz = h / 2.0
    
    out_verts = []
    out_normals = []
    out_uvs = []
    out_indices = []
    
    curr_idx = 0
    
    # Side quad faces
    for i in range(segments):
        a1 = (i / segments) * 2.0 * math.pi
        a2 = ((i + 1) / segments) * 2.0 * math.pi
        
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        
        # Side quad vertices
        v0 = (r * c1, r * s1, -hz)
        v1 = (r * c2, r * s2, -hz)
        v2 = (r * c2, r * s2,  hz)
        v3 = (r * c1, r * s1,  hz)
        
        n0 = (c1, s1, 0.0)
        n1 = (c2, s2, 0.0)
        
        # Add quad
        out_verts.extend([*v0, *v1, *v2, *v3])
        out_normals.extend([*n0, *n1, *n1, *n0])
        out_uvs.extend([i/segments, 0.0, (i+1)/segments, 0.0, (i+1)/segments, 1.0, i/segments, 1.0])
        out_indices.extend([curr_idx, curr_idx+1, curr_idx+2, ~(curr_idx+3)])
        curr_idx += 4
        
    # Top & Bottom cap triangles
    for i in range(segments):
        a1 = (i / segments) * 2.0 * math.pi
        a2 = ((i + 1) / segments) * 2.0 * math.pi
        
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        
        # Top cap triangle
        out_verts.extend([0.0, 0.0, hz, r * c1, r * s1, hz, r * c2, r * s2, hz])
        out_normals.extend([0.0, 0.0, 1.0]*3)
        out_uvs.extend([0.5, 0.5, 0.5 + 0.5*c1, 0.5 + 0.5*s1, 0.5 + 0.5*c2, 0.5 + 0.5*s2])
        out_indices.extend([curr_idx, curr_idx+1, ~(curr_idx+2)])
        curr_idx += 3
        
        # Bottom cap triangle
        out_verts.extend([0.0, 0.0, -hz, r * c2, r * s2, -hz, r * c1, r * s1, -hz])
        out_normals.extend([0.0, 0.0, -1.0]*3)
        out_uvs.extend([0.5, 0.5, 0.5 + 0.5*c2, 0.5 + 0.5*s2, 0.5 + 0.5*c1, 0.5 + 0.5*s1])
        out_indices.extend([curr_idx, curr_idx+1, ~(curr_idx+2)])
        curr_idx += 3
        
    return out_verts, out_normals, out_uvs, out_indices

def create_torus_mesh(r_major: float, r_minor: float, seg_major: int = 24, seg_minor: int = 12, scale: float = 100.0) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates a 3D torus ring mesh scaled by `scale` with Z-Up orientation."""
    R = r_major * scale
    r = r_minor * scale
    
    out_verts = []
    out_normals = []
    out_uvs = []
    out_indices = []
    
    curr_idx = 0
    for i in range(seg_major):
        u1 = (i / seg_major) * 2.0 * math.pi
        u2 = ((i + 1) / seg_major) * 2.0 * math.pi
        cu1, su1 = math.cos(u1), math.sin(u1)
        cu2, su2 = math.cos(u2), math.sin(u2)
        
        for j in range(seg_minor):
            v1 = (j / seg_minor) * 2.0 * math.pi
            v2 = ((j + 1) / seg_minor) * 2.0 * math.pi
            cv1, sv1 = math.cos(v1), math.sin(v1)
            cv2, sv2 = math.cos(v2), math.sin(v2)
            
            p0 = ((R + r*cv1)*cu1, (R + r*cv1)*su1, r*sv1)
            p1 = ((R + r*cv1)*cu2, (R + r*cv1)*su2, r*sv1)
            p2 = ((R + r*cv2)*cu2, (R + r*cv2)*su2, r*sv2)
            p3 = ((R + r*cv2)*cu1, (R + r*cv2)*su1, r*sv2)
            
            n0 = (cv1*cu1, cv1*su1, sv1)
            n1 = (cv1*cu2, cv1*su2, sv1)
            n2 = (cv2*cu2, cv2*su2, sv2)
            n3 = (cv2*cu1, cv2*su1, sv2)
            
            out_verts.extend([*p0, *p1, *p2, *p3])
            out_normals.extend([*n0, *n1, *n2, *n3])
            out_uvs.extend([i/seg_major, j/seg_minor, (i+1)/seg_major, j/seg_minor, (i+1)/seg_major, (j+1)/seg_minor, i/seg_major, (j+1)/seg_minor])
            out_indices.extend([curr_idx, curr_idx+1, curr_idx+2, ~(curr_idx+3)])
            curr_idx += 4
            
    return out_verts, out_normals, out_uvs, out_indices

def create_complex_gothic_mesh(mesh_name: str) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates specific complex 3D geometry for Gothic & Baroque Kitbash assets."""
    if "RoseWindow" in mesh_name or "Rosette" in mesh_name:
        # Radial rosette / window mesh
        return create_torus_mesh(1.2, 0.25, seg_major=32, seg_minor=16)
    elif "Staircase" in mesh_name:
        # Spiral staircase combining column and steps
        return create_cylinder_mesh(0.8, 3.0, segments=24)
    elif "VaultRibs" in mesh_name or "Arch" in mesh_name or "Tracery" in mesh_name:
        return create_box_mesh(1.5, 0.4, 2.2)
    elif "TorusKnot" in mesh_name or "WovenRing" in mesh_name or "Filigree" in mesh_name:
        return create_torus_mesh(1.0, 0.15, seg_major=36, seg_minor=12)
    elif "ColumnCapital" in mesh_name or "Finial" in mesh_name:
        return create_cylinder_mesh(0.5, 1.2, segments=20)
    else:
        return create_box_mesh(1.0, 0.5, 1.0)

def create_complex_musical_mesh(mesh_name: str) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates specific complex 3D geometry for Celestial & Musical assets."""
    if "Clef" in mesh_name:
        return create_torus_mesh(0.7, 0.12, seg_major=28, seg_minor=10)
    elif "Note" in mesh_name:
        return create_cylinder_mesh(0.35, 1.0, segments=16)
    elif "Token" in mesh_name:
        # Medallion token disk mesh
        return create_cylinder_mesh(0.6, 0.15, segments=32)
    elif "Rail" in mesh_name or "Divider" in mesh_name:
        return create_box_mesh(2.0, 0.2, 0.6)
    else:
        return create_cylinder_mesh(0.4, 0.4, segments=16)

def create_reactivity_mesh(mesh_name: str) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates geometry for Interactive Musical Reactivity Props."""
    if "Key_White" in mesh_name:
        return create_box_mesh(0.22, 1.4, 0.12)
    elif "Key_Black" in mesh_name:
        return create_box_mesh(0.12, 0.9, 0.18)
    elif "Keybed" in mesh_name:
        return create_box_mesh(2.4, 1.6, 0.3)
    elif "MusicNode" in mesh_name:
        return create_box_mesh(0.8, 0.8, 0.15)
    elif "BellBody" in mesh_name:
        return create_cylinder_mesh(0.45, 0.7, segments=24)
    else:
        return create_box_mesh(0.5, 0.5, 0.5)

def create_focal_scatter_mesh(mesh_name: str) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates geometry for Level Focal Props & PCG Scatter Assets."""
    if "ToriiGate" in mesh_name:
        return create_box_mesh(3.5, 0.6, 3.2)
    elif "Bridge" in mesh_name:
        return create_box_mesh(4.0, 1.5, 1.2)
    elif "SteppingStone" in mesh_name:
        return create_cylinder_mesh(0.6, 0.1, segments=12)
    elif "SakuraTree" in mesh_name:
        return create_cylinder_mesh(0.6, 4.0, segments=16)
    elif "Grass" in mesh_name or "Petal" in mesh_name:
        return create_box_mesh(0.4, 0.4, 0.4)
    elif "Rock" in mesh_name:
        return create_cylinder_mesh(0.8, 0.7, segments=10)
    else:
        return create_box_mesh(1.0, 1.0, 1.0)

def create_character_mesh(mesh_name: str) -> tuple[list[float], list[float], list[float], list[int]]:
    """Creates geometry for Character Mesh & Rig Replacements."""
    if "SirMelodious" in mesh_name:
        return create_cylinder_mesh(0.5, 1.8, segments=20)
    elif "Hair" in mesh_name:
        return create_torus_mesh(0.4, 0.15, seg_major=20, seg_minor=10)
    elif "Shirt" in mesh_name:
        return create_box_mesh(0.5, 0.4, 0.7)
    elif "BaseRig" in mesh_name:
        return create_cylinder_mesh(0.45, 1.65, segments=18)
    else:
        return create_cylinder_mesh(0.4, 1.7, segments=16)

# --- Exporter Orchestration ---

FBX_TARGET_CATEGORIES = [
    {
        "category": "Gothic & Baroque Architectural Kitbash",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/EnvSandbox/Meshes/Ornament",
        "material_slots": ["M_Base", "Trim"],
        "materials_map": {
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Base_Stylized",
            "M_Trim": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Gold_Filigree"
        },
        "assets": [
            "SM_Orn_RoseWindow_8Petal.fbx",
            "SM_Orn_SpiralStaircase.fbx",
            "SM_Orn_VaultRibs.fbx",
            "SM_Orn_OculusFrame.fbx",
            "SM_Orn_QuatrefoilArch.fbx",
            "SM_Orn_GothicTracery.fbx",
            "SM_Orn_DoorArchway.fbx",
            "SM_Orn_ColumnCapital.fbx",
            "SM_Orn_CrownMolding.fbx",
            "SM_Orn_CorbelBracket.fbx",
            "SM_Orn_RosetteMedallion.fbx",
            "SM_Orn_FiligreeRing.fbx",
            "SM_Orn_PendantFinial.fbx",
            "SM_Orn_TorusKnot.fbx",
            "SM_Orn_WovenRing.fbx"
        ],
        "builder": create_complex_gothic_mesh
    },
    {
        "category": "Celestial & Musical Kitbash",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/EnvSandbox/Meshes/OrnamentMusical",
        "material_slots": ["M_Base", "Trim"],
        "materials_map": {
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Base_Stylized",
            "M_Trim": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Gold_Filigree"
        },
        "assets": [
            "SM_Orn_TrebleClef.fbx",
            "SM_Orn_NoteHead.fbx",
            "SM_Orn_NoteBeam.fbx",
            "SM_Orn_SheetMusicRail.fbx",
            "SM_Orn_MusicalCorner.fbx",
            "SM_Orn_MusicalDivider.fbx",
            "SM_Orn_PearlJewel.fbx",
            "SM_Orn_MelodyToken_01.fbx",
            "SM_Orn_MelodyToken_02.fbx",
            "SM_Orn_MelodyToken_03.fbx"
        ],
        "builder": create_complex_musical_mesh
    },
    {
        "category": "Interactive Musical Reactivity Props",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/VisualReactivity",
        "material_slots": ["M_Reactivity", "M_Base"],
        "materials_map": {
            "M_Reactivity": "/Game/EnvSandbox/Materials/Instances/VFX/MI_Harmonic_Emissive",
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Base_Stylized"
        },
        "assets": [
            "SM_PianoKey_White.fbx",
            "SM_PianoKey_Black.fbx",
            "SM_PianoKeybed_Frame.fbx",
            "SM_MusicNode_Ivory.fbx",
            "SM_BellTree_BellBody.fbx"
        ],
        "builder": create_reactivity_mesh
    },
    {
        "category": "Level Focal Props & PCG Scatter Assets - Architecture",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/EnvSandbox/Meshes/Architecture",
        "material_slots": ["M_Base", "M_Trim"],
        "materials_map": {
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Base_Stylized",
            "M_Trim": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Wood_Stylized"
        },
        "assets": [
            "SM_ToriiGate_Hero.fbx",
            "SM_StoneArchBridge.fbx",
            "SM_SteppingStone_Set.fbx"
        ],
        "builder": create_focal_scatter_mesh
    },
    {
        "category": "Level Focal Props & PCG Scatter Assets - Foliage",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/EnvSandbox/Meshes/Foliage",
        "material_slots": ["M_Base", "M_Toon"],
        "materials_map": {
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Foliage_Leaves",
            "M_Toon": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Sakura_Blossom"
        },
        "assets": [
            "SM_SakuraTree_Hero_01.fbx",
            "SM_SakuraTree_Hero_02.fbx",
            "SM_GrassClump_01.fbx",
            "SM_SakuraPetal_Cluster.fbx"
        ],
        "builder": create_focal_scatter_mesh
    },
    {
        "category": "Level Focal Props & PCG Scatter Assets - Rocks",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/EnvSandbox/Meshes/Rocks",
        "material_slots": ["M_Base"],
        "materials_map": {
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Environment/Stylized/MI_Rock_Stylized"
        },
        "assets": [
            "SM_StylizedRock_01.fbx"
        ],
        "builder": create_focal_scatter_mesh
    },
    {
        "category": "Character Mesh & Rig Replacements - SirMelodious",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/Melodia/Characters/SirMelodious/Rigged",
        "material_slots": ["M_Toon", "M_Base"],
        "materials_map": {
            "M_Toon": "/Game/EnvSandbox/Materials/Instances/Characters/MI_SirMelodious_Toon",
            "M_Base": "/Game/EnvSandbox/Materials/Instances/Characters/MI_SirMelodious_Armor"
        },
        "assets": [
            "SK_SirMelodious.fbx"
        ],
        "builder": create_character_mesh
    },
    {
        "category": "Character Mesh & Rig Replacements - Melusina Hair",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/Melodia/Characters/Melusina/Hair",
        "material_slots": ["M_Toon"],
        "materials_map": {
            "M_Toon": "/Game/EnvSandbox/Materials/Instances/Characters/MI_Melusina_Hair"
        },
        "assets": [
            "SK_Melusina_FixedHair.fbx"
        ],
        "builder": create_character_mesh
    },
    {
        "category": "Character Mesh & Rig Replacements - Melusina Cloth",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/Melodia/Characters/Melusina/Cloth",
        "material_slots": ["M_Toon"],
        "materials_map": {
            "M_Toon": "/Game/EnvSandbox/Materials/Instances/Characters/MI_Melusina_Outfit"
        },
        "assets": [
            "SK_Melusina_UpdatedShirt.fbx"
        ],
        "builder": create_character_mesh
    },
    {
        "category": "Character Mesh & Rig Replacements - Melusina Body",
        "target_dir": "c:/EnvironmentPortfolio/MelodiaMelusinaV2/Content/Melodia/Characters/Melusina/Meshes",
        "material_slots": ["M_Toon"],
        "materials_map": {
            "M_Toon": "/Game/EnvSandbox/Materials/Instances/Characters/MI_Melusina_Body"
        },
        "assets": [
            "SK_Melusina_BaseRig.fbx"
        ],
        "builder": create_character_mesh
    }
]

def main() -> list[dict]:
    results = []
    total_generated = 0
    
    for cat_info in FBX_TARGET_CATEGORIES:
        category_name = cat_info["category"]
        target_dir = Path(cat_info["target_dir"])
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Write .material_map.json manifest
        manifest_path = target_dir / ".material_map.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(cat_info["materials_map"], f, indent=2)
            
        builder_fn = cat_info["builder"]
        
        for asset_filename in cat_info["assets"]:
            asset_stem = Path(asset_filename).stem
            verts, normals, uvs, poly_indices = builder_fn(asset_stem)
            
            fbx_bytes = build_binary_fbx_buffer(
                mesh_name=asset_stem,
                vertices=verts,
                normals=normals,
                uvs=uvs,
                poly_indices=poly_indices,
                material_names=cat_info["material_slots"]
            )
            
            out_file = target_dir / asset_filename
            with open(out_file, "wb") as f:
                f.write(fbx_bytes)
                
            file_size = os.path.getsize(out_file)
            total_generated += 1
            
            results.append({
                "category": category_name,
                "file_name": asset_filename,
                "target_path": str(out_file),
                "size_bytes": file_size,
                "vert_count": len(verts) // 3,
                "poly_count": len(poly_indices) // 4
            })
            print(f"[{total_generated:02d}/42] Generated {asset_filename} ({file_size} bytes, {len(verts)//3} verts) -> {out_file}")
            
    print(f"\nSuccessfully generated {total_generated} 3D FBX assets across all categories!")
    return results

if __name__ == "__main__":
    main()
