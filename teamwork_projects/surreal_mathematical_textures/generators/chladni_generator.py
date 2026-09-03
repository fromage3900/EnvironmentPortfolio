"""
Chladni Cymatics & Harmonic Acoustic Lattice Procedural Generator.
Synthesizes high-fidelity 2048x2048 POT PBR texture suites based on 2D modal standing wave
equations and multi-frequency acoustic interference lattices.

Mathematical Domains:
1. Suite 5: T_Chladni_ResonantModal
   - 2D modal acoustic standing wave equation:
     W_{m,n}(x, y) = cos(n*pi*x/L)*cos(m*pi*y/L) - cos(m*pi*x/L)*cos(n*pi*y/L) = 0
   - Resonant modal superposition and inverted-Gaussian acoustic sand particle dynamics.
2. Suite 6: T_Cymatic_HarmonicLattice
   - 5-mode multi-frequency acoustic superposition with phase modulation and radial Bessel-type harmonics.
   - Multi-tier particle accumulation and harmonic resonance lattice relief.

Pure NumPy + Pillow implementation. Zero SciPy dependency.
"""

import os
import sys
import math
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image

# Import PBREngine from generators or fallback
try:
    from generators.pbr_engine import PBREngine
except ImportError:
    try:
        from pbr_engine import PBREngine
    except ImportError:
        current_dir = Path(__file__).resolve().parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from pbr_engine import PBREngine


