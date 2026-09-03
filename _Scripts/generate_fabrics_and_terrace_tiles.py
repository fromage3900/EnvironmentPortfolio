"""
Haute-Couture Iridescent Fabric & Stylized Terrace Tilework PBR Generator
1. Genuine Iridescent Weave Fabrics: Duchess Satin, Chromatic Jacquard, Opalescent Chiffon Plisse, Crushed Aquatic Velvet.
2. Stylized Terrace Tilework: Water-Organ Majolica, Sunken Plaza Marble, Mossy Glazed Terracotta, Petal Fountain Hex Mosaic.
Strict UE5 PBR: 2048x2048 POT, DirectX Tangent Normals, Linear ORM Packing.
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

def calculate_spectral_iridescence(phase: np.ndarray, palette_type: str = "pastel") -> np.ndarray:
    """Multi-stop optical thin-film spectral interference."""
    if palette_type == "champagne_rose":
        a = np.array([0.92, 0.82, 0.85], dtype=np.float32)
        b = np.array([0.18, 0.22, 0.15], dtype=np.float32)
        c = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        d = np.array([0.0, 0.25, 0.50], dtype=np.float32)
    elif palette_type == "cyan_lilac":
        a = np.array([0.65, 0.75, 0.95], dtype=np.float32)
        b = np.array([0.35, 0.25, 0.15], dtype=np.float32)
        c = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        d = np.array([0.1, 0.4, 0.7], dtype=np.float32)
    else: # opal pastel
        a = np.array([0.88, 0.86, 0.93], dtype=np.float32)
        b = np.array([0.22, 0.24, 0.20], dtype=np.float32)
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

# =============================================================================
# PART 1: HAUTE-COUTURE IRIDESCENT FABRIC SUITES
# =============================================================================

def generate_duchess_satin(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 1: T_Fabric_IridescentDuchessSatin_ChampagneRose
    Heavy 400g duchess silk satin with dual-color iridescent warp/weft (Champagne Gold x Rose Quartz), micro-twill striations, and anisotropic sheen.
    """
    print(f"Generating Suite 1: T_Fabric_IridescentDuchessSatin_ChampagneRose ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Diagonal Twill Weave Striations (Warp & Weft)
    twill_diag = np.sin((x + y) * res * 0.4 * np.pi) * 0.5 + 0.5
    warp_lines = np.sin(x * res * 0.8 * np.pi) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.52, scale=res/4, seed=101)
    fbm_fuzz = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=202)
    
    # Dual-Color Iridescence: Champagne Gold (#F4E7D3) -> Blush Rose (#F2C2C6) -> Peach Shimmer (#FBE4D8)
    phase = fbm * 0.75 + twill_diag * 0.15 + (x * 0.3)
    irid_color = calculate_spectral_iridescence(phase, "champagne_rose")
    
    c_champagne = np.array([244, 231, 211], dtype=np.float32)
    c_rose = np.array([242, 194, 198], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_champagne[c] * 0.45 + c_rose[c] * 0.25 + irid_color[:, :, c] * 0.30
        base = base * (0.94 + twill_diag * 0.04 + warp_lines * 0.03 + fbm_fuzz * 0.04)
        bc[:, :, c] = base
        
    height = 0.5 + twill_diag * 0.04 + warp_lines * 0.02 + fbm_fuzz * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=1.6, flip_green=True)
    
    # Ultra-smooth satin micro-roughness (0.24 - 0.32)
    roughness = 0.26 + twill_diag * 0.05 + fbm * 0.06
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness) # Silk is dielectric
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.92 + twill_diag * 0.08
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.95 + twill_diag * 0.05
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

