#!/usr/bin/env python3
import unreal

hero_path = "/Game/EnvSandbox/Materials/ToonProfiles/TP_Hero"
melusina_path = "/Game/EnvSandbox/Materials/ToonProfiles/TP_Melusina"

if not unreal.EditorAssetLibrary.does_asset_exist(hero_path):
    print("ERROR: TP_Hero not found")
    exit(1)

tp_hero = unreal.EditorAssetLibrary.load_asset(hero_path)
if not tp_hero:
    print("ERROR: Failed to load TP_Hero")
    exit(1)

print("Loaded TP_Hero")

for prop in tp_hero.get_class().get_properties():
    try:
        value = prop.get_value_in_object(tp_hero)
        print(prop.get_name() + ": " + str(value))
    except Exception as e:
        print(prop.get_name() + ": ERROR: " + str(e))

success = unreal.EditorAssetLibrary.duplicate_asset(hero_path, melusina_path)
if not success:
    print("ERROR: Failed to duplicate")
    exit(1)

print("Duplicated")

tp_melusina = unreal.EditorAssetLibrary.load_asset(melusina_path)
if not tp_melusina:
    print("ERROR: Failed to load TP_Melusina")
    exit(1)

try:
    tp_melusina.set_editor_property("IndirectDiffuseIntensity", 0.3)
    tp_melusina.set_editor_property("IndirectSpecularIntensity", 0.3)
    tp_melusina.set_editor_property("ShadowingExtinction", 0.3)
    print("Set scalar properties")
except Exception as e:
    print("Error setting scalars: " + str(e))

try:
    import math
    def srgb_to_linear(c):
        c = c / 255.0
        if c <= 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    r = srgb_to_linear(53)
    g = srgb_to_linear(45)
    b = srgb_to_linear(64)
    shadow_color = unreal.LinearColor(r, g, b, 1.0)
    warm_bias = unreal.LinearColor(1.1, 1.05, 1.0, 1.0)
    dr = tp_melusina.get_editor_property("DiffuseRamp")
    if dr:
        print("DiffuseRamp: " + str(dr))
        dr.empty()
        dr.add_key(0.0, shadow_color)
        dr.add_key(0.3, unreal.LinearColor(1,1,1,1))
        dr.add_key(1.0, warm_bias)
    sr = tp_melusina.get_editor_property("SpecularRamp")
    if sr:
        print("SpecularRamp: " + str(sr))
        sr.empty()
        sr.add_key(0.9, unreal.LinearColor(1,1,1,1))
except Exception as e:
    print("Error setting ramps: " + str(e))

hatch_path = "/Game/EnvSandbox/Materials/ToonProfiles/T_HatchPattern"
if unreal.EditorAssetLibrary.does_asset_exist(hatch_path):
    hatch = unreal.EditorAssetLibrary.load_asset(hatch_path)
    if hatch:
        try:
            tp_melusina.set_editor_property("ShadowHatchingPattern", hatch)
            print("Set hatch pattern")
        except Exception as e:
            print("Error setting hatch: " + str(e))
else:
    print("T_HatchPattern not found, skipping")

unreal.EditorAssetLibrary.save_asset(melusina_path)
print("SUCCESS: TP_Melusina saved")
