#!/usr/bin/env python3
"""
Surreal Mathematical PBR Texture Suites - Master Batch Synthesis Runner
=======================================================================
Orchestrates procedural synthesis across all three mathematical domains:
1. Domain 1: Non-Euclidean Hyperbolic Tilings (Suites 1 & 2)
   - T_Hyperbolic_PoincareTriangular ({7,3} Poincaré Disk)
   - T_Hyperbolic_HalfPlaneEscher ({5,4} Upper Half-Plane Escher Limiting)
2. Domain 2: 4D Hypersurface Slices & Hopf Fibrations (Suites 3 & 4)
   - T_Hopf_ToroidalFibration (Toroidal Fiber Bundle S^3 -> S^2)
   - T_Hypersphere_DimensionalInterference (4D Clifford Torus Slicing)
3. Domain 3: Harmonic Chladni Acoustic & Cymatic Lattices (Suites 5 & 6)
   - T_Chladni_ResonantModal (2D Degenerate Plate Standing Waves)
   - T_Cymatic_HarmonicLattice (5-Mode Multi-Frequency Acoustic Superposition)

Target Resolution: 2048x2048 Power-of-Two (POT)
Total Maps: 6 Suites x 7 Maps = 42 Maps
Zero SciPy Dependency (Pure NumPy + Pillow)

Usage:
    python generators/run_batch_synthesis.py --all
    python generators/run_batch_synthesis.py --domain <hyperbolic|hopf|chladni>
    python generators/run_batch_synthesis.py --suite <suite_name>
    python generators/run_batch_synthesis.py --all --verify
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Ensure project root and generators directory are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
GENERATORS_DIR = PROJECT_ROOT / "generators"
if str(GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATORS_DIR))

# Generator imports with graceful fallback
try:
    from generators import PBREngine, HyperbolicGenerator, HopfGenerator, ChladniGenerator
except ImportError:
    try:
        from pbr_engine import PBREngine
        from hyperbolic_generator import HyperbolicGenerator
        from hopf_generator import HopfGenerator
        from chladni_generator import ChladniGenerator
    except ImportError:
        PBREngine = None
        HyperbolicGenerator = None
        HopfGenerator = None
        ChladniGenerator = None


SUITE_REGISTRY = {
    "T_Hyperbolic_PoincareTriangular": {
        "domain": "hyperbolic",
        "description": "Poincaré Disk {7,3} Heptagonal Triangular Coxeter Group Reflection Lattice",
        "generator_cls": HyperbolicGenerator,
        "method": "generate_poincare_triangular_suite",
        "palette": "lapis_gold",
        "default_bump": 4.5,
    },
    "T_Hyperbolic_HalfPlaneEscher": {
        "domain": "hyperbolic",
        "description": "Hyperbolic Upper Half-Plane {5,4} Escher Limiting Conformal Lattice",
        "generator_cls": HyperbolicGenerator,
        "method": "generate_halfplane_escher_suite",
        "palette": "amethyst_quartz",
        "default_bump": 6.5,
    },
    "T_Hopf_ToroidalFibration": {
        "domain": "hopf",
        "description": "Toroidal Hopf Fiber Bundle Projection (S^3 -> S^2) with Villarceau Circles",
        "generator_cls": HopfGenerator,
        "method": "generate_toroidal_fibration_suite",
        "palette": "sapphire_celestial",
        "default_bump": 7.5,
    },
    "T_Hypersphere_DimensionalInterference": {
        "domain": "hopf",
        "description": "4D Hypersphere Cross-Sections with Double-Rotated Clifford Torus Interference",
        "generator_cls": HopfGenerator,
        "method": "generate_dimensional_interference_suite",
        "palette": "amethyst_quartz",
        "default_bump": 7.5,
    },
    "T_Chladni_ResonantModal": {
        "domain": "chladni",
        "description": "2D Degenerate Resonant Modal Standing Wave Plate with Sand Accumulation",
        "generator_cls": ChladniGenerator,
        "method": "generate_resonant_modal_suite",
        "palette": "titanium_cymatic",
        "default_bump": 3.5,
    },
    "T_Cymatic_HarmonicLattice": {
        "domain": "chladni",
        "description": "Multi-Frequency Harmonic Acoustic Lattice Superposition with Radial Bessel Modes",
        "generator_cls": ChladniGenerator,
        "method": "generate_harmonic_lattice_suite",
        "palette": "sapphire_celestial",
        "default_bump": 3.5,
    },
}


def run_suite_synthesis(
    suite_name: str,
    output_base_dir: Path,
    resolution: int = 2048,
    bump_strength: Optional[float] = None,
) -> Dict[str, str]:
    """Execute synthesis for a single named suite."""
    if suite_name not in SUITE_REGISTRY:
        raise ValueError(f"Unknown suite '{suite_name}'. Available: {list(SUITE_REGISTRY.keys())}")

    config = SUITE_REGISTRY[suite_name]
    gen_cls = config["generator_cls"]
    if gen_cls is None:
        raise RuntimeError(
            f"Generator class for domain '{config['domain']}' is not yet available/imported."
        )

    pbr_eng = PBREngine(resolution=resolution) if PBREngine else None
    generator = gen_cls(resolution=resolution, pbr_engine=pbr_eng)

    target_suite_dir = output_base_dir / suite_name
    method_name = config["method"]
    palette = config["palette"]
    effective_bump = bump_strength if bump_strength is not None else config.get("default_bump", 3.5)

    gen_method = getattr(generator, method_name)
    paths = gen_method(
        output_dir=target_suite_dir,
        palette=palette,
        bump_strength=effective_bump,
    )
    return paths


def run_batch(
    target_suites: List[str],
    output_base_dir: Path,
    resolution: int = 2048,
    bump_strength: Optional[float] = None,
) -> bool:
    """Run batch synthesis for multiple suites and report telemetry."""
    print("=" * 80)
    print(" SURREAL MATHEMATICAL PBR TEXTURE SUITES - BATCH SYNTHESIS RUNNER")
    print("=" * 80)
    print(f"Target Resolution: {resolution} x {resolution} POT")
    print(f"Textures Root:     {output_base_dir}")
    print(f"Suites to Bake:    {len(target_suites)}")
    print("-" * 80)

    total_start = time.perf_counter()
    success_count = 0
    failure_count = 0
    results = {}

    for idx, suite_name in enumerate(target_suites, 1):
        desc = SUITE_REGISTRY[suite_name]["description"]
        print(f"\n[{idx}/{len(target_suites)}] Baking Suite: {suite_name}")
        print(f"    Formula: {desc}")
        suite_start = time.perf_counter()
        try:
            paths = run_suite_synthesis(
                suite_name=suite_name,
                output_base_dir=output_base_dir,
                resolution=resolution,
                bump_strength=bump_strength,
            )
            suite_dur = time.perf_counter() - suite_start
            print(f"    [OK] Generated {len(paths)} maps in {suite_dur:.2f}s:")
            for map_key, path_str in paths.items():
                p = Path(path_str)
                size_kb = p.stat().st_size / 1024.0 if p.exists() else 0.0
                print(f"      + {map_key:<4} -> {p.name} ({size_kb:.1f} KB)")
            success_count += 1
            results[suite_name] = {"status": "SUCCESS", "time": suite_dur, "maps": paths}
        except Exception as ex:
            suite_dur = time.perf_counter() - suite_start
            print(f"    [ERROR] Failed to synthesize {suite_name}: {ex}")
            failure_count += 1
            results[suite_name] = {"status": "FAILED", "error": str(ex), "time": suite_dur}

    total_dur = time.perf_counter() - total_start
    print("\n" + "=" * 80)
    print(" BATCH SYNTHESIS SUMMARY")
    print("=" * 80)
    print(f"Total Suites Processed: {len(target_suites)}")
    print(f"  + Successful: {success_count}")
    print(f"  - Failed:     {failure_count}")
    print(f"Total Time:     {total_dur:.2f} seconds (Avg: {total_dur/max(1, len(target_suites)):.2f}s/suite)")
    print("=" * 80)

    return failure_count == 0


def main():
    parser = argparse.ArgumentParser(description="Master Batch Synthesis Runner for Surreal Mathematical PBR Textures")
    parser.add_argument("--all", action="store_true", help="Synthesize all 6 texture suites across all 3 domains")
    parser.add_argument("--domain", type=str, choices=["hyperbolic", "hopf", "chladni"], help="Synthesize all suites for a given domain")
    parser.add_argument("--suite", type=str, choices=list(SUITE_REGISTRY.keys()), help="Synthesize a single specific suite")
    parser.add_argument("--res", type=int, default=2048, help="Power-of-Two resolution (default: 2048)")
    parser.add_argument("--out", type=str, default=None, help="Base textures directory (default: <PROJECT_ROOT>/textures)")
    parser.add_argument("--bump", type=float, default=None, help="Normal bump strength override (default: per-suite optimal)")
    parser.add_argument("--verify", action="store_true", help="Run automated verification test harness after synthesis")

    args = parser.parse_args()

    if args.out:
        textures_dir = Path(args.out)
    else:
        if args.res != 2048:
            textures_dir = PROJECT_ROOT / f"textures_{args.res}"
        else:
            textures_dir = PROJECT_ROOT / "textures"

    # Determine targets
    if args.suite:
        targets = [args.suite]
    elif args.domain:
        targets = [name for name, cfg in SUITE_REGISTRY.items() if cfg["domain"] == args.domain]
    elif args.all:
        targets = list(SUITE_REGISTRY.keys())
    else:
        # Default to all if run without args or prompt
        targets = list(SUITE_REGISTRY.keys())

    success = run_batch(
        target_suites=targets,
        output_base_dir=textures_dir,
        resolution=args.res,
        bump_strength=args.bump,
    )

    if args.verify:
        print("\n" + "=" * 80)
        print(" RUNNING AUTOMATED QUALITY GATE VERIFICATION")
        print("=" * 80)
        test_script = PROJECT_ROOT / "tests" / "test_mathematical_pbr_verification.py"
        test_cmd = [sys.executable, str(test_script)]
        if len(targets) == 1:
            test_cmd.extend(["--suite", targets[0]])
        res = subprocess.run(test_cmd)
        if res.returncode != 0:
            print(f"\n[FAIL] Verification tests failed with exit code {res.returncode}")
            sys.exit(res.returncode)
        else:
            print(f"\n[PASS] All verification tests passed with exit code 0!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