def generate_chromatic_jacquard(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 2: T_Fabric_ChromaticJacquard_AcanthusBrocade
    Heavy metallic brocade with raised 24k gold bullion acanthus embroidery over cyan-to-lilac iridescent silk jacquard.
    """
    print(f"Generating Suite 2: T_Fabric_ChromaticJacquard_AcanthusBrocade ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Woven Micro-Weave
    micro_grid = (np.sin(x * res * 0.35 * np.pi) * np.sin(y * res * 0.35 * np.pi)) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=303)
    fbm_thread = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/32, seed=404)
    
    # 4-Fold Baroque Acanthus Leaf & Floral Damask
    damask_x = np.sin(x * 6.0 * np.pi + np.cos(y * 4.0 * np.pi)) * np.cos(y * 6.0 * np.pi)
    damask_leaf = np.clip(damask_x * 2.2 + fbm * 0.4, 0.0, 1.0) ** 1.8
    is_gold_bullion = damask_leaf > 0.45
    
    # Chromatic Silk Base (Cyan #64DFDF -> Royal Lilac #7209B7 -> Rose #F72585)
    irid_silk = calculate_spectral_iridescence(fbm * 0.8 + (x * 0.4), "cyan_lilac")
    c_gold_thread = np.array([238, 195, 78], dtype=np.float32)
    c_gold_hi = np.array([255, 235, 160], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Base chromatic silk
        silk_val = irid_silk[:, :, c] * (0.90 + micro_grid * 0.12)
        # 24k Gold bullion embroidery with thread texture
        gold_val = c_gold_thread[c] * (0.85 + fbm_thread * 0.25) + c_gold_hi[c] * 0.15
        base = np.where(is_gold_bullion, gold_val, silk_val)
        bc[:, :, c] = base
        
    height = 0.5 + micro_grid * 0.03 + is_gold_bullion * (damask_leaf * 0.28 + fbm_thread * 0.05)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.4, flip_green=True)
    
    roughness = np.where(is_gold_bullion, 0.22 + fbm_thread * 0.08, 0.35 + micro_grid * 0.08)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_bullion, 0.94, 0.0) # Gold bullion is metal, silk is dielectric
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (1.0 - damask_leaf) * is_gold_bullion * 0.2 - (micro_grid < 0.2) * 0.08
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_gold_bullion, 0.15, 0.90 + fbm * 0.10)
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

def generate_opalescent_plisse_chiffon(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 3: T_Fabric_OpalescentChiffon_Plisse
    Fine micro-pleated (plissé) semi-sheer chiffon with iridescent white-opal luster, translucent drape, and micro-fold normals.
    """
    print(f"Generating Suite 3: T_Fabric_OpalescentChiffon_Plisse ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Micro-Accordion Plissé Pleats (vertical sharp ridges)
    pleat_freq = 64.0
    px = (x * pleat_freq) % 1.0
    pleat_profile = np.abs(px - 0.5) * 2.0  # Triangular sawtooth
    pleat_profile = pleat_profile ** 1.4
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/4, seed=505)
    fbm_thread = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/64, seed=606)
    
    # Opal Thin-Film Shimmer
    irid_opal = calculate_spectral_iridescence(fbm * 0.7 + pleat_profile * 0.3 + (y * 0.2), "opal")
    
    c_chiffon_base = np.array([250, 248, 253], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        base = c_chiffon_base[c] * 0.65 + irid_opal[:, :, c] * 0.35
        # Modulate by pleat ridges and sheer micro-fiber transparency
        base = base * (0.92 + pleat_profile * 0.12 + fbm_thread * 0.05)
        bc[:, :, c] = base
        
    height = 0.5 + pleat_profile * 0.22 + fbm_thread * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.2, flip_green=True)
    
    roughness = 0.32 + pleat_profile * 0.08 + fbm_thread * 0.05
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.88 + pleat_profile * 0.12
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.95 # Highly translucent opalescent sheen
    sheen_uint8 = np.full_like(rough_uint8, int(0.95 * 255))
    
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

