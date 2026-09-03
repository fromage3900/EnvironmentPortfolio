#!/usr/bin/env python3
"""
Unreal Engine 5 Substrate & Material Function Specifications Test Suite
======================================================================
Authoritative validation harness for Infinity Nikki Haute-Couture UE5 Shaders:
- MF_ThinFilm_Iridescence (Multi-stop spectral Airy thin-film interference)
- MF_DualLobe_SubstrateVelvet (Dual-lobe anisotropic fuzz & pile shift)
- MF_Translucent_OrganzaSSS (Sheer fabric opacity & dual-sided SSS)
- MF_Bullion_MicroRelief (Parallax occlusion & embroidery contact relief)
- M_Master_HauteCouture_Substrate (Master Substrate Slab Material graph)

Validates:
1. JSON interface schemas (AssetType, AssetName, Inputs, Outputs, pins, types, defaults).
2. HLSL source file existence, syntax structure, and entry point function implementations.
3. Master Substrate Material topology (Slabs, Operators, TextureBindings, Function Dependencies).

Usage:
    python -m unittest tests/test_ue5_shader_specifications.py
"""

import os
import sys
import json
import re
import unittest
from pathlib import Path
from typing import Dict, List, Any, Optional

# ---------------------------------------------------------------------------
# Project Configuration & Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHADERS_DIR = PROJECT_ROOT / "shaders"
JSON_DIR = SHADERS_DIR / "json"
HLSL_DIR = SHADERS_DIR / "hlsl"
GRAPHS_DIR = SHADERS_DIR / "graphs"

# ---------------------------------------------------------------------------
# Authoritative Shader Interface Contracts
# ---------------------------------------------------------------------------
EXPECTED_MATERIAL_FUNCTIONS: Dict[str, Dict[str, Any]] = {
    "MF_ThinFilm_Iridescence": {
        "json_file": "MF_ThinFilm_Iridescence.json",
        "hlsl_file": "ThinFilmIridescence.hlsl",
        "hlsl_entry_candidates": ["CalculateThinFilmAiry", "CalculateThinFilmIridescence", "EvaluateThinFilmIridescence"],
        "description": "Multi-stop spectral thin-film optical wave interference.",
        "expected_inputs": [
            "FilmThickness_nm", "FilmIOR", "SubstrateIOR", "Normal", "CurvatureMask"
        ],
        "expected_outputs": [
            "IridescenceColor", "FresnelMultiplier", "PhaseShift", "ModulatedRoughness", "Substrate_F0"
        ]
    },
    "MF_DualLobe_SubstrateVelvet": {
        "json_file": "MF_DualLobe_SubstrateVelvet.json",
        "hlsl_file": "DualLobeVelvet.hlsl",
        "hlsl_entry_candidates": ["CalculateVelvetDualLobe", "CalculateDualLobeVelvet", "EvaluateDualLobeVelvet"],
        "description": "Dual-lobe anisotropic velvet/fuzz shading with customizable edge rim glow.",
        "expected_inputs": [
            "BaseColor", "RimColor", "Normal", "TangentFlowMap", "RoughnessCore", "RoughnessRim"
        ],
        "expected_outputs": [
            "CompositeBaseColor", "SheenColor", "SheenRoughness", "AnisotropicTangent", "AnisotropyAmount", "RimMask"
        ]
    },
    "MF_Translucent_OrganzaSSS": {
        "json_file": "MF_Translucent_OrganzaSSS.json",
        "hlsl_file": "TranslucentOrganzaSSS.hlsl",
        "hlsl_entry_candidates": ["CalculateOrganzaTranslucency", "CalculateTranslucentOrganzaSSS", "EvaluateTranslucentOrganzaSSS"],
        "description": "Sheer fabric opacity, micro-twill normal blending (RNM), and dual-sided SSS.",
        "expected_inputs": [
            "BaseColor", "SubsurfaceColor", "Normal", "MicroTwillNormal", "TwillTiling", "TwillWeight", "BaseOpacity"
        ],
        "expected_outputs": [
            "PerturbedNormal", "TransmittanceColor", "SubsurfaceScatteringProfile", "FinalOpacity", "Thickness"
        ]
    },
    "MF_Bullion_MicroRelief": {
        "json_file": "MF_Bullion_MicroRelief.json",
        "hlsl_file": "BullionMicroRelief.hlsl",
        "hlsl_entry_candidates": ["CalculateBullionParallaxRelief", "CalculateParallaxMicroRelief", "FBullionPOMOutputs", "CalculateBullionPOM"],
        "description": "Metallic embroidery dynamic-step POM and contact self-shadowing.",
        "expected_inputs": [
            "UVs", "HeightMap", "HeightScale", "MinSteps", "MaxSteps", "BullionMetallic", "BullionRoughness"
        ],
        "expected_outputs": [
            "DisplacedUV", "ParallaxHeight", "SelfShadowAO", "BullionMask", "BlendedRoughness", "BlendedMetallic"
        ]
    }
}

