// =============================================================================
// Infinity Nikki Haute-Couture Asset Elevation Ecosystem
// File: BullionMicroRelief.hlsl
// Description: Tangent-space Parallax Occlusion Mapping (POM) for raised metallic
//              embroidery, dynamic-step raymarching, secant linear refinement,
//              contact self-shadowing micro-cavity occlusion, and height-blended
//              conductor/dielectric PBR parameter transitions.
// Target: Unreal Engine 5.3+ Substrate Material Framework / SM6 HLSL Custom Expression
// =============================================================================

#ifndef HAUTE_COUTURE_BULLION_MICRO_RELIEF_HLSL
#define HAUTE_COUTURE_BULLION_MICRO_RELIEF_HLSL

// Struct holding inputs for Bullion Parallax Occlusion & Micro-Relief calculation
struct FBullionPOMInputs
{
    float2 UVs;                   // Base texture coordinates
    float3 TangentView;           // View vector in tangent space (X, Y, Z)
    float3 TangentLight;          // Light vector in tangent space (X, Y, Z)
    float HeightScale;            // Maximum parallax depth offset [0.0, 0.15]
    float MinSteps;               // Minimum POM raymarch steps (facing angle) [4.0, 32.0]
    float MaxSteps;               // Maximum POM raymarch steps (grazing angle) [16.0, 128.0]
    float ShadowSteps;            // Contact shadow raymarch step count [0.0, 32.0]
    float ShadowHardness;         // Hardness of micro-cavity contact shadows [1.0, 10.0]
    float HeightThreshold;        // Cutoff elevation separating bullion from backing fabric [0.0, 1.0]
    float BlendContrast;          // Edge sharpness of the bullion-to-fabric transition [1.0, 32.0]
    float BullionMetallic;        // Metallic value of gold bullion coils (1.0)
    float BullionRoughness;       // Micro-roughness of metallic bullion threads (0.22)
    float FabricRoughness;        // Micro-roughness of backing fabric (0.82)
};

// Struct holding outputs for Substrate BSDF Slab blending and UV displacement
struct FBullionPOMOutputs
{
    float2 DisplacedUV;           // Parallax-shifted UV coordinates for sampling PBR textures
    float ParallaxHeight;         // Refined surface elevation at the displaced UV [0.0, 1.0]
    float SelfShadowAO;           // Micro-cavity contact self-shadowing factor [0.0, 1.0]
    float BullionMask;            // Anti-aliased binary mask (1.0 = Bullion, 0.0 = Fabric)
    float BlendedRoughness;       // Composite roughness blended across height relief
    float BlendedMetallic;        // Composite metallic blended across height relief
    float3 ContactCavityNormal;   // Tangent-space normal perturbed by micro-cavity height gradient
};

/**
 * Executes dynamic-step Parallax Occlusion Mapping (POM) and contact self-shadowing.
 *
 * In UE5 Custom Material Expressions, texture sampling is passed via Texture2D and SamplerState.
 * When included in standalone HLSL / Engine shaders, standard sample macros are used.
 */
#define SAMPLE_HEIGHT_LOD(tex, samp, uv) tex.SampleLevel(samp, uv, 0).r

