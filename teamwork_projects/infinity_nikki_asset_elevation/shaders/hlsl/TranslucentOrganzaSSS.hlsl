// =============================================================================
// Infinity Nikki Haute-Couture Asset Elevation Ecosystem
// File: TranslucentOrganzaSSS.hlsl
// Description: Sheer organza translucency with view-dependent optical transparency,
//              dual-sided thin-sheet subsurface scattering (SSS), and Reoriented Normal
//              Mapping (RNM) micro-twill perturbation for ethereal haute-couture fabrics.
// Target: Unreal Engine 5.3+ Substrate Material Framework / SM6 HLSL Custom Expression
// =============================================================================

#ifndef HAUTE_COUTURE_TRANSLUCENT_ORGANZA_SSS_HLSL
#define HAUTE_COUTURE_TRANSLUCENT_ORGANZA_SSS_HLSL

// Struct holding inputs for Translucent Organza & SSS calculation
struct FOrganzaSSSInputs
{
    float3 BaseColor;            // Sheer cloth albedo tint
    float3 SubsurfaceColor;      // Subsurface transmission scattering glow
    float3 MacroNormal;          // Macro garment fold normal in world/tangent space
    float3 MicroTwillNormal;     // High-frequency 45-degree twill weave normal
    float TwillWeight;           // Blend strength of micro-twill normal [0.0, 1.0]
    float BaseOpacity;           // Perpendicular viewing opacity [0.0, 1.0]
    float SheernessAnglePower;   // Power exponent controlling angle-dependent opacity buildup [1.0, 6.0]
    float AbsorptionDepth;       // Mean Free Path (MFP) / absorption depth in millimeters [0.1, 20.0]
    float DualSidedScattering;   // Backface diffuse subsurface multiplier [0.0, 1.0]
    float3 WorldView;            // Normalized world view vector (pointing toward camera)
};

// Struct holding outputs for Substrate Translucent / Thin-Slab BSDF integration
struct FOrganzaSSSOutputs
{
    float3 PerturbedNormal;                  // Reoriented Normal Mapped (RNM) composite normal
    float3 TransmittanceColor;               // Substrate Transmittance / Volume absorption color
    float3 SubsurfaceScatteringProfile;      // Mean Free Path (MFP) color profile for Substrate SSS
    float FinalOpacity;                      // Angle-modulated sheer opacity for Translucent Blend Mode
    float Thickness;                         // Normalized physical thickness for Substrate Thin-Slab
    float3 SubstrateTranslucentBSDF_Inputs;  // Packed parameters for Substrate Translucent integration
};

/**
 * Blends two tangent-space normal vectors using Reoriented Normal Mapping (RNM).
 * RNM correctly rotates the micro detail normal around the macro base normal without
 * flattening or distorting the hemispherical vector space.
 */
float3 BlendNormalsRNM(float3 nMacro, float3 nMicro)
{
    float3 n1 = nMacro + float3(0.0, 0.0, 1.0);
    float3 n2 = nMicro * float3(-1.0, -1.0, 1.0);
    return normalize(n1 * dot(n1, n2) / max(n1.z, 0.0001) - n2);
}

/**
 * Calculates sheer organza optical transmission, RNM perturbation, and dual-sided SSS.
 *
 * Physical Model:
 * 1. Reoriented Normal Mapping: Combines macro draped folds with ultra-fine diagonal twill fibers
 * 2. View-Dependent Sheerness: Normal incidence transmits maximum background light, while grazing angles accumulate optical density
 * 3. Beer-Lambert Transmittance: Exponential light absorption across the thin organza weave: T = exp(-d * sigma_a)
 * 4. Dual-Sided Subsurface Scattering: Subsurface glow illuminates from both key-light and backlight sources
 */