EXPECTED_MASTER_MATERIAL = {
    "json_file": "M_Master_HauteCouture_Substrate.json",
    "graph_file": "SubstrateMasterTopology.md",
    "expected_slabs": ["Slab_FabricBase", "Slab_BullionMetallic", "Slab_ThinFilmClearcoat"],
    "expected_operators": ["SubstrateHorizontalBlend", "SubstrateVerticalLayer"],
    "expected_texture_bindings": ["BaseColor", "Normal", "ORM", "Height", "Sheen", "Alpha"],
    "expected_dependencies": [
        "MF_ThinFilm_Iridescence",
        "MF_DualLobe_SubstrateVelvet",
        "MF_Translucent_OrganzaSSS",
        "MF_Bullion_MicroRelief"
    ]
}


# ---------------------------------------------------------------------------
# Schema Validator Engine
# ---------------------------------------------------------------------------
def validate_function_schema_data(data: Dict[str, Any], contract: Dict[str, Any]) -> List[str]:
    """
    Validate a parsed Material Function JSON data dictionary against UE5 schema standards.
    Supports both UE5 PascalCase and standard lowercase key structures.
    """
    errors = []

    # 1. Identify asset identity
    asset_name = data.get("AssetName") or data.get("name")
    if not asset_name:
        errors.append("Missing required asset name field ('AssetName' or 'name')")

    asset_type = data.get("AssetType") or data.get("type")
    if not asset_type:
        errors.append("Missing required asset type field ('AssetType' or 'type')")

    description = data.get("Description") or data.get("description")
    if not description:
        errors.append("Missing required description field ('Description' or 'description')")

    # 2. Validate Inputs
    raw_inputs = data.get("Inputs") or data.get("inputs")
    if raw_inputs is None or not isinstance(raw_inputs, list):
        errors.append("Missing or invalid 'Inputs' array")
    else:
        input_names = set()
        for inp in raw_inputs:
            if not isinstance(inp, dict):
                errors.append(f"Invalid input element: {inp}")
                continue
            name = inp.get("Name") or inp.get("name")
            inp_type = inp.get("Type") or inp.get("type")
            if not name or not inp_type:
                errors.append(f"Input pin missing name or type: {inp}")
            else:
                input_names.add(name)

        for req_in in contract["expected_inputs"]:
            if req_in not in input_names:
                errors.append(f"Missing expected input pin: '{req_in}'")

    # 3. Validate Outputs
    raw_outputs = data.get("Outputs") or data.get("outputs")
    if raw_outputs is None or not isinstance(raw_outputs, list):
        errors.append("Missing or invalid 'Outputs' array")
    else:
        output_names = set()
        for out in raw_outputs:
            if not isinstance(out, dict):
                errors.append(f"Invalid output element: {out}")
                continue
            name = out.get("Name") or out.get("name")
            out_type = out.get("Type") or out.get("type")
            if not name or not out_type:
                errors.append(f"Output pin missing name or type: {out}")
            else:
                output_names.add(name)

        for req_out in contract["expected_outputs"]:
            if req_out not in output_names:
                errors.append(f"Missing expected output pin: '{req_out}'")

    return errors


