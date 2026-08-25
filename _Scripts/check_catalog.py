import json, os

# Read the material catalog
catalog_path = 'C:/EnvironmentPortfolio/BS_GodFile/Docs/T3D_Baseline/material_catalog.json'
with open(catalog_path, 'r') as f:
    catalog = json.load(f)

print('Material catalog total assets: ' + str(catalog.get('total_nodes', '?')) + ' nodes, ' + str(catalog.get('total_payload_bytes', '?')) + ' bytes')
print()

# List families
for family_name, family_data in catalog.get('families', {}).items():
    assets = family_data.get('assets', [])
    print('Family: ' + family_name)
    print('  Assets: ' + str(len(assets)))
    for a in assets[:3]:  # Show first 3
        print('    ' + a['name'] + ': sha256=' + a['sha256'][:16] + '... payload=' + str(a['payload_bytes']) + ' bytes')
    if len(assets) > 3:
        print('    ... and ' + str(len(assets)-3) + ' more')
    print()