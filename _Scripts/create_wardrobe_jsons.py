import os
import json

base = r'C:\EnvironmentPortfolio\BS_GodFile\Plugins\MelodiaWardrobe\Content\MelodiaWardrobe\Drafts'
os.makedirs(base, exist_ok=True)

# 38 remaining cosmetics after Cos_Dress_Melusina
cosmetics = [
    # Dress variants
    'Cos_Dress_Melusina_Noble', 'Cos_Dress_Melusina_Royal', 'Cos_Dress_Melusina_Ethereal', 'Cos_Dress_Melusina_Elemental',
    # Skirt variants
    'Cos_Skirt_Melusina_Sailor', 'Cos_Skirt_Melusina_Gothic', 'Cos_Skirt_Melusina_Classical', 'Cos_Skirt_Melusina_Fantasy',
    # Top variants  
    'Cos_Top_Melusina_Blouse', 'Cos_Top_Melusina_Corset', 'Cos_Top_Melusina_Sweater', 'Cos_Top_Melusina_Vest',
    # Accessory variants
    'Cos_Accessory_Melusina_Hat', 'Cos_Accessory_Melusina_Ribbon', 'Cos_Accessory_Melusina_Wings', 'Cos_Accessory_Melusina_Headband',
    # Footwear variants
    'Cos_Footwear_Melusina_Shoes', 'Cos_Footwear_Melusina_Boot', 'Cos_Footwear_Melusina_Sandals', 'Cos_Footwear_Melusina_Slippers',
    # Outerwear variants
    'Cos_Outerwear_Melusina_Cloak', 'Cos_Outerwear_Melusina_Jackets', 'Cos_Outerwear_Melusina_Coat', 'Cos_Outerwear_Melusina_Vestment',
    # Special variants
    'Cos_Special_Melusina_Event1', 'Cos_Special_Melusina_Event2', 'Cos_Special_Melusina_Event3', 'Cos_Special_Melusina_Event4',
    'Cos_Special_Melusina_Event5', 'Cos_Special_Melusina_Event6', 'Cos_Special_Melusina_Event7', 'Cos_Special_Melusina_Event8',
]

for i, name in enumerate(cosmetics):
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

print(f'\nTotal: {len(cosmetics)} cosmetic JSON draft files created.')
PYEOF