import json

with open(r'C:\EnvironmentPortfolio\my-site-clean\content\site-copy.json', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Alembic 1-240', 'Alembic cache')
text = text.replace('SK_MelusinaHair', 'hero hair mesh')
text = text.replace('A_Melusina_Idle_Mocap_RootX', 'hero idle animation')
text = text.replace('L_MelusinaMorning', 'morning stage')
text = text.replace('L_KaleidoNave', 'cathedral stage')
text = text.replace('MI_Show_CosmicNebula', 'cosmic nebula material')
text = text.replace('T_CosmicNebula_N', 'nebula normal map')
text = text.replace('T_CosmicNebula_R', 'nebula roughness map')
text = text.replace('M_Master_Toon_Universal', 'universal toon shader')
text = text.replace('MI_ZenTrim_FlowersLots', 'zen trim material')
text = text.replace('F_Melodia_UI', 'UI font library')
text = text.replace(':9876', '')
text = text.replace('L_MaterialPreview_Studio', 'material preview stage')

with open(r'C:\EnvironmentPortfolio\my-site-clean\content\site-copy.json', 'w', encoding='utf-8') as f:
    f.write(text)

import glob
for html_file in glob.glob(r'C:\EnvironmentPortfolio\my-site-clean\wix\*.html'):
    with open(html_file, 'r', encoding='utf-8') as f:
        t = f.read()
    t = t.replace('Alembic 1-240', 'Alembic cache')
    t = t.replace('SK_MelusinaHair', 'hero hair mesh')
    t = t.replace('A_Melusina_Idle_Mocap_RootX', 'hero idle animation')
    t = t.replace('L_MelusinaMorning', 'morning stage')
    t = t.replace('L_KaleidoNave', 'cathedral stage')
    t = t.replace('MI_Show_CosmicNebula', 'cosmic nebula material')
    t = t.replace('T_CosmicNebula_N', 'nebula normal map')
    t = t.replace('T_CosmicNebula_R', 'nebula roughness map')
    t = t.replace('M_Master_Toon_Universal', 'universal toon shader')
    t = t.replace('MI_ZenTrim_FlowersLots', 'zen trim material')
    t = t.replace('F_Melodia_UI', 'UI font library')
    t = t.replace(':9876', '')
    t = t.replace('L_MaterialPreview_Studio', 'material preview stage')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(t)

