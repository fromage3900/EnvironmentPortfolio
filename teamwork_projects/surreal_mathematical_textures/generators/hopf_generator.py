"""
Hopf & Hypersurface Generator: 4D Non-Euclidean Mathematical PBR Texture Synthesis
==================================================================================
Procedural generation engine for 4D hypersurface projections and fiber bundles:
1. Suite 3: Toroidal Hopf Fibration Bundle (S^3 -> S^2) with Interlocking Villarceau Circle Braids.
2. Suite 4: 4D Hypersphere Cross-Sections with 4D Isoclinic Double-Rotated Clifford Torus Interference.

Resolution: 2048x2048 Power-of-Two (POT)
Dependencies: Pure NumPy 2.4.6 + Pillow 12.2.0 (Zero SciPy)
Integration: PBREngine (DirectX Tangent Normal Green=-Y, Multiscale AO, ORM Packing, Haute-Couture BaseColor)
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image

# Ensure project root is in sys.path for robust module resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from generators.pbr_engine import PBREngine
except ImportError:
    # Fallback to local import if executed within generators directory
    from pbr_engine import PBREngine


class HopfFibrationGenerator:
    """
    Procedural mathematical generator for 4D Hopf Fibrations and 4D Hypersphere Slices.
    Vectorized NumPy implementation for high performance at 2048x2048 resolution.
    """

    def __init__(self, resolution: int = 2048, pbr_engine: Optional[PBREngine] = None):
        self.resolution = resolution
        self.res = resolution
        self.pbr_engine = pbr_engine or PBREngine(resolution=resolution)

    def generate_hopf_toroidal_fibration(
        self,
        resolution: Optional[int] = None,
        z0_slice: float = 0.25,
        domain_scale: float = 3.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes the Toroidal Hopf Fibration Fiber Bundle (S^3 -> S^2) heightfield.

        Mathematical Formulation:
        -------------------------
        1. Consider S^3 in C^2: |z_0|^2 + |z_1|^2 = 1.
        2. Planar stereographic projection slice at z = z0_slice from R^3 to S^3:
           rho^2 = x^2 + y^2 + z0^2
           P = (2x / (1 + rho^2), 2y / (1 + rho^2), 2z0 / (1 + rho^2), (rho^2 - 1) / (1 + rho^2)) in S^3
        3. Complex coordinates: z0 = P_0 + i*P_1, z1 = P_2 + i*P_3.
        4. Hopf projection pi(z0, z1) -> S^2:
           X_1 = 2*Re(z0 * conj(z1)) = 2*(P_0*P_2 + P_1*P_3)
           X_2 = 2*Im(z0 * conj(z1)) = 2*(P_1*P_2 - P_0*P_3)
           X_3 = |z0|^2 - |z1|^2 = (P_0^2 + P_1^2) - (P_2^2 + P_3^2)
        5. Fiber coordinates & Toroidal angles:
           psi = Arg(z0) + Arg(z1) = atan2(P_1, P_0) + atan2(P_3, P_2)
           phi_base = atan2(X_2, X_1)
           eta = 0.5 * arccos(clip(X_3, -1, 1))
        6. Multiscale Toroidal harmonics, Villarceau circle crests, and micro-braided threads:
           B1 = cos(7*psi + 3*phi_base) (7-fold Hopf fiber bundle)
           B2 = sin(4*(psi - phi_base)) * cos(4*(psi + phi_base)) (Chiral interlocking braid)
           B3 = exp(-((eta - pi/4)^2)/0.035) + 0.85*exp(-((eta - pi/6)^2)/0.02) + 0.85*exp(-((eta - pi/3)^2)/0.02)
           B4 = cos(24*psi - 10*phi_base) * sin(10*eta) (Meso-scale filigree ribs)
           B5 = cos(64*psi + 24*phi_base) * cos(16*eta) * 0.45 (Jacquard bullion weave)
           B6 = cos(192*psi - 64*phi_base) * 0.40 (High-frequency micro-relief)
           B7 = sin(320*(X_1*X_2 + P_0*P_1)) * 0.25 (Sub-pixel acoustic interference)

        Returns:
            Tuple[np.ndarray, np.ndarray]: (height_normalized, feature_field) in float32 [0.0, 1.0].
        """
        n = resolution if resolution is not None else self.res
        x = np.linspace(-domain_scale, domain_scale, n, dtype=np.float64)
        y = np.linspace(-domain_scale, domain_scale, n, dtype=np.float64)
        X, Y = np.meshgrid(x, y)

        # 1. Stereographic projection to 4D unit 3-sphere S^3
        rho_sq = X**2 + Y**2 + (z0_slice**2)
        denom = 1.0 + rho_sq
        P0 = 2.0 * X / denom
        P1 = 2.0 * Y / denom
        P2 = 2.0 * z0_slice / denom
        P3 = (rho_sq - 1.0) / denom

        # 2. Base 2-sphere coordinates (Hopf map S^3 -> S^2)
        X1 = 2.0 * (P0 * P2 + P1 * P3)
        X2 = 2.0 * (P1 * P2 - P0 * P3)
        X3 = (P0**2 + P1**2) - (P2**2 + P3**2)

        # 3. Fiber phase, base angle, and nested torus latitude
        psi = np.arctan2(P1, P0) + np.arctan2(P3, P2)
        phi_base = np.arctan2(X2, X1)
        eta = 0.5 * np.arccos(np.clip(X3, -1.0, 1.0))

        # 4. Multi-scale toroidal wave interference modes
        B1 = np.cos(7.0 * psi + 3.0 * phi_base)
        B1_sharp = np.sign(B1) * (np.abs(B1) ** 0.65)

        B2 = np.sin(4.0 * (psi - phi_base)) * np.cos(4.0 * (psi + phi_base))

        # Concentric Villarceau circles & nested coaxial tori
        B3 = (
            np.exp(-((eta - np.pi / 4.0) ** 2) / 0.035)
            + 0.85 * np.exp(-((eta - np.pi / 6.0) ** 2) / 0.02)
            + 0.85 * np.exp(-((eta - np.pi / 3.0) ** 2) / 0.02)
        )

        # Meso-scale and micro-scale braided bullion thread harmonics
        B4 = np.cos(24.0 * psi - 10.0 * phi_base) * np.sin(10.0 * eta)
        B5 = np.cos(64.0 * psi + 24.0 * phi_base) * np.cos(16.0 * eta) * 0.45
        B6 = np.cos(192.0 * psi - 64.0 * phi_base) * 0.40
        B7 = np.sin(320.0 * (X1 * X2 + P0 * P1)) * 0.25

        # 5. Composite heightfield evaluation
        H_raw = (
            0.26 * B1_sharp
            + 0.16 * B2
            + 0.18 * B3
            + 0.12 * B4
            + 0.10 * B5
            + 0.10 * B6
            + 0.08 * B7
        )

        h_min, h_max = float(H_raw.min()), float(H_raw.max())
        height_normalized = ((H_raw - h_min) / (h_max - h_min + 1e-8)).astype(np.float32)

        # 6. Feature field for vitreous enamel vs platinum bullion partitioning
        feature_field = np.clip(
            0.5 + 0.5 * np.sin(3.0 * phi_base + 2.0 * psi) * np.cos(4.0 * eta),
            0.0,
            1.0,
        ).astype(np.float32)

        return height_normalized, feature_field

    def generate_hypersphere_dimensional_interference(
        self,
        resolution: Optional[int] = None,
        alpha1: float = np.pi / 5.0,
        alpha2: float = 3.0 * np.pi / 7.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes the 4D Hypersphere Cross-Section Dimensional Interference heightfield.

        Mathematical Formulation:
        -------------------------
        1. Flat Clifford Torus T^2 in S^3 in R^4 parameterized by (u, v) in [-pi, pi)^2:
           X_base(u, v) = (cos(u)/sqrt(2), sin(u)/sqrt(2), cos(v)/sqrt(2), sin(v)/sqrt(2))
        2. 4D Isoclinic Double Rotation in SO(4) with distinct irrational angle ratios (alpha1, alpha2):
           X_1 = cos(u + alpha1) / sqrt(2),  Y_1 = sin(u + alpha1) / sqrt(2)
           X_2 = cos(v + alpha2) / sqrt(2),  Y_2 = sin(v + alpha2) / sqrt(2)
        3. Multiscale Dimensional Interference Standing Waves:
           W1 = cos(4*X_1 + 6*Y_1 + 2*X_2)
           W2 = cos(3*Y_1 + 5*X_2 - 4*Y_2)
           W3 = cos(7*(X_1*X_2 - Y_1*Y_2) + 3*(X_1*Y_2 + Y_1*X_2)) (Cross-dimensional chiral spin)
           W4 = exp(-18 * ((X_1^2 + Y_1^2) - (X_2^2 + Y_2^2))^2) (Clifford torus metric balance crest)
           W5 = sin(8*(u + v)) * cos(6*(u - v)) (Harmonic torus lattice resonance)
           W6 = cos(14*(X_1*Y_2 - X_2*Y_1)) (4D symplectic area wave)
           W7 = cos(48*(u + 2*v)) * cos(36*(2*u - v)) * 0.40
           W8 = cos(192*(X_1*Y_2 + Y_1*X_2)) * 0.50 (High-frequency standing node)
           W9 = cos(256*(u - v)) * 0.35 (Micro-jacquard thread structure)
           W10 = sin(384*(X_1*X_2 - Y_1*Y_2)) * 0.25 (Sub-pixel dimensional ripple)

        Returns:
            Tuple[np.ndarray, np.ndarray]: (height_normalized, feature_field) in float32 [0.0, 1.0].
        """
        n = resolution if resolution is not None else self.res
        u = np.linspace(-np.pi, np.pi, n, endpoint=False, dtype=np.float64)
        v = np.linspace(-np.pi, np.pi, n, endpoint=False, dtype=np.float64)
        U, V = np.meshgrid(u, v)

        # 1. 4D Isoclinic double rotation of Clifford torus coordinates
        inv_sqrt2 = 1.0 / np.sqrt(2.0)
        X1 = np.cos(U + alpha1) * inv_sqrt2
        Y1 = np.sin(U + alpha1) * inv_sqrt2
        X2 = np.cos(V + alpha2) * inv_sqrt2
        Y2 = np.sin(V + alpha2) * inv_sqrt2

        # 2. Dimensional wave interference standing equations
        W1 = np.cos(4.0 * X1 + 6.0 * Y1 + 2.0 * X2)
        W2 = np.cos(3.0 * Y1 + 5.0 * X2 - 4.0 * Y2)
        W3 = np.cos(7.0 * (X1 * X2 - Y1 * Y2) + 3.0 * (X1 * Y2 + Y1 * X2))
        W3_sharp = np.sign(W3) * (np.abs(W3) ** 0.65)

        # Clifford Torus balance Gaussian ridge
        W4 = np.exp(-18.0 * (((X1**2 + Y1**2) - (X2**2 + Y2**2)) ** 2))

        # Resonance lattice & 4D symplectic spin
        W5 = np.sin(8.0 * (U + V)) * np.cos(6.0 * (U - V))
        W6 = np.cos(14.0 * (X1 * Y2 - X2 * Y1))

        # High-order micro-wave standing harmonics
        W7 = np.cos(48.0 * (U + 2.0 * V)) * np.cos(36.0 * (2.0 * U - V)) * 0.40
        W8 = np.cos(192.0 * (X1 * Y2 + Y1 * X2)) * 0.50
        W9 = np.cos(256.0 * (U - V)) * 0.35
        W10 = np.sin(384.0 * (X1 * X2 - Y1 * Y2)) * 0.25

        # 3. Superposition & composite heightfield
        H_raw = (
            0.18 * (W1 * W2)
            + 0.16 * W3_sharp
            + 0.14 * W4
            + 0.12 * W5
            + 0.09 * W6
            + 0.08 * W7
            + 0.09 * W8
            + 0.08 * W9
            + 0.06 * W10
        )

        h_min, h_max = float(H_raw.min()), float(H_raw.max())
        height_normalized = ((H_raw - h_min) / (h_max - h_min + 1e-8)).astype(np.float32)

        # 4. Feature field for amethyst enamel vs gold bullion partitioning
        feature_field = np.clip(0.5 + 0.5 * (W1 + W3) * 0.5, 0.0, 1.0).astype(np.float32)

        return height_normalized, feature_field

    def generate_toroidal_fibration_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "sapphire_celestial",
        palette_name: Optional[str] = None,
        bump_strength: float = 7.5,
        z0_slice: float = 0.25,
        domain_scale: float = 3.0,
    ) -> Dict[str, str]:
        """Synthesizes all 7 PBR maps for Suite 3 (T_Hopf_ToroidalFibration)."""
        suite_name = "T_Hopf_ToroidalFibration"
        selected_palette = palette_name or palette
        height, feature = self.generate_hopf_toroidal_fibration(
            resolution=self.resolution,
            z0_slice=z0_slice,
            domain_scale=domain_scale,
        )
        paths = self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=height,
            feature_field=feature,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )
        return paths

    def generate_dimensional_interference_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "amethyst_quartz",
        palette_name: Optional[str] = None,
        bump_strength: float = 7.5,
        alpha1: float = np.pi / 5.0,
        alpha2: float = 3.0 * np.pi / 7.0,
    ) -> Dict[str, str]:
        """Synthesizes all 7 PBR maps for Suite 4 (T_Hypersphere_DimensionalInterference)."""
        suite_name = "T_Hypersphere_DimensionalInterference"
        selected_palette = palette_name or palette
        height, feature = self.generate_hypersphere_dimensional_interference(
            resolution=self.resolution,
            alpha1=alpha1,
            alpha2=alpha2,
        )
        paths = self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=height,
            feature_field=feature,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )
        return paths

    def bake_hopf_toroidal_fibration(
        self,
        output_root: Optional[Union[str, Path]] = None,
        resolution: Optional[int] = None,
        bump_strength: float = 7.5,
        palette_name: str = "sapphire_celestial",
        output_dir: Optional[Union[str, Path]] = None,
        palette: Optional[str] = None,
    ) -> Dict[str, str]:
        """Bakes all 7 PBR maps for Suite 3 (T_Hopf_ToroidalFibration)."""
        res = resolution if resolution is not None else self.res
        selected_palette = palette or palette_name
        if output_dir is not None:
            target_dir = Path(output_dir)
        elif output_root is not None:
            target_dir = Path(output_root) / "T_Hopf_ToroidalFibration"
        else:
            target_dir = PROJECT_ROOT / "textures" / "T_Hopf_ToroidalFibration"

        t0 = time.perf_counter()
        if res != self.resolution:
            gen = HopfFibrationGenerator(resolution=res)
            paths = gen.generate_toroidal_fibration_suite(
                output_dir=target_dir,
                palette=selected_palette,
                bump_strength=bump_strength,
            )
        else:
            paths = self.generate_toroidal_fibration_suite(
                output_dir=target_dir,
                palette=selected_palette,
                bump_strength=bump_strength,
            )
        elapsed = time.perf_counter() - t0
        print(f"[T_Hopf_ToroidalFibration] Baked 7 PBR maps to {target_dir} in {elapsed:.2f}s")
        return paths

    def bake_hypersphere_dimensional_interference(
        self,
        output_root: Optional[Union[str, Path]] = None,
        resolution: Optional[int] = None,
        bump_strength: float = 7.5,
        palette_name: str = "amethyst_quartz",
        output_dir: Optional[Union[str, Path]] = None,
        palette: Optional[str] = None,
    ) -> Dict[str, str]:
        """Bakes all 7 PBR maps for Suite 4 (T_Hypersphere_DimensionalInterference)."""
        res = resolution if resolution is not None else self.res
        selected_palette = palette or palette_name
        if output_dir is not None:
            target_dir = Path(output_dir)
        elif output_root is not None:
            target_dir = Path(output_root) / "T_Hypersphere_DimensionalInterference"
        else:
            target_dir = PROJECT_ROOT / "textures" / "T_Hypersphere_DimensionalInterference"

        t0 = time.perf_counter()
        if res != self.resolution:
            gen = HopfFibrationGenerator(resolution=res)
            paths = gen.generate_dimensional_interference_suite(
                output_dir=target_dir,
                palette=selected_palette,
                bump_strength=bump_strength,
            )
        else:
            paths = self.generate_dimensional_interference_suite(
                output_dir=target_dir,
                palette=selected_palette,
                bump_strength=bump_strength,
            )
        elapsed = time.perf_counter() - t0
        print(f"[T_Hypersphere_DimensionalInterference] Baked 7 PBR maps to {target_dir} in {elapsed:.2f}s")
        return paths

    def bake_all(
        self,
        output_root: Optional[Union[str, Path]] = None,
        resolution: Optional[int] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Bakes all 14 maps for both 4D Domain Suites (Suite 3 & Suite 4)."""
        res = resolution if resolution is not None else self.res
        root = Path(output_root) if output_root is not None else PROJECT_ROOT / "textures"

        print("=" * 70)
        print(f"Baking Domain 2: 4D Hopf & Hypersurface Slices ({res}x{res} POT)")
        print("=" * 70)

        results = {
            "T_Hopf_ToroidalFibration": self.bake_hopf_toroidal_fibration(
                output_root=root,
                resolution=res,
                bump_strength=7.5,
                palette_name="sapphire_celestial",
            ),
            "T_Hypersphere_DimensionalInterference": self.bake_hypersphere_dimensional_interference(
                output_root=root,
                resolution=res,
                bump_strength=7.5,
                palette_name="amethyst_quartz",
            ),
        }
        print("=" * 70)
        print("Domain 2 Synthesis Complete: 14 maps authored successfully.")
        print("=" * 70)
        return results


# Standardized class alias for unified orchestrator integration
HopfGenerator = HopfFibrationGenerator


def main():
    parser = argparse.ArgumentParser(
        description="4D Hopf & Hypersurface PBR Texture Suite Generator"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=2048,
        help="POT Resolution (default: 2048)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "textures"),
        help="Output directory root for textures",
    )
    parser.add_argument(
        "--suite",
        type=str,
        choices=[
            "all",
            "T_Hopf_ToroidalFibration",
            "T_Hypersphere_DimensionalInterference",
        ],
        default="all",
        help="Which suite to synthesize",
    )
    parser.add_argument(
        "--bump-strength",
        type=float,
        default=7.5,
        help="DirectX tangent normal bump multiplier (default: 7.5)",
    )

    args = parser.parse_args()
    generator = HopfGenerator(resolution=args.resolution)

    if args.suite == "all":
        generator.bake_all(output_root=args.output_dir, resolution=args.resolution)
    elif args.suite == "T_Hopf_ToroidalFibration":
        generator.bake_hopf_toroidal_fibration(
            output_root=args.output_dir,
            resolution=args.resolution,
            bump_strength=args.bump_strength,
        )
    elif args.suite == "T_Hypersphere_DimensionalInterference":
        generator.bake_hypersphere_dimensional_interference(
            output_root=args.output_dir,
            resolution=args.resolution,
            bump_strength=args.bump_strength,
        )


if __name__ == "__main__":
    main()
