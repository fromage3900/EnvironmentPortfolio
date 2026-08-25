import sys
sys.path.insert(0, 'C:/EnvironmentPortfolio/BS_GodFile/Tools')
from model_router import run_chat
result = run_chat('author', 'Given the Melodia wardrobe codebase: BP_MelusinaJRPGCharacter has MelodiaWardrobeComponent (MelodiaOutfitComponent re-hosted per Decision 044). UMelodiaWardrobeGachaSubsystem::PullOnce() spends 1 Golden token and calls Wardrobe->GrantCosmetic(PickedId, Result.GrantId). UMelodiaWardrobeComponent::EquipCosmetic(CosmeticId) calls Wardrobe->EquipCosmetic then EquipGarment(). Write a concrete C++ code snippet that connects PullOnce() -> GrantCosmetic -> EquipCosmetic in the gacha subsystem, and show the exact Blueprint event graph steps needed. Keep under 400 words, focus on actual code, not philosophy.')
print(result)