#define EXECUTE_BULLION_POM(TexHeight, TexSampler, In, Out) \
{ \
    float3 V = normalize(In.TangentView); \
    float absVz = clamp(abs(V.z), 0.001, 1.0); \
    \
    /* 1. Dynamic Step Allocation */ \
    float numSteps = lerp(In.MaxSteps, In.MinSteps, absVz); \
    float stepSize = 1.0 / max(numSteps, 1.0); \
    \
    /* Tangent space ray offset vector with grazing safety guard */ \
    float2 maxOffset = -V.xy * (In.HeightScale / max(absVz, 0.05)); \
    float2 stepUV = maxOffset * stepSize; \
    \
    float currLayerHeight = 0.0; \
    float2 currUV = In.UVs; \
    float currHeightMapVal = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, currUV); \
    \
    /* 2. POM Raymarching Loop */ \
    [loop] \
    for (int i = 0; i < int(numSteps); ++i) \
    { \
        if (currLayerHeight >= (1.0 - currHeightMapVal)) break; \
        currUV += stepUV; \
        currLayerHeight += stepSize; \
        currHeightMapVal = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, currUV); \
    } \
    \
    /* 3. Secant Linear Interpolation Refinement */ \
    float2 prevUV = currUV - stepUV; \
    float prevLayerHeight = currLayerHeight - stepSize; \
    float prevHeightMapVal = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, prevUV); \
    \
    float nextH = (1.0 - currHeightMapVal) - currLayerHeight; \
    float prevH = (1.0 - prevHeightMapVal) - prevLayerHeight; \
    float weight = nextH / max(nextH - prevH, 0.00001); \
    float2 finalUV = lerp(currUV, prevUV, clamp(weight, 0.0, 1.0)); \
    float finalHeight = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, finalUV); \
    \
    /* 4. Contact Self-Shadowing Loop */ \
    float shadow = 1.0; \
    if (In.ShadowSteps > 0.5) \
    { \
        float3 L = normalize(In.TangentLight); \
        if (L.z > 0.0) \
        { \
            float shadowStepSize = finalHeight / max(In.ShadowSteps, 1.0); \
            float2 shadowStepUV = L.xy * (In.HeightScale / max(L.z, 0.05)) / max(In.ShadowSteps, 1.0); \
            float currShadowHeight = (1.0 - finalHeight) - shadowStepSize; \
            float2 currShadowUV = finalUV + shadowStepUV; \
            \
            [loop] \
            for (int j = 0; j < int(In.ShadowSteps); ++j) \
            { \
                float sampledH = 1.0 - SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, currShadowUV); \
                if (sampledH < currShadowHeight) \
                { \
                    shadow -= (currShadowHeight - sampledH) * In.ShadowHardness; \
                } \
                currShadowHeight -= shadowStepSize; \
                currShadowUV += shadowStepUV; \
            } \
            shadow = clamp(shadow, 0.0, 1.0); \
        } \
    } \
    \
    /* 5. Bullion vs Fabric Mask & Material Blending */ \
    float bullionMask = clamp((finalHeight - In.HeightThreshold) * In.BlendContrast + 0.5, 0.0, 1.0); \
    float blendedRough = lerp(In.FabricRoughness, In.BullionRoughness, bullionMask); \
    float blendedMetal = lerp(0.0, In.BullionMetallic, bullionMask); \
    \
    /* 6. Cavity Normal Gradient Derivation */ \
    float deltaUV = 0.001; \
    float hL = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, finalUV - float2(deltaUV, 0.0)); \
    float hR = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, finalUV + float2(deltaUV, 0.0)); \
    float hD = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, finalUV - float2(0.0, deltaUV)); \
    float hU = SAMPLE_HEIGHT_LOD(TexHeight, TexSampler, finalUV + float2(0.0, deltaUV)); \
    float3 cavityN = normalize(float3((hL - hR) * In.HeightScale * 10.0, (hD - hU) * In.HeightScale * 10.0, 1.0)); \
    \
    Out.DisplacedUV = finalUV; \
    Out.ParallaxHeight = finalHeight; \
    Out.SelfShadowAO = shadow; \
    Out.BullionMask = bullionMask; \
    Out.BlendedRoughness = blendedRough; \
    Out.BlendedMetallic = blendedMetal; \
    Out.ContactCavityNormal = cavityN; \
}

/**
 * UE5 Custom Material Node Entry Point: CalculateParallaxMicroRelief
 *
 * Wire into Unreal Engine 5 Custom HLSL Material Expression with matching pin names.
 */
float4 CalculateParallaxMicroRelief(
    Texture2D TexHeight,
    SamplerState TexHeightSampler,
    float2 InUV,
    float3 TangentView,
    float3 TangentLight,
    float HeightScale,
    float MinSteps,
    float MaxSteps,
    float ShadowSteps,
    float ShadowHardness,
    float HeightThresh,
    float BlendContrast,
    float BullionMetal,
    float BullionRough,
    float FabricRough,
    out float2 OutDisplacedUV,
    out float OutHeight,
    out float OutShadow,
    out float OutBullionMask,
    out float OutRoughness,
    out float OutMetallic,
    out float3 OutCavityNormal)
{
    FBullionPOMInputs Inputs;
    Inputs.UVs = InUV;
    Inputs.TangentView = TangentView;
    Inputs.TangentLight = TangentLight;
    Inputs.HeightScale = HeightScale;
    Inputs.MinSteps = MinSteps;
    Inputs.MaxSteps = MaxSteps;
    Inputs.ShadowSteps = ShadowSteps;
    Inputs.ShadowHardness = ShadowHardness;
    Inputs.HeightThreshold = HeightThresh;
    Inputs.BlendContrast = BlendContrast;
    Inputs.BullionMetallic = BullionMetal;
    Inputs.BullionRoughness = BullionRough;
    Inputs.FabricRoughness = FabricRough;

    FBullionPOMOutputs Outputs;
    EXECUTE_BULLION_POM(TexHeight, TexHeightSampler, Inputs, Outputs);

    OutDisplacedUV = Outputs.DisplacedUV;
    OutHeight = Outputs.ParallaxHeight;
    OutShadow = Outputs.SelfShadowAO;
    OutBullionMask = Outputs.BullionMask;
    OutRoughness = Outputs.BlendedRoughness;
    OutMetallic = Outputs.BlendedMetallic;
    OutCavityNormal = Outputs.ContactCavityNormal;

    return float4(Outputs.DisplacedUV, Outputs.ParallaxHeight, Outputs.SelfShadowAO);
}

#endif // HAUTE_COUTURE_BULLION_MICRO_RELIEF_HLSL
