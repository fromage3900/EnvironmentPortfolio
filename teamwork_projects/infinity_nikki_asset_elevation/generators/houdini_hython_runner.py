"""
Native Houdini / hython Automation Script for Haute-Couture Geometry & PBR Texture Baking.
Constructs Houdini SOP/VEX networks via `hou` API when running inside hython,
or seamlessly bridges to standalone Python synthesizers in headless non-Houdini environments.
"""

import argparse
import os
import sys
from typing import Optional

# -----------------------------------------------------------------------------
# Embedded VEX Code Snippets for Houdini Wranglers
# -----------------------------------------------------------------------------

VEX_CHANTILLY_CORDONNET = """
// VEX Detail Wrangle: Superformula Floral Rosettes & Scalloped Borders
int n_petals = chi("num_petals");
float radius_base = chf("radius_base");
float scallop_freq = chf("scallop_freq");
int num_pts = chi("num_samples");

int prim = addprim(geoself(), "polyline");

for(int i = 0; i <= num_pts; i++) {
    float theta = (float(i) / float(num_pts)) * 2.0 * PI;
    
    // Multi-frequency harmonic floral envelope
    float r = radius_base * (1.0 + 0.38 * cos(float(n_petals) * theta) 
                                + 0.14 * cos(2.0 * float(n_petals) * theta)
                                + 0.05 * sin(3.0 * float(n_petals) * theta));
                                
    float y_scallop = 0.035 * pow(abs(sin(scallop_freq * theta)), 1.6);
    vector pos = set(r * cos(theta), r * sin(theta) + y_scallop, 0.0);
    pos.z = 0.012 * (1.0 - smoothstep(0.0, radius_base * 1.5, r));
    
    int pt = addpoint(geoself(), pos);
    setpointattrib(geoself(), "cordonnet_weight", pt, 1.0, "set");
    setpointattrib(geoself(), "pscale", pt, 0.0045, "set");
    addvertex(geoself(), prim, pt);
}
"""

VEX_CHANTILLY_BEAD_ORIENT = """
// VEX Point Wrangle: Frenet-Serret Orthonormal Orientation & Attribute Tagging
vector tangent = normalize(point(0, "tangentu", @ptnum));
vector up = set(0, 0, 1);
vector normal = normalize(cross(tangent, up));

matrix3 rot = set(tangent, normal, up);
vector4 orient = quaternion(rot);

float seed = float(@ptnum) * 17.41;
vector rand_axis = sample_sphere_uniform(vector2(rand(seed), rand(seed + 1.0)));
vector4 wobble = quaternion(radians(fit01(rand(seed + 2.0), -10.0, 10.0)), rand_axis);
@orient = qmultiply(orient, wobble);

@bead_type = (rand(seed + 3.0) > 0.45) ? 0 : 1; // 0 = Pearl, 1 = Bicone Crystal
@pscale = fit01(rand(seed + 4.0), 0.006, 0.010);
@Cd = (@bead_type == 0) ? set(0.98, 0.95, 0.92) : set(0.88, 0.92, 1.0);
@roughness = (@bead_type == 0) ? 0.26 : 0.04;
@metallic = 0.0;
"""

VEX_ORGANZA_SOLVER = """
// VEX Point Wrangle: Morphogenetic Differential Line Growth inside Solver SOP
float rep_radius = chf("repulsion_radius"); // 0.04m
float k_rep = chf("repulsion_force");       // 0.30
float k_spring = chf("spring_force");       // 0.25
float buckle_amp = chf("buckle_amplitude"); // 0.06

// 1. Point Cloud Self-Avoidance
int close_pts[] = pcfind(0, "P", @P, rep_radius, 32);
vector f_rep = set(0, 0, 0);

foreach(int other_pt; close_pts) {
    if(other_pt == @ptnum) continue;
    vector other_pos = point(0, "P", other_pt);
    vector diff = @P - other_pos;
    float dist = length(diff);
    if(dist > 0.0001 && dist < rep_radius) {
        float factor = (1.0 - (dist / rep_radius));
        f_rep += normalize(diff) * (factor * factor / (dist + 0.005)) * k_rep;
    }
}

// 2. Neighbor Spring Tension
int pt_prev = (@ptnum - 1 + @numpt) % @numpt;
int pt_next = (@ptnum + 1) % @numpt;
vector p_prev = point(0, "P", pt_prev);
vector p_next = point(0, "P", pt_next);

vector laplacian = 0.5 * (p_prev + p_next) - @P;
vector f_spring = laplacian * k_spring;

// 3. Out-of-Plane Buckling (3D Ruffles)
float curvature = length(laplacian);
float buckle_dir = sin(@P.x * 24.0 + @P.y * 24.0);
vector f_buckle = set(0, 0, curvature * buckle_amp * buckle_dir);

@P += (f_rep + f_spring + f_buckle) * 0.12;
"""

