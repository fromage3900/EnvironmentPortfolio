import os
import json

base = r'C:\EnvironmentPortfolio\BS_GodFile\Plugins\MelodiaWardrobe\Content\MelodiaWardrobe\Drafts'

# 6 remaining cosmetics to reach 38 gacha-derived + 1 demo = 39 total
remaining = [
    'Cos_Special_Melusina_Event9',
    'Cos_Special_Melusina_Event10', 
    'Cos_Special_Melusina_Event11',
    'Cos_Special_Melusina_Event12', 
    'Cos_Special_Melusina_Event13',
    'Cos_Special_Melusina_Event14',
]

for name in remaining:
    data = {
        'CosmeticId': name,
        'Slot': 'Body',
        'Rarity': 'Common',
        'SourceDraftPath': f'MelodiaWardrobe/Drafts/{name}'
    }
    filepath = os.path.join(base, f'{name}.json')
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'Created {filepath}')

print(f'\nTotal: Now {32 + 6} cosmetic JSON draft files in the Drafts folder.')