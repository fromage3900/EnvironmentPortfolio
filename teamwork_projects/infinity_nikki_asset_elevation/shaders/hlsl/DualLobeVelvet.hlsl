// =============================================================================
// Infinity Nikki Haute-Couture Asset Elevation Ecosystem
// File: DualLobeVelvet.hlsl
// Description: Dual-lobe anisotropic velvet/fuzz shading with Ashikhmin-Charlie sheen,
//              forward grazing rim glow, retro-reflective pile backscatter, and
//              chromatic pile hue shift for haute-couture plush fabrics.
// Target: Unreal Engine 5.3+ Substrate Material Framework / SM6 HLSL Custom Expression
// =============================================================================

#ifndef HAUTE_COUTURE_DUAL_LOBE_VELVET_HLSL
#define HAUTE_COUTURE_DUAL_LOBE_VELVET_HLSL

// Struct holding inputs for Dual-Lobe Velvet calculation
struct FDualLobeVelvetInputs
{
    float3 BaseColor;             // Core textile dye albedo color (sRGB converted)
    float3 RimColor;              // Grazing sheen edge tint
    float3 WorldNormal;           // Normalized world surface normal
    float3 WorldView;             // Normalized world view vector (pointing toward camera)
    float3 TangentFlow;           // Combed fabric pile direction vector in world/tangent space
    float RoughnessCore;          // Base fabric micro-roughness [0.4, 1.0]
    float RoughnessRim;           // Sheen fuzz highlight roughness [0.1, 0.6]
    float RimExponent;            // Exponential falloff curve for rim lighting [1.0, 8.0]
    float RimIntensity;           // Sheen glow amplitude multiplier [0.0, 5.0]
    float AnisotropyStrength;     // Directional pile stretch factor [0.0, 1.0]
    float ChromaticShiftAmount;   // Weight of the core-to-rim chromatic shift [0.0, 1.0]
    float BackscatterIntensity;   // Retro-reflective backward scatter intensity [0.0, 2.0]
};

// Struct holding outputs for Substrate Cloth / Velvet BSDF integration
struct FDualLobeVelvetOutputs
{
    float3 CompositeBaseColor;    // BaseColor chromatically shifted by viewing angle and pile depth
    float3 SheenColor;            // Evaluated sheen color for Substrate Sheen / Cloth BSDF
    float SheenRoughness;         // Micro-fuzz roughness input for Substrate Sheen
    float3 AnisotropicTangent;    // Combed tangent vector in World/Tangent space
    float AnisotropyAmount;       // Anisotropy scalar for Substrate Slab
    float RimMask;                // Isolated scalar rim glow mask for secondary styling
    float SubstrateClothWeight;   // Weight for activating Substrate Cloth Shading Model [0.0, 1.0]
};

/**
 * Calculates dual-lobe anisotropic velvet shading.
 *
 * Physical Model:
 * 1. Forward Grazing Rim: Charlie / Microfiber distribution modeled via exponential Fresnel falloff (1 - N.V)^gamma
 * 2. Retro-Reflective Backscatter: Secondary backward reflection peak from micro-fiber pile tips
 * 3. Chromatic Pile Shift: Pigment absorption deepens perpendicular rays, while grazing rays scatter off outer fiber cuticles
 * 4. Anisotropic Combing: Perturbs tangent along the fiber growth / weave vector
 */