VEX_BULLION_BRAID = """
// VEX Detail Wrangle: 3-Strand Gold Cannetille Braid & Micro-Purl Wire
int spine_prim = 0;
int num_spine_pts = primpoints(geoself(), spine_prim);
int num_strands = 3;
float braid_radius = chf("braid_radius"); // 0.007m
float braid_freq = chf("braid_freq");     // 42.0
float purl_radius = chf("purl_radius");   // 0.002m
float purl_freq = chf("purl_freq");       // 300.0

for(int s = 0; s < num_strands; s++) {
    int strand_prim = addprim(geoself(), "polyline");
    float strand_phase = float(s) * (2.0 * PI / float(num_strands));
    
    for(int i = 0; i < len(num_spine_pts); i++) {
        int pt = num_spine_pts[i];
        vector P_spine = point(geoself(), "P", pt);
        vector T = normalize(point(geoself(), "tangentu", pt));
        vector N = normalize(point(geoself(), "N", pt));
        vector B = normalize(cross(T, N));
        
        float u = point(geoself(), "u_coord", pt);
        float s_dist = u * 10.0;
        
        // Macro braid orbit
        float braid_angle = s_dist * braid_freq + strand_phase;
        vector macro_offset = braid_radius * (cos(braid_angle) * N + sin(braid_angle) * B);
        
        // Micro-purl helical winding
        float purl_angle = s_dist * purl_freq;
        vector micro_offset = purl_radius * (cos(purl_angle) * N + sin(purl_angle) * T);
        
        vector P_final = P_spine + macro_offset + micro_offset;
        int new_pt = addpoint(geoself(), P_final);
        setpointattrib(geoself(), "metallic", new_pt, 1.0, "set");
        setpointattrib(geoself(), "roughness", new_pt, 0.22, "set");
        setpointattrib(geoself(), "Cd", new_pt, set(1.0, 0.84, 0.20), "set"); // 24k Gold
        addvertex(geoself(), strand_prim, new_pt);
    }
}
"""

VEX_REACTION_DIFFUSION_SOLVER = """
// VEX Point Wrangle: Gray-Scott 9-Point Laplacian Kernel
float Du = chf("Du"); // 0.16
float Dv = chf("Dv"); // 0.08
float F  = chf("F");  // 0.034
float k  = chf("k");  // 0.065
float dt = chf("dt"); // 1.0

int res_x = chi("res_x");
int res_y = chi("res_y");
int ix = @ptnum % res_x;
int iy = @ptnum / res_x;

float weights[9] = {0.25, 0.5, 0.25, 0.5, -3.0, 0.5, 0.25, 0.5, 0.25};
float lap_u = 0.0;
float lap_v = 0.0;
int idx = 0;

for(int dy = -1; dy <= 1; dy++) {
    for(int dx = -1; dx <= 1; dx++) {
        int nx = (ix + dx + res_x) % res_x;
        int ny = (iy + dy + res_y) % res_y;
        int n_pt = ny * res_x + nx;
        
        float nu = point(0, "u_val", n_pt);
        float nv = point(0, "v_val", n_pt);
        
        lap_u += nu * weights[idx];
        lap_v += nv * weights[idx];
        idx++;
    }
}

float u = @u_val;
float v = @v_val;
float uvv = u * v * v;

float du = (Du * lap_u - uvv + F * (1.0 - u)) * dt;
float dv = (Dv * lap_v + uvv - (F + k) * v) * dt;

@u_val = clamp(u + du, 0.0, 1.0);
@v_val = clamp(v + dv, 0.0, 1.0);
"""


def build_houdini_native_networks():
    """
    Constructs the Houdini SOP node networks when running inside hython.
    """
    try:
        import hou
    except ImportError:
        print("[HoudiniHythonRunner] `hou` module not found. Skipping native node graph construction.")
        return False

    print("[HoudiniHythonRunner] Connected to Houdini Engine / `hou` API.")
    obj = hou.node("/obj")
    if not obj:
        print("[HoudiniHythonRunner] /obj context not found.")
        return False

    # 1. Chantilly Lace SOP
    geo_lace = obj.createNode("geo", "geo_chantilly_lace")
    wrangle_cord = geo_lace.createNode("attribwrangle", "cordonnet_superformula")
    wrangle_cord.parm("class").set(0)  # Detail wrangle
    wrangle_cord.parm("snippet").set(VEX_CHANTILLY_CORDONNET)

    # 2. Differential Organza SOP
    geo_organza = obj.createNode("geo", "geo_differential_organza")
    solver_organza = geo_organza.createNode("solver", "differential_growth_solver")

    # 3. Baroque Bullion SOP
    geo_bullion = obj.createNode("geo", "geo_baroque_bullion")
    wrangle_braid = geo_bullion.createNode("attribwrangle", "braided_gold_strands")
    wrangle_braid.parm("class").set(0)  # Detail wrangle
    wrangle_braid.parm("snippet").set(VEX_BULLION_BRAID)

    # 4. Reaction-Diffusion Cloisons SOP
    geo_rd = obj.createNode("geo", "geo_reaction_diffusion")
    wrangle_rd = geo_rd.createNode("attribwrangle", "gray_scott_kernel")
    wrangle_rd.parm("class").set(1)  # Point wrangle
    wrangle_rd.parm("snippet").set(VEX_REACTION_DIFFUSION_SOLVER)

    print("[HoudiniHythonRunner] Successfully created native SOP node graphs:")
    print("  - /obj/geo_chantilly_lace")
    print("  - /obj/geo_differential_organza")
    print("  - /obj/geo_baroque_bullion")
    print("  - /obj/geo_reaction_diffusion")
    return True