def parse_hlsl_symbols(hlsl_content: str) -> List[str]:
    """Extract declared function and struct names from HLSL code."""
    # Matches function prototypes: e.g. float3 CalculateThinFilmAiry(...) or void CalculateVelvet(...)
    func_pattern = r'(?:void|float|float2|float3|float4|half|half2|half3|half4|struct\s+\w+|F\w+Outputs)\s+([A-Za-z0-9_]+)\s*\('
    funcs = re.findall(func_pattern, hlsl_content)

    # Matches struct declarations: struct FBullionPOMOutputs { ... }
    struct_pattern = r'struct\s+([A-Za-z0-9_]+)'
    structs = re.findall(struct_pattern, hlsl_content)

    return list(set(funcs + structs))


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
class TestShaderSpecificationContracts(unittest.TestCase):
    """
    Validates the contract definitions, schema rules, and prototype validators
    in memory to ensure quality gate correctness.
    """

    def test_01_all_four_material_functions_defined_in_contract(self):
        self.assertEqual(len(EXPECTED_MATERIAL_FUNCTIONS), 4)
        for mf_name in [
            "MF_ThinFilm_Iridescence",
            "MF_DualLobe_SubstrateVelvet",
            "MF_Translucent_OrganzaSSS",
            "MF_Bullion_MicroRelief"
        ]:
            self.assertIn(mf_name, EXPECTED_MATERIAL_FUNCTIONS)
            contract = EXPECTED_MATERIAL_FUNCTIONS[mf_name]
            self.assertTrue(len(contract["expected_inputs"]) >= 4)
            self.assertTrue(len(contract["expected_outputs"]) >= 4)

    def test_02_validator_engine_on_synthetic_valid_data(self):
        contract = EXPECTED_MATERIAL_FUNCTIONS["MF_ThinFilm_Iridescence"]
        valid_data = {
            "AssetName": "MF_ThinFilm_Iridescence",
            "AssetType": "MaterialFunction",
            "Description": "Multi-stop spectral thin-film optical interference.",
            "Inputs": [
                {"Name": "FilmThickness_nm", "Type": "FunctionInput_Scalar", "DefaultValue": 380.0},
                {"Name": "FilmIOR", "Type": "FunctionInput_Scalar", "DefaultValue": 1.45},
                {"Name": "SubstrateIOR", "Type": "FunctionInput_Scalar", "DefaultValue": 1.55},
                {"Name": "Normal", "Type": "FunctionInput_Vector3", "DefaultValue": [0.0, 0.0, 1.0]},
                {"Name": "CurvatureMask", "Type": "FunctionInput_Scalar", "DefaultValue": 0.5},
            ],
            "Outputs": [
                {"Name": "IridescenceColor", "Type": "FunctionOutput_Vector3"},
                {"Name": "FresnelMultiplier", "Type": "FunctionOutput_Scalar"},
                {"Name": "PhaseShift", "Type": "FunctionOutput_Scalar"},
                {"Name": "ModulatedRoughness", "Type": "FunctionOutput_Scalar"},
                {"Name": "Substrate_F0", "Type": "FunctionOutput_Vector3"},
            ]
        }
        errors = validate_function_schema_data(valid_data, contract)
        self.assertEqual(len(errors), 0, f"Valid schema failed validation: {errors}")

    def test_03_validator_engine_catches_missing_and_invalid_pins(self):
        contract = EXPECTED_MATERIAL_FUNCTIONS["MF_ThinFilm_Iridescence"]
        invalid_data = {
            "AssetName": "MF_ThinFilm_Iridescence",
            "AssetType": "MaterialFunction",
            "Description": "Broken schema",
            "Inputs": [
                {"Name": "WrongPin", "Type": "FunctionInput_Scalar"},
            ],
            "Outputs": [
                {"Name": "WrongOutputPin", "Type": "FunctionOutput_Vector3"}
            ]
        }
        errors = validate_function_schema_data(invalid_data, contract)
        self.assertTrue(len(errors) >= 5, f"Expected multiple validation errors, got {errors}")

    def test_04_hlsl_parser_regex(self):
        synthetic_hlsl = """
        struct FThinFilmOutputs { float3 Color; };
        float3 CalculateThinFilmAiry(float FilmThickness, float3 Normal)
        {
            return float3(1.0, 0.5, 0.2);
        }
        """
        symbols = parse_hlsl_symbols(synthetic_hlsl)
        self.assertIn("CalculateThinFilmAiry", symbols)
        self.assertIn("FThinFilmOutputs", symbols)