def generate_crushed_aquatic_velvet(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 4: T_Fabric_AquaticVelvet_CrushedFuzz
    Crushed aquatic silk velvet with multidirectional pile fuzz, deep indigo/seafoam chromatic sheen, and tactile micro-fiber relief.
    """
    print(f"Generating Suite 4: T_Fabric_AquaticVelvet_CrushedFuzz ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm_crush = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/3, seed=707)
    fbm_fuzz = create_fbm_noise(res, res, octaves=5, persistence=0.6, scale=res/48, seed=808)
    
    # Multidirectional crushed velvet pile swirl
    pile_angle = (fbm_crush * 4.0 * np.pi)
    pile_spec = np.cos(pile_angle + (x * 2.0 * np.pi)) * 0.5 + 0.5
    
    # Palette: Deep Midnight Navy (#0D1B2A), Aquamarine Glow (#48CAE4), Lilac Sheen (#9D4EDD)
    c_navy = np.array([13, 27, 42], dtype=np.float32)
    c_aqua = np.array([72, 202, 228], dtype=np.float32)
    c_lilac = np.array([157, 78, 221], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Base velvet with directional light scatter
        col = c_navy[c] * (1.0 - pile_spec * 0.6) + c_aqua[c] * (pile_spec * 0.4) + c_lilac[c] * ((1.0 - pile_spec) * 0.25)
        col = col * (0.88 + fbm_fuzz * 0.24)
        bc[:, :, c] = col
        
    height = 0.5 + fbm_crush * 0.08 + fbm_fuzz * 0.05
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.2, flip_green=True)
    
    roughness = 0.48 + fbm_crush * 0.15 + fbm_fuzz * 0.08 # Soft velvet diffuse
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + fbm_crush * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.95 # Anisotropic velvet fuzz sheen
    sheen_uint8 = np.full_like(rough_uint8, int(0.95 * 255))
    
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

# =============================================================================
# PART 2: STYLIZED TERRACE TILEWORK SUITES
# =============================================================================

def generate_water_organ_majolica(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 5: T_Terrace_WaterOrgan_MajolicaTile
    Glazed Portuguese/Moroccan majolica ceramic terrace tiles with musical water-organ motifs, hand-painted pastel turquoise and peach floral medallions, beveled mortar, and glossy pooled enamel.
    """
    print(f"Generating Suite 5: T_Terrace_WaterOrgan_MajolicaTile ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # 4x4 Majolica Square Grid
    grid_size = 4.0
    gx = (x * grid_size) % 1.0
    gy = (y * grid_size) % 1.0
    
    # Grout line
    grout_dist = np.minimum(np.minimum(gx, 1.0 - gx), np.minimum(gy, 1.0 - gy))
    grout_mask = np.clip(1.0 - (grout_dist / 0.04), 0.0, 1.0) ** 2.0
    tile_bevel = (np.sin(gx * np.pi) * np.sin(gy * np.pi)) ** 0.4
    
    # Central Floral Water-Organ Medallion
    cx = gx - 0.5
    cy = gy - 0.5
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/4, seed=909)
    fbm_fine = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=1010)
    
    # 8-Petal Rosette & Treble Clef Arabesques
    rosette = np.cos(angle * 8.0 + radius * 12.0 * np.pi)
    is_medallion = (radius < 0.42) & (rosette > -0.2)
    center_pearl = radius < 0.10
    
    # Palette: Glazed Turquoise (#2A9D8F), Peach Blossom (#F4A261), Milk White Enamel (#F8F9FA), Gold Filigree (#E9C46A), Mortar (#D8D4D0)
    c_white = np.array([248, 249, 250], dtype=np.float32)
    c_turquoise = np.array([42, 157, 143], dtype=np.float32)
    c_peach = np.array([244, 162, 97], dtype=np.float32)
    c_gold = np.array([233, 196, 106], dtype=np.float32)
    c_mortar = np.array([216, 212, 208], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Base ceramic glaze with watercolor wash
        tile_base = c_white[c] * (0.95 + fbm * 0.08)
        # Floral medallion painting
        floral_col = c_turquoise[c] * (1.0 - radius / 0.42) + c_peach[c] * (radius / 0.42)
        tile_base = np.where(is_medallion, floral_col * (0.88 + fbm_fine * 0.2), tile_base)
        # Center pearl / Gold rim
        tile_base = np.where(center_pearl, c_gold[c] * 1.1, tile_base)
        # Grout
        base = tile_base * (1.0 - grout_mask) + c_mortar[c] * grout_mask
        bc[:, :, c] = base
        
    height = (tile_bevel * 0.70 + is_medallion * 0.10 + center_pearl * 0.18) * (1.0 - grout_mask) + fbm_fine * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.6, flip_green=True)
    
    roughness = (0.10 + fbm_fine * 0.05) * (1.0 - grout_mask) + grout_mask * 0.88
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = center_pearl * 0.92 * (1.0 - grout_mask)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (grout_mask * 0.45 + (1.0 - tile_bevel) * 0.25)
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

