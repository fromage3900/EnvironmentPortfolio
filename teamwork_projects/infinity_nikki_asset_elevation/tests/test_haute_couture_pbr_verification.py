#!/usr/bin/env python3
"""
Infinity Nikki Haute-Couture PBR Verification - Automated Multi-Tier Test Suite
=============================================================================
Authoritative Quality Gate & Verification Harness for 4 Haute-Couture PBR
Material Suites (36 Texture Maps at 2048x2048 POT) for Infinity Nikki assets.

Test Tiers:
- Tier 0: Verification Harness Self-Tests (Mathematical correctness of test algorithms)
- Tier 1: Directory Structure, File Naming, and 2048x2048 Power-of-Two Dimensions
- Tier 2: Bit Depth, Color Formats, and Dynamic Range Integrity
- Tier 3: DirectX Normal Unit Vector Normalization (||N|| ≈ 1.0) & Green Channel (-Y)
- Tier 4: ORM Channel Packing vs Discrete Maps (AO, Roughness, Metallic) Consistency
- Tier 5: Mathematical Non-Triviality, Shannon Entropy, and Spatial Frequency
- Tier 6: Fabric Masks (_Sheen, _Alpha) Translucency and Highlight Integrity

Usage:
    python -m unittest tests/test_haute_couture_pbr_verification.py
    python -m unittest tests/test_haute_couture_pbr_verification.py -k Tier0
    python tests/test_haute_couture_pbr_verification.py [--suite <name>] [--tier <0-6>] [--summary]
"""

import os
import sys
import math
import argparse
import unittest
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Project Configuration & Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEXTURES_DIR = PROJECT_ROOT / "textures"

SUITE_NAMES = [
    "T_HauteCouture_ChantillyLace_PearlBeading",
    "T_HauteCouture_DifferentialOrganza_Petals",
    "T_HauteCouture_BaroqueBullion_Acanthus",
    "T_HauteCouture_ReactionDiffusion_Cloisonne",
]

MAP_SUFFIXES = [
    "_BC.png",     # BaseColor (sRGB 8-bit RGB/RGBA)
    "_N.png",      # DirectX Tangent Normal (Linear 8-bit RGB, Green=-Y)
    "_ORM.png",    # Packed ORM: R=AO, G=Roughness, B=Metallic (Linear 8-bit RGB)
    "_H.png",      # Micro-Elevation / Height (Linear 16-bit uint16 / 8-bit Grayscale)
    "_AO.png",     # Ambient Occlusion (Linear 8-bit Grayscale/RGB)
    "_R.png",      # Roughness (Linear 8-bit Grayscale/RGB)
    "_M.png",      # Metallic (Linear 8-bit Grayscale/RGB)
    "_Sheen.png",  # Sheen / Micro-fuzz / Pearlescence (Linear 8-bit Grayscale/RGB)
    "_Alpha.png",  # Alpha / Opacity / Translucency Mask (Linear 8-bit Grayscale/RGB)
]

EXPECTED_RESOLUTION = (2048, 2048)
EXPECTED_MAP_COUNT_PER_SUITE = 9
TOTAL_EXPECTED_MAPS = len(SUITE_NAMES) * EXPECTED_MAP_COUNT_PER_SUITE


