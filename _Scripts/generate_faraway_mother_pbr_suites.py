"""
P1 Faraway Mother Haute-Couture PBR Material Suites
High-fidelity Infinity Nikki / Baroque Musical Aquatic Material Generator
Strict UE PBR Standards: 2048x2048 POT, DirectX Normals, ORM Packing (R=AO, G=Roughness, B=Metallic)
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

# =============================================================================
# 6 HAUTE-COUTURE SUITES FOR P1 FARAWAY MOTHER
# =============================================================================

def generate_gown_celestial_jacquard(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 1: T_FarawayMother_Gown_CelestialSilkJacquard ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    weave_x = np.sin(x * res * 0.5 * np.pi)
    weave_y = np.cos(y * res * 0.5 * np.pi)
    twill = (weave_x * weave_y) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.52, scale=res/4, seed=111)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/32, seed=222)
    
    staff_lines = np.abs(np.sin(y * 20.0 * np.pi + fbm * 1.2)) < 0.08
    damask_droplet = np.sin(x * 12.0 * np.pi + np.cos(y * 8.0 * np.pi)) * np.cos(y * 12.0 * np.pi)
    jacquard_pattern = np.clip(damask_droplet * 1.5 + fbm * 0.4, 0.0, 1.0)
    
    embroidery_band = (y > 0.82) & (np.sin(x * 32.0 * np.pi + fbm_fine * 8.0) > -0.2)
    is_gold_thread = (embroidery_band | (jacquard_pattern > 0.75))
    
    c_ivory = np.array([245, 244, 240], dtype=np.float32)
    c_lavender = np.array([164, 145, 199], dtype=np.float32)
    c_seafoam = np.array([120, 201, 207], dtype=np.float32)
    c_gold = np.array([223, 186, 82], dtype=np.float32)
    c_gold_hi = np.array([255, 235, 150], dtype=np.float32)
    
    wc_shift = fbm * 0.6 + (x * 0.4)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        wc_col = c_ivory[c] * (1.0 - fbm * 0.35) + c_lavender[c] * (wc_shift * 0.35) + c_seafoam[c] * ((1.0 - wc_shift) * 0.35)
        base = wc_col * (0.92 + twill * 0.08 + jacquard_pattern * 0.12)
        gold_val = c_gold[c] * (0.85 + fbm_fine * 0.3) + c_gold_hi[c] * (fbm_fine * 0.2)
        base = np.where(is_gold_thread, gold_val, base)
        bc[:, :, c] = base
        
    height = 0.5 + twill * 0.04 + jacquard_pattern * 0.10 + np.where(is_gold_thread, 0.25, 0.0)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.2, flip_green=True)
    
    roughness = np.where(is_gold_thread, 0.26 + fbm_fine * 0.1, 0.32 + jacquard_pattern * 0.12)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_thread, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.88 + jacquard_pattern * 0.12 - np.where(is_gold_thread, 0.0, 0.05)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.80 + fbm * 0.20
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

def generate_veil_aquatic_lace(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 2: T_FarawayMother_Veil_AquaticLullabyLace ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/8, seed=333)
    fbm_thread = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=444)
    
    hex_scale = 48.0
    hx = (x * hex_scale) % 1.0 - 0.5
    hy = (y * hex_scale * 0.866) % 1.0 - 0.5
    hex_dist = np.sqrt(hx**2 + hy**2)
    tulle_net = np.clip(1.0 - np.abs(hex_dist - 0.35) / 0.08, 0.0, 1.0)
    
    willow_wave = np.sin(x * 8.0 * np.pi + np.cos(y * 4.0 * np.pi)) * np.cos(y * 12.0 * np.pi + fbm * 2.0)
    lace_fronds = np.clip(willow_wave * 2.0 + fbm * 0.5, 0.0, 1.0) ** 1.8
    
    scallop = np.sin(x * 16.0 * np.pi) * 0.06 + 0.88
    hem_mask = np.clip(1.0 - (y - scallop) / 0.04, 0.0, 1.0)
    
    alpha = np.clip(tulle_net * 0.30 + lace_fronds * 0.90 + (y > 0.88) * 0.85, 0.0, 1.0)
    alpha_uint8 = (alpha * 255.0).clip(0, 255).astype(np.uint8)
    
    c_lace_white = np.array([245, 242, 250], dtype=np.float32)
    c_lilac_fog = np.array([208, 200, 228], dtype=np.float32)
    c_pale_gold = np.array([232, 208, 141], dtype=np.float32)
    
    is_gold_contour = (lace_fronds > 0.65) & (lace_fronds < 0.80)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        col = c_lace_white[c] * (0.94 + fbm_thread * 0.12) * (1.0 - fbm * 0.15) + c_lilac_fog[c] * (fbm * 0.15)
        col = np.where(is_gold_contour, c_pale_gold[c], col)
        bc[:, :, c] = col
        
    height = alpha * 0.5 + lace_fronds * 0.3 + fbm_thread * 0.08
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.6, flip_green=True)
    
    roughness = np.where(is_gold_contour, 0.24, 0.42 + fbm_thread * 0.1)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_contour, 0.88, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + (1.0 - alpha) * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Alpha": alpha_uint8,
        "Mask": alpha_uint8
    }

def generate_corset_gilded_brocade(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 3: T_FarawayMother_Corset_GildedAcanthusBrocade ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    moire_1 = np.sin((x * 40.0 + np.sin(y * 8.0 * np.pi) * 2.0) * np.pi)
    moire_2 = np.sin((x * 42.0 + np.cos(y * 6.0 * np.pi) * 2.0) * np.pi)
    moire = (moire_1 * moire_2) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.52, scale=res/4, seed=555)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=666)
    
    bx = (x * 5.0) % 1.0
    boning_rib = np.clip(1.0 - np.abs(bx - 0.5) / 0.12, 0.0, 1.0) ** 0.5
    
    acanthus_scroll = np.sin(y * 16.0 * np.pi + np.cos(x * 10.0 * np.pi) * 3.0) * np.cos(x * 8.0 * np.pi)
    is_gold_filigree = (boning_rib > 0.6) | (acanthus_scroll > 0.45)
    
    opal_dist_x = np.abs(x - 0.5)
    opal_dist_y = np.abs((y * 6.0) % 1.0 - 0.5)
    opal_radius = np.sqrt((opal_dist_x * 5.0)**2 + (opal_dist_y)**2)
    is_opal = opal_radius < 0.22
    opal_dome = np.clip(1.0 - (opal_radius / 0.22), 0.0, 1.0) ** 0.5
    
    c_ivory_moire = np.array([242, 238, 230], dtype=np.float32)
    c_gold_boning = np.array([228, 192, 70], dtype=np.float32)
    c_gold_dark = np.array([170, 130, 40], dtype=np.float32)
    c_opal_base = np.array([195, 235, 245], dtype=np.float32)
    c_opal_fire = np.array([255, 180, 200], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_ivory_moire[c] * (0.90 + moire * 0.16 + fbm * 0.08)
        gold_val = c_gold_boning[c] * (0.85 + fbm_fine * 0.3) + c_gold_dark[c] * (1.0 - fbm_fine * 0.3)
        base = np.where(is_gold_filigree, gold_val, base)
        opal_val = c_opal_base[c] * (1.0 - fbm * 0.5) + c_opal_fire[c] * (fbm * 0.5)
        base = np.where(is_opal, opal_val, base)
        bc[:, :, c] = base
        
    height = 0.5 + moire * 0.03 + boning_rib * 0.20 + is_gold_filigree * 0.12 + is_opal * opal_dome * 0.35
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.4, flip_green=True)
    
    roughness = np.where(is_opal, 0.08, np.where(is_gold_filigree, 0.22, 0.38 + moire * 0.1))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_filigree, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (1.0 - boning_rib) * 0.35 - (is_gold_filigree == 0) * (is_opal == 0) * 0.1
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

def generate_ornament_musicbox_jewel(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 4: T_FarawayMother_Ornament_NacreMusicBoxJewel ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    cx = x - 0.5
    cy = y - 0.5
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=777)
    
    gear_teeth = np.cos(angle * 16.0)
    is_gear_ring = (radius > 0.38) & (radius < 0.48) & (gear_teeth > -0.2)
    
    is_nacre_disc = (radius > 0.18) & (radius <= 0.38)
    nacre_wave = np.sin(radius * 36.0 * np.pi + angle * 8.0 + fbm * 2.0)
    
    is_gem = radius <= 0.18
    facet_angle = (angle + np.pi) % (np.pi / 4.0) - (np.pi / 8.0)
    facet_plane = np.cos(facet_angle) * (1.0 - radius / 0.18)
    
    c_brass = np.array([212, 172, 59], dtype=np.float32)
    c_nacre = np.array([244, 241, 250], dtype=np.float32)
    c_nacre_tint = np.array([215, 235, 245], dtype=np.float32)
    c_gem_light = np.array([85, 210, 245], dtype=np.float32)
    c_gem_deep = np.array([20, 85, 125], dtype=np.float32)
    c_black_shadow = np.array([15, 18, 24], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_black_shadow[c]
        base = np.where(is_gear_ring, c_brass[c] * (0.90 + fbm * 0.2), base)
        nacre_col = c_nacre[c] * (1.0 - fbm * 0.2) + c_nacre_tint[c] * (fbm * 0.2)
        base = np.where(is_nacre_disc, nacre_col * (0.92 + nacre_wave * 0.12), base)
        gem_col = c_gem_deep[c] * (1.0 - facet_plane) + c_gem_light[c] * facet_plane
        base = np.where(is_gem, gem_col, base)
        bc[:, :, c] = base
        
    height = is_gear_ring * 0.35 + is_nacre_disc * (0.50 + nacre_wave * 0.08) + is_gem * (0.65 + facet_plane * 0.30)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.2, flip_green=True)
    
    roughness = np.where(is_gem, 0.06, np.where(is_nacre_disc, 0.12, np.where(is_gear_ring, 0.20, 0.85)))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gear_ring, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(is_gem | is_nacre_disc | is_gear_ring, 0.95, 0.35)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_nacre_disc, 0.95, np.where(is_gem, 0.75, 0.0))
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

def generate_mantle_nightsky_velvet(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 5: T_FarawayMother_Mantle_NightSkyVelvet ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm_sky = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/3, seed=888)
    fbm_fuzz = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=999)
    
    aurora_flow = np.sin((x * 3.0 + y * 2.0 + fbm_sky * 2.0) * np.pi) * 0.5 + 0.5
    
    star_grid_x = (x * 16.0) % 1.0 - 0.5
    star_grid_y = (y * 16.0) % 1.0 - 0.5
    star_dist = np.sqrt(star_grid_x**2 + star_grid_y**2)
    stars = (star_dist < 0.08) & (fbm_sky > 0.45)
    
    stave_wave = np.abs(np.sin(y * 24.0 * np.pi + fbm_sky * 3.0)) < 0.02
    is_gold_staves = (stars | stave_wave)
    
    c_midnight = np.array([11, 19, 43], dtype=np.float32)
    c_indigo = np.array([28, 37, 65], dtype=np.float32)
    c_aurora = np.array([72, 202, 228], dtype=np.float32)
    c_gold = np.array([244, 208, 111], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        velvet_col = c_midnight[c] * (1.0 - aurora_flow * 0.5) + c_indigo[c] * (aurora_flow * 0.5) + c_aurora[c] * (aurora_flow * 0.25)
        velvet_col = velvet_col * (0.88 + fbm_fuzz * 0.24)
        base = np.where(is_gold_staves, c_gold[c] * (0.90 + fbm_fuzz * 0.2), velvet_col)
        bc[:, :, c] = base
        
    height = 0.5 + fbm_fuzz * 0.06 + is_gold_staves * 0.15
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=1.8, flip_green=True)
    
    roughness = np.where(is_gold_staves, 0.22, 0.48 + fbm_fuzz * 0.15)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_staves, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + fbm_sky * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_gold_staves, 0.0, 0.90 + fbm_fuzz * 0.10)
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

def generate_cradle_carved_wood(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 6: T_FarawayMother_Cradle_CarvedAlabasterWood ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm_wood = create_fbm_noise(res, res, octaves=5, persistence=0.52, scale=res/2, seed=1010)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=1111)
    
    grain = np.sin((x * 90.0 + fbm_wood * 18.0) * np.pi) * 0.5 + 0.5
    
    scallop_x = (x - 0.5) * 2.0
    scallop_y = (y - 0.5) * 2.0
    scallop_r = np.sqrt(scallop_x**2 + scallop_y**2)
    scallop_a = np.arctan2(scallop_y, scallop_x)
    
    is_carved_medallion = scallop_r < 0.65
    fluted_ribs = np.sin(scallop_a * 12.0) * np.cos(scallop_r * 8.0 * np.pi)
    carved_relief = np.where(is_carved_medallion, fluted_ribs * (1.0 - scallop_r / 0.65), 0.0)
    
    c_limed_oak = np.array([213, 204, 190], dtype=np.float32)
    c_alabaster = np.array([232, 226, 214], dtype=np.float32)
    c_crevice = np.array([98, 78, 56], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        wood = c_limed_oak[c] * (0.90 + grain * 0.20 + fbm_wood * 0.10)
        relief_factor = (carved_relief * 0.5 + 0.5)
        base = np.where(is_carved_medallion, wood * (0.8 + relief_factor * 0.4), wood)
        crevice_mask = (carved_relief < -0.3)
        base = np.where(crevice_mask, c_crevice[c] * 0.9, base)
        bc[:, :, c] = base
        
    height = 0.5 + grain * 0.04 + carved_relief * 0.25 + fbm_fine * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.5, flip_green=True)
    
    roughness = 0.38 + grain * 0.12 - np.where(is_carved_medallion, 0.08, 0.0)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (carved_relief < -0.2) * 0.35 - (grain < 0.2) * 0.1
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
    faraway_dir = root / "BS_GodFile" / "Content" / "Textures" / "FarawayMother_Suites"
    
    print("==================================================================")
    print("P1 FARAWAY MOTHER HAUTE-COUTURE PBR SUITE SYNTHESIS")
    print("==================================================================")
    
    suites = [
        (faraway_dir, "T_FarawayMother_Gown_CelestialSilkJacquard", generate_gown_celestial_jacquard),
        (faraway_dir, "T_FarawayMother_Veil_AquaticLullabyLace", generate_veil_aquatic_lace),
        (faraway_dir, "T_FarawayMother_Corset_GildedAcanthusBrocade", generate_corset_gilded_brocade),
        (faraway_dir, "T_FarawayMother_Ornament_NacreMusicBoxJewel", generate_ornament_musicbox_jewel),
        (faraway_dir, "T_FarawayMother_Mantle_NightSkyVelvet", generate_mantle_nightsky_velvet),
        (faraway_dir, "T_FarawayMother_Cradle_CarvedAlabasterWood", generate_cradle_carved_wood),
    ]
    
    total_maps = 0
    for out_dir, name, func in suites:
        maps = func(res=2048)
        save_suite(out_dir, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} P1 Faraway Mother PBR suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directory: {faraway_dir}")

if __name__ == "__main__":
    main()
