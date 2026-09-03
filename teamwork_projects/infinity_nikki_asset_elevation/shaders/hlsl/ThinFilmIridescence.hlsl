// =============================================================================
// Infinity Nikki Haute-Couture Asset Elevation Ecosystem
// File: ThinFilmIridescence.hlsl
// Description: Multi-stop spectral thin-film optical interference shader function
//              governed by Airy wave optics, Snell refraction, optical path difference (OPD),
//              phase boundary shifts, and surface curvature thickness modulation.
// Target: Unreal Engine 5.3+ Substrate Material Framework / SM6 HLSL Custom Expression
// =============================================================================

#ifndef HAUTE_COUTURE_THIN_FILM_IRIDESCENCE_HLSL
#define HAUTE_COUTURE_THIN_FILM_IRIDESCENCE_HLSL

// Struct holding inputs for Thin-Film Airy interference calculation
struct FThinFilmInputs
{
    float FilmThickness_nm;      // Film physical thickness in nanometers (100 - 1200 nm)
    float FilmIOR;               // Index of Refraction of thin film layer (e.g. 1.3 - 2.2)
    float SubstrateIOR;          // Index of Refraction of underlying substrate (e.g. 1.4 - 2.5)
    float3 WorldNormal;          // Normalized world surface normal
    float3 WorldView;            // Normalized world view vector (pointing toward camera)
    float CurvatureMask;         // Local surface curvature / micro-crevice mask [0.0, 1.0]
    float CurvatureIntensity;    // Strength of curvature-driven thickness variation [0.0, 2.0]
    float IridescenceIntensity;  // Master amplitude multiplier [0.0, 2.0]
    float3 BaseReflectanceTint;  // Multi-stop chromatic filter tint
};

// Struct holding outputs from Thin-Film Airy interference calculation
struct FThinFilmOutputs
{
    float3 IridescenceColor;     // Resulting spectral RGB interference reflection color
    float FresnelMultiplier;     // View-dependent Schlick Fresnel falloff factor
    float PhaseShift;            // Normalized optical phase [0.0, 1.0]
    float ModulatedRoughness;    // Micro-facet roughness modulated by optical interference
    float3 Substrate_F0;         // Specular F0 reflectance for Substrate Slab BSDF wiring
};

/**
 * Evaluates Airy thin-film optical interference for spectral RGB wavebands.
 *
 * Physical Principles:
 * 1. Medium 0 (Air, n0 = 1.00029) -> Medium 1 (Film, n1) -> Medium 2 (Substrate, n2)
 * 2. Snell's Law: sin(theta1) = (n0/n1)*sin(theta0)
 * 3. Optical Path Difference (OPD): OPD = 2 * n1 * d_eff * cos(theta1)
 * 4. Phase Shifts: phi01 = (n0 < n1) ? pi : 0; phi12 = (n1 < n2) ? pi : 0;
 * 5. Wavelength Bands: Red = 650nm, Green = 532nm, Blue = 450nm
 */
