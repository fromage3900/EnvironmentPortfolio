"""
Grand Roman Cathedral & Cosmati Pavement PBR Material Generator
Authentic Opus Sectile, Cosmatesque Guilloche Pavements, Imperial Porphyry, Byzantine Gold Smalti,
Bookmatched Cipollino Verde Nave Slabs, and Sacred 12-Fold Baptistery Rosaces.
Strict UE5 PBR: 2048x2048 POT, DirectX Tangent Normals with Hand-Cut Tesserae 3D Micro-Tilts, Linear ORM.
"""

from __future__ import annotations

import math
import numpy as np
from pathlib import Path
from PIL import Image

def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    norm[norm == 0] = 1.0
    return v / norm

def create_fbm_noise(w: int, h: int, octaves: int = 5, persistence: float = 0.5, scale: float = 4.0, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    noise = np.zeros((h, w), dtype=np.float32)
    current_scale = scale
    amplitude = 1.0
    total_amp = 0.0
    
    for _ in range(octaves):
        gw = int(math.ceil(w / current_scale)) + 2
        gh = int(math.ceil(h / current_scale)) + 2
        grid = np.random.uniform(0.0, 1.0, (gh, gw)).astype(np.float32)
        
        img = Image.fromarray((grid * 255).astype(np.uint8), mode='L')
        resampled = np.array(img.resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0
        
        noise += resampled * amplitude
        total_amp += amplitude
        amplitude *= persistence
        current_scale /= 2.0
        if current_scale < 1.0:
            current_scale = 1.0
            
    return noise / total_amp

def sobel_normal_map(height_map: np.ndarray, strength: float = 2.0, flip_green: bool = True) -> np.ndarray:
    h, w = height_map.shape
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    
    padded = np.pad(height_map, ((1, 1), (1, 1)), mode='wrap')
    from numpy.lib.stride_tricks import sliding_window_view
    windows = sliding_window_view(padded, (3, 3))
    
    dx = np.sum(windows * kx, axis=(-2, -1)) * strength
    dy = np.sum(windows * ky, axis=(-2, -1)) * strength
    
    if flip_green:
        dy = -dy
        
    dz = np.ones_like(dx, dtype=np.float32)
    normals = np.stack([dx, dy, dz], axis=-1)
    normals = normalize(normals)
    return ((normals + 1.0) * 0.5 * 255.0).clip(0, 255).astype(np.uint8)

def pack_orm(ao: np.ndarray, roughness: np.ndarray, metallic: np.ndarray) -> np.ndarray:
    h, w = ao.shape
    orm = np.zeros((h, w, 3), dtype=np.uint8)
    orm[:, :, 0] = ao.clip(0, 255).astype(np.uint8)
    orm[:, :, 1] = roughness.clip(0, 255).astype(np.uint8)
    orm[:, :, 2] = metallic.clip(0, 255).astype(np.uint8)
    return orm

def save_suite(output_dir: Path, suite_name: str, maps: dict[str, np.ndarray]):
    output_dir.mkdir(parents=True, exist_ok=True)
    for channel_suffix, arr in maps.items():
        filename = f"{suite_name}_{channel_suffix}.png"
        filepath = output_dir / filename
        if arr.ndim == 2:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='L')
        elif arr.ndim == 3 and arr.shape[2] == 3:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='RGB')
        elif arr.ndim == 3 and arr.shape[2] == 4:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='RGBA')
        else:
            raise ValueError(f"Unsupported array shape {arr.shape} for {filename}")
        img.save(filepath, format='PNG')
        print(f"  -> Generated: {filepath.name} ({img.size[0]}x{img.size[1]})")

