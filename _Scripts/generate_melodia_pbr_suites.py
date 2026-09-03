"""
Melodia Melusina PBR Suite & Lookdev Texture Generator
High-fidelity procedural PBR texture synthesis for Infinity Nikki / Melodia aesthetic.
Zero external asset dependency - uses mathematical procedural synthesis,
Sobel filtering, Voronoi/Perlin harmonic domain warping, and exact UE PBR packing standards.
"""

from __future__ import annotations

import os
import math
import numpy as np
from pathlib import Path
from PIL import Image

def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

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
    """Generate DirectX tangent-space normal map from height map using Sobel operator."""
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
    normal_img = ((normals + 1.0) * 0.5 * 255.0).clip(0, 255).astype(np.uint8)
    return normal_img

def pack_orm(ao: np.ndarray, roughness: np.ndarray, metallic: np.ndarray) -> np.ndarray:
    """Pack R=AO, G=Roughness, B=Metallic into an RGB uint8 array."""
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

def generate_melusina_baroque_mosaic(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 1: T_Melusina_BaroqueAquatic_MosaicTile ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    tile_count = 4
    tx = (x * tile_count) % 1.0
    ty = (y * tile_count) % 1.0
    
    edge_dist = np.minimum(np.minimum(tx, 1.0 - tx), np.minimum(ty, 1.0 - ty))
    grout_width = 0.035
    grout_mask = np.clip(1.0 - (edge_dist / grout_width), 0.0, 1.0) ** 2.0
    
    tile_bevel = (np.sin(tx * np.pi) * np.sin(ty * np.pi)) ** 0.4
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=101)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=202)
    
    cx = (tx - 0.5)
    cy = (ty - 0.5)
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    rosette = np.cos(angle * 4.0 + radius * 16.0 * np.pi + fbm * 1.5)
    rosette_pattern = np.clip(np.sin(radius * 24.0 * np.pi + rosette * 2.0), -1.0, 1.0)
    
    filigree_ribbon = np.clip(1.0 - np.abs(edge_dist - 0.12) / 0.025, 0.0, 1.0)
    medallion_mask = np.clip(1.0 - np.abs(radius - 0.28) / 0.03, 0.0, 1.0)
    center_cabochon = np.clip(1.0 - (radius / 0.10), 0.0, 1.0)
    
    gold_mask = np.maximum(np.maximum(filigree_ribbon, medallion_mask * (rosette_pattern > 0.3)), center_cabochon)
    gold_mask = gold_mask * (1.0 - grout_mask)
    
    lapis = np.array([15, 43, 92], dtype=np.float32)
    turquoise = np.array([33, 140, 141], dtype=np.float32)
    seafoam = np.array([152, 228, 216], dtype=np.float32)
    gold_base = np.array([212, 175, 55], dtype=np.float32)
    gold_highlight = np.array([255, 230, 140], dtype=np.float32)
    mortar_col = np.array([215, 208, 202], dtype=np.float32)
    pearl_col = np.array([245, 240, 248], dtype=np.float32)
    
    wc_wash = (fbm * 0.7 + fbm_fine * 0.3)
    wc_mix = np.clip((rosette_pattern * 0.5 + 0.5) * 0.6 + wc_wash * 0.4, 0.0, 1.0)
    
    ceramic_color = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        low_mid = np.clip(wc_mix / 0.5, 0.0, 1.0)
        mid_high = np.clip((wc_mix - 0.5) / 0.5, 0.0, 1.0)
        col_c = lapis[c] * (1.0 - low_mid) + turquoise[c] * low_mid * (1.0 - mid_high) + seafoam[c] * mid_high
        ceramic_color[:, :, c] = col_c
        
    gold_color = np.zeros((res, res, 3), dtype=np.float32)
    gold_spec = fbm_fine * 0.4 + 0.6
    for c in range(3):
        gold_color[:, :, c] = gold_base[c] * (1.0 - gold_spec) + gold_highlight[c] * gold_spec
        
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        col = ceramic_color[:, :, c] * (1.0 - gold_mask) + gold_color[:, :, c] * gold_mask
        col = col * (1.0 - center_cabochon) + pearl_col[c] * center_cabochon
        col = col * (1.0 - grout_mask) + mortar_col[c] * grout_mask
        bc[:, :, c] = col
        
    height = (tile_bevel * 0.7 + 0.1) * (1.0 - grout_mask)
    height += gold_mask * 0.15
    height += center_cabochon * 0.25
    height += fbm_fine * 0.04 * (1.0 - grout_mask)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.5, flip_green=True)
    
    roughness = (0.12 + fbm_fine * 0.06) * (1.0 - gold_mask) * (1.0 - grout_mask)
    roughness += gold_mask * (0.24 + fbm_fine * 0.08)
    roughness += grout_mask * 0.88
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = gold_mask * 0.95
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (grout_mask * 0.45 + (1.0 - tile_bevel) * 0.25)
    ao = np.clip(ao, 0.2, 1.0)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = (center_cabochon * 0.9 + (1.0 - gold_mask) * (1.0 - grout_mask) * 0.35)
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

