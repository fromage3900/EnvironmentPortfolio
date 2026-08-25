# Water V7 ray-tracing fix

## Diagnosis

`M_Water_Master_Grand_v7` was configured as `MSM_SingleLayerWater` and used `SubstrateSingleLayerWaterBSDF`, but it had no legacy `SingleLayerWaterMaterialOutput` node. UE 5.8's ray-tracing water shader still references the generated functions `GetSingleLayerWaterMaterialOutput0`, `1`, and `2`. Because the legacy output node was absent, those functions were not generated and the SM6 material fell back to the default material.

## Applied change

Only V7 was edited. V6 remains the working rollback/reference material.

Added `MaterialExpressionSingleLayerWaterMaterialOutput_0` to:

`/Game/EnvSandbox/Materials/Masters/M_Water_Master_Grand_v7`

Connected the existing optical material function `/Game/EnvSandbox/Materials/Masters/M_Water_Master_Grand_v7` node `MaterialExpressionMaterialFunctionCall_9`:

- `Scattering` -> `ScatteringCoefficients`
- `Absorption` -> `AbsorptionCoefficients`
- `PhaseGOut` -> `PhaseG`

The existing Substrate water BSDF and its `FrontMaterial` connection were preserved.

## Verification

- V7 saved successfully.
- V7 material recompile returned `recompiled`.
- A fresh search found no new matching `Failed to compile Material ... M_Water_Master_Grand_v7` entry after the fix.
- Validator warnings remain for disconnected optional branches (`SceneDepth`, one texture sample, and a depth-fade chain). These are separate from the missing legacy output functions and were not removed.

## If the error returns

Check the newest shader log timestamp, not the historical entry in the existing log. Confirm the three legacy connections still exist before changing shading model or disabling ray tracing. Do not modify V6 as a first response.