FThinFilmOutputs CalculateThinFilmIridescence(in FThinFilmInputs In)
{
    FThinFilmOutputs Out;

    // Normalize input vectors and compute safe N.V
    float3 N = normalize(In.WorldNormal);
    float3 V = normalize(In.WorldView);
    float NdotV = clamp(dot(N, V), 0.0001, 1.0);

    // Refractive indices
    const float n0 = 1.00029; // Air at standard ambient temperature & pressure
    float n1 = max(In.FilmIOR, 1.001);
    float n2 = max(In.SubstrateIOR, 1.001);

    // Snell's Law: compute cosine of transmitted angle inside thin film
    float sin2_theta0 = max(0.0, 1.0 - (NdotV * NdotV));
    float sin2_theta1 = (n0 * n0) / (n1 * n1) * sin2_theta0;
    
    // Guard against total internal reflection or precision underflow
    float cos_theta1 = sqrt(max(0.0, 1.0 - sin2_theta1));

    // Curvature-driven local thickness modulation
    // Organic folds in haute-couture silks compress thin coatings in high-curvature valleys
    float curvatureOffset = (In.CurvatureMask - 0.5) * In.CurvatureIntensity * 0.8;
    float effectiveThickness = In.FilmThickness_nm * max(0.1, 1.0 + curvatureOffset);
    effectiveThickness = clamp(effectiveThickness, 10.0, 2000.0);

    // Optical Path Difference (OPD) in nanometers
    float OPD = 2.0 * n1 * effectiveThickness * cos_theta1;

    // Wavelengths for RGB primary spectral bands (nm)
    const float3 lambda = float3(650.0, 532.0, 450.0);
    const float PI = 3.14159265358979323846;

    // Interface phase shifts (Fresnel reflection phase inversion on lower-to-higher IOR transitions)
    float phi01 = (n0 < n1) ? PI : 0.0;
    float phi12 = (n1 < n2) ? PI : 0.0;
    float delta_phi = phi01 + phi12;

    // Phase difference per spectral wavelength band: delta = (2*pi/lambda)*OPD + delta_phi
    float3 delta = (2.0 * PI * OPD) / lambda + float3(delta_phi, delta_phi, delta_phi);

    // Airy interference factor: I(lambda) = 0.5 + 0.5 * cos(delta)
    float3 interference = 0.5 + 0.5 * cos(delta);

    // Dielectric interface base reflectance (Fresnel F0)
    float r0 = (n1 - n0) / (n1 + n0);
    float F0_scalar = r0 * r0;
    float3 F0 = float3(F0_scalar, F0_scalar, F0_scalar);

    // Schlick Fresnel grazing enhancement
    float fresnelFactor = F0_scalar + (1.0 - F0_scalar) * pow(1.0 - NdotV, 5.0);

    // Normalized phase shift for secondary modulation (referenced to 532nm green channel)
    Out.PhaseShift = frac(OPD / 532.0);
    Out.FresnelMultiplier = clamp(fresnelFactor, 0.0, 1.0);

    // Composite spectral iridescence color with chromatic tint & grazing falloff
    Out.IridescenceColor = interference * In.BaseReflectanceTint * In.IridescenceIntensity * (0.3 + 0.7 * fresnelFactor);

    // Substrate F0 specular reflectance integration
    Out.Substrate_F0 = lerp(F0, Out.IridescenceColor, clamp(In.IridescenceIntensity * 0.7, 0.0, 1.0));

    // Modulate micro-facet roughness slightly based on optical destructive interference fringes
    Out.ModulatedRoughness = 0.02 * (1.0 - interference.g);

    return Out;
}

/**
 * UE5 Custom Material Node Entry Point: CalculateThinFilmAiry
 *
 * Wire into Unreal Engine 5 Custom HLSL Material Expression with matching pin names.
 */
float3 CalculateThinFilmAiry(
    float FilmThickness_nm,
    float FilmIOR,
    float SubstrateIOR,
    float3 WorldNormal,
    float3 WorldView,
    float CurvatureMask,
    float CurvatureIntensity,
    float IridescenceIntensity,
    float3 BaseReflectanceTint,
    out float OutFresnel,
    out float OutPhase,
    out float OutRoughnessMod,
    out float3 OutSubstrateF0)
{
    FThinFilmInputs Inputs;
    Inputs.FilmThickness_nm = FilmThickness_nm;
    Inputs.FilmIOR = FilmIOR;
    Inputs.SubstrateIOR = SubstrateIOR;
    Inputs.WorldNormal = WorldNormal;
    Inputs.WorldView = WorldView;
    Inputs.CurvatureMask = CurvatureMask;
    Inputs.CurvatureIntensity = CurvatureIntensity;
    Inputs.IridescenceIntensity = IridescenceIntensity;
    Inputs.BaseReflectanceTint = BaseReflectanceTint;

    FThinFilmOutputs Outputs = CalculateThinFilmIridescence(Inputs);

    OutFresnel = Outputs.FresnelMultiplier;
    OutPhase = Outputs.PhaseShift;
    OutRoughnessMod = Outputs.ModulatedRoughness;
    OutSubstrateF0 = Outputs.Substrate_F0;

    return Outputs.IridescenceColor;
}

#endif // HAUTE_COUTURE_THIN_FILM_IRIDESCENCE_HLSL