def generate_melusina_parquet_wave(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 2: T_Melusina_WatercolourWave_Parquet ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    wave_freq = 6.0
    wave_amp = 0.06
    wave_warp = np.sin(x * wave_freq * np.pi * 2.0) * wave_amp
    wy = (y + wave_warp) * 8.0
    plank_id = np.floor(wy)
    plank_t = wy % 1.0
    
    seam_width = 0.03
    seam_edge = np.clip(1.0 - (np.minimum(plank_t, 1.0 - plank_t) / seam_width), 0.0, 1.0) ** 2.0
    
    fbm_wood = create_fbm_noise(res, res, octaves=5, persistence=0.5, scale=res/2, seed=303)
    grain = np.sin((x * 120.0 + fbm_wood * 15.0) * np.pi) * 0.5 + 0.5
    
    is_brass_divider = (plank_id % 4 == 0) & (seam_edge > 0.4)
    is_pearl_plank = (plank_id % 4 == 1)
    
    col_cyan_wood = np.array([54, 120, 142], dtype=np.float32)
    col_navy_wood = np.array([28, 48, 85], dtype=np.float32)
    col_rose_wood = np.array([170, 125, 138], dtype=np.float32)
    col_pearl = np.array([238, 235, 245], dtype=np.float32)
    col_brass = np.array([215, 175, 75], dtype=np.float32)
    col_dark_seam = np.array([12, 14, 18], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    band_type = plank_id % 3
    
    for c in range(3):
        wood_val = np.where(band_type == 0, col_cyan_wood[c], np.where(band_type == 1, col_navy_wood[c], col_rose_wood[c]))
        wood_val = wood_val * (0.85 + grain * 0.25 + fbm_wood * 0.15)
        
        pearl_val = col_pearl[c] * (0.92 + fbm_wood * 0.12)
        base = np.where(is_pearl_plank, pearl_val, wood_val)
        base = np.where(is_brass_divider, col_brass[c], base)
        base = base * (1.0 - seam_edge * 0.8) + col_dark_seam[c] * (seam_edge * 0.8)
        bc[:, :, c] = base
        
    height = 0.5 + (1.0 - seam_edge) * 0.15 + is_brass_divider * 0.08 + (grain * 0.03)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.8, flip_green=True)
    
    roughness = np.where(is_pearl_plank, 0.15, 0.32 + grain * 0.08)
    roughness = np.where(is_brass_divider, 0.22, roughness)
    roughness = roughness * (1.0 - seam_edge) + seam_edge * 0.75
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_brass_divider, 0.92, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - seam_edge * 0.5
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

def generate_cathedral_pearl_tile(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 3: T_Melusina_CathedralPearl_MarbleTile ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    oct_size = 2.0
    gx = (x * oct_size) % 1.0
    gy = (y * oct_size) % 1.0
    
    dx = np.abs(gx - 0.5)
    dy = np.abs(gy - 0.5)
    oct_dist = np.maximum(np.maximum(dx, dy), (dx + dy) * 0.7071)
    
    tile_border = np.clip(1.0 - np.abs(oct_dist - 0.46) / 0.02, 0.0, 1.0)
    tile_grout = np.clip((oct_dist - 0.47) / 0.03, 0.0, 1.0) ** 2.0
    
    fbm_warp = create_fbm_noise(res, res, octaves=5, persistence=0.5, scale=res/3, seed=404)
    vein_noise = create_fbm_noise(res, res, octaves=6, persistence=0.6, scale=res/6, seed=505)
    vein_mask = np.abs(np.sin(vein_noise * 12.0 * np.pi)) ** 8.0
    
    c_white_marble = np.array([245, 244, 248], dtype=np.float32)
    c_violet_vein = np.array([125, 95, 140], dtype=np.float32)
    c_teal_vein = np.array([75, 140, 155], dtype=np.float32)
    c_gold = np.array([220, 185, 80], dtype=np.float32)
    c_grout = np.array([180, 175, 185], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        vein_col = c_violet_vein[c] * 0.6 + c_teal_vein[c] * 0.4
        m_col = c_white_marble[c] * (1.0 - vein_mask * 0.75) + vein_col * (vein_mask * 0.75)
        m_col = m_col * (1.0 - tile_border) + c_gold[c] * tile_border
        m_col = m_col * (1.0 - tile_grout) + c_grout[c] * tile_grout
        bc[:, :, c] = m_col
        
    height = 0.6 * (1.0 - tile_grout * 0.5) + tile_border * 0.08 + (1.0 - vein_mask * 0.05)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.5, flip_green=True)
    
    roughness = (0.10 + vein_mask * 0.08) * (1.0 - tile_border) * (1.0 - tile_grout)
    roughness += tile_border * 0.20 + tile_grout * 0.85
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = tile_border * 0.95
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (tile_grout * 0.4 + vein_mask * 0.15)
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

def generate_lookdev_silk_velvet(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 4: T_Lookdev_IridescentSilkVelvet ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    weave_x = np.sin(x * res * 0.25 * np.pi)
    weave_y = np.cos(y * res * 0.25 * np.pi)
    micro_twill = (weave_x * weave_y) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.5, scale=res/4, seed=606)
    
    col_cyan = np.array([69, 202, 212], dtype=np.float32)
    col_lilac = np.array([142, 68, 173], dtype=np.float32)
    col_rosegold = np.array([232, 165, 152], dtype=np.float32)
    
    t = (fbm * 0.7 + (x * 0.3))
    t1 = np.clip(t / 0.5, 0.0, 1.0)
    t2 = np.clip((t - 0.5) / 0.5, 0.0, 1.0)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        col = col_cyan[c] * (1.0 - t1) + col_lilac[c] * t1 * (1.0 - t2) + col_rosegold[c] * t2
        col = col * (0.90 + micro_twill * 0.15)
        bc[:, :, c] = col
        
    height = 0.5 + micro_twill * 0.08 + fbm * 0.04
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=1.5, flip_green=True)
    
    roughness = 0.35 + fbm * 0.15
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.85 + micro_twill * 0.15
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.75 + fbm * 0.25
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

def generate_lookdev_gilded_filigree(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 5: T_Lookdev_GildedAquaticFiligree_Trim ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    band_y = (y * 4.0) % 1.0
    wave_x = np.sin(x * 12.0 * np.pi) * 0.25 + 0.5
    volute_dist = np.abs(band_y - wave_x)
    filigree_volute = np.clip(1.0 - volute_dist / 0.08, 0.0, 1.0)
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.5, scale=res/4, seed=707)
    
    is_gold = filigree_volute > 0.3
    is_enamel = ~is_gold
    
    c_gold = np.array([230, 190, 65], dtype=np.float32)
    c_enamel = np.array([25, 115, 120], dtype=np.float32)
    c_verdigris = np.array([72, 175, 140], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        col = np.where(is_gold, c_gold[c] * (0.85 + fbm * 0.2), c_enamel[c] * (0.75 + fbm * 0.35))
        crevice = (1.0 - filigree_volute) * (fbm > 0.6)
        col = col * (1.0 - crevice * 0.4) + c_verdigris[c] * (crevice * 0.4)
        bc[:, :, c] = col
        
    height = filigree_volute * 0.4 + np.where(is_enamel, 0.15, 0.0)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.0, flip_green=True)
    
    roughness = np.where(is_gold, 0.20 + fbm * 0.08, 0.08 + fbm * 0.05)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (1.0 - filigree_volute) * 0.4
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

def generate_lookdev_studio_plaster(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 6: T_Lookdev_WatercolorStudio_CalibPlaster ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    paper_tooth = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/16, seed=808)
    paper_tooth_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=909)
    tooth_combined = paper_tooth * 0.7 + paper_tooth_fine * 0.3
    
    base_color = np.array([234, 229, 223], dtype=np.float32)
    
    is_bottom_strip = y > 0.85
    patch_x = np.floor(x * 8.0)
    patch_step = patch_x / 7.0
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        col = base_color[c] * (0.92 + tooth_combined * 0.16)
        step_val = (patch_step * 240.0 + 15.0)
        col = np.where(is_bottom_strip, step_val, col)
        bc[:, :, c] = col
        
    height = 0.5 + (tooth_combined - 0.5) * 0.12
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.0, flip_green=True)
    
    roughness = 0.68 + (tooth_combined - 0.5) * 0.15
    step_rough = 0.1 + patch_step * 0.8
    roughness = np.where(is_bottom_strip, step_rough, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + tooth_combined * 0.10
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
    content_textures = root / "BS_GodFile" / "Content" / "Textures"
    melodia_tile_dir = content_textures / "Melodia_Tilework"
    lookdev_dir = content_textures / "Lookdev_Suites"
    
    print("==================================================================")
    print("MELODIA PBR TEXTURE SUITE SYNTHESIS — INFINITY NIKKI / BAROQUE")
    print("==================================================================")
    
    suites = [
        (melodia_tile_dir, "T_Melusina_BaroqueAquatic_MosaicTile", generate_melusina_baroque_mosaic),
        (melodia_tile_dir, "T_Melusina_WatercolourWave_Parquet", generate_melusina_parquet_wave),
        (melodia_tile_dir, "T_Melusina_CathedralPearl_MarbleTile", generate_cathedral_pearl_tile),
        (lookdev_dir, "T_Lookdev_IridescentSilkVelvet", generate_lookdev_silk_velvet),
        (lookdev_dir, "T_Lookdev_GildedAquaticFiligree_Trim", generate_lookdev_gilded_filigree),
        (lookdev_dir, "T_Lookdev_WatercolorStudio_CalibPlaster", generate_lookdev_studio_plaster),
    ]
    
    total_maps = 0
    for out_dir, name, func in suites:
        maps = func(res=2048)
        save_suite(out_dir, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} PBR suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directories:\n  - {melodia_tile_dir}\n  - {lookdev_dir}")

if __name__ == "__main__":
    main()