def generate_sunken_plaza_marble(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 6: T_Terrace_SunkenPlaza_MarbleTessellation
    Concentric terrace plaza tiles combining Carrara rose marble, sea-mist celadon tiles, and flush brushed-brass geometric borders.
    """
    print(f"Generating Suite 6: T_Terrace_SunkenPlaza_MarbleTessellation ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Octagonal + Diamond Interlocking Tessellation
    oct_scale = 3.0
    ox = (x * oct_scale) % 1.0 - 0.5
    oy = (y * oct_scale) % 1.0 - 0.5
    oct_dist = np.maximum(np.abs(ox), np.abs(oy)) + np.abs(ox + oy) * 0.4
    
    is_brass_ribbon = np.abs(oct_dist - 0.42) < 0.03
    is_center_diamond = oct_dist < 0.22
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.52, scale=res/4, seed=1111)
    veins = np.abs(np.sin(fbm * 14.0 * np.pi)) ** 6.0
    
    # Palette: Rose Carrara (#F4ECEF), Celadon Jade (#D8E2DC), Polished Brass (#D4AF37), Grout (#BDB2BF)
    c_rose_marble = np.array([244, 236, 239], dtype=np.float32)
    c_celadon = np.array([216, 226, 220], dtype=np.float32)
    c_brass = np.array([212, 175, 55], dtype=np.float32)
    c_grout = np.array([189, 178, 191], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Rose marble vs Celadon tile
        marble_col = c_rose_marble[c] * (1.0 - veins * 0.3) + np.array([160, 110, 130])[c] * (veins * 0.3)
        celadon_col = c_celadon[c] * (0.95 + fbm * 0.08)
        base = np.where(is_center_diamond, celadon_col, marble_col)
        # Brass inlay ribbon
        base = np.where(is_brass_ribbon, c_brass[c] * (1.0 + fbm * 0.2), base)
        bc[:, :, c] = base
        
    height = 0.55 + (1.0 - veins * 0.04) + is_brass_ribbon * 0.08
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.6, flip_green=True)
    
    roughness = np.where(is_brass_ribbon, 0.22, 0.12 + veins * 0.08)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_brass_ribbon, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - is_brass_ribbon * 0.15 - veins * 0.10
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

def generate_mossy_glazed_terracotta(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 7: T_Terrace_MossyGrotto_GlazedTerracotta
    Weathered Mediterranean terracotta terrace tiles with damp watercolor moss in grout lines, dewy sheen, and clay grain.
    """
    print(f"Generating Suite 7: T_Terrace_MossyGrotto_GlazedTerracotta ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # 5x5 Cobblestone / Paver Layout
    tile_scale = 5.0
    tx = (x * tile_scale) % 1.0
    ty = (y * tile_scale) % 1.0
    
    edge_d = np.minimum(np.minimum(tx, 1.0 - tx), np.minimum(ty, 1.0 - ty))
    grout = np.clip(1.0 - edge_d / 0.06, 0.0, 1.0) ** 1.8
    pillow = (np.sin(tx * np.pi) * np.sin(ty * np.pi)) ** 0.5
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=1212)
    fbm_moss = create_fbm_noise(res, res, octaves=5, persistence=0.6, scale=res/8, seed=1313)
    
    # Watercolor Damp Moss growing along grout lines
    is_moss = (grout > 0.4) & (fbm_moss > 0.45)
    
    # Palette: Warm Glazed Terracotta (#E07A5F), Soft Clay Pink (#F2CC8F), Damp Emerald Moss (#3D5A40), Mortar (#7F7F7F)
    c_terracotta = np.array([224, 122, 95], dtype=np.float32)
    c_clay_tint = np.array([242, 204, 143], dtype=np.float32)
    c_moss = np.array([61, 90, 64], dtype=np.float32)
    c_mortar = np.array([140, 135, 130], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Terracotta glaze variation
        tile_val = c_terracotta[c] * (0.85 + pillow * 0.3 + fbm * 0.1)
        base = tile_val * (1.0 - grout) + c_mortar[c] * grout
        # Damp moss overlay
        base = np.where(is_moss, c_moss[c] * (0.9 + fbm * 0.2), base)
        bc[:, :, c] = base
        
    height = (pillow * 0.65) * (1.0 - grout) + np.where(is_moss, 0.25, 0.0) + fbm * 0.04
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.8, flip_green=True)
    
    roughness = (0.28 + fbm * 0.08) * (1.0 - grout) + grout * 0.85
    roughness = np.where(is_moss, 0.55, roughness)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness) # Clay & moss are dielectric
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - grout * 0.5 - np.where(is_moss, 0.15, 0.0)
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

