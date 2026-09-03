"""
Unit Tests for Infinity Nikki Haute-Couture Procedural Asset & Trim Synthesizers (Milestone M1).
Verifies BaseSynthesizer, HighToLowBaker, ChantillyLaceSynthesizer, DifferentialOrganzaSynthesizer,
BaroqueBullionSynthesizer, ReactionDiffusionSynthesizer, and Houdini hython automation runners.
"""

import os
import shutil
import tempfile
import unittest
import numpy as np
from PIL import Image

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
for p in [str(PROJECT_ROOT), str(WORKSPACE_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generators.base_synthesizer import BaseSynthesizer
from generators.high_to_low_baker import HighToLowBaker
from generators.chantilly_lace_synthesizer import ChantillyLaceSynthesizer
from generators.differential_organza_synthesizer import DifferentialOrganzaSynthesizer
from generators.baroque_bullion_synthesizer import BaroqueBullionSynthesizer
from generators.reaction_diffusion_synthesizer import ReactionDiffusionSynthesizer
from generators.houdini_hython_runner import (
    build_houdini_native_networks,
    run_standalone_generation,
)
from generators.generate_all import run_batch_generation


class TestHighToLowBaker(unittest.TestCase):
    """Verifies mathematical invariants and channel outputs of the High-to-Low Baker."""

    def setUp(self):
        self.res = 256
        self.baker = HighToLowBaker(resolution=self.res)
        self.test_dir = tempfile.mkdtemp(prefix="nikki_baker_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_height_16bit_normalization(self):
        """Verifies 16-bit displacement height is strictly uint16 [0, 65535]."""
        raw_depth = np.linspace(-5.0, 15.0, self.res * self.res, dtype=np.float32).reshape(self.res, self.res)
        out_path = os.path.join(self.test_dir, "test_H.png")
        h_norm, h_u16 = self.baker.bake_height_16bit(raw_depth, out_path)

        self.assertEqual(h_u16.dtype, np.uint16)
        self.assertEqual(h_u16.min(), 0)
        self.assertEqual(h_u16.max(), 65535)
        self.assertTrue(os.path.exists(out_path))

        # Check loaded PIL image mode
        with Image.open(out_path) as img:
            self.assertEqual(img.mode, "I;16")
            self.assertEqual(img.size, (self.res, self.res))

    def test_directx_normal_math(self):
        """Verifies unit vector length ||N|| == 1.0 and DirectX Green = -Y orientation."""
        # Create a linear incline in Y: height increases with Y
        y_grid, _ = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        normal_rgb = self.baker.compute_directx_normals(y_grid, bump_scale=10.0)

        self.assertEqual(normal_rgb.shape, (self.res, self.res, 3))
        self.assertEqual(normal_rgb.dtype, np.uint8)

        # Decode normal vectors from [0, 255] to [-1.0, 1.0]
        n_float = (normal_rgb.astype(np.float32) / 255.0) * 2.0 - 1.0
        nx, ny, nz = n_float[..., 0], n_float[..., 1], n_float[..., 2]
        lengths = np.sqrt(nx * nx + ny * ny + nz * nz)

        # Length must be within 0.05 of 1.0 everywhere
        self.assertTrue(np.all(np.abs(lengths - 1.0) < 0.05))

        # For positive dY slope, tangent normal Ny = -dY < 0.
        # In DirectX Green = -Y standard, Ny is encoded in Green channel, so Green channel < 128
        green_mean = float(normal_rgb[..., 1].mean())
        self.assertLess(green_mean, 128)

    def test_curvature_and_ao(self):
        """Verifies curvature baseline at 128 and AO in [0, 255]."""
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        h_dome = np.sin(x_grid * np.pi) * np.sin(y_grid * np.pi)

        curv = self.baker.compute_curvature(h_dome)
        self.assertEqual(curv.dtype, np.uint8)
        self.assertEqual(curv.shape, (self.res, self.res))

        ao = self.baker.compute_ambient_occlusion(h_dome, num_directions=4, max_radius=8)
        self.assertEqual(ao.dtype, np.uint8)
        self.assertEqual(ao.shape, (self.res, self.res))
        self.assertTrue(ao.min() >= 0 and ao.max() <= 255)

    def test_pack_orm(self):
        """Verifies ORM packing: R=AO, G=Roughness, B=Metallic."""
        ao = np.full((self.res, self.res), 200, dtype=np.uint8)
        rough = np.full((self.res, self.res), 100, dtype=np.uint8)
        metal = np.full((self.res, self.res), 255, dtype=np.uint8)

        orm = self.baker.pack_orm(ao, rough, metal)
        self.assertEqual(orm.shape, (self.res, self.res, 3))
        self.assertEqual(orm.dtype, np.uint8)
        self.assertTrue(np.all(orm[..., 0] == 200))
        self.assertTrue(np.all(orm[..., 1] == 100))
        self.assertTrue(np.all(orm[..., 2] == 255))


class TestHauteCoutureSynthesizers(unittest.TestCase):
    """Verifies geometry generation and PBR map synthesis across all 4 archetypes."""

    def setUp(self):
        self.res = 256
        self.seed = 42

    def test_chantilly_lace_synthesizer(self):
        """Verifies Archetype 1: Chantilly Lace & Micro-Beading."""
        synth = ChantillyLaceSynthesizer(resolution=self.res, seed=self.seed)

        geo = synth.generate_geometry()
        self.assertIn("vertices", geo)
        self.assertIn("faces", geo)
        self.assertGreater(len(geo["vertices"]), 1000)
        self.assertGreater(len(geo["faces"]), 1000)

        maps = synth.synthesize_maps()
        for expected_key in ["BaseColor", "Roughness", "Metallic", "Sheen", "Alpha", "Height"]:
            self.assertIn(expected_key, maps)
            self.assertEqual(maps[expected_key].shape[:2], (self.res, self.res))

    def test_differential_organza_synthesizer(self):
        """Verifies Archetype 2: Differential Line Growth Organza."""
        synth = DifferentialOrganzaSynthesizer(resolution=self.res, seed=self.seed)

        geo = synth.generate_geometry()
        self.assertIn("vertices", geo)
        self.assertIn("faces", geo)
        self.assertGreater(len(geo["vertices"]), 500)
        self.assertGreater(len(geo["faces"]), 500)

        maps = synth.synthesize_maps()
        for expected_key in ["BaseColor", "Roughness", "Metallic", "Sheen", "Alpha", "Height"]:
            self.assertIn(expected_key, maps)
            self.assertEqual(maps[expected_key].shape[:2], (self.res, self.res))

        # Organza has subtle lurex shimmer (std > 0.5)
        self.assertGreater(float(maps["Metallic"].std()), 0.5)
        # Sheen is high (> 0.70)
        self.assertGreater(maps["Sheen"].mean(), 180)

    def test_baroque_bullion_synthesizer(self):
        """Verifies Archetype 3: Baroque Bullion Acanthus Embroidery."""
        synth = BaroqueBullionSynthesizer(resolution=self.res, seed=self.seed)

        geo = synth.generate_geometry()
        self.assertIn("vertices", geo)
        self.assertIn("faces", geo)
        self.assertGreater(len(geo["vertices"]), 1000)
        self.assertGreater(len(geo["faces"]), 1000)

        maps = synth.synthesize_maps()
        for expected_key in ["BaseColor", "Roughness", "Metallic", "Sheen", "Alpha", "Height"]:
            self.assertIn(expected_key, maps)
            self.assertEqual(maps[expected_key].shape[:2], (self.res, self.res))

        # Contains 100% metallic gold wires
        self.assertEqual(maps["Metallic"].max(), 255)

    def test_reaction_diffusion_synthesizer(self):
        """Verifies Archetype 4: Reaction-Diffusion Cloisons / Micro-Filigree."""
        synth = ReactionDiffusionSynthesizer(resolution=self.res, seed=self.seed)

        geo = synth.generate_geometry()
        self.assertIn("vertices", geo)
        self.assertIn("faces", geo)
        self.assertGreater(len(geo["vertices"]), 1000)
        self.assertGreater(len(geo["faces"]), 1000)

        maps = synth.synthesize_maps()
        for expected_key in ["BaseColor", "Roughness", "Metallic", "Sheen", "Alpha", "Height"]:
            self.assertIn(expected_key, maps)
            self.assertEqual(maps[expected_key].shape[:2], (self.res, self.res))

        # Contains ultra-glossy vitreous enamel (Roughness < 30) and gold filigree (Metallic = 255)
        self.assertLess(maps["Roughness"].min(), 30)
        self.assertEqual(maps["Metallic"].max(), 255)


class TestMeshExportAndBatchRunner(unittest.TestCase):
    """Verifies OBJ exporter and batch runner."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="nikki_batch_test_")
        self.tex_dir = os.path.join(self.test_dir, "textures")
        self.geo_dir = os.path.join(self.test_dir, "models")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_obj(self):
        """Verifies standard Wavefront OBJ file export."""
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        normals = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype=np.float32)
        uvs = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)

        obj_path = os.path.join(self.test_dir, "test_triangle.obj")
        res_path = BaseSynthesizer.export_obj(obj_path, verts, faces, normals, uvs)

        self.assertTrue(os.path.exists(res_path))
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("v 0.000000 0.000000 0.000000", content)
        self.assertIn("f 1/1/1 2/2/2 3/3/3", content)

    def test_run_batch_generation(self):
        """Verifies full batch synthesis of 4 archetypes at 256 resolution."""
        results = run_batch_generation(
            archetype="all",
            resolution=256,
            out_dir=self.tex_dir,
            geo_dir=self.geo_dir,
            seed=42,
        )

        self.assertEqual(len(results), 4)
        for prefix, channels in results.items():
            self.assertIn("BaseColor", channels)
            self.assertIn("Normal", channels)
            self.assertIn("ORM", channels)
            self.assertIn("Height", channels)
            self.assertIn("AO", channels)
            self.assertIn("Roughness", channels)
            self.assertIn("Metallic", channels)
            self.assertIn("Sheen", channels)
            self.assertIn("Alpha", channels)
            self.assertIn("Mesh_OBJ", channels)

            # Check that files exist on disk
            for channel_name, fpath in channels.items():
                self.assertTrue(os.path.exists(fpath), f"File missing: {fpath}")


if __name__ == "__main__":
    unittest.main()
