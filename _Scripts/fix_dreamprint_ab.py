"""Fix the A/B isolation bug in Dreamprint stack.

The candidate PPV_Dreamprint_Candidate uses different outline+grade blendables
than the source PPV_NikkiDream, contaminating the A/B comparison.

Fix: Replace candidate's weighted_blendables with:
  1. MI_Outline_PremiumV3_Gameplay (weight=1.0) - match source outline
  2. M_PP_MeluColorGrade (weight=0.69) - match source grade
  3. MI_MelodiaInk_PortfolioHero (weight=1.0) - ink on top
"""
import unreal


def fix_dreamprint_candidate():
    """Fix the A/B isolation bug by replacing candidate's blendables."""
    
    CANDIDATE_PPV = "PPV_Dreamprint_Candidate"
    SOURCE_PPV = "PPV_NikkiDream"
    
    # The correct blendables matching source + ink
    new_blendables = [
        unreal.WeightedBlendable(1.0, unreal.EditorAssetLibrary.load_asset("/Game/EnvSandbox/Materials/PostProcess/Candidates/Profiles/MI_Outline_PremiumV3_Gameplay")),
        unreal.WeightedBlendable(0.69, unreal.EditorAssetLibrary.load_asset("/Game/Melodia/_PROJECT/04_Materials/PostProcess/Candidates/Profiles/M_PP_MeluColorGrade")),
        unreal.WeightedBlendable(1.0, unreal.EditorAssetLibrary.load_asset("/Game/Melodia/_PROJECT/04_Materials/PostProcess/Candidates/Profiles/MI_MelodiaInk_PortfolioHero")),
    ]
    
    # Find the candidate actor
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ppv = None
    for a in eas.get_all_level_actors() or []:
        if a.get_actor_label() == CANDIDATE_PPV:
            ppv = a
            break
    
    if ppv is None:
        print(f"FAIL: Could not find {CANDIDATE_PPV} in current level")
        return False
    
    # Set the weighted blendables
    settings = ppv.get_editor_property("settings")
    settings.set_editor_property("weighted_blendables", unreal.WeightedBlendables(new_blendables))
    ppv.set_editor_property("settings", settings)
    
    # Verify and print
    wb = ppv.get_editor_property("settings").get_editor_property("weighted_blendables")
    arr = wb.get_editor_property("array") or []
    names = []
    for e in arr:
        obj = e.get_editor_property("object")
        if obj:
            names.append(obj.get_name())
    
    print(f"SUCCESS: Updated {CANDIDATE_PPV} blendables:")
    for i, name in enumerate(names):
        print(f"  {i+1}. {name}")
    
    # Also verify source PPV for comparison
    src = None
    for a in eas.get_all_level_actors() or []:
        if a.get_actor_label() == SOURCE_PPV:
            src = a
            break
    
    if src:
        swb = src.get_editor_property("settings").get_editor_property("weighted_blendables")
        sarr = swb.get_editor_property("array") or []
        snames = []
        for e in sarr:
            obj = e.get_editor_property("object")
            if obj:
                snames.append(obj.get_name())
        print(f"\nSource {SOURCE_PPV} blendables: {snames}")
    
    # Save the level
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return True


if __name__ == "__main__":
    success = fix_dreamprint_candidate()
    exit(0 if success else 1)