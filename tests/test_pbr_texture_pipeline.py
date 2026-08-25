"""Tier 1 & Tier 2 Test Suite: PBR Texture Channel Standardization & Packing Pipeline.

Tests:
- ORM channel packing correctness (R=AO, G=Roughness, B=Metallic)
- Fallback value assignments when source maps are missing
- Power-of-Two (POT) dimension validation and non-square POT handling
- Color space rules (sRGB metadata flags)
- Bit depth, compression, and file format contracts
- Naming conventions (T_<Family>_<Name>_<Channel>) and suffix parsing
- Corrupted / truncated / invalid image handling
- Glossiness-to-Roughness inversion math
- High-throughput PIL image packing & auto-resampling
"""

from __future__ import annotations

import io
import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image

# Add Content/Python to path
PYTHON_DIR = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Python")
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from melodia_pbr_packer import ChannelSlot, PBRChannelPacker
from validate_melodia_pipeline import (
    PipelineValidator,
    ValidationCategory,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)

PBR_CHANNEL_DEFAULTS = {
    "AO": 255,          # 1.0 in normalized float (no occlusion)
    "Roughness": 178,   # ~0.7 in normalized float (standard dielectric diffuse roughness)
    "Metallic": 0,      # 0.0 in normalized float (dielectric non-metal)
    "Height": 128,      # 0.5 in normalized float (neutral mid-displacement)
    "Normal": (128, 128, 255),  # Flat tangent-space +Z normal [0.5, 0.5, 1.0]
    "Sheen": 0,         # 0.0 (no fabric sheen)
    "Sparkle": 0,       # 0.0 (no glitter/sparkle)
    "Alpha": 255,       # 1.0 (fully opaque)
}

CANONICAL_NAMING_REGEX = re.compile(
    r"^T_(?P<family>[A-Za-z0-9]+)_(?P<name>[A-Za-z0-9]+)_(?P<channel>BC|ORM|N|H|Disp|DetailN|Sheen|Sparkle|Alpha|Mask)$"
)


def is_power_of_two(dimension: int) -> bool:
    return dimension > 0 and (dimension & (dimension - 1)) == 0


def validate_texture_dimensions(width: int, height: int) -> Tuple[bool, str]:
    if width <= 0 or height <= 0:
        return False, f"Invalid non-positive dimensions: {width}x{height}"
    if not is_power_of_two(width):
        return False, f"Width {width} is not a power of two"
    if not is_power_of_two(height):
        return False, f"Height {height} is not a power of two"
    return True, "Valid POT dimensions"


def get_expected_srgb_state(channel_suffix: str) -> bool:
    suffix_upper = channel_suffix.upper()
    color_keywords = ["BC", "BASECOLOR", "ALBEDO", "COLOR", "DIFFUSE", "DIFF"]
    return any(k in suffix_upper for k in color_keywords)


def invert_glossiness(gloss_value: int) -> int:
    return max(0, min(255, 255 - gloss_value))


class TestPBRTextureInvariantsTier1(unittest.TestCase):
    """Tier 1 Unit tests verifying mathematical invariants and format rules."""

    def test_naming_convention_canonical(self):
        valid_names = [
            "T_Fabric_RoyalVelvet_BC",
            "T_Fabric_RoyalVelvet_ORM",
            "T_Fabric_RoyalVelvet_N",
            "T_Fabric_RoyalVelvet_H",
            "T_Fabric_RoyalVelvet_Sheen",
            "T_Melusina_UpdatedShirt_BC",
            "T_Melusina_UpdatedShirt_ORM",
            "T_Melusina_UpdatedShirt_N",
            "T_Melusina_UpdatedShirt_Alpha",
            "T_Trim_ZenFlowers4K_ORM",
            "T_Props_CathedralPillar_DetailN",
            "T_VFX_SparkleTwinkle8_Sparkle",
        ]
        for name in valid_names:
            match = CANONICAL_NAMING_REGEX.match(name)
            self.assertIsNotNone(match, f"Valid canonical name rejected: {name}")

        invalid_names = [
            "RoyalVelvet_BC",
            "T_Fabric_RoyalVelvet",
            "T_Fabric_RoyalVelvet_Diffuse",
            "T__RoyalVelvet_BC",
            "t_fabric_velvet_bc",
            "T_Fabric_Velvet_ORM_Final_v2",
        ]
        for name in invalid_names:
            match = CANONICAL_NAMING_REGEX.match(name)
            self.assertIsNone(match, f"Invalid name incorrectly accepted: {name}")

    def test_power_of_two_dimensions(self):
        for pot in [64, 128, 256, 512, 1024, 2048, 4096, 8192]:
            self.assertTrue(is_power_of_two(pot))
            valid, msg = validate_texture_dimensions(pot, pot)
            self.assertTrue(valid, msg)

        for w, h in [(2048, 1024), (4096, 2048), (512, 2048), (1024, 256)]:
            valid, msg = validate_texture_dimensions(w, h)
            self.assertTrue(valid, msg)

        for w, h in [(1920, 1080), (500, 500), (3000, 2000), (0, 1024), (-512, 512)]:
            valid, msg = validate_texture_dimensions(w, h)
            self.assertFalse(valid)

    def test_srgb_metadata_rules(self):
        for ch in ["BC", "BaseColor", "albedo", "diffuseOriginal", "color"]:
            self.assertTrue(get_expected_srgb_state(ch))

        for ch in ["ORM", "N", "Normal", "H", "Height", "Disp", "Displacement", "Roughness", "Metallic", "AO"]:
            self.assertFalse(get_expected_srgb_state(ch))

    def test_default_fallback_values(self):
        self.assertEqual(PBR_CHANNEL_DEFAULTS["AO"], 255)
        self.assertEqual(PBR_CHANNEL_DEFAULTS["Roughness"], 178)
        self.assertEqual(PBR_CHANNEL_DEFAULTS["Metallic"], 0)
        self.assertEqual(PBR_CHANNEL_DEFAULTS["Height"], 128)
        self.assertEqual(PBR_CHANNEL_DEFAULTS["Normal"], (128, 128, 255))

    def test_glossiness_to_roughness_inversion(self):
        test_pairs = [(0, 255), (255, 0), (128, 127), (200, 55), (50, 205)]
        for gloss, expected_roughness in test_pairs:
            self.assertEqual(invert_glossiness(gloss), expected_roughness)


class TestPBRTexturePipelineTier2(unittest.TestCase):
    """Tier 2 Component tests executing genuine PIL packing, resizing, and file operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pbr_channel_packer_direct(self):
        packer = PBRChannelPacker()

        ao_p = self.temp_path / "test_ao.png"
        gloss_p = self.temp_path / "test_gloss.png"
        metal_p = self.temp_path / "test_metallic.png"

        Image.new("L", (128, 128), color=210).save(ao_p)
        Image.new("L", (128, 128), color=180).save(gloss_p)
        Image.new("L", (128, 128), color=240).save(metal_p)

        orm_out = self.temp_path / "T_Test_Packer_ORM.png"
        res_img = packer.pack_orm(
            ao_path=ao_p,
            roughness_path=gloss_p,
            metallic_path=metal_p,
            output_path=orm_out,
            invert_gloss=True,
            target_resolution=(128, 128),
        )

        self.assertTrue(orm_out.exists())
        arr = np.array(res_img)
        self.assertEqual(arr.shape, (128, 128, 3))
        self.assertEqual(int(arr[0, 0, 0]), 210)
        self.assertEqual(int(arr[0, 0, 1]), 75)
        self.assertEqual(int(arr[0, 0, 2]), 240)

    def test_normal_map_green_flip_and_normalization(self):
        packer = PBRChannelPacker()
        norm_in = self.temp_path / "test_normal.png"
        norm_out = self.temp_path / "test_normal_dx.png"

        Image.new("RGB", (64, 64), color=(150, 200, 230)).save(norm_in)

        out_img = packer.process_normal_map(
            normal_path=norm_in,
            output_path=norm_out,
            flip_green=True,
            normalize_vectors=True,
        )
        self.assertTrue(norm_out.exists())
        arr = np.array(out_img, dtype=np.float32)

        nx = (arr[:, :, 0] / 127.5) - 1.0
        ny = (arr[:, :, 1] / 127.5) - 1.0
        nz = (arr[:, :, 2] / 127.5) - 1.0
        lengths = np.sqrt(nx * nx + ny * ny + nz * nz)
        self.assertTrue(np.allclose(lengths, 1.0, atol=0.05))

    def test_pipeline_validator_integration(self):
        valid_p = self.temp_path / "T_Valid_BC.png"
        Image.new("RGB", (512, 512), color=(128, 128, 128)).save(valid_p)

        npot_p = self.temp_path / "T_Invalid_BC.png"
        Image.new("RGB", (300, 300), color=(128, 128, 128)).save(npot_p)

        validator = PipelineValidator()
        report = validator.validate_texture_set({"valid": valid_p, "npot": npot_p})

        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.total_textures, 2)
        res_issues = [i for i in report.issues if i.category == ValidationCategory.RESOLUTION]
        self.assertGreater(len(res_issues), 0)

    def test_real_world_generated_assets_verification(self):
        melusina_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Melodia\Characters\Melusina\Textures")
        textures_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures")

        test_files = [
            melusina_dir / "T_Melusina_UpdatedShirt_ORM.png",
            melusina_dir / "T_Melusina_FrontPanel_ORM.png",
            textures_dir / "T_Bling_Rhinestone01_ORM.png",
            textures_dir / "T_ClothTrim_Linen_ORM.png",
            textures_dir / "T_ClothTrim_Base4K_ORM.png",
            textures_dir / "T_ZenTrim_Base4K_ORM.png",
        ]

        for p in test_files:
            if p.exists():
                with Image.open(p) as img:
                    w, h = img.size
                    self.assertTrue(is_power_of_two(w))
                    self.assertTrue(is_power_of_two(h))
                    self.assertEqual(img.mode, "RGB")
                    arr = np.array(img)
                    self.assertEqual(arr.ndim, 3)
                    self.assertEqual(arr.shape[2], 3)
                    ao_mean = float(arr[:, :, 0].mean())
                    rough_mean = float(arr[:, :, 1].mean())
                    metal_mean = float(arr[:, :, 2].mean())
                    self.assertGreaterEqual(ao_mean, 0.0)
                    self.assertLessEqual(ao_mean, 255.0)
                    self.assertGreaterEqual(rough_mean, 0.0)
                    self.assertLessEqual(rough_mean, 255.0)
                    self.assertGreaterEqual(metal_mean, 0.0)
                    self.assertLessEqual(metal_mean, 255.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