class TestLiveShaderFilesConformance(unittest.TestCase):
    """
    Validates actual files on disk in shaders/ when generated in Milestone M2.
    """

    def setUp(self):
        if not SHADERS_DIR.exists():
            self.skipTest(f"Shaders directory not created yet at {SHADERS_DIR} (Scheduled for Milestone M2)")

    def test_05_json_schemas_exist_and_conform(self):
        if not JSON_DIR.exists():
            self.skipTest("shaders/json/ directory does not exist yet.")

        for mf_name, contract in EXPECTED_MATERIAL_FUNCTIONS.items():
            json_path = JSON_DIR / contract["json_file"]
            self.assertTrue(
                json_path.is_file(),
                f"Missing Material Function JSON schema: {json_path.relative_to(PROJECT_ROOT)}"
            )

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            errors = validate_function_schema_data(data, contract)
            self.assertEqual(
                len(errors), 0,
                f"Schema validation failed for {contract['json_file']}:\n" + "\n".join(f"  - {e}" for e in errors)
            )

    def test_06_hlsl_files_exist_and_conform(self):
        if not HLSL_DIR.exists():
            self.skipTest("shaders/hlsl/ directory does not exist yet.")

        for mf_name, contract in EXPECTED_MATERIAL_FUNCTIONS.items():
            hlsl_path = HLSL_DIR / contract["hlsl_file"]
            self.assertTrue(
                hlsl_path.is_file(),
                f"Missing HLSL implementation: {hlsl_path.relative_to(PROJECT_ROOT)}"
            )

            content = hlsl_path.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 50, f"{hlsl_path.name} is empty or trivial")

            symbols = parse_hlsl_symbols(content)
            candidates = contract["hlsl_entry_candidates"]
            found = any(cand in symbols for cand in candidates)
            self.assertTrue(
                found,
                f"{hlsl_path.name} does not define any expected entry point from {candidates}. Found symbols: {symbols}"
            )

    def test_07_master_substrate_material_specification(self):
        if not JSON_DIR.exists():
            self.skipTest("shaders/json/ directory does not exist yet.")

        master_json = JSON_DIR / EXPECTED_MASTER_MATERIAL["json_file"]
        self.assertTrue(
            master_json.is_file(),
            f"Missing Master Substrate Material JSON: {master_json.relative_to(PROJECT_ROOT)}"
        )

        with open(master_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("AssetName", data)
        self.assertEqual(data.get("ShadingModel"), "Substrate")

        # Check SubstrateTopology
        topology = data.get("SubstrateTopology", {})
        slabs = [s.get("ID") for s in topology.get("Slabs", [])]
        for exp_slab in EXPECTED_MASTER_MATERIAL["expected_slabs"]:
            self.assertIn(exp_slab, slabs, f"Master Material missing expected Substrate Slab '{exp_slab}'")

        operators = [op.get("Type") for op in topology.get("Operators", [])]
        for exp_op in EXPECTED_MASTER_MATERIAL["expected_operators"]:
            self.assertIn(exp_op, operators, f"Master Material missing expected Substrate Operator '{exp_op}'")

        # Check TextureBindings
        bindings = data.get("TextureBindings", {})
        for exp_bind in EXPECTED_MASTER_MATERIAL["expected_texture_bindings"]:
            self.assertIn(exp_bind, bindings, f"Master Material missing texture binding '{exp_bind}'")

        # Check Material Function Dependencies
        deps = [d.get("Function") for d in data.get("MaterialFunctionDependencies", [])]
        for exp_dep in EXPECTED_MASTER_MATERIAL["expected_dependencies"]:
            self.assertIn(exp_dep, deps, f"Master Material missing Material Function dependency '{exp_dep}'")


if __name__ == "__main__":
    unittest.main()