class ChladniGenerator:
    """
    Procedural generator for 2D Chladni plate standing waves and multi-frequency
    cymatic harmonic lattice PBR texture suites.
    """

    def __init__(self, resolution: int = 2048, pbr_engine: Optional[PBREngine] = None):
        self.resolution = resolution
        self.pbr_engine = pbr_engine or PBREngine(resolution=resolution)

        # Coordinate grid with periodic boundary coordinates in [-1, 1]
        self.x = np.linspace(-1.0, 1.0, resolution, endpoint=False, dtype=np.float32)
        self.y = np.linspace(-1.0, 1.0, resolution, endpoint=False, dtype=np.float32)
        self.X, self.Y = np.meshgrid(self.x, self.y)

    def generate_resonant_modal_heightfield(
        self,
        mode_pairs: Optional[list] = None,
        sigma_nodal: float = 0.09,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes 2D Degenerate Resonant Modal Chladni plate standing wave heightfield.
        Governing equation for square plate with free boundaries:
            W(x, y) = sum_k A_k * (cos(n_k*pi*x)*cos(m_k*pi*y) - cos(m_k*pi*x)*cos(n_k*pi*y))

        Particles accumulate along the nodal lines (W ≈ 0) via acoustic radiation pressure:
            H_nodal(x, y) = exp(-W(x, y)^2 / (2 * sigma_nodal^2))
        """
        if mode_pairs is None:
            # Multi-mode degenerate resonance combining (7,3), (5,1), and (11,5) modes
            mode_pairs = [
                {"n": 7, "m": 3, "weight": 0.55},
                {"n": 5, "m": 1, "weight": 0.25},
                {"n": 11, "m": 5, "weight": 0.20},
            ]

        w_total = np.zeros_like(self.X, dtype=np.float32)

        for mode in mode_pairs:
            n = mode["n"]
            m = mode["m"]
            weight = mode["weight"]

            # Degenerate standing wave mode
            w_mode = (
                np.cos(n * np.pi * self.X) * np.cos(m * np.pi * self.Y)
                - np.cos(m * np.pi * self.X) * np.cos(n * np.pi * self.Y)
            )
            w_total += weight * w_mode

        # Normalize wave amplitude field
        w_max = np.max(np.abs(w_total)) + 1e-8
        w_norm = w_total / w_max

        # 1. Primary crisp sand accumulation on nodal lines (W ≈ 0)
        h_nodal = np.exp(-(w_norm**2) / (2.0 * (sigma_nodal**2)))

        # 2. Antinodal plate relief: antinodes form smooth vibrating basins
        h_basin = 1.0 - np.minimum(1.0, np.abs(w_norm) * 1.2) ** 1.4

        # 3. Acoustic standing wave micro-ripples along vibration gradients
        h_ripples = 0.5 + 0.5 * np.cos(14.0 * np.pi * np.abs(w_norm))
        h_ripples *= np.exp(-1.8 * np.abs(w_norm))

        # 4. Acoustic sand granular chladni texture
        h_gran = (
            np.cos(20.0 * np.pi * self.X) * np.cos(20.0 * np.pi * self.Y)
            * h_nodal
            * 0.15
        )

        # Composite micro-elevation heightfield
        h_raw = (
            0.50 * h_nodal
            + 0.22 * h_basin
            + 0.18 * h_ripples
            + 0.10 * h_gran
        )

        # Normalize heightfield to full [0.0, 1.0] dynamic range
        h_min, h_max = float(h_raw.min()), float(h_raw.max())
        height = ((h_raw - h_min) / (h_max - h_min + 1e-8)).astype(np.float32)

        # Feature field for material zoning (emphasizing crisp nodal ridges for gold inlays)
        feature_field = (0.75 * h_nodal + 0.25 * h_basin).astype(np.float32)

        return height, feature_field

    def generate_cymatic_lattice_heightfield(
        self,
        sigma_nodal: float = 0.09,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes Multi-Frequency Acoustic Cymatic Harmonic Lattice heightfield.
        Superposes 5 distinct harmonic vibrational modes with phase shifts,
        analytic J0-type radial Bessel membrane standing waves, and diagonal lattice interference.
        """
        modes = [
            {"n": 3, "m": 5, "A": 0.30, "px": 0.0, "py": 0.0, "alpha": 1.0},
            {"n": 7, "m": 1, "A": 0.25, "px": 0.3, "py": 0.2, "alpha": -1.0},
            {"n": 4, "m": 8, "A": 0.20, "px": 0.5, "py": 0.1, "alpha": 1.0},
            {"n": 8, "m": 6, "A": 0.15, "px": 0.0, "py": 0.0, "alpha": 0.5},
            {"n": 2, "m": 9, "A": 0.10, "px": 0.7, "py": 0.4, "alpha": -1.0},
        ]

        w_total = np.zeros_like(self.X, dtype=np.float32)

        for mode in modes:
            n = mode["n"]
            m = mode["m"]
            A = mode["A"]
            px = mode["px"]
            py = mode["py"]
            alpha = mode["alpha"]

            w_k = (
                np.cos(n * np.pi * self.X + px) * np.cos(m * np.pi * self.Y + py)
                - alpha * np.cos(m * np.pi * self.X + py) * np.cos(n * np.pi * self.Y + px)
            )
            w_total += A * w_k

        # Analytic J0-type radial Bessel standing wave (smooth and non-singular at r=0)
        r = np.sqrt(self.X**2 + self.Y**2)
        r_bessel = np.cos(8.0 * np.pi * r) * np.exp(-(r**2) / 2.5)

        # High-order diagonal acoustic lattice interference
        lattice_diag = np.cos(8.0 * np.pi * (self.X + self.Y)) * np.cos(8.0 * np.pi * (self.X - self.Y))

        # Composite acoustic wave field
        c_field = (
            0.55 * w_total
            + 0.25 * r_bessel
            + 0.20 * lattice_diag
        )
        c_max = np.max(np.abs(c_field)) + 1e-8
        c_norm = c_field / c_max

        # Multi-tier particle accumulation
        # 1. Primary sharp nodal curves
        h_primary = np.exp(-(c_norm**2) / (2.0 * (sigma_nodal**2)))

        # 2. Antinodal plate relief
        h_basin = 1.0 - np.minimum(1.0, np.abs(c_norm) * 1.2) ** 1.4

        # 3. Acoustic standing wave micro-ripples
        h_ripples = (0.5 + 0.5 * np.cos(14.0 * np.pi * np.abs(c_norm))) * np.exp(-1.8 * np.abs(c_norm))

        # 4. Fine granular micro-texture on nodal curves
        h_gran = (
            np.cos(18.0 * np.pi * self.X) * np.cos(18.0 * np.pi * self.Y)
            * h_primary
            * 0.15
        )

        # Composite raw heightfield
        h_raw = (
            0.50 * h_primary
            + 0.22 * h_basin
            + 0.18 * h_ripples
            + 0.10 * h_gran
        )

        # Normalize heightfield to full [0.0, 1.0] dynamic range
        h_min, h_max = float(h_raw.min()), float(h_raw.max())
        height = ((h_raw - h_min) / (h_max - h_min + 1e-8)).astype(np.float32)

        # Feature field for material zoning (emphasizing crisp nodal ridges for gold inlays)
        feature_field = (0.75 * h_primary + 0.25 * h_basin).astype(np.float32)

        return height, feature_field

    def generate_chladni_resonant_modal_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "titanium_cymatic",
        palette_name: Optional[str] = None,
        bump_strength: float = 3.5,
    ) -> Dict[str, str]:
        """
        Synthesizes all 7 PBR texture maps for Suite 5: T_Chladni_ResonantModal.
        """
        suite_name = "T_Chladni_ResonantModal"
        selected_palette = palette_name or palette
        height, feature_field = self.generate_resonant_modal_heightfield()

        paths = self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=height,
            feature_field=feature_field,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )
        return paths

    def generate_resonant_modal_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "titanium_cymatic",
        palette_name: Optional[str] = None,
        bump_strength: float = 3.5,
    ) -> Dict[str, str]:
        """Alias for generate_chladni_resonant_modal_suite."""
        return self.generate_chladni_resonant_modal_suite(
            output_dir=output_dir,
            palette=palette,
            palette_name=palette_name,
            bump_strength=bump_strength,
        )

    def generate_cymatic_harmonic_lattice_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "sapphire_celestial",
        palette_name: Optional[str] = None,
        bump_strength: float = 3.5,
    ) -> Dict[str, str]:
        """
        Synthesizes all 7 PBR texture maps for Suite 6: T_Cymatic_HarmonicLattice.
        """
        suite_name = "T_Cymatic_HarmonicLattice"
        selected_palette = palette_name or palette
        height, feature_field = self.generate_cymatic_lattice_heightfield()

        paths = self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=height,
            feature_field=feature_field,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )
        return paths

    def generate_harmonic_lattice_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "sapphire_celestial",
        palette_name: Optional[str] = None,
        bump_strength: float = 3.5,
    ) -> Dict[str, str]:
        """Alias for generate_cymatic_harmonic_lattice_suite."""
        return self.generate_cymatic_harmonic_lattice_suite(
            output_dir=output_dir,
            palette=palette,
            palette_name=palette_name,
            bump_strength=bump_strength,
        )

    def bake_all(
        self,
        output_root: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Bakes all 14 maps for both Chladni Domain Suites (Suite 5 & Suite 6)."""
        out_root = Path(output_root) if output_root is not None else PROJECT_ROOT / "textures"
        suite5_dir = out_root / "T_Chladni_ResonantModal"
        suite6_dir = out_root / "T_Cymatic_HarmonicLattice"
        return {
            "T_Chladni_ResonantModal": self.generate_resonant_modal_suite(
                output_dir=suite5_dir,
                palette="titanium_cymatic",
                bump_strength=3.5,
            ),
            "T_Cymatic_HarmonicLattice": self.generate_harmonic_lattice_suite(
                output_dir=suite6_dir,
                palette="sapphire_celestial",
                bump_strength=3.5,
            ),
        }


def main():
    parser = argparse.ArgumentParser(description="Chladni Cymatics & Harmonic Lattice PBR Texture Generator")
    parser.add_argument("--suite", type=str, choices=["all", "T_Chladni_ResonantModal", "T_Cymatic_HarmonicLattice"], default="all", help="Suite to synthesize")
    parser.add_argument("--res", type=int, default=2048, help="POT Resolution (default: 2048)")
    parser.add_argument("--out", type=str, default=None, help="Base textures output directory")
    parser.add_argument("--bump", type=float, default=3.5, help="Normal bump strength (default: 3.5)")

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    base_out = Path(args.out) if args.out else project_root / "textures"

    generator = ChladniGenerator(resolution=args.res)

    print("=" * 70)
    print(f"Chladni & Cymatics PBR Generator | Resolution: {args.res}x{args.res}")
    print(f"Output Directory: {base_out}")
    print("=" * 70)

    if args.suite in ["all", "T_Chladni_ResonantModal"]:
        suite_name = "T_Chladni_ResonantModal"
        suite_dir = base_out / suite_name
        print(f"\n[1/2] Synthesizing Suite: {suite_name} ...")
        paths = generator.generate_chladni_resonant_modal_suite(
            output_dir=suite_dir,
            palette_name="titanium_cymatic",
            bump_strength=args.bump,
        )
        for key, p in paths.items():
            print(f"  + Generated {key:<4} -> {p}")

    if args.suite in ["all", "T_Cymatic_HarmonicLattice"]:
        suite_name = "T_Cymatic_HarmonicLattice"
        suite_dir = base_out / suite_name
        print(f"\n[2/2] Synthesizing Suite: {suite_name} ...")
        paths = generator.generate_cymatic_harmonic_lattice_suite(
            output_dir=suite_dir,
            palette_name="sapphire_celestial",
            bump_strength=args.bump,
        )
        for key, p in paths.items():
            print(f"  + Generated {key:<4} -> {p}")

    print("\n" + "=" * 70)
    print("Chladni & Cymatics Texture Synthesis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