FDualLobeVelvetOutputs CalculateDualLobeVelvet(in FDualLobeVelvetInputs In)
{
    FDualLobeVelvetOutputs Out;

    // Vector normalization & safe dot products
    float3 N = normalize(In.WorldNormal);
    float3 V = normalize(In.WorldView);
    float NdotV = clamp(dot(N, V), 0.0001, 1.0);

    // 1. Forward Grazing Rim (Charlie / Microfiber Lobe)
    float safeExp = max(In.RimExponent, 0.1);
    float rimFactor = pow(1.0 - NdotV, safeExp) * In.RimIntensity;
    float clampedRim = clamp(rimFactor, 0.0, 1.0);

    // 2. Retro-Reflective Backscatter Lobe
    // Backscatter reflects light along grazing angles opposite to the specular bounce
    float backscatterFactor = pow(1.0 - NdotV, 2.0) * In.BackscatterIntensity;

    // 3. Chromatic Pile Shift
    // In velvet textiles, deep pile absorbs light selectively, causing edge fibers to exhibit a distinct hue/tint
    float3 shiftedBase = lerp(In.BaseColor, In.RimColor * 1.25, clampedRim * clamp(In.ChromaticShiftAmount, 0.0, 1.0));

    // 4. Sheen Color & Dual-Lobe Composition
    float3 sheen = In.RimColor * (clampedRim + backscatterFactor);

    // 5. Anisotropic Tangent Combing
    float3 T = In.TangentFlow;
    float lenT = length(T);
    if (lenT < 0.01)
    {
        // Generate stable orthogonal fallback tangent
        float3 up = abs(N.z) < 0.999 ? float3(0.0, 0.0, 1.0) : float3(1.0, 0.0, 0.0);
        T = normalize(cross(up, N));
    }
    else
    {
        T = normalize(T - N * dot(T, N)); // Gram-Schmidt orthogonalization against surface normal
    }

    // 6. Substrate Output Struct Population
    Out.CompositeBaseColor = shiftedBase;
    Out.SheenColor = sheen;
    Out.SheenRoughness = lerp(In.RoughnessCore, In.RoughnessRim, clampedRim);
    Out.AnisotropicTangent = T;
    Out.AnisotropyAmount = clamp(In.AnisotropyStrength, -1.0, 1.0);
    Out.RimMask = clampedRim;
    Out.SubstrateClothWeight = clamp(0.5 + 0.5 * clampedRim, 0.0, 1.0);

    return Out;
}

/**
 * UE5 Custom Material Node Entry Point: CalculateVelvetDualLobe
 *
 * Wire into Unreal Engine 5 Custom HLSL Material Expression with matching pin names.
 */
float3 CalculateVelvetDualLobe(
    float3 InBaseColor,
    float3 InRimColor,
    float3 WorldNormal,
    float3 WorldView,
    float3 FlowTangent,
    float RoughnessCore,
    float RoughnessRim,
    float RimExp,
    float RimIntensity,
    float AnisoStrength,
    float ChromaShift,
    float Backscatter,
    out float3 OutSheenColor,
    out float OutSheenRoughness,
    out float3 OutTangent,
    out float OutAniso,
    out float OutRimMask,
    out float OutClothWeight)
{
    FDualLobeVelvetInputs Inputs;
    Inputs.BaseColor = InBaseColor;
    Inputs.RimColor = InRimColor;
    Inputs.WorldNormal = WorldNormal;
    Inputs.WorldView = WorldView;
    Inputs.TangentFlow = FlowTangent;
    Inputs.RoughnessCore = RoughnessCore;
    Inputs.RoughnessRim = RoughnessRim;
    Inputs.RimExponent = RimExp;
    Inputs.RimIntensity = RimIntensity;
    Inputs.AnisotropyStrength = AnisoStrength;
    Inputs.ChromaticShiftAmount = ChromaShift;
    Inputs.BackscatterIntensity = Backscatter;

    FDualLobeVelvetOutputs Outputs = CalculateDualLobeVelvet(Inputs);

    OutSheenColor = Outputs.SheenColor;
    OutSheenRoughness = Outputs.SheenRoughness;
    OutTangent = Outputs.AnisotropicTangent;
    OutAniso = Outputs.AnisotropyAmount;
    OutRimMask = Outputs.RimMask;
    OutClothWeight = Outputs.SubstrateClothWeight;

    return Outputs.CompositeBaseColor;
}

#endif // HAUTE_COUTURE_DUAL_LOBE_VELVET_HLSL
