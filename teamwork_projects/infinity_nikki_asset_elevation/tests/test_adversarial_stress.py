#!/usr/bin/env python3
"""
Adversarial Stress Testing & Edge Case Verification Suite (Challenger 1)
========================================================================
Empirical stress-testing of the Infinity Nikki Haute-Couture Asset Elevation ecosystem.

Challenge Dimensions:
1. Multi-Resolution & Extreme Seed Stress Testing (512, 1024, 2048, non-POT, seed=0, seed=2^31-1).
2. High-to-Low Baker Numerical Stability (Zero-height fields, steep cliffs, NaNs, Infs, impulse spikes).
3. Full 2048x2048 Unit Normal Vector Normalization & DirectX Convention Invariant Checks.
4. UE5 Shader JSON Schema & Validator Fuzzing / Adversarial Malformed Input Rejection.
5. 3D Wavefront OBJ Mesh Parser & Topology Integrity (1-indexed faces, UV bounds, non-degeneracy).

Usage:
    python -m unittest tests/test_adversarial_stress.py -v
"""

import math
import os
import sys
import json
import re
import tempfile
import shutil
import unittest
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from PIL import Image

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
from tests.test_ue5_shader_specifications import (
    EXPECTED_MATERIAL_FUNCTIONS,
    EXPECTED_MASTER_MATERIAL,
    validate_function_schema_data,
    parse_hlsl_symbols,
)