def run_standalone_generation(
    archetype: str, resolution: int, out_dir: str, geo_dir: str, seed: int
):
    """
    Executes standalone procedural synthesis using Python / NumPy generators.
    """
    from .chantilly_lace_synthesizer import ChantillyLaceSynthesizer
    from .differential_organza_synthesizer import DifferentialOrganzaSynthesizer
    from .baroque_bullion_synthesizer import BaroqueBullionSynthesizer
    from .reaction_diffusion_synthesizer import ReactionDiffusionSynthesizer
    from .high_to_low_baker import HighToLowBaker

    baker = HighToLowBaker(resolution=resolution)

    archetype_map = {
        "chantilly_lace": (
            ChantillyLaceSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_ChantillyLace_PearlBeading",
        ),
        "differential_organza": (
            DifferentialOrganzaSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_DifferentialOrganza_Petals",
        ),
        "baroque_bullion": (
            BaroqueBullionSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_BaroqueBullion_Acanthus",
        ),
        "reaction_diffusion": (
            ReactionDiffusionSynthesizer(resolution=resolution, seed=seed),
            "T_HauteCouture_ReactionDiffusion_Cloisonne",
        ),
    }

    targets = list(archetype_map.keys()) if archetype == "all" else [archetype]

    for arch_key in targets:
        if arch_key not in archetype_map:
            print(f"[HoudiniHythonRunner] Unknown archetype: {arch_key}")
            continue

        synth, prefix = archetype_map[arch_key]
        print(f"\n=======================================================")
        print(f"[HoudiniHythonRunner] Synthesizing Archetype: {prefix}")
        print(f"  Resolution: {resolution}x{resolution} POT | Seed: {seed}")
        print(f"=======================================================")

        # 1. 3D Mesh Generation & OBJ Export
        print(f"  -> Building high-poly 3D micro-geometry...")
        geo_data = synth.generate_geometry()
        obj_filename = f"{prefix}_HighPoly.obj"
        obj_path = os.path.join(geo_dir, obj_filename)
        synth.export_obj(
            filepath=obj_path,
            vertices=geo_data["vertices"],
            faces=geo_data["faces"],
            normals=geo_data.get("normals"),
            uvs=geo_data.get("uvs"),
            material_name=f"M_{prefix}",
        )
        print(f"  [OK] Exported 3D Mesh ({len(geo_data['vertices'])} verts, {len(geo_data['faces'])} faces): {obj_path}")

        # 2. Map Synthesis & High-to-Low Bake
        print(f"  -> Synthesizing PBR texture maps and baking high-to-low channels...")
        maps = synth.synthesize_maps()
        baked_files = baker.bake_all_channels(maps=maps, out_dir=out_dir, prefix=prefix)

        print(f"  [OK] Successfully baked 9 PBR texture channels to {out_dir}:")
        for channel_name, file_path in baked_files.items():
            print(f"     - [{channel_name:10s}] -> {os.path.basename(file_path)}")


def main():
    parser = argparse.ArgumentParser(
        description="Infinity Nikki Haute-Couture Houdini / hython Procedural Generator & Baker"
    )
    parser.add_argument(
        "--archetype",
        choices=["all", "chantilly_lace", "differential_organza", "baroque_bullion", "reaction_diffusion"],
        default="all",
        help="Target procedural archetype to synthesize.",
    )
    parser.add_argument("--res", type=int, default=2048, help="Power-of-Two texture resolution (default: 2048).")
    parser.add_argument("--out", type=str, default="textures", help="Output directory for baked PBR maps.")
    parser.add_argument("--geo", type=str, default="models", help="Output directory for exported 3D OBJ meshes.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for procedural variations.")
    parser.add_argument("--build-hou", action="store_true", help="Build native Houdini SOP networks if hou is available.")

    args = parser.parse_args()

    # Attempt Houdini node creation if requested or if hou is present
    has_hou = build_houdini_native_networks()

    # Always execute standalone generation to produce high-poly meshes and baked maps
    run_standalone_generation(
        archetype=args.archetype,
        resolution=args.res,
        out_dir=args.out,
        geo_dir=args.geo,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
