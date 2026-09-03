"""
Master Unified CLI Generator & Baker for Infinity Nikki Haute-Couture Asset Elevation.
Synthesizes 3D micro-geometry (.obj) and bakes complete 2048x2048 POT PBR material suites
across all 4 signature haute-couture archetypes.
"""

import argparse
import os
import sys
import time
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image

# Add parent directory to sys.path to allow execution from any working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from generators.chantilly_lace_synthesizer import ChantillyLaceSynthesizer
from generators.differential_organza_synthesizer import DifferentialOrganzaSynthesizer
from generators.baroque_bullion_synthesizer import BaroqueBullionSynthesizer
from generators.reaction_diffusion_synthesizer import ReactionDiffusionSynthesizer
from generators.high_to_low_baker import HighToLowBaker


def run_batch_generation(
    archetype: str = "all",
    resolution: int = 2048,
    out_dir: str = None,
    geo_dir: str = None,
    seed: int = 42,
) -> Dict[str, Dict[str, str]]:
    """
    Executes end-to-end procedural synthesis and PBR map extraction.

    Returns:
        Dictionary mapping archetype prefix to generated file paths.
    """
    start_time = time.time()

    if out_dir is None:
        out_dir = os.path.join(PROJECT_ROOT, "textures")
    if geo_dir is None:
        geo_dir = os.path.join(PROJECT_ROOT, "models")

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(geo_dir, exist_ok=True)

    baker = HighToLowBaker(resolution=resolution)

    archetype_registry = {
        "chantilly_lace": (
            ChantillyLaceSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_ChantillyLace_PearlBeading",
            "Chantilly Lace & Micro-Beading Lattice",
        ),
        "differential_organza": (
            DifferentialOrganzaSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_DifferentialOrganza_Petals",
            "Differential Line Growth Organza Petals",
        ),
        "baroque_bullion": (
            BaroqueBullionSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_BaroqueBullion_Acanthus",
            "Baroque Bullion Acanthus Embroidery",
        ),
        "reaction_diffusion": (
            ReactionDiffusionSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_ReactionDiffusion_Cloisonne",
            "Reaction-Diffusion Cloisonne Filigree",
        ),
    }

    selected_keys = (
        list(archetype_registry.keys())
        if archetype == "all"
        else [archetype]
    )

    all_results: Dict[str, Dict[str, str]] = {}

    print("=" * 75)
    print(" INFINITY NIKKI HAUTE-COUTURE PROCEDURAL SYNTHESIZER & BAKER")
    print(f" Target Resolution: {resolution}x{resolution} POT | Seed: {seed}")
    print(f" Textures Destination: {out_dir}")
    print(f" 3D Geometry Destination: {geo_dir}")
    print("=" * 75)

    for arch_key in selected_keys:
        if arch_key not in archetype_registry:
            print(f"[Error] Unknown archetype: {arch_key}")
            continue

        synth, prefix, title = archetype_registry[arch_key]
        arch_start = time.time()
        print(f"\n[Archetype: {title}]")
        print(f"  Identifier: {prefix}")

        # 1. 3D High-Poly Geometry Synthesis
        print("  [1/3] Generating 3D physical micro-geometry mesh...")
        geo_data = synth.generate_geometry()
        obj_name = f"{prefix}_HighPoly.obj"
        obj_path = os.path.join(geo_dir, obj_name)
        synth.export_obj(
            filepath=obj_path,
            vertices=geo_data["vertices"],
            faces=geo_data["faces"],
            normals=geo_data.get("normals"),
            uvs=geo_data.get("uvs"),
            material_name=f"M_{prefix}",
        )
        print(f"        [OK] Saved Wavefront OBJ: {obj_name} ({len(geo_data['vertices'])} vertices, {len(geo_data['faces'])} faces)")

        # 2. PBR Map Generation
        print(f"  [2/3] Synthesizing PBR texture maps at {resolution}x{resolution} POT...")
        maps = synth.synthesize_maps()

        # 3. High-to-Low Baker (16-bit Height, DirectX Normal, Curvature, AO, ORM)
        print("  [3/3] Baking high-to-low PBR channels and packing Linear ORM...")
        baked_channels = baker.bake_all_channels(maps=maps, out_dir=out_dir, prefix=prefix)
        baked_channels["Mesh_OBJ"] = obj_path
        all_results[prefix] = baked_channels

        arch_elapsed = time.time() - arch_start
        print(f"  [OK] Archetype complete in {arch_elapsed:.2f}s ({len(baked_channels)} files generated)")

    total_elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f" BATCH GENERATION SUMMARY -- Total Time: {total_elapsed:.2f}s")
    print("=" * 75)

    total_files = 0
    for prefix, files in all_results.items():
        print(f"\n  * {prefix}:")
        for channel, fpath in files.items():
            fsize = os.path.getsize(fpath) / 1024.0
            print(f"    - {channel:10s} : {os.path.basename(fpath):50s} ({fsize:7.1f} KB)")
            total_files += 1

    print(f"\n[Success] Generated {total_files} assets across {len(all_results)} haute-couture suites.")
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Infinity Nikki Haute-Couture Procedural Asset & Trim Synthesizer Master CLI"
    )
    parser.add_argument(
        "--archetype",
        choices=["all", "chantilly_lace", "differential_organza", "baroque_bullion", "reaction_diffusion"],
        default="all",
        help="Target procedural archetype to synthesize (default: all).",
    )
    parser.add_argument(
        "--res",
        type=int,
        default=2048,
        help="Power-of-Two texture resolution: 512, 1024, 2048 (default: 2048).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output textures directory (default: teamwork_projects/infinity_nikki_asset_elevation/textures).",
    )
    parser.add_argument(
        "--geo",
        type=str,
        default=None,
        help="Output models directory (default: teamwork_projects/infinity_nikki_asset_elevation/models).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for procedural variation (default: 42).",
    )

    args = parser.parse_args()

    run_batch_generation(
        archetype=args.archetype,
        resolution=args.res,
        out_dir=args.out,
        geo_dir=args.geo,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
