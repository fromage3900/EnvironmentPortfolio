import json
import re

def clean_text(text):
    if not isinstance(text, str):
        return text
    # Asset names
    text = re.sub(r'SK_[A-Za-z0-9_]+', 'gameplay mesh', text)
    text = re.sub(r'A_[A-Za-z0-9_]+', 'mocap animation', text)
    text = re.sub(r'L_WP_[A-Za-z0-9_]+', 'world map', text)
    text = re.sub(r'L_[A-Za-z0-9_]+', 'environment stage', text)
    text = re.sub(r'MI_[A-Za-z0-9_]+', 'material instance', text)
    text = re.sub(r'M_[A-Za-z0-9_]+', 'shader', text)
    text = re.sub(r'SM_[A-Za-z0-9_]+', 'mesh', text)
    text = re.sub(r'PCG_[A-Za-z0-9_]+', 'procedural graph', text)
    text = re.sub(r'WP_[A-Za-z0-9_]+', 'world map', text)
    # Ports
    text = re.sub(r':9876', '', text)
    text = re.sub(r':8080', '', text)
    # QA/Internal
    text = re.sub(r'Alembic 1-240', 'Alembic cache', text)
    text = re.sub(r'scalp Z-offsets?', 'hair alignment', text)
    text = re.sub(r'owner-lock worked;?', '', text)
    text = re.sub(r'A1 stock battle still open', '', text)
    text = re.sub(r'A1 stock battle is still open', '', text)
    text = re.sub(r'A1 battle open', '', text)
    return text

def process_dict(d):
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = clean_text(v)
        elif isinstance(v, dict):
            process_dict(v)
        elif isinstance(v, list):
            process_list(v)

def process_list(l):
    for i in range(len(l)):
        if isinstance(l[i], str):
            l[i] = clean_text(l[i])
        elif isinstance(l[i], dict):
            process_dict(l[i])
        elif isinstance(l[i], list):
            process_list(l[i])

with open(r'C:\EnvironmentPortfolio\my-site-clean\content\site-copy.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

process_dict(data)

with open(r'C:\EnvironmentPortfolio\my-site-clean\content\site-copy.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

import glob
import os

for html_file in glob.glob(r'C:\EnvironmentPortfolio\my-site-clean\wix\*.html'):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = clean_text(content)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)

print('Done cleaning.')