def generate_petal_fountain_hex_mosaic(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 8: T_Terrace_PetalFountain_HexMosaic
    Micro-hexagonal mosaic tiles arranged in a radiating cherry blossom / siren scale fountain basin with mother-of-pearl tesserae and water-worn grout.
    """
    print(f"Generating Suite 8: T_Terrace_PetalFountain_HexMosaic ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Hexagonal Grid
    hex_s = 16.0
    hx = (x * hex_s) % 1.0 - 0.5
    hy = (y * hex_s * 0.866) % 1.0 - 0.5
    hex_dist = np.maximum(np.abs(hx) * 0.866 + np.abs(hy) * 0.5, np.abs(hy))
    
    is_hex_grout = hex_dist > 0.44
    hex_dome = np.clip(1.0 - (hex_dist / 0.44)**2.0, 0.0, 1.0)
    
    # Radiating Water Petal Wave Flow
    cx = x - 0.5
    cy = y - 0.5
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    petal_wave = np.sin(angle * 6.0 + radius * 16.0 * np.pi) * 0.5 + 0.5
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/4, seed=1414)
    irid_nacre = calculate_spectral_iridescence(fbm * 0.8 + petal_wave * 0.4, "opal")
    
    # Palette: Pink Pearl (#FDE2E4), Seafoam Glaze (#C7F9CC), Rose Gold (#E8B4A8), Grout (#E2E2E2)
    c_pink = np.array([253, 226, 228], dtype=np.float32)
    c_seafoam = np.array([199, 249, 204], dtype=np.float32)
    c_rosegold = np.array([232, 180, 168], dtype=np.float32)
    c_grout = np.array([220, 220, 225], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        mosaic_col = c_pink[c] * (1.0 - petal_wave) + c_seafoam[c] * petal_wave + irid_nacre[:, :, c] * 0.25
        base = np.where(is_hex_grout, c_grout[c], mosaic_col * (0.94 + hex_dome * 0.12))
        bc[:, :, c] = base
        
    height = np.where(is_hex_grout, 0.15, 0.60 + hex_dome * 0.25) + fbm * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.2, flip_green=True)
    
    roughness = np.where(is_hex_grout, 0.85, 0.10 + fbm * 0.05)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(is_hex_grout, 0.60, 0.95)
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
    fabric_dir = content_textures / "HauteCouture_Iridescent_Fabrics"
    terrace_dir = content_textures / "Stylized_Terrace_Tilework"
    
    print("==================================================================")
    print("HAUTE-COUTURE IRIDESCENT FABRICS & STYLIZED TERRACE TILEWORK")
    print("==================================================================")
    
    suites = [
        # Part 1: Fabrics
        (fabric_dir, "T_Fabric_IridescentDuchessSatin_ChampagneRose", generate_duchess_satin),
        (fabric_dir, "T_Fabric_ChromaticJacquard_AcanthusBrocade", generate_chromatic_jacquard),
        (fabric_dir, "T_Fabric_OpalescentChiffon_Plisse", generate_opalescent_plisse_chiffon),
        (fabric_dir, "T_Fabric_AquaticVelvet_CrushedFuzz", generate_crushed_aquatic_velvet),
        # Part 2: Terrace Tiles
        (terrace_dir, "T_Terrace_WaterOrgan_MajolicaTile", generate_water_organ_majolica),
        (terrace_dir, "T_Terrace_SunkenPlaza_MarbleTessellation", generate_sunken_plaza_marble),
        (terrace_dir, "T_Terrace_MossyGrotto_GlazedTerracotta", generate_mossy_glazed_terracotta),
        (terrace_dir, "T_Terrace_PetalFountain_HexMosaic", generate_petal_fountain_hex_mosaic),
    ]
    
    total_maps = 0
    for out_dir, name, func in suites:
        maps = func(res=2048)
        save_suite(out_dir, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directories:\n  - {fabric_dir}\n  - {terrace_dir}")

if __name__ == "__main__":
    main()