def generate_cosmati_quincunx_guilloche(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 1: T_Cathedral_Cosmati_QuincunxGuilloche ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    cx = x - 0.5
    cy = y - 0.5
    center_r = np.sqrt(cx**2 + cy**2)
    center_a = np.arctan2(cy, cx)
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=101)
    fbm_tess = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=202)
    
    is_center_porphyry = center_r < 0.20
    porphyry_bevel = np.clip(1.0 - (center_r / 0.20)**4.0, 0.0, 1.0)
    
    is_guilloche_band = (center_r >= 0.20) & (center_r <= 0.38)
    guilloche_braid = np.sin(center_a * 16.0 + center_r * 32.0 * np.pi) * 0.5 + 0.5
    
    tess_triangle = np.sin(center_a * 48.0) * np.cos(center_r * 64.0 * np.pi)
    is_gold_smalti = is_guilloche_band & (tess_triangle > 0.3)
    is_white_tess = is_guilloche_band & (tess_triangle <= 0.3) & (tess_triangle > -0.3)
    is_red_tess = is_guilloche_band & (tess_triangle <= -0.3)
    
    corner_dists = []
    for ox, oy in [(0.15, 0.15), (0.85, 0.15), (0.15, 0.85), (0.85, 0.85)]:
        cdist = np.sqrt((x - ox)**2 + (y - oy)**2)
        corner_dists.append(cdist)
    min_corner_r = np.min(corner_dists, axis=0)
    is_corner_verde = min_corner_r < 0.14
    
    is_molding_frame = (np.abs(center_r - 0.20) < 0.012) | (np.abs(center_r - 0.38) < 0.012) | (np.abs(min_corner_r - 0.14) < 0.012)
    grout = (np.abs(center_r - 0.20) < 0.006) | (np.abs(center_r - 0.38) < 0.006) | (np.abs(min_corner_r - 0.14) < 0.006)
    
    c_porphyry = np.array([88, 24, 37], dtype=np.float32)
    c_porphyry_crystal = np.array([175, 120, 130], dtype=np.float32)
    c_verde = np.array([28, 68, 52], dtype=np.float32)
    c_verde_breccia = np.array([180, 210, 195], dtype=np.float32)
    c_gold_smalti = np.array([232, 190, 74], dtype=np.float32)
    c_white_marble = np.array([250, 249, 246], dtype=np.float32)
    c_red_jasper = np.array([168, 48, 40], dtype=np.float32)
    c_mortar = np.array([158, 154, 148], dtype=np.float32)
    
    porphyry_phenocrysts = (fbm_tess > 0.65) * 0.4
    verde_breccia = (fbm > 0.60) * np.abs(np.sin(fbm_tess * 12.0 * np.pi)) * 0.5
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        marble_base = c_white_marble[c] * (0.96 + fbm * 0.08) - (fbm > 0.7) * 20.0
        porphyry_val = c_porphyry[c] * (0.92 + fbm * 0.15) + c_porphyry_crystal[c] * porphyry_phenocrysts
        base = np.where(is_center_porphyry, porphyry_val, marble_base)
        verde_val = c_verde[c] * (0.85 + fbm * 0.3) + c_verde_breccia[c] * verde_breccia
        base = np.where(is_corner_verde, verde_val, base)
        base = np.where(is_gold_smalti, c_gold_smalti[c] * (0.9 + fbm_tess * 0.2), base)
        base = np.where(is_red_tess, c_red_jasper[c] * (0.9 + fbm_tess * 0.2), base)
        base = np.where(is_white_tess, c_white_marble[c] * (0.95 + fbm_tess * 0.1), base)
        base = np.where(grout, c_mortar[c], base)
        bc[:, :, c] = base
        
    height = 0.55 + is_center_porphyry * porphyry_bevel * 0.12 + is_corner_verde * 0.08 + is_guilloche_band * (0.05 + fbm_tess * 0.03) - grout * 0.25
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.8, flip_green=True)
    
    roughness = 0.16 + fbm * 0.04
    roughness = np.where(is_center_porphyry, 0.10, roughness)
    roughness = np.where(is_gold_smalti, 0.08, roughness)
    roughness = np.where(is_corner_verde, 0.14, roughness)
    roughness = np.where(grout, 0.88, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_smalti, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - grout * 0.45 - is_guilloche_band * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_gold_smalti, 0.95, np.where(is_center_porphyry, 0.85, 0.35))
    sheen_uint8 = (sheen * 255.0).clip(0, 255).astype(np.uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_opus_sectile_porphyry(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 2: T_Cathedral_OpusSectile_ImperialPorphyry ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    scale = 2.0
    gx = (x * scale) % 1.0 - 0.5
    gy = (y * scale) % 1.0 - 0.5
    r = np.sqrt(gx**2 + gy**2)
    angle = np.arctan2(gy, gx)
    
    star_8 = np.cos(angle * 8.0) * 0.15 + 0.30
    is_star_center = r < star_8
    
    lozenge = np.abs(gx) + np.abs(gy)
    is_lozenge_band = (lozenge > 0.45) & (lozenge < 0.62)
    is_corner_square = lozenge >= 0.62
    
    seam = (np.abs(r - star_8) < 0.015) | (np.abs(lozenge - 0.45) < 0.015) | (np.abs(lozenge - 0.62) < 0.015)
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=303)
    fbm_veins = create_fbm_noise(res, res, octaves=5, persistence=0.58, scale=res/8, seed=404)
    pavonazzo_veins = np.abs(np.sin(fbm_veins * 14.0 * np.pi + x * 6.0)) ** 7.0
    
    c_porphyry = np.array([85, 22, 35], dtype=np.float32)
    c_giallo = np.array([222, 155, 53], dtype=np.float32)
    c_pavonazzo = np.array([245, 242, 248], dtype=np.float32)
    c_pavonazzo_vein = np.array([115, 68, 110], dtype=np.float32)
    c_verde = np.array([24, 62, 48], dtype=np.float32)
    c_lead_seam = np.array([68, 65, 72], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        porphyry_val = c_porphyry[c] * (0.90 + fbm * 0.20)
        giallo_val = c_giallo[c] * (0.85 + fbm * 0.30)
        pavonazzo_val = c_pavonazzo[c] * (1.0 - pavonazzo_veins * 0.65) + c_pavonazzo_vein[c] * (pavonazzo_veins * 0.65)
        verde_val = c_verde[c] * (0.88 + fbm * 0.25)
        
        base = np.where(is_star_center, porphyry_val, giallo_val)
        base = np.where(is_lozenge_band, pavonazzo_val, base)
        base = np.where(is_corner_square, verde_val, base)
        base = np.where(seam, c_lead_seam[c], base)
        bc[:, :, c] = base
        
    height = 0.58 + is_star_center * 0.06 + is_lozenge_band * 0.04 - seam * 0.18 + fbm * 0.02
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.2, flip_green=True)
    
    roughness = 0.14 + fbm * 0.04
    roughness = np.where(is_star_center, 0.10, roughness)
    roughness = np.where(is_lozenge_band, 0.12 + pavonazzo_veins * 0.06, roughness)
    roughness = np.where(seam, 0.78, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(seam, 0.25, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - seam * 0.40
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8
    }

def generate_bookmatched_cipollino(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 3: T_Cathedral_BasilicaNave_BookmatchedCipollino ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    mirror_x = np.abs(x - 0.5) * 2.0
    
    is_portoro_border = (x < 0.12) | (x > 0.88)
    is_bronze_divider = (np.abs(x - 0.12) < 0.012) | (np.abs(x - 0.88) < 0.012) | (np.abs(x - 0.5) < 0.008)
    
    fbm_flow = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/2, seed=505)
    fbm_veins = create_fbm_noise(res, res, octaves=5, persistence=0.6, scale=res/8, seed=606)
    
    cipollino_waves = np.sin((mirror_x * 8.0 + y * 6.0 + fbm_flow * 3.0) * np.pi) * 0.5 + 0.5
    cipollino_micro = np.sin((mirror_x * 32.0 + fbm_veins * 6.0) * np.pi) * 0.5 + 0.5
    
    portoro_gold_veins = (np.abs(np.sin(fbm_veins * 16.0 * np.pi + y * 8.0)) > 0.88) * (fbm_flow > 0.4)
    
    c_cip_light = np.array([136, 183, 164], dtype=np.float32)
    c_cip_dark = np.array([49, 90, 75], dtype=np.float32)
    c_cip_white = np.array([242, 247, 244], dtype=np.float32)
    c_portoro_black = np.array([24, 24, 26], dtype=np.float32)
    c_portoro_gold = np.array([212, 175, 55], dtype=np.float32)
    c_bronze = np.array([158, 120, 66], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        cip_col = c_cip_dark[c] * (1.0 - cipollino_waves) + c_cip_light[c] * cipollino_waves
        cip_col = cip_col * (0.85 + cipollino_micro * 0.15) + c_cip_white[c] * (cipollino_waves**4.0 * 0.35)
        portoro_col = c_portoro_black[c] + c_portoro_gold[c] * portoro_gold_veins
        base = np.where(is_portoro_border, portoro_col, cip_col)
        base = np.where(is_bronze_divider, c_bronze[c] * (0.90 + fbm_veins * 0.2), base)
        bc[:, :, c] = base
        
    height = 0.55 + is_bronze_divider * 0.05 + cipollino_waves * 0.03 + fbm_flow * 0.02
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.2, flip_green=True)
    
    roughness = 0.14 + cipollino_micro * 0.04
    roughness = np.where(is_portoro_border, 0.11, roughness)
    roughness = np.where(is_bronze_divider, 0.22, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_bronze_divider, 0.94, np.where(is_portoro_border & (portoro_gold_veins > 0.5), 0.65, 0.0))
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - is_bronze_divider * 0.15
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8
    }

def generate_byzantine_gilded_smalti(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 4: T_Cathedral_ByzantineApse_GildedSmalti ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    tess_scale = 32.0
    tx = (x * tess_scale) % 1.0 - 0.5
    ty = (y * tess_scale) % 1.0 - 0.5
    tess_id_x = np.floor(x * tess_scale)
    tess_id_y = np.floor(y * tess_scale)
    
    np.random.seed(707)
    cell_seed = np.sin(tess_id_x * 12.9898 + tess_id_y * 78.233) * 43758.5453
    cell_rand = cell_seed - np.floor(cell_seed)
    
    tess_dist = np.maximum(np.abs(tx), np.abs(ty))
    grout = tess_dist > 0.42
    
    is_cross = ((np.abs(x - 0.5) < 0.08) & (y > 0.20) & (y < 0.80)) | ((np.abs(y - 0.40) < 0.08) & (x > 0.25) & (x < 0.75))
    is_lapis_border = (x < 0.12) | (x > 0.88) | (y < 0.12) | (y > 0.88)
    
    fbm = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/32, seed=808)
    
    c_gold_smalti = np.array([230, 186, 71], dtype=np.float32)
    c_gold_hi = np.array([255, 242, 168], dtype=np.float32)
    c_lapis = np.array([20, 52, 114], dtype=np.float32)
    c_lapis_deep = np.array([11, 30, 74], dtype=np.float32)
    c_cross_crimson = np.array([150, 32, 42], dtype=np.float32)
    c_mortar = np.array([138, 133, 125], dtype=np.float32)
    
    facet_tilt_x = np.sin(cell_rand * 2.0 * np.pi) * 0.35
    facet_tilt_y = np.cos(cell_rand * 2.0 * np.pi) * 0.35
    tessera_facet = tx * facet_tilt_x + ty * facet_tilt_y
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        gold_val = c_gold_smalti[c] * (0.85 + cell_rand * 0.25 + tessera_facet * 0.2) + c_gold_hi[c] * (tessera_facet > 0.1) * 0.15
        lapis_val = c_lapis[c] * (0.85 + cell_rand * 0.3) + c_lapis_deep[c] * (1.0 - cell_rand * 0.3)
        cross_val = c_cross_crimson[c] * (0.90 + cell_rand * 0.2)
        
        base = np.where(is_lapis_border, lapis_val, gold_val)
        base = np.where(is_cross, cross_val, base)
        base = np.where(grout, c_mortar[c], base)
        bc[:, :, c] = base
        
    height = np.where(grout, 0.10, 0.55 + tessera_facet * 0.15 + (1.0 - tess_dist / 0.42) * 0.08)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.5, flip_green=True)
    
    roughness = np.where(grout, 0.88, 0.06 + cell_rand * 0.08)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    is_gold_tile = (~is_lapis_border) & (~is_cross) & (~grout)
    metallic = np.where(is_gold_tile, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(grout, 0.45, 0.95)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_gold_tile, 0.95, np.where(~grout, 0.75, 0.0))
    sheen_uint8 = (sheen * 255.0).clip(0, 255).astype(np.uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_baptistery_twelve_fold_rosace(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 5: T_Cathedral_Baptistery_TwelveFoldRosace ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    cx = x - 0.5
    cy = y - 0.5
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    star_12 = np.cos(angle * 12.0) * 0.12 + 0.35
    is_star_ring = (radius <= star_12) & (radius > 0.18)
    is_center_medallion = radius <= 0.18
    is_outer_ring = (radius > star_12) & (radius <= 0.48)
    
    is_brass_ribbon = (np.abs(radius - 0.18) < 0.01) | (np.abs(radius - star_12) < 0.012) | (np.abs(radius - 0.48) < 0.012)
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=909)
    fbm_nacre = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=1010)
    
    c_jasper = np.array([162, 44, 41], dtype=np.float32)
    c_lapis = np.array([27, 59, 111], dtype=np.float32)
    c_nacre = np.array([245, 243, 247], dtype=np.float32)
    c_carrara = np.array([250, 250, 248], dtype=np.float32)
    c_brass = np.array([212, 175, 55], dtype=np.float32)
    c_grout = np.array([145, 140, 135], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        field_val = c_carrara[c] * (0.95 + fbm * 0.08)
        star_alt = np.sin(angle * 12.0) > 0.0
        star_val = np.where(star_alt, c_jasper[c], c_lapis[c]) * (0.9 + fbm * 0.2)
        nacre_val = c_nacre[c] * (0.92 + fbm_nacre * 0.16)
        
        base = np.where(is_outer_ring, field_val, star_val)
        base = np.where(is_center_medallion, nacre_val, base)
        base = np.where(is_brass_ribbon, c_brass[c] * 1.1, base)
        bc[:, :, c] = base
        
    height = 0.55 + is_center_medallion * 0.12 + is_brass_ribbon * 0.08 + (radius < 0.48) * 0.04
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.4, flip_green=True)
    
    roughness = 0.14 + fbm * 0.04
    roughness = np.where(is_center_medallion, 0.08, roughness)
    roughness = np.where(is_brass_ribbon, 0.20, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_brass_ribbon, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - is_brass_ribbon * 0.15
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_center_medallion, 0.95, 0.40)
    sheen_uint8 = (sheen * 255.0).clip(0, 255).astype(np.uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_cloister_worn_travertine(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 6: T_Cathedral_CloisterWalk_WornTravertine ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    slab_scale = 2.0
    sx = (x * slab_scale) % 1.0
    sy = (y * slab_scale) % 1.0
    
    edge_d = np.minimum(np.minimum(sx, 1.0 - sx), np.minimum(sy, 1.0 - sy))
    grout = np.clip(1.0 - edge_d / 0.035, 0.0, 1.0) ** 1.8
    slab_wear = (np.sin(sx * np.pi) * np.sin(sy * np.pi)) ** 0.35
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=1111)
    fbm_pits = create_fbm_noise(res, res, octaves=5, persistence=0.65, scale=res/16, seed=1212)
    
    is_travertine_pit = (fbm_pits > 0.72) & (grout < 0.2)
    
    corner_d = np.sqrt(np.minimum(sx, 1.0 - sx)**2 + np.minimum(sy, 1.0 - sy)**2)
    is_corner_medallion = corner_d < 0.08
    
    c_travertine = np.array([230, 223, 211], dtype=np.float32)
    c_pit_color = np.array([148, 134, 118], dtype=np.float32)
    c_majolica = np.array([30, 63, 102], dtype=np.float32)
    c_gold = np.array([212, 175, 55], dtype=np.float32)
    c_mortar = np.array([120, 114, 104], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        trav_val = c_travertine[c] * (0.90 + slab_wear * 0.15 + fbm * 0.08)
        trav_val = np.where(is_travertine_pit, c_pit_color[c] * 0.9, trav_val)
        trav_val = np.where(is_corner_medallion, c_majolica[c] * 1.1 + c_gold[c] * 0.2, trav_val)
        base = trav_val * (1.0 - grout) + c_mortar[c] * grout
        bc[:, :, c] = base
        
    height = (slab_wear * 0.65) * (1.0 - grout) - is_travertine_pit * 0.25 + is_corner_medallion * 0.10
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.8, flip_green=True)
    
    roughness = 0.32 + fbm * 0.08 - slab_wear * 0.10
    roughness = np.where(is_travertine_pit, 0.75, roughness)
    roughness = np.where(is_corner_medallion, 0.08, roughness)
    roughness = np.where(grout > 0.4, 0.88, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_corner_medallion, 0.35, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - grout * 0.5 - is_travertine_pit * 0.35
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8
    }

def main():
    root = Path(r"C:\EnvironmentPortfolio")
    out_dir = root / "BS_GodFile" / "Content" / "Textures" / "Grand_Roman_Cathedral_Tiles"
    
    print("==================================================================")
    print("GRAND ROMAN CATHEDRAL & COSMATESQUE PAVEMENT PBR SYNTHESIS")
    print("==================================================================")
    
    suites = [
        (out_dir, "T_Cathedral_Cosmati_QuincunxGuilloche", generate_cosmati_quincunx_guilloche),
        (out_dir, "T_Cathedral_OpusSectile_ImperialPorphyry", generate_opus_sectile_porphyry),
        (out_dir, "T_Cathedral_BasilicaNave_BookmatchedCipollino", generate_bookmatched_cipollino),
        (out_dir, "T_Cathedral_ByzantineApse_GildedSmalti", generate_byzantine_gilded_smalti),
        (out_dir, "T_Cathedral_Baptistery_TwelveFoldRosace", generate_baptistery_twelve_fold_rosace),
        (out_dir, "T_Cathedral_CloisterWalk_WornTravertine", generate_cloister_worn_travertine),
    ]
    
    total_maps = 0
    for d, name, func in suites:
        maps = func(res=2048)
        save_suite(d, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} Grand Roman Cathedral suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directory: {out_dir}")

if __name__ == "__main__":
    main()
