"""
Melusina & Infinity Nikki Haute-Couture Feminine Iridescent PBR Material Generator
Deeply feminine, hyper-iridescent, whimsical watercolor, and baroque musical aquatic aesthetic.
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

def calculate_thin_film_iridescence(phase: np.ndarray) -> np.ndarray:
    """Optical thin-film interference calculating pastel rainbow spectral shift."""
    a = np.array([0.88, 0.85, 0.92], dtype=np.float32)
    b = np.array([0.22, 0.25, 0.20], dtype=np.float32)
    c = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    d = np.array([0.0, 0.33, 0.67], dtype=np.float32)
    
    irid = np.zeros((phase.shape[0], phase.shape[1], 3), dtype=np.float32)
    for ch in range(3):
        irid[:, :, ch] = a[ch] + b[ch] * np.cos(2.0 * np.pi * (c[ch] * phase + d[ch]))
    return (irid * 255.0).clip(0, 255)

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

def generate_siren_opal_scales(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 1: T_Melusina_IridescentSiren_ScaleTessellation ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    scale_count_x = 6.0
    scale_count_y = 12.0
    
    row = np.floor(y * scale_count_y)
    x_offset = np.where(row % 2 == 1, 0.5 / scale_count_x, 0.0)
    
    sx = ((x + x_offset) * scale_count_x) % 1.0 - 0.5
    sy = (y * scale_count_y) % 1.0 - 0.5
    
    scale_radius = np.sqrt(sx**2 + (sy + 0.3)**2)
    is_scale = scale_radius < 0.65
    scale_dome = np.clip(1.0 - (scale_radius / 0.65)**1.5, 0.0, 1.0)
    edge_rim = np.clip(1.0 - np.abs(scale_radius - 0.62) / 0.04, 0.0, 1.0)
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=101)
    fbm_opal = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=202)
    
    phase = fbm * 0.8 + scale_dome * 0.5 + (x * 0.3)
    irid_color = calculate_thin_film_iridescence(phase)
    
    c_rose_gold = np.array([232, 165, 152], dtype=np.float32)
    c_opal_base = np.array([250, 245, 252], dtype=np.float32)
    c_mortar = np.array([235, 225, 235], dtype=np.float32)
    
    dew_x = (x * 32.0) % 1.0 - 0.5
    dew_y = (y * 32.0) % 1.0 - 0.5
    dew_r = np.sqrt(dew_x**2 + dew_y**2)
    dew_mask = (dew_r < 0.18) & (fbm_opal > 0.55) & is_scale
    dew_dome = np.clip(1.0 - (dew_r / 0.18)**2.0, 0.0, 1.0) * dew_mask
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        opal_val = c_opal_base[c] * 0.45 + irid_color[:, :, c] * 0.55
        scale_val = opal_val * (1.0 - edge_rim) + c_rose_gold[c] * (1.1 + fbm_opal * 0.2) * edge_rim
        scale_val = np.where(dew_mask, scale_val * 1.15 + 30.0, scale_val)
        base = np.where(is_scale, scale_val, c_mortar[c])
        bc[:, :, c] = base
        
    height = is_scale * (scale_dome * 0.55 + edge_rim * 0.15 + fbm_opal * 0.04) + dew_dome * 0.25
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.5, flip_green=True)
    
    roughness = np.where(dew_mask, 0.04, np.where(edge_rim > 0.5, 0.22, 0.10 + fbm_opal * 0.06))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(edge_rim > 0.5, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (1.0 - scale_dome) * 0.35 - (is_scale == 0) * 0.3
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.92 + fbm_opal * 0.08
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

def generate_sakura_silk_organza(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 2: T_Melusina_SakuraLullaby_SilkOrganza ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    twill = (np.sin(x * res * 0.5 * np.pi) * np.cos(y * res * 0.5 * np.pi)) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.52, scale=res/4, seed=303)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/32, seed=404)
    
    px = (x * 4.0) % 1.0 - 0.5
    py = (y * 4.0) % 1.0 - 0.5
    p_radius = np.sqrt(px**2 + py**2)
    p_angle = np.arctan2(py, px)
    petal_shape = 0.28 + 0.08 * np.cos(p_angle * 5.0 + fbm * 1.5)
    is_sakura_petal = p_radius < petal_shape
    
    ripple = np.sin(p_radius * 36.0 * np.pi - fbm * 2.0) * 0.5 + 0.5
    petal_rim = np.clip(1.0 - np.abs(p_radius - petal_shape) / 0.03, 0.0, 1.0)
    
    c_organza = np.array([249, 248, 252], dtype=np.float32)
    c_sakura = np.array([255, 183, 197], dtype=np.float32)
    c_coral = np.array([255, 218, 193], dtype=np.float32)
    c_rosegold = np.array([229, 169, 155], dtype=np.float32)
    
    irid_shift = calculate_thin_film_iridescence(fbm * 0.7 + ripple * 0.3)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_organza[c] * 0.75 + irid_shift[:, :, c] * 0.25
        base = base * (0.94 + twill * 0.06 + ripple * 0.08)
        petal_col = c_sakura[c] * (1.0 - p_radius / petal_shape) + c_coral[c] * (p_radius / petal_shape)
        base = np.where(is_sakura_petal, base * 0.35 + petal_col * 0.65, base)
        base = np.where(petal_rim > 0.4, c_rosegold[c] * (1.0 + fbm_fine * 0.2), base)
        bc[:, :, c] = base
        
    height = 0.5 + twill * 0.03 + ripple * 0.06 + is_sakura_petal * 0.12 + petal_rim * 0.20
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.2, flip_green=True)
    
    roughness = np.where(petal_rim > 0.4, 0.24, 0.30 + twill * 0.08)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(petal_rim > 0.4, 0.92, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + ripple * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.90 + ripple * 0.10
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

def generate_baroque_tiara_filigree(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 3: T_Melusina_BaroqueTiara_RoseGoldFiligree ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=505)
    fbm_gem = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=606)
    
    volute_y = (y * 3.0) % 1.0
    volute_curve = np.sin(x * 6.0 * np.pi) * 0.28 + 0.5
    is_filigree = np.clip(1.0 - np.abs(volute_y - volute_curve) / 0.08, 0.0, 1.0) ** 0.5
    
    gem_x = (x * 6.0) % 1.0 - 0.5
    gem_y = (y * 3.0) % 1.0 - 0.5
    gem_r = np.sqrt(gem_x**2 + (gem_y * 1.5)**2)
    is_gem = gem_r < 0.22
    gem_facet = np.clip(1.0 - (gem_r / 0.22), 0.0, 1.0)
    
    pearl_y = (y * 3.0 + 0.5) % 1.0 - 0.5
    pearl_r = np.sqrt(gem_x**2 + (pearl_y * 1.2)**2)
    is_pearl = pearl_r < 0.16
    pearl_dome = np.clip(1.0 - (pearl_r / 0.16)**2.0, 0.0, 1.0)
    
    c_rosegold = np.array([232, 180, 168], dtype=np.float32)
    c_morganite = np.array([255, 198, 199], dtype=np.float32)
    c_enamel = np.array([226, 109, 124], dtype=np.float32)
    c_pearl = np.array([253, 251, 247], dtype=np.float32)
    c_bg = np.array([20, 18, 24], dtype=np.float32)
    
    irid_pearl = calculate_thin_film_iridescence(fbm * 0.9 + pearl_dome * 0.4)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_bg[c]
        gold_val = c_rosegold[c] * (0.90 + fbm * 0.2)
        base = np.where(is_filigree > 0.3, gold_val, base)
        gem_col = c_morganite[c] * (0.8 + gem_facet * 0.4 + fbm_gem * 0.15)
        base = np.where(is_gem, gem_col, base)
        pearl_col = c_pearl[c] * 0.5 + irid_pearl[:, :, c] * 0.5
        base = np.where(is_pearl, pearl_col, base)
        bc[:, :, c] = base
        
    height = is_filigree * 0.30 + is_gem * (0.45 + gem_facet * 0.25) + is_pearl * (0.50 + pearl_dome * 0.30)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.5, flip_green=True)
    
    roughness = np.where(is_gem, 0.05, np.where(is_pearl, 0.10, np.where(is_filigree > 0.3, 0.20, 0.85)))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_filigree > 0.3, 0.95, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(is_gem | is_pearl | (is_filigree > 0.3), 0.95, 0.35)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_pearl, 0.95, np.where(is_gem, 0.80, 0.0))
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

def generate_porcelain_kintsugi_lapis(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 4: T_Melusina_PorcelainMusicBox_KintsugiLapis ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=707)
    fbm_cracks = create_fbm_noise(res, res, octaves=5, persistence=0.6, scale=res/8, seed=808)
    
    kintsugi_vein = np.abs(np.sin(fbm_cracks * 16.0 * np.pi + x * 4.0)) < 0.035
    hydrangea_wash = np.sin((x * 6.0 + y * 4.0 + fbm * 2.0) * np.pi) * 0.5 + 0.5
    
    c_porcelain = np.array([252, 250, 254], dtype=np.float32)
    c_lilac = np.array([189, 178, 255], dtype=np.float32)
    c_skyblue = np.array([160, 196, 255], dtype=np.float32)
    c_rosegold_kintsugi = np.array([238, 175, 160], dtype=np.float32)
    c_kintsugi_hi = np.array([255, 230, 215], dtype=np.float32)
    
    irid_glaze = calculate_thin_film_iridescence(fbm * 0.8 + hydrangea_wash * 0.4)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        wash_col = c_lilac[c] * (1.0 - hydrangea_wash) + c_skyblue[c] * hydrangea_wash
        porcelain_val = c_porcelain[c] * 0.70 + irid_glaze[:, :, c] * 0.15 + wash_col * 0.15
        kintsugi_val = c_rosegold_kintsugi[c] * (0.85 + fbm * 0.3) + c_kintsugi_hi[c] * 0.2
        base = np.where(kintsugi_vein, kintsugi_val, porcelain_val)
        bc[:, :, c] = base
        
    height = 0.55 + fbm * 0.03 + np.where(kintsugi_vein, 0.20, 0.0)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.0, flip_green=True)
    
    roughness = np.where(kintsugi_vein, 0.22, 0.08 + fbm * 0.04)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(kintsugi_vein, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - np.where(kintsugi_vein, 0.0, (1.0 - hydrangea_wash) * 0.1)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.full_like(roughness, 0.95 * 255.0)
    sheen_uint8 = sheen.clip(0, 255).astype(np.uint8)
    
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

def generate_pastel_wave_parquet(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 5: T_Melusina_MoonlitHarbor_WaterRippleParquet ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    wave_freq = 5.0
    wave_amp = 0.07
    wy = (y + np.sin(x * wave_freq * np.pi * 2.0) * wave_amp) * 8.0
    plank_id = np.floor(wy)
    plank_t = wy % 1.0
    
    seam_edge = np.clip(1.0 - (np.minimum(plank_t, 1.0 - plank_t) / 0.025), 0.0, 1.0) ** 2.0
    
    fbm_wood = create_fbm_noise(res, res, octaves=5, persistence=0.5, scale=res/2, seed=909)
    grain = np.sin((x * 140.0 + fbm_wood * 15.0) * np.pi) * 0.5 + 0.5
    
    is_rose_gold_ribbon = (plank_id % 4 == 0) & (seam_edge > 0.3)
    is_abalone_inlay = (plank_id % 4 == 2)
    
    c_blush = np.array([247, 225, 215], dtype=np.float32)
    c_lilac = np.array([224, 195, 252], dtype=np.float32)
    c_mint = np.array([216, 243, 220], dtype=np.float32)
    c_rosegold = np.array([232, 180, 168], dtype=np.float32)
    
    irid_abalone = calculate_thin_film_iridescence(fbm_wood * 0.9 + (x * 0.4))
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    band_type = plank_id % 3
    
    for c in range(3):
        wood_val = np.where(band_type == 0, c_blush[c], np.where(band_type == 1, c_lilac[c], c_mint[c]))
        wood_val = wood_val * (0.92 + grain * 0.16 + fbm_wood * 0.08)
        abalone_val = irid_abalone[:, :, c] * 0.85 + 35.0
        base = np.where(is_abalone_inlay, abalone_val, wood_val)
        base = np.where(is_rose_gold_ribbon, c_rosegold[c] * 1.1, base)
        bc[:, :, c] = base
        
    height = 0.5 + (1.0 - seam_edge) * 0.12 + is_rose_gold_ribbon * 0.08 + (grain * 0.02)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.6, flip_green=True)
    
    roughness = np.where(is_abalone_inlay, 0.12, np.where(is_rose_gold_ribbon, 0.20, 0.32 + grain * 0.06))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_rose_gold_ribbon, 0.92, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - seam_edge * 0.4
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_abalone_inlay, 0.95 * 255.0, 0.40 * 255.0)
    sheen_uint8 = sheen.clip(0, 255).astype(np.uint8)
    
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

def generate_starlight_chantilly_lace(res: int = 2048) -> dict[str, np.ndarray]:
    print(f"Generating Suite 6: T_Melusina_EtherealVeil_StarlightChantilly ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/8, seed=1212)
    fbm_thread = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=1313)
    
    mesh_scale = 56.0
    mx = np.abs((x * mesh_scale) % 1.0 - 0.5)
    my = np.abs((y * mesh_scale) % 1.0 - 0.5)
    mesh_net = np.clip(1.0 - np.abs((mx + my) - 0.5) / 0.09, 0.0, 1.0)
    
    star_wave = np.cos(x * 10.0 * np.pi + np.sin(y * 8.0 * np.pi)) * np.cos(y * 10.0 * np.pi)
    lace_pattern = np.clip(star_wave * 2.2 + fbm * 0.6, 0.0, 1.0) ** 1.6
    
    scallop = np.sin(x * 12.0 * np.pi) * 0.05 + 0.90
    hem_edge = np.clip(1.0 - (y - scallop) / 0.03, 0.0, 1.0)
    
    alpha = np.clip(mesh_net * 0.28 + lace_pattern * 0.88 + (y > 0.90) * 0.85, 0.0, 1.0)
    alpha_uint8 = (alpha * 255.0).clip(0, 255).astype(np.uint8)
    
    is_pearl_bead = (lace_pattern > 0.72) & (fbm_thread > 0.65)
    
    c_white = np.array([250, 249, 253], dtype=np.float32)
    c_rosepearl = np.array([253, 226, 228], dtype=np.float32)
    c_rosegold_thread = np.array([232, 180, 168], dtype=np.float32)
    
    irid_lace = calculate_thin_film_iridescence(fbm * 0.8 + (x * 0.3))
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        lace_col = c_white[c] * 0.70 + irid_lace[:, :, c] * 0.30
        lace_col = lace_col * (0.95 + fbm_thread * 0.10)
        lace_col = np.where(is_pearl_bead, c_rosepearl[c] * 1.15, lace_col)
        is_gold_edge = (lace_pattern > 0.55) & (lace_pattern < 0.65)
        lace_col = np.where(is_gold_edge, c_rosegold_thread[c], lace_col)
        bc[:, :, c] = lace_col
        
    height = alpha * 0.45 + lace_pattern * 0.30 + np.where(is_pearl_bead, 0.35, 0.0)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.8, flip_green=True)
    
    roughness = np.where(is_pearl_bead, 0.08, 0.38 + fbm_thread * 0.10)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where((lace_pattern > 0.55) & (lace_pattern < 0.65), 0.88, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + (1.0 - alpha) * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.full_like(roughness, 0.95 * 255.0)
    sheen_uint8 = sheen.clip(0, 255).astype(np.uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8,
        "Alpha": alpha_uint8,
        "Mask": alpha_uint8
    }

def main():
    root = Path(r"C:\EnvironmentPortfolio")
    out_dir = root / "BS_GodFile" / "Content" / "Textures" / "Melusina_Feminine_Iridescent_Suites"
    
    print("==================================================================")
    print("MELUSINA HAUTE-COUTURE FEMININE & IRIDESCENT PBR SUITE SYNTHESIS")
    print("==================================================================")
    
    suites = [
        (out_dir, "T_Melusina_IridescentSiren_ScaleTessellation", generate_siren_opal_scales),
        (out_dir, "T_Melusina_SakuraLullaby_SilkOrganza", generate_sakura_silk_organza),
        (out_dir, "T_Melusina_BaroqueTiara_RoseGoldFiligree", generate_baroque_tiara_filigree),
        (out_dir, "T_Melusina_PorcelainMusicBox_KintsugiLapis", generate_porcelain_kintsugi_lapis),
        (out_dir, "T_Melusina_MoonlitHarbor_WaterRippleParquet", generate_pastel_wave_parquet),
        (out_dir, "T_Melusina_EtherealVeil_StarlightChantilly", generate_starlight_chantilly_lace),
    ]
    
    total_maps = 0
    for d, name, func in suites:
        maps = func(res=2048)
        save_suite(d, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} Feminine Iridescent PBR suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directory: {out_dir}")

if __name__ == "__main__":
    main()