# ---------------------------------------------------------------------------
# Helper Mathematical & Image Functions
# ---------------------------------------------------------------------------
def is_power_of_two(n: int) -> bool:
    """Return True if n is a strictly positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


def calculate_shannon_entropy(image_array: np.ndarray) -> float:
    """
    Calculate Shannon entropy in bits for an image or channel.
    H(X) = -sum(p * log2(p)) for p > 0.
    """
    if image_array.ndim > 2:
        return float(np.mean([calculate_shannon_entropy(image_array[:, :, c]) for c in range(image_array.shape[2])]))

    flat = image_array.ravel()
    if np.issubdtype(flat.dtype, np.floating):
        flat = np.clip(flat * 255.0, 0, 255).astype(np.uint8)
    elif flat.dtype == np.uint16:
        # Quantize 16-bit to 256 bins for uniform entropy measurement
        flat = (flat >> 8).astype(np.uint8)

    hist, _ = np.histogram(flat, bins=256, range=(0, 256))
    total_pixels = hist.sum()
    if total_pixels == 0:
        return 0.0

    probs = hist / total_pixels
    non_zero_probs = probs[probs > 0]
    return float(-np.sum(non_zero_probs * np.log2(non_zero_probs)))


def calculate_laplacian_variance(gray_array: np.ndarray) -> float:
    """
    Calculate spatial frequency / edge sharpness via 2D discrete 3x3 Laplacian operator.
    Kernel: [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    """
    if gray_array.ndim == 3:
        gray_array = 0.299 * gray_array[:, :, 0] + 0.587 * gray_array[:, :, 1] + 0.114 * gray_array[:, :, 2]
    
    gray = gray_array.astype(np.float64)
    lap = (
        gray[0:-2, 1:-1] +
        gray[2:, 1:-1] +
        gray[1:-1, 0:-2] +
        gray[1:-1, 2:] -
        4.0 * gray[1:-1, 1:-1]
    )
    return float(np.var(lap))


def calculate_sobel_gradient_y(gray_array: np.ndarray) -> np.ndarray:
    """
    Calculate discrete vertical gradient (d_height / dy) using 3x3 Sobel kernel.
    Sobel Y kernel:
      [-1, -2, -1]
      [ 0,  0,  0]
      [ 1,  2,  1] / 8.0
    """
    if gray_array.ndim == 3:
        gray_array = gray_array[:, :, 0]
    gray = gray_array.astype(np.float64)
    h, w = gray.shape
    if h < 3 or w < 3:
        return np.gradient(gray, axis=0)

    grad_y = (
        (gray[2:, 0:-2] + 2.0 * gray[2:, 1:-1] + gray[2:, 2:]) -
        (gray[0:-2, 0:-2] + 2.0 * gray[0:-2, 1:-1] + gray[0:-2, 2:])
    ) / 8.0
    # Pad borders to match original shape
    padded = np.pad(grad_y, ((1, 1), (1, 1)), mode='edge')
    return padded


def calculate_mean_absolute_difference(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate Mean Absolute Difference (MAD) between two arrays."""
    return float(np.mean(np.abs(a.astype(np.float64) - b.astype(np.float64))))


def decode_tangent_normal(normal_rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Decode 8-bit RGB normal map to tangent vectors (Nx, Ny, Nz) and calculate norm length.
    RGB in [0, 255] -> [-1.0, 1.0].
    """
    rgb_float = normal_rgb[:, :, :3].astype(np.float64) / 255.0
    nx = rgb_float[:, :, 0] * 2.0 - 1.0
    ny = rgb_float[:, :, 1] * 2.0 - 1.0
    nz = rgb_float[:, :, 2] * 2.0 - 1.0
    norm_length = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return nx, ny, nz, norm_length


def load_as_grayscale_array(image_path: Path) -> np.ndarray:
    """Load image and return single 2D channel in native format."""
    with Image.open(image_path) as img:
        arr = np.array(img)
        if arr.ndim == 3:
            return arr[:, :, 0]
        return arr


def resolve_map_path(suite: str, suffix: str, base_dir: Path = TEXTURES_DIR) -> Optional[Path]:
    """
    Resolve map path looking both in flat textures/ and nested textures/<suite>/ folders.
    """
    # 1. Flat hierarchy: textures/T_HauteCouture_..._BC.png
    flat_path = base_dir / f"{suite}{suffix}"
    if flat_path.is_file():
        return flat_path

    # 2. Nested hierarchy: textures/<suite>/T_HauteCouture_..._BC.png
    nested_path = base_dir / suite / f"{suite}{suffix}"
    if nested_path.is_file():
        return nested_path

    return None


# ---------------------------------------------------------------------------
# Tier 0: Harness Math & Self-Test Verification
# ---------------------------------------------------------------------------
class TestTier0HarnessSelfVerification(unittest.TestCase):
    """
    Tier 0 tests verify that the mathematical algorithms and metrics inside
    this test harness (Shannon entropy, Laplacian variance, Sobel gradient,
    DirectX tangent coordinate systems, ORM packing checks, and mask validators)
    execute flawlessly and accurately classify synthetic test buffers.
    """

    def test_tier0_01_power_of_two_logic(self):
        for pot in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
            self.assertTrue(is_power_of_two(pot), f"{pot} should be recognized as Power-of-Two")
        for non_pot in [0, -1, -16, 3, 5, 100, 1920, 1080, 2000, 2047, 2049]:
            self.assertFalse(is_power_of_two(non_pot), f"{non_pot} should not be Power-of-Two")

    def test_tier0_02_shannon_entropy_accuracy(self):
        # 1. Flat constant image -> Entropy = 0.0 bits
        flat = np.full((128, 128), 128, dtype=np.uint8)
        self.assertAlmostEqual(calculate_shannon_entropy(flat), 0.0, places=4)

        # 2. Binary split 50/50 -> Entropy = 1.0 bit
        binary = np.zeros((128, 128), dtype=np.uint8)
        binary[:64, :] = 255
        self.assertAlmostEqual(calculate_shannon_entropy(binary), 1.0, places=4)

        # 3. 4 equal states -> Entropy = 2.0 bits (log2(4) = 2)
        four_states = (np.arange(128 * 128) % 4) * 64
        four_states = four_states.reshape((128, 128)).astype(np.uint8)
        self.assertAlmostEqual(calculate_shannon_entropy(four_states), 2.0, places=2)

        # 4. 8 equal states -> Entropy = 3.0 bits (log2(8) = 3)
        eight_states = (np.arange(128 * 128) % 8) * 32
        eight_states = eight_states.reshape((128, 128)).astype(np.uint8)
        self.assertAlmostEqual(calculate_shannon_entropy(eight_states), 3.0, places=2)

        # 5. Uniform 256 states -> Entropy = 8.0 bits (log2(256) = 8)
        uniform_256 = np.tile(np.arange(256, dtype=np.uint8), (256, 1))
        self.assertAlmostEqual(calculate_shannon_entropy(uniform_256), 8.0, places=2)

    def test_tier0_03_laplacian_variance_accuracy(self):
        # Flat constant -> variance = 0.0
        flat = np.full((128, 128), 100, dtype=np.uint8)
        self.assertAlmostEqual(calculate_laplacian_variance(flat), 0.0, places=4)

        # High-frequency checkerboard -> high variance
        y, x = np.mgrid[0:128, 0:128]
        checker = (((x // 4) + (y // 4)) % 2 * 255).astype(np.uint8)
        self.assertGreater(calculate_laplacian_variance(checker), 500.0)

    def test_tier0_04_tangent_normal_decoding_and_unit_normalization(self):
        # 1. Flat upward normal vector (0, 0, 1) encoded in DirectX RGB:
        # R = 128 (Nx ≈ 0), G = 128 (Ny ≈ 0), B = 255 (Nz = 1.0)
        flat_normal = np.zeros((64, 64, 3), dtype=np.uint8)
        flat_normal[:, :, 0] = 128
        flat_normal[:, :, 1] = 128
        flat_normal[:, :, 2] = 255

        nx, ny, nz, norm = decode_tangent_normal(flat_normal)
        self.assertAlmostEqual(float(np.mean(norm)), 1.0, delta=0.01)
        self.assertAlmostEqual(float(np.mean(nx)), 0.0, delta=0.01)
        self.assertAlmostEqual(float(np.mean(ny)), 0.0, delta=0.01)
        self.assertAlmostEqual(float(np.mean(nz)), 1.0, delta=0.01)

        # 2. Arbitrary hemisphere patch: ensure normalized vectors produce length = 1.0
        vx = np.random.uniform(-0.5, 0.5, (64, 64))
        vy = np.random.uniform(-0.5, 0.5, (64, 64))
        vz = np.sqrt(np.maximum(0.01, 1.0 - vx**2 - vy**2))
        enc_r = np.clip((vx + 1.0) * 127.5, 0, 255).astype(np.uint8)
        enc_g = np.clip((vy + 1.0) * 127.5, 0, 255).astype(np.uint8)
        enc_b = np.clip((vz + 1.0) * 127.5, 0, 255).astype(np.uint8)
        synth_normal = np.stack([enc_r, enc_g, enc_b], axis=-1)

        _, _, _, synth_norm = decode_tangent_normal(synth_normal)
        self.assertAlmostEqual(float(np.mean(synth_norm)), 1.0, delta=0.02)

    def test_tier0_05_directx_green_channel_sobel_gradient_correlation(self):
        """
        Verify that our Sobel gradient and correlation algorithm accurately detects
        DirectX Green = -Y convention and rejects OpenGL Green = +Y inversion.
        """
        # Create a synthetic Gaussian bump heightfield
        y, x = np.mgrid[-2.0:2.0:128j, -2.0:2.0:128j]
        h_field = np.exp(-(x**2 + y**2)) * 100.0  # Peak in center

        # Downward gradient (d_height / dy in image space, where row index increases down)
        dh_dy = calculate_sobel_gradient_y(h_field)

        # For DirectX tangent space: Ny = -dh/dy (normalized)
        # Normal map Green channel maps Ny to [0, 255]
        dh_dx = np.gradient(h_field, axis=1)
        scale = 0.05
        nx = -dh_dx * scale
        ny = -dh_dy * scale
        nz = np.sqrt(np.maximum(0.01, 1.0 - nx**2 - ny**2))
        norm_len = np.sqrt(nx**2 + ny**2 + nz**2)
        nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len

        dx_green = np.clip((ny + 1.0) * 127.5, 0, 255).astype(np.uint8)
        ny_decoded = (dx_green.astype(np.float64) / 255.0) * 2.0 - 1.0

        # Correlation between -dh_dy and Ny should be strongly positive (DirectX)
        corr_dx = float(np.corrcoef(-dh_dy.ravel(), ny_decoded.ravel())[0, 1])
        self.assertGreater(corr_dx, 0.90, f"DirectX correlation failed: {corr_dx}")

        # Inverted OpenGL Green channel (+Y) should have negative correlation with -dh_dy
        gl_green = 255 - dx_green
        ny_gl_decoded = (gl_green.astype(np.float64) / 255.0) * 2.0 - 1.0
        corr_gl = float(np.corrcoef(-dh_dy.ravel(), ny_gl_decoded.ravel())[0, 1])
        self.assertLess(corr_gl, -0.90, f"OpenGL inverted channel should give negative correlation: {corr_gl}")

    def test_tier0_06_orm_packing_discrepancy_and_mad_detection(self):
        # Create synthetic ORM and matching discrete maps
        ao_true = np.random.randint(50, 240, (64, 64), dtype=np.uint8)
        r_true = np.random.randint(20, 220, (64, 64), dtype=np.uint8)
        m_true = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        orm = np.stack([ao_true, r_true, m_true], axis=-1)

        # Matched comparison -> MAD = 0.0
        mad_ao = calculate_mean_absolute_difference(orm[:, :, 0], ao_true)
        self.assertEqual(mad_ao, 0.0)

        # Tampered discrete map -> MAD > 0.0
        tampered_r = r_true.copy()
        tampered_r[0:10, 0:10] = (tampered_r[0:10, 0:10].astype(np.int32) + 50) % 256
        mad_tampered = calculate_mean_absolute_difference(orm[:, :, 1], tampered_r)
        self.assertGreater(mad_tampered, 0.0)

    def test_tier0_07_fabric_sheen_and_alpha_mask_validators(self):
        # Synthetic sheer organza alpha mask with varying opacity
        alpha_mask = np.linspace(30, 240, 128 * 128, dtype=np.uint8).reshape((128, 128))
        self.assertGreater(float(alpha_mask.std()), 5.0)
        self.assertGreater(int(alpha_mask.max()) - int(alpha_mask.min()), 30)

        # Synthetic velvet sheen grazing angle mask
        y, x = np.mgrid[-1.0:1.0:128j, -1.0:1.0:128j]
        r = np.sqrt(x**2 + y**2)
        sheen_mask = np.clip((r**2) * 255.0, 0, 255).astype(np.uint8)
        self.assertGreater(int(sheen_mask.max()), 100)
        self.assertGreater(float(sheen_mask.std()), 1.0)


# ---------------------------------------------------------------------------
# Tier 1: Directory Structure, File Naming, and POT Dimensions
# ---------------------------------------------------------------------------
class TestTier1StructureAndDimensions(unittest.TestCase):
    """
    Tier 1 tests assert:
    - Textures directory exists.
    - All 36 required map files exist across 4 suites with strict naming conventions.
    - Every texture file has exact 2048x2048 Power-of-Two (POT) dimensions.
    """

    def test_tier1_01_texture_root_exists(self):
        self.assertTrue(
            TEXTURES_DIR.exists() and TEXTURES_DIR.is_dir(),
            f"Textures directory does not exist at {TEXTURES_DIR}"
        )

    def test_tier1_02_all_36_texture_maps_exist(self):
        missing_files = []
        for suite in SUITE_NAMES:
            for suffix in MAP_SUFFIXES:
                resolved = resolve_map_path(suite, suffix)
                if resolved is None:
                    missing_files.append(f"{suite}{suffix}")

        self.assertEqual(
            len(missing_files), 0,
            f"Missing {len(missing_files)} / {TOTAL_EXPECTED_MAPS} texture maps:\n" +
            "\n".join(f"  - {f}" for f in missing_files)
        )

    def test_tier1_03_power_of_two_dimensions(self):
        invalid_dimensions = []
        for suite in SUITE_NAMES:
            for suffix in MAP_SUFFIXES:
                resolved = resolve_map_path(suite, suffix)
                if resolved is None:
                    continue
                try:
                    with Image.open(resolved) as img:
                        w, h = img.size
                        if (w, h) != EXPECTED_RESOLUTION:
                            invalid_dimensions.append((resolved.name, (w, h), "Expected (2048, 2048)"))
                        elif not (is_power_of_two(w) and is_power_of_two(h)):
                            invalid_dimensions.append((resolved.name, (w, h), "Non-POT dimensions"))
                except Exception as ex:
                    invalid_dimensions.append((resolved.name, "Corrupt", str(ex)))

        self.assertEqual(
            len(invalid_dimensions), 0,
            f"Found {len(invalid_dimensions)} textures with invalid dimensions:\n" +
            "\n".join(f"  - {f}: {dims} ({err})" for f, dims, err in invalid_dimensions)
        )

    def test_tier1_04_file_naming_conventions(self):
        for suite in SUITE_NAMES:
            for suffix in MAP_SUFFIXES:
                resolved = resolve_map_path(suite, suffix)
                if resolved is None:
                    continue
                expected_filename = f"{suite}{suffix}"
                self.assertEqual(
                    resolved.name, expected_filename,
                    f"Texture filename '{resolved.name}' does not match expected convention '{expected_filename}'"
                )


# ---------------------------------------------------------------------------
# Tier 2: Bit Depth, Color Formats, and Dynamic Range Integrity
# ---------------------------------------------------------------------------
class TestTier2BitDepthAndDynamicRange(unittest.TestCase):
    """
    Tier 2 tests assert:
    - BaseColor (`_BC`) is 8-bit RGB/RGBA with rich non-zero dynamic range in all 3 channels.
    - Normal (`_N`) is 8-bit RGB.
    - Packed ORM (`_ORM`) is 8-bit RGB.
    - Height (`_H`) is high dynamic range elevation (16-bit uint16 or 8-bit uint8).
    - Discrete maps (`_AO`, `_R`, `_M`, `_Sheen`, `_Alpha`) have valid bounds [0, 255].
    """

    def test_tier2_01_basecolor_format_and_dynamic_range(self):
        for suite in SUITE_NAMES:
            resolved = resolve_map_path(suite, "_BC.png")
            if resolved is None:
                self.fail(f"Missing BaseColor map for suite: {suite}")

            with Image.open(resolved) as img:
                self.assertIn(
                    img.mode, ["RGB", "RGBA"],
                    f"{resolved.name}: BaseColor must be RGB or RGBA, got mode '{img.mode}'"
                )
                arr = np.array(img)
                self.assertEqual(arr.dtype, np.uint8, f"{resolved.name}: BaseColor must be 8-bit uint8")
                
                # Check channel variance and dynamic range span across R, G, B
                for c, name in enumerate(["Red", "Green", "Blue"]):
                    channel = arr[:, :, c]
                    c_min, c_max = int(channel.min()), int(channel.max())
                    c_std = float(channel.std())
                    self.assertGreater(
                        c_max - c_min, 30,
                        f"{resolved.name} {name} channel dynamic range too low: [{c_min}, {c_max}]"
                    )
                    self.assertGreater(
                        c_std, 5.0,
                        f"{resolved.name} {name} channel standard deviation too low: {c_std:.2f}"
                    )

    def test_tier2_02_height_elevation_dynamic_range(self):
        for suite in SUITE_NAMES:
            resolved = resolve_map_path(suite, "_H.png")
            if resolved is None:
                self.fail(f"Missing Height map for suite: {suite}")

            with Image.open(resolved) as img:
                self.assertIn(
                    img.mode, ["L", "I;16", "I", "RGB", "RGBA"],
                    f"{resolved.name}: Unexpected Height map mode '{img.mode}'"
                )
                arr = np.array(img)
                if arr.ndim == 3:
                    h_channel = arr[:, :, 0]
                else:
                    h_channel = arr

                h_min, h_max = float(h_channel.min()), float(h_channel.max())
                h_std = float(h_channel.std())
                dynamic_span = h_max - h_min

                min_expected_span = 1000.0 if arr.dtype in [np.uint16, np.int32] else 40.0
                self.assertGreaterEqual(
                    dynamic_span, min_expected_span,
                    f"{resolved.name}: Height map dynamic range too flat: span={dynamic_span:.1f} (min={h_min}, max={h_max})"
                )
                self.assertGreater(
                    h_std, 2.0,
                    f"{resolved.name}: Height map standard deviation too low: {h_std:.2f}"
                )

    def test_tier2_03_discrete_maps_channel_bounds(self):
        for suite in SUITE_NAMES:
            for suffix in ["_AO.png", "_R.png", "_M.png", "_Sheen.png", "_Alpha.png"]:
                resolved = resolve_map_path(suite, suffix)
                if resolved is None:
                    self.fail(f"Missing discrete map {suffix} for suite: {suite}")

                with Image.open(resolved) as img:
                    arr = np.array(img)
                    self.assertEqual(arr.dtype, np.uint8, f"{resolved.name} must be 8-bit uint8")
                    v_min, v_max = int(arr.min()), int(arr.max())
                    self.assertGreaterEqual(v_min, 0, f"{resolved.name} min value < 0: {v_min}")
                    self.assertLessEqual(v_max, 255, f"{resolved.name} max value > 255: {v_max}")


# ---------------------------------------------------------------------------
# Tier 3: DirectX Normal Unit Vector Math & Green Channel (-Y) Orientation
# ---------------------------------------------------------------------------
class TestTier3DirectXNormalVectors(unittest.TestCase):
    """
    Tier 3 tests assert:
    - Normal maps are 8-bit RGB with tangent vectors normalized to unit length.
    - Mean vector length ||N|| = sqrt(nx^2 + ny^2 + nz^2) is in [0.95, 1.05].
    - Blue channel is dominant (> 180 mean) reflecting outward tangent-space +Z.
    - DirectX Green channel orientation (-Y) correlates with negative vertical height slope.
    """

    def test_tier3_01_normal_vector_unit_length(self):
        for suite in SUITE_NAMES:
            resolved = resolve_map_path(suite, "_N.png")
            if resolved is None:
                self.fail(f"Missing normal map for suite: {suite}")

            with Image.open(resolved) as img:
                self.assertIn(img.mode, ["RGB", "RGBA"], f"{resolved.name} mode must be RGB/RGBA")
                arr = np.array(img)
                nx, ny, nz, norm = decode_tangent_normal(arr)

                mean_norm = float(np.mean(norm))
                std_norm = float(np.std(norm))
                valid_ratio = float(np.mean((norm >= 0.90) & (norm <= 1.10)))

                self.assertAlmostEqual(
                    mean_norm, 1.0, delta=0.05,
                    msg=f"{resolved.name}: Mean normal vector length {mean_norm:.4f} deviates from 1.0"
                )
                self.assertLess(
                    std_norm, 0.08,
                    msg=f"{resolved.name}: Normal vector length variance too high: std={std_norm:.4f}"
                )
                self.assertGreaterEqual(
                    valid_ratio, 0.95,
                    msg=f"{resolved.name}: Only {valid_ratio*100:.1f}% of pixels have valid unit normal length"
                )

    def test_tier3_02_normal_blue_channel_dominance(self):
        for suite in SUITE_NAMES:
            resolved = resolve_map_path(suite, "_N.png")
            if resolved is None:
                continue

            with Image.open(resolved) as img:
                arr = np.array(img)
                blue = arr[:, :, 2]
                mean_blue = float(np.mean(blue))
                min_blue = int(np.min(blue))

                self.assertGreater(
                    mean_blue, 180.0,
                    f"{resolved.name}: Mean Blue channel ({mean_blue:.1f}) should be > 180 in tangent space"
                )
                self.assertGreaterEqual(
                    min_blue, 32,
                    f"{resolved.name}: Min Blue channel ({min_blue}) indicates invalid backward-facing normals"
                )

    def test_tier3_03_directx_green_channel_consistency(self):
        """
        Verify DirectX -Y convention:
        Vertical slope of heightfield correlates with -Ny (Green channel = -Y).
        """
        for suite in SUITE_NAMES:
            normal_path = resolve_map_path(suite, "_N.png")
            height_path = resolve_map_path(suite, "_H.png")
            if normal_path is None or height_path is None:
                continue

            h_arr = load_as_grayscale_array(height_path).astype(np.float64)
            with Image.open(normal_path) as n_img:
                n_arr = np.array(n_img)

            # Compute height gradient in Y direction (d_height / dy)
            dh_dy = calculate_sobel_gradient_y(h_arr)
            ny = (n_arr[:, :, 1].astype(np.float64) / 255.0) * 2.0 - 1.0

            # Subsample for correlation test to maintain high speed
            sub_dh = dh_dy[::16, ::16].ravel()
            sub_ny = ny[::16, ::16].ravel()

            if np.std(sub_dh) > 0.1 and np.std(sub_ny) > 0.05:
                correlation_matrix = np.corrcoef(-sub_dh, sub_ny)
                corr = float(correlation_matrix[0, 1])
                self.assertGreater(
                    corr, 0.35,
                    f"{suite}: DirectX Green channel (-Y) correlation with heightfield gradient is weak: {corr:.3f}"
                )


# ---------------------------------------------------------------------------
# Tier 4: ORM Channel Packing vs Discrete Maps Consistency
# ---------------------------------------------------------------------------
class TestTier4ORMPackingConsistency(unittest.TestCase):
    """
    Tier 4 tests assert:
    - Packed ORM (`_ORM.png`) channels strictly map:
        Red = Ambient Occlusion (AO)
        Green = Roughness (R)
        Blue = Metallic (M)
    - Pixel-by-pixel alignment between ORM channels and discrete `_AO`, `_R`, `_M` maps.
    - Mean Absolute Difference (MAD) <= 1.0 LSB and Max Absolute Difference <= 3 LSB.
    """

    def test_tier4_01_orm_format_and_channels(self):
        for suite in SUITE_NAMES:
            orm_path = resolve_map_path(suite, "_ORM.png")
            if orm_path is None:
                self.fail(f"Missing ORM map for suite: {suite}")

            with Image.open(orm_path) as img:
                self.assertIn(img.mode, ["RGB", "RGBA"], f"{orm_path.name}: ORM must be RGB or RGBA")
                arr = np.array(img)
                self.assertEqual(arr.dtype, np.uint8, f"{orm_path.name}: ORM must be 8-bit uint8")

                ao = arr[:, :, 0]
                roughness = arr[:, :, 1]
                metallic = arr[:, :, 2]

                self.assertGreater(float(ao.std()), 0.5, f"{orm_path.name}: AO channel (Red) near-zero variance")
                self.assertGreater(float(roughness.std()), 0.5, f"{orm_path.name}: Roughness channel (Green) near-zero variance")
                self.assertGreater(float(metallic.std()), 0.5, f"{orm_path.name}: Metallic channel (Blue) near-zero variance")

    def test_tier4_02_orm_red_matches_discrete_ao(self):
        for suite in SUITE_NAMES:
            orm_path = resolve_map_path(suite, "_ORM.png")
            ao_path = resolve_map_path(suite, "_AO.png")
            if orm_path is None or ao_path is None:
                continue

            with Image.open(orm_path) as orm_img:
                orm_r = np.array(orm_img)[:, :, 0]
            ao_disc = load_as_grayscale_array(ao_path)

            mad = calculate_mean_absolute_difference(orm_r, ao_disc)
            max_diff = int(np.max(np.abs(orm_r.astype(np.int32) - ao_disc.astype(np.int32))))

            self.assertLessEqual(
                mad, 1.0,
                f"{suite}: ORM Red channel differs from discrete AO map (MAD={mad:.3f} > 1.0 LSB)"
            )
            self.assertLessEqual(
                max_diff, 3,
                f"{suite}: ORM Red channel max pixel discrepancy too large ({max_diff} > 3 LSB)"
            )

    def test_tier4_03_orm_green_matches_discrete_roughness(self):
        for suite in SUITE_NAMES:
            orm_path = resolve_map_path(suite, "_ORM.png")
            r_path = resolve_map_path(suite, "_R.png")
            if orm_path is None or r_path is None:
                continue

            with Image.open(orm_path) as orm_img:
                orm_g = np.array(orm_img)[:, :, 1]
            r_disc = load_as_grayscale_array(r_path)

            mad = calculate_mean_absolute_difference(orm_g, r_disc)
            max_diff = int(np.max(np.abs(orm_g.astype(np.int32) - r_disc.astype(np.int32))))

            self.assertLessEqual(
                mad, 1.0,
                f"{suite}: ORM Green channel differs from discrete Roughness map (MAD={mad:.3f} > 1.0 LSB)"
            )
            self.assertLessEqual(
                max_diff, 3,
                f"{suite}: ORM Green channel max pixel discrepancy too large ({max_diff} > 3 LSB)"
            )

    def test_tier4_04_orm_blue_matches_discrete_metallic(self):
        for suite in SUITE_NAMES:
            orm_path = resolve_map_path(suite, "_ORM.png")
            m_path = resolve_map_path(suite, "_M.png")
            if orm_path is None or m_path is None:
                continue

            with Image.open(orm_path) as orm_img:
                orm_b = np.array(orm_img)[:, :, 2]
            m_disc = load_as_grayscale_array(m_path)

            mad = calculate_mean_absolute_difference(orm_b, m_disc)
            max_diff = int(np.max(np.abs(orm_b.astype(np.int32) - m_disc.astype(np.int32))))

            self.assertLessEqual(
                mad, 1.0,
                f"{suite}: ORM Blue channel differs from discrete Metallic map (MAD={mad:.3f} > 1.0 LSB)"
            )
            self.assertLessEqual(
                max_diff, 3,
                f"{suite}: ORM Blue channel max pixel discrepancy too large ({max_diff} > 3 LSB)"
            )


# ---------------------------------------------------------------------------
# Tier 5: Mathematical Non-Triviality, Shannon Entropy, & Spatial Frequency
# ---------------------------------------------------------------------------
class TestTier5MathematicalEntropyAndStructure(unittest.TestCase):
    """
    Tier 5 tests assert:
    - Textures are mathematically non-trivial (not blank, uniform, or flat).
    - Shannon entropy H >= 3.0 bits for BaseColor, Normal, and Height maps.
    - High spatial frequency energy (Laplacian variance > 5.0 for BaseColor, > 3.0 for Height).
    - Rich color quantization diversity (>= 256 distinct colors).
    """

    def test_tier5_01_shannon_entropy_richness(self):
        for suite in SUITE_NAMES:
            for suffix in ["_BC.png", "_N.png", "_H.png"]:
                resolved = resolve_map_path(suite, suffix)
                if resolved is None:
                    continue

                with Image.open(resolved) as img:
                    arr = np.array(img)
                    entropy = calculate_shannon_entropy(arr)

                    self.assertGreater(
                        entropy, 3.0,
                        f"{resolved.name}: Shannon entropy too low ({entropy:.2f} < 3.0 bits) - image lacks detail"
                    )

    def test_tier5_02_spatial_frequency_and_laplacian_variance(self):
        for suite in SUITE_NAMES:
            bc_path = resolve_map_path(suite, "_BC.png")
            h_path = resolve_map_path(suite, "_H.png")
            if bc_path is None or h_path is None:
                continue

            with Image.open(bc_path) as bc_img:
                bc_arr = np.array(bc_img)
            h_arr = load_as_grayscale_array(h_path)

            lap_var_bc = calculate_laplacian_variance(bc_arr)
            lap_var_h = calculate_laplacian_variance(h_arr)

            self.assertGreater(
                lap_var_bc, 5.0,
                f"{suite}_BC: BaseColor Laplacian variance too low ({lap_var_bc:.2f}), lacks edge definition"
            )
            self.assertGreater(
                lap_var_h, 3.0,
                f"{suite}_H: Height map Laplacian variance too low ({lap_var_h:.2f}), lacks structural contours"
            )

    def test_tier5_03_color_and_tonal_diversity(self):
        for suite in SUITE_NAMES:
            bc_path = resolve_map_path(suite, "_BC.png")
            if bc_path is None:
                continue

            with Image.open(bc_path) as img:
                arr = np.array(img)
                sample_pixels = arr[::8, ::8, :3].reshape(-1, 3)
                unique_colors = len(np.unique(sample_pixels, axis=0))

                self.assertGreater(
                    unique_colors, 256,
                    f"{suite}_BC: Only {unique_colors} unique colors in sample, expected painterly palette >= 256"
                )


# ---------------------------------------------------------------------------
# Tier 6: Fabric Masks (_Sheen, _Alpha) Translucency and Highlight Integrity
# ---------------------------------------------------------------------------
class TestTier6FabricMasksAndTranslucency(unittest.TestCase):
    """
    Tier 6 tests assert:
    - Fabric masks (`_Sheen`, `_Alpha`) have proper dynamic ranges and distributions.
    - `_Sheen` contains non-zero sheen/pearlescent highlight variance.
    - `_Alpha` exhibits meaningful opacity/translucency structure for lace, organza, and filigree.
    """

    def test_tier6_01_sheen_mask_dynamic_range_and_distribution(self):
        for suite in SUITE_NAMES:
            sheen_path = resolve_map_path(suite, "_Sheen.png")
            if sheen_path is None:
                self.fail(f"Missing Sheen map for suite: {suite}")

            with Image.open(sheen_path) as img:
                arr = np.array(img)
                if arr.ndim == 3:
                    sheen = arr[:, :, 0]
                else:
                    sheen = arr

                s_max = int(np.max(sheen))
                s_std = float(np.std(sheen))

                self.assertGreaterEqual(
                    s_max, 50,
                    f"{suite}_Sheen: Max sheen value ({s_max}) indicates no sheen/specular highlights"
                )
                self.assertGreater(
                    s_std, 1.0,
                    f"{suite}_Sheen: Sheen mask variance too low (std={s_std:.2f})"
                )

    def test_tier6_02_alpha_mask_translucency_and_contrast(self):
        for suite in SUITE_NAMES:
            alpha_path = resolve_map_path(suite, "_Alpha.png")
            if alpha_path is None:
                self.fail(f"Missing Alpha map for suite: {suite}")

            with Image.open(alpha_path) as img:
                arr = np.array(img)
                if arr.ndim == 3:
                    alpha = arr[:, :, 0]
                else:
                    alpha = arr

                a_min, a_max = int(np.min(alpha)), int(np.max(alpha))
                a_std = float(np.std(alpha))
                span = a_max - a_min

                self.assertGreater(
                    span, 30,
                    f"{suite}_Alpha: Alpha mask dynamic span too flat: span={span} ([{a_min}, {a_max}])"
                )
                self.assertGreater(
                    a_std, 2.0,
                    f"{suite}_Alpha: Alpha mask standard deviation too low: {a_std:.2f}"
                )


# ---------------------------------------------------------------------------
# Formatted Summary & CLI Runner
# ---------------------------------------------------------------------------
def generate_summary_report() -> Dict[str, Any]:
    """Generate a structured dictionary summary of the haute-couture texture suites status."""
    report: Dict[str, Any] = {
        "suites_checked": len(SUITE_NAMES),
        "total_expected_maps": TOTAL_EXPECTED_MAPS,
        "existing_maps_count": 0,
        "suites": {},
    }

    for suite in SUITE_NAMES:
        suite_info: Dict[str, Any] = {
            "maps": {},
            "all_present": True,
        }
        for suffix in MAP_SUFFIXES:
            resolved = resolve_map_path(suite, suffix)
            exists = resolved is not None
            map_data: Dict[str, Any] = {
                "exists": exists,
                "path": str(resolved) if resolved else f"{suite}{suffix} (Not Found)",
                "details": {},
            }

            if exists and resolved:
                report["existing_maps_count"] += 1
                try:
                    with Image.open(resolved) as img:
                        arr = np.array(img)
                        map_data["details"] = {
                            "size": img.size,
                            "mode": img.mode,
                            "entropy": round(calculate_shannon_entropy(arr), 2),
                        }
                except Exception as e:
                    map_data["details"] = {"error": str(e)}
            else:
                suite_info["all_present"] = False

            suite_info["maps"][suffix] = map_data

        report["suites"][suite] = suite_info

    return report


def print_cli_summary():
    """Print an ASCII table summarizing texture suite verification status."""
    report = generate_summary_report()
    print("=" * 80)
    print(" INFINITY NIKKI HAUTE-COUTURE PBR VERIFICATION STATUS")
    print("=" * 80)
    print(f"Textures Root: {TEXTURES_DIR}")
    print(f"Total Maps Expected: {report['total_expected_maps']} | Found: {report['existing_maps_count']}")
    print("-" * 80)

    for suite, info in report["suites"].items():
        status = "[OK]" if info["all_present"] else "[MISSING/PARTIAL]"
        print(f"\nSuite: {suite} {status}")
        for suffix, m_info in info["maps"].items():
            if m_info["exists"]:
                d = m_info["details"]
                print(f"  + {suffix:<10} Size={d.get('size')} Mode={d.get('mode')} Entropy={d.get('entropy')} bits")
            else:
                print(f"  - {suffix:<10} MISSING")
    print("=" * 80)


def main():
    global SUITE_NAMES, TOTAL_EXPECTED_MAPS
    parser = argparse.ArgumentParser(description="Infinity Nikki Haute-Couture PBR Verification Test Suite")
    parser.add_argument("--suite", type=str, choices=SUITE_NAMES, help="Filter tests to a specific texture suite")
    parser.add_argument("--tier", type=int, choices=[0, 1, 2, 3, 4, 5, 6], help="Run specific tier only")
    parser.add_argument("--summary", action="store_true", help="Print summary report table")
    parser.add_argument("unittest_args", nargs="*", help="Arguments passed to unittest")

    args, remaining = parser.parse_known_args()

    if args.suite:
        SUITE_NAMES = [args.suite]
        TOTAL_EXPECTED_MAPS = len(SUITE_NAMES) * EXPECTED_MAP_COUNT_PER_SUITE

    if args.summary:
        print_cli_summary()
        sys.exit(0)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    tier_map = {
        0: [TestTier0HarnessSelfVerification],
        1: [TestTier1StructureAndDimensions],
        2: [TestTier2BitDepthAndDynamicRange],
        3: [TestTier3DirectXNormalVectors],
        4: [TestTier4ORMPackingConsistency],
        5: [TestTier5MathematicalEntropyAndStructure],
        6: [TestTier6FabricMasksAndTranslucency],
    }

    if args.tier is not None:
        for test_cls in tier_map[args.tier]:
            suite.addTests(loader.loadTestsFromTestCase(test_cls))
    else:
        for test_classes in tier_map.values():
            for test_cls in test_classes:
                suite.addTests(loader.loadTestsFromTestCase(test_cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        unittest.main()
    else:
        main()