FOrganzaSSSOutputs CalculateTranslucentOrganzaSSS(in FOrganzaSSSInputs In)
{
    FOrganzaSSSOutputs Out;

    // 1. Reoriented Normal Mapping (RNM)
    float3 nMacro = normalize(In.MacroNormal);
    float3 nMicro = lerp(float3(0.0, 0.0, 1.0), normalize(In.MicroTwillNormal), clamp(In.TwillWeight, 0.0, 1.0));
    float3 blendedN = BlendNormalsRNM(nMacro, nMicro);

    // 2. View-Dependent Sheer Opacity
    float3 V = normalize(In.WorldView);
    float NdotV = clamp(dot(blendedN, V), 0.0001, 1.0);
    float sheerExp = max(In.SheernessAnglePower, 0.1);
    float sheerFresnel = pow(1.0 - NdotV, sheerExp);
    float baseOp = clamp(In.BaseOpacity, 0.0, 1.0);
    float finalOpacity = clamp(baseOp + (1.0 - baseOp) * sheerFresnel, 0.0, 1.0);

    // 3. Volumetric Transmittance & SSS Profile (Beer-Lambert Law)
    float safeAbsorbDepth = max(In.AbsorptionDepth, 0.01);
    float3 extinctionCoeff = float3(0.12, 0.15, 0.18); // Wavelength-selective extinction for soft pink/pearl organza
    float3 transmittance = In.BaseColor * exp(-safeAbsorbDepth * extinctionCoeff);

    // Dual-sided diffuse subsurface scattering profile
    float3 sssProfile = In.SubsurfaceColor * (1.0 + In.DualSidedScattering * 0.65);

    // 4. Substrate Translucent / Thin-Slab Outputs
    Out.PerturbedNormal = blendedN;
    Out.TransmittanceColor = transmittance;
    Out.SubsurfaceScatteringProfile = sssProfile;
    Out.FinalOpacity = finalOpacity;
    Out.Thickness = clamp(safeAbsorbDepth / 10.0, 0.001, 1.0);
    Out.SubstrateTranslucentBSDF_Inputs = float3(finalOpacity, Out.Thickness, In.DualSidedScattering);

    return Out;
}

/**
 * UE5 Custom Material Node Entry Point: CalculateOrganzaTranslucency
 *
 * Wire into Unreal Engine 5 Custom HLSL Material Expression with matching pin names.
 */
float3 CalculateOrganzaTranslucency(
    float3 InBaseColor,
    float3 InSSSColor,
    float3 MacroNormal,
    float3 TwillNormal,
    float TwillWeight,
    float BaseOpacity,
    float SheerPower,
    float AbsorbDepth,
    float DualSided,
    float3 ViewVec,
    out float3 OutNormal,
    out float3 OutSSS,
    out float OutOpacity,
    out float OutThickness,
    out float3 OutSubstrateInputs)
{
    FOrganzaSSSInputs Inputs;
    Inputs.BaseColor = InBaseColor;
    Inputs.SubsurfaceColor = InSSSColor;
    Inputs.MacroNormal = MacroNormal;
    Inputs.MicroTwillNormal = TwillNormal;
    Inputs.TwillWeight = TwillWeight;
    Inputs.BaseOpacity = BaseOpacity;
    Inputs.SheernessAnglePower = SheerPower;
    Inputs.AbsorptionDepth = AbsorbDepth;
    Inputs.DualSidedScattering = DualSided;
    Inputs.WorldView = ViewVec;

    FOrganzaSSSOutputs Outputs = CalculateTranslucentOrganzaSSS(Inputs);

    OutNormal = Outputs.PerturbedNormal;
    OutSSS = Outputs.SubsurfaceScatteringProfile;
    OutOpacity = Outputs.FinalOpacity;
    OutThickness = Outputs.Thickness;
    OutSubstrateInputs = Outputs.SubstrateTranslucentBSDF_Inputs;

    return Outputs.TransmittanceColor;
}

#endif // HAUTE_COUTURE_TRANSLUCENT_ORGANZA_SSS_HLSL