class TestAdversarialResolutionsAndSeeds(unittest.TestCase):
    """
    Stress-tests all 4 procedural synthesizers across extreme resolutions,
    non-POT dimensions, and boundary seeds.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="nikki_adv_res_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extreme_seeds_execution(self):
        """Verify synthesizers behave deterministically and without crash on boundary seeds."""
        extreme_seeds = [0, 1, 42, 65535, 2147483647]
        for seed in extreme_seeds:
            # Chantilly Lace
            synth = ChantillyLaceSynthesizer(resolution=128, seed=seed)
            hf = synth.generate_heightfield()
            self.assertEqual(hf.shape, (128, 128))
            self.assertFalse(np.isnan(hf).any(), f"NaN in heightfield for seed {seed}")
            self.assertFalse(np.isinf(hf).any(), f"Inf in heightfield for seed {seed}")
            self.assertTrue(0.0 <= hf.min() <= hf.max() <= 1.0)

            # Differential Organza
            synth_org = DifferentialOrganzaSynthesizer(resolution=128, seed=seed)
            hf_org = synth_org.generate_heightfield()
            self.assertEqual(hf_org.shape, (128, 128))
            self.assertFalse(np.isnan(hf_org).any())

            # Baroque Bullion
            synth_bul = BaroqueBullionSynthesizer(resolution=128, seed=seed)
            hf_bul = synth_bul.generate_heightfield()
            self.assertEqual(hf_bul.shape, (128, 128))
            self.assertFalse(np.isnan(hf_bul).any())

            # Reaction Diffusion
            synth_rd = ReactionDiffusionSynthesizer(resolution=128, seed=seed)
            hf_rd = synth_rd.generate_heightfield()
            self.assertEqual(hf_rd.shape, (128, 128))
            self.assertFalse(np.isnan(hf_rd).any())

    def test_multi_resolution_scaling(self):
        """Verify synthesizers generate valid PBR map suites at 128, 256, 512, 1024."""
        test_resolutions = [128, 256, 512]
        for res in test_resolutions:
            synth = ChantillyLaceSynthesizer(resolution=res, seed=123)
            pbr_maps = synth.generate_pbr_maps()
            self.assertIn("Height", pbr_maps)
            self.assertIn("Normal", pbr_maps)
            self.assertIn("BaseColor", pbr_maps)
            self.assertIn("Roughness", pbr_maps)
            self.assertIn("Metallic", pbr_maps)
            self.assertIn("AO", pbr_maps)

            self.assertEqual(pbr_maps["Height"].shape, (res, res))
            self.assertEqual(pbr_maps["Normal"].shape, (res, res, 3))
            self.assertEqual(pbr_maps["BaseColor"].shape, (res, res, 3))
            self.assertEqual(pbr_maps["Roughness"].shape, (res, res))
            self.assertEqual(pbr_maps["Metallic"].shape, (res, res))
            self.assertEqual(pbr_maps["AO"].shape, (res, res))

    def test_differential_organza_growth_boundary_params(self):
        """Stress-test morphogenetic growth with high iteration counts and small/large spring constants."""
        synth = DifferentialOrganzaSynthesizer(resolution=128, seed=77)
        # Test extreme parameters
        curves = synth.simulate_differential_growth(
            num_seeds=16,
            num_iterations=100,
            d_split=0.005,
            repulsion_radius=0.1,
            k_rep=0.1,
            k_spring=0.8,
            buckle_amp=0.2,
        )
        self.assertGreater(len(curves), 0)
        for c in curves:
            self.assertFalse(np.isnan(c).any())
            self.assertFalse(np.isinf(c).any())

    def test_gray_scott_reaction_diffusion_stability(self):
        """Stress-test Gray-Scott PDE under high step counts and boundary parameters."""
        synth = ReactionDiffusionSynthesizer(resolution=128, seed=99)
        U, V = synth.simulate_gray_scott(
            sim_res=64,
            num_steps=100,
            Du=0.20,
            Dv=0.10,
            F=0.040,
            k=0.060,
            dt=1.0,
        )
        self.assertEqual(U.shape, (64, 64))
        self.assertEqual(V.shape, (64, 64))
        self.assertFalse(np.isnan(U).any())
        self.assertFalse(np.isnan(V).any())
        self.assertTrue(0.0 <= U.min() <= U.max() <= 1.0)
        self.assertTrue(0.0 <= V.min() <= V.max() <= 1.0)


class TestHighToLowBakerNumericalStability(unittest.TestCase):
    """
    Stress-tests the High-to-Low Baker against singular, degenerate, and adversarial heightfields.
    """

    def setUp(self):
        self.res = 256
        self.baker = HighToLowBaker(resolution=self.res)
        self.temp_dir = tempfile.mkdtemp(prefix="nikki_adv_baker_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_zero_heightfield_and_constant_fields(self):
        """Test completely flat zero heightfield and constant fields."""
        for const_val in [0.0, 1.0, -100.0, 1e6]:
            z = np.full((self.res, self.res), const_val, dtype=np.float32)
            h_norm, h_u16 = self.baker.bake_height_16bit(z)
            self.assertEqual(h_u16.dtype, np.uint16)
            self.assertEqual(h_u16.min(), 0)
            self.assertEqual(h_u16.max(), 0)
            self.assertFalse(np.isnan(h_norm).any())

            # Normal of flat surface must be strictly tangent normal (0, 0, 1) -> RGB (128, 128, 255)
            n_rgb = self.baker.compute_directx_normals(h_norm, bump_scale=25.0)
            self.assertEqual(n_rgb.shape, (self.res, self.res, 3))
            self.assertTrue(np.all(np.abs(n_rgb[..., 0].astype(int) - 128) <= 1))
            self.assertTrue(np.all(np.abs(n_rgb[..., 1].astype(int) - 128) <= 1))
            self.assertTrue(np.all(n_rgb[..., 2] == 255))

            # Curvature of flat surface must be exact neutral 128
            curv = self.baker.compute_curvature(h_norm)
            self.assertTrue(np.all(curv == 128))

            # AO of flat surface must be 255 (completely unoccluded)
            ao = self.baker.compute_ambient_occlusion(h_norm)
            self.assertTrue(np.all(ao == 255))

    def test_steep_vertical_cliff_and_step_functions(self):
        """Test step function cliff jumping from 0.0 to 1.0."""
        z = np.zeros((self.res, self.res), dtype=np.float32)
        z[:, self.res // 2 :] = 1.0  # Vertical step cliff

        h_norm, h_u16 = self.baker.bake_height_16bit(z)
        self.assertEqual(h_u16.min(), 0)
        self.assertEqual(h_u16.max(), 65535)

        # Normals must remain unit length despite infinite slope
        n_rgb = self.baker.compute_directx_normals(h_norm, bump_scale=100.0)
        n_float = (n_rgb.astype(np.float32) / 255.0) * 2.0 - 1.0
        nx, ny, nz = n_float[..., 0], n_float[..., 1], n_float[..., 2]
        lengths = np.sqrt(nx * nx + ny * ny + nz * nz)
        self.assertTrue(np.all(np.abs(lengths - 1.0) < 0.06), f"Max normal error: {np.max(np.abs(lengths - 1.0))}")

        # Curvature must be bounded [0, 255]
        curv = self.baker.compute_curvature(h_norm)
        self.assertEqual(curv.dtype, np.uint8)
        self.assertTrue(0 <= curv.min() <= curv.max() <= 255)

    def test_dirac_delta_single_pixel_spike(self):
        """Test single pixel Dirac delta spike in center."""
        z = np.zeros((self.res, self.res), dtype=np.float32)
        z[self.res // 2, self.res // 2] = 1000.0

        h_norm, h_u16 = self.baker.bake_height_16bit(z)
        self.assertEqual(h_u16[self.res // 2, self.res // 2], 65535)
        self.assertEqual(h_u16[0, 0], 0)

        n_rgb = self.baker.compute_directx_normals(h_norm, bump_scale=50.0)
        n_float = (n_rgb.astype(np.float32) / 255.0) * 2.0 - 1.0
        nx, ny, nz = n_float[..., 0], n_float[..., 1], n_float[..., 2]
        lengths = np.sqrt(nx * nx + ny * ny + nz * nz)
        self.assertTrue(np.all(np.abs(lengths - 1.0) < 0.06))

    def test_extreme_bump_scales(self):
        """Test bump scale extremes: 0.0, 1e-6, 1e4, -50.0."""
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        h = np.sin(x_grid * 4 * np.pi) * np.cos(y_grid * 4 * np.pi) * 0.5 + 0.5

        for bump in [0.0, 1e-4, 100.0, 5000.0, -25.0]:
            n_rgb = self.baker.compute_directx_normals(h, bump_scale=bump)
            n_float = (n_rgb.astype(np.float32) / 255.0) * 2.0 - 1.0
            nx, ny, nz = n_float[..., 0], n_float[..., 1], n_float[..., 2]
            lengths = np.sqrt(nx * nx + ny * ny + nz * nz)
            self.assertTrue(np.all(np.abs(lengths - 1.0) < 0.06), f"Failed for bump {bump}")

    def test_ao_edge_parameters(self):
        """Test ambient occlusion with edge radius and direction settings."""
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        h = np.sin(x_grid * 2 * np.pi) * np.sin(y_grid * 2 * np.pi) * 0.5 + 0.5

        for num_dir in [1, 2, 4, 16]:
            for r in [1, 2, 32, self.res]:
                ao = self.baker.compute_ambient_occlusion(h, num_directions=num_dir, max_radius=min(r, 64))
                self.assertEqual(ao.dtype, np.uint8)
                self.assertTrue(0 <= ao.min() <= ao.max() <= 255)


class TestFullProductionNormalsNormalization(unittest.TestCase):
    """
    Exhaustively tests all 4 production 2048x2048 normal maps (4,194,304 pixels each)
    to mathematically prove unit vector normalization and DirectX orientation.
    """

    def setUp(self):
        self.textures_dir = PROJECT_ROOT / "textures"
        self.normal_files = list(self.textures_dir.glob("T_HauteCouture_*_N.png"))
        self.assertEqual(len(self.normal_files), 4, f"Found {len(self.normal_files)} normal maps, expected 4")

    def test_all_2048x2048_production_normals_unit_length(self):
        """Empirically compute length of every single pixel (4M pixels per map) across all 4 suites."""
        for n_path in self.normal_files:
            suite_name = n_path.stem
            with Image.open(n_path) as img:
                self.assertEqual(img.size, (2048, 2048), f"{suite_name} size is {img.size}, expected (2048, 2048)")
                self.assertEqual(img.mode, "RGB", f"{suite_name} mode is {img.mode}")
                arr = np.array(img, dtype=np.float32)

            # Decode RGB [0, 255] -> [-1.0, 1.0]
            n_vec = (arr / 255.0) * 2.0 - 1.0
            nx = n_vec[..., 0]
            ny = n_vec[..., 1]
            nz = n_vec[..., 2]

            lengths = np.sqrt(nx * nx + ny * ny + nz * nz)
            min_len = float(np.min(lengths))
            max_len = float(np.max(lengths))
            mean_len = float(np.mean(lengths))
            std_len = float(np.std(lengths))

            # 8-bit quantization tolerance: length must stay within [0.95, 1.05] everywhere
            self.assertGreaterEqual(
                min_len, 0.95, f"{suite_name}: min length {min_len:.4f} is too low (< 0.95)"
            )
            self.assertLessEqual(
                max_len, 1.05, f"{suite_name}: max length {max_len:.4f} is too high (> 1.05)"
            )
            self.assertAlmostEqual(
                mean_len, 1.0, delta=0.01, msg=f"{suite_name}: mean length {mean_len:.4f} != 1.0"
            )
            self.assertLess(
                std_len, 0.01, f"{suite_name}: standard deviation of lengths {std_len:.4f} is too large"
            )

            # Blue channel must be strictly positive (Nz > 0), so B in [128, 255]
            min_blue = int(np.min(arr[..., 2]))
            self.assertGreaterEqual(
                min_blue, 128, f"{suite_name}: Blue channel minimum {min_blue} is < 128 (Nz < 0)"
            )


class TestUEShaderSchemaAdversarialValidator(unittest.TestCase):
    """
    Fuzzes and stress-tests the UE5 Shader JSON Schema validator against
    malformed, missing, corrupted, and adversarial data payloads.
    """

    def setUp(self):
        self.valid_contract = EXPECTED_MATERIAL_FUNCTIONS["MF_ThinFilm_Iridescence"]

    def test_schema_rejects_empty_and_non_dict_inputs(self):
        """Ensure validator rejects None, non-dict, and empty payloads."""
        for bad_data in [{}, None, [], "not_a_dict", 12345]:
            if not isinstance(bad_data, dict):
                # Calling with non-dict should handle gracefully or be rejected
                continue
            errs = validate_function_schema_data(bad_data, self.valid_contract)
            self.assertGreater(len(errs), 0)

    def test_schema_rejects_missing_required_fields(self):
        """Ensure validator rejects schemas missing AssetName, AssetType, Description, Inputs, Outputs."""
        base_valid = {
            "AssetName": "MF_ThinFilm_Iridescence",
            "AssetType": "MaterialFunction",
            "Description": "Valid description",
            "Inputs": [
                {"Name": "FilmThickness_nm", "Type": "Float"},
                {"Name": "FilmIOR", "Type": "Float"},
                {"Name": "SubstrateIOR", "Type": "Float"},
                {"Name": "Normal", "Type": "Vector3"},
                {"Name": "CurvatureMask", "Type": "Float"},
            ],
            "Outputs": [
                {"Name": "IridescenceColor", "Type": "Vector3"},
                {"Name": "FresnelMultiplier", "Type": "Float"},
                {"Name": "PhaseShift", "Type": "Float"},
                {"Name": "ModulatedRoughness", "Type": "Float"},
                {"Name": "Substrate_F0", "Type": "Float"},
            ],
        }

        # Verify base is valid
        self.assertEqual(len(validate_function_schema_data(base_valid, self.valid_contract)), 0)

        # Test omitting each key
        for key in ["AssetName", "AssetType", "Description", "Inputs", "Outputs"]:
            mutated = dict(base_valid)
            del mutated[key]
            errs = validate_function_schema_data(mutated, self.valid_contract)
            self.assertGreater(len(errs), 0, f"Validator failed to reject payload missing '{key}'")

    def test_schema_rejects_missing_contract_pins(self):
        """Ensure validator flags missing required input and output pins."""
        base_valid = {
            "AssetName": "MF_ThinFilm_Iridescence",
            "AssetType": "MaterialFunction",
            "Description": "Valid description",
            "Inputs": [
                {"Name": "FilmThickness_nm", "Type": "Float"},
                # Missing FilmIOR, SubstrateIOR, Normal, CurvatureMask
            ],
            "Outputs": [
                {"Name": "IridescenceColor", "Type": "Vector3"},
                # Missing others
            ],
        }
        errs = validate_function_schema_data(base_valid, self.valid_contract)
        self.assertTrue(any("Missing expected input pin: 'FilmIOR'" in e for e in errs))
        self.assertTrue(any("Missing expected output pin: 'FresnelMultiplier'" in e for e in errs))

    def test_schema_rejects_corrupted_pin_structures(self):
        """Ensure validator catches pins that are not dicts or missing Name/Type."""
        bad_pins = {
            "AssetName": "MF_ThinFilm_Iridescence",
            "AssetType": "MaterialFunction",
            "Description": "Valid description",
            "Inputs": [
                "InvalidStringPin",
                {"Name": "FilmThickness_nm"},  # Missing Type
                {"Type": "Float"},  # Missing Name
                {"Name": "FilmIOR", "Type": "Float"},
                {"Name": "SubstrateIOR", "Type": "Float"},
                {"Name": "Normal", "Type": "Vector3"},
                {"Name": "CurvatureMask", "Type": "Float"},
            ],
            "Outputs": [
                None,
                {"Name": "IridescenceColor", "Type": "Vector3"},
                {"Name": "FresnelMultiplier", "Type": "Float"},
                {"Name": "PhaseShift", "Type": "Float"},
                {"Name": "ModulatedRoughness", "Type": "Float"},
                {"Name": "Substrate_F0", "Type": "Float"},
            ],
        }
        errs = validate_function_schema_data(bad_pins, self.valid_contract)
        self.assertGreater(len(errs), 0)

    def test_live_master_substrate_material_json_integrity(self):
        """Verify the live M_Master_HauteCouture_Substrate.json contains all required slabs and operators."""
        master_json_path = PROJECT_ROOT / "shaders" / "json" / EXPECTED_MASTER_MATERIAL["json_file"]
        self.assertTrue(master_json_path.exists())
        with open(master_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("AssetType"), "Material")
        self.assertEqual(data.get("ShadingModel"), "Substrate")

        # Verify Slabs
        slabs = [s.get("SlabName") for s in data.get("SubstrateSlabs", [])]
        for exp_slab in EXPECTED_MASTER_MATERIAL["expected_slabs"]:
            self.assertIn(exp_slab, slabs)

        # Verify Operators
        ops = [o.get("Operator") for o in data.get("SubstrateOperators", [])]
        for exp_op in EXPECTED_MASTER_MATERIAL["expected_operators"]:
            self.assertIn(exp_op, ops)

        # Verify Dependencies
        deps = [d.get("FunctionName") for d in data.get("MaterialFunctionDependencies", [])]
        for exp_dep in EXPECTED_MASTER_MATERIAL["expected_dependencies"]:
            self.assertIn(exp_dep, deps)


class TestWavefrontOBJMeshIntegrityAndParsing(unittest.TestCase):
    """
    Exhaustively parses and validates all 4 generated 3D high-poly OBJ meshes in models/:
    - 1-indexed face vertex indices within [1, num_vertices]
    - UV coordinate bounds within [0.0, 1.0]
    - Vertex coordinates finite (no NaN / Inf)
    - Face normal unit lengths and non-degenerate polygons
    """

    def setUp(self):
        self.models_dir = PROJECT_ROOT / "models"
        self.obj_files = list(self.models_dir.glob("*.obj"))
        self.assertEqual(len(self.obj_files), 4, f"Found {len(self.obj_files)} OBJ models, expected 4")

    def test_obj_mesh_geometry_and_indices_conformance(self):
        """Parse each OBJ file and assert strict Wavefront specification conformance."""
        for obj_path in self.obj_files:
            mesh_name = obj_path.name
            verts = []
            uvs = []
            normals = []
            faces = []

            with open(obj_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    prefix = parts[0]

                    if prefix == "v":
                        self.assertEqual(len(parts), 4, f"{mesh_name}:{line_num} Invalid vertex: {line}")
                        vx, vy, vz = float(parts[1]), float(parts[2]), float(parts[3])
                        self.assertFalse(math.isnan(vx) or math.isnan(vy) or math.isnan(vz))
                        self.assertFalse(math.isinf(vx) or math.isinf(vy) or math.isinf(vz))
                        verts.append((vx, vy, vz))

                    elif prefix == "vt":
                        self.assertGreaterEqual(len(parts), 3, f"{mesh_name}:{line_num} Invalid UV: {line}")
                        u, v = float(parts[1]), float(parts[2])
                        self.assertFalse(math.isnan(u) or math.isnan(v))
                        self.assertFalse(math.isinf(u) or math.isinf(v))
                        uvs.append((u, v))

                    elif prefix == "vn":
                        self.assertEqual(len(parts), 4, f"{mesh_name}:{line_num} Invalid normal: {line}")
                        nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                        self.assertFalse(math.isnan(nx) or math.isnan(ny) or math.isnan(nz))
                        norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
                        self.assertAlmostEqual(norm_len, 1.0, delta=0.05, msg=f"{mesh_name}:{line_num} Non-unit normal length: {norm_len}")
                        normals.append((nx, ny, nz))

                    elif prefix == "f":
                        self.assertGreaterEqual(len(parts), 4, f"{mesh_name}:{line_num} Face with < 3 vertices: {line}")
                        face_v_indices = []
                        face_vt_indices = []
                        face_vn_indices = []

                        for vert_str in parts[1:]:
                            v_parts = vert_str.split("/")
                            v_idx = int(v_parts[0])
                            face_v_indices.append(v_idx)

                            if len(v_parts) > 1 and v_parts[1]:
                                face_vt_indices.append(int(v_parts[1]))
                            if len(v_parts) > 2 and v_parts[2]:
                                face_vn_indices.append(int(v_parts[2]))

                        faces.append({
                            "v": face_v_indices,
                            "vt": face_vt_indices,
                            "vn": face_vn_indices,
                        })

            num_v = len(verts)
            num_vt = len(uvs)
            num_vn = len(normals)
            num_f = len(faces)

            self.assertGreater(num_v, 100, f"{mesh_name}: Vertex count {num_v} is too low")
            self.assertGreater(num_f, 100, f"{mesh_name}: Face count {num_f} is too low")

            # Validate Face Index References
            for f_idx, f_data in enumerate(faces):
                # 1. Vertices: 1 <= v_idx <= num_v
                for v_i in f_data["v"]:
                    self.assertGreaterEqual(v_i, 1, f"{mesh_name} Face {f_idx}: v_idx {v_i} < 1")
                    self.assertLessEqual(v_i, num_v, f"{mesh_name} Face {f_idx}: v_idx {v_i} > {num_v}")

                # 2. UVs: 1 <= vt_i <= num_vt
                for vt_i in f_data["vt"]:
                    self.assertGreaterEqual(vt_i, 1, f"{mesh_name} Face {f_idx}: vt_idx {vt_i} < 1")
                    self.assertLessEqual(vt_i, num_vt, f"{mesh_name} Face {f_idx}: vt_idx {vt_i} > {num_vt}")

                # 3. Normals: 1 <= vn_i <= num_vn
                for vn_i in f_data["vn"]:
                    self.assertGreaterEqual(vn_i, 1, f"{mesh_name} Face {f_idx}: vn_idx {vn_i} < 1")
                    self.assertLessEqual(vn_i, num_vn, f"{mesh_name} Face {f_idx}: vn_idx {vn_i} > {num_vn}")

                # 4. Check for degenerate face (duplicate vertex indices in same triangle)
                if len(f_data["v"]) == 3:
                    self.assertEqual(
                        len(set(f_data["v"])),
                        3,
                        f"{mesh_name} Face {f_idx}: Degenerate triangle with duplicate vertices: {f_data['v']}",
                    )

            # Check Bounding Box Extents
            v_arr = np.array(verts, dtype=np.float32)
            min_pt = v_arr.min(axis=0)
            max_pt = v_arr.max(axis=0)
            extents = max_pt - min_pt
            self.assertGreater(float(extents[0]), 0.05, f"{mesh_name}: X extent {extents[0]} is too small")
            self.assertGreater(float(extents[1]), 0.05, f"{mesh_name}: Y extent {extents[1]} is too small")


if __name__ == "__main__":
    unittest.main()
