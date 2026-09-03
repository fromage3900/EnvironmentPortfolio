import base64, io, json
from pathlib import Path
from PIL import Image

cathedral_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Grand_Roman_Cathedral_Tiles")

suites_meta = [
    {
        "id": "T_Cathedral_Cosmati_QuincunxGuilloche",
        "title": "Cosmatesque Quincunx Guilloche Pavement",
        "category": "Imperial Cosmati Mosaic",
        "desc": "Grand Roman Cosmati pavement featuring a monumental Imperial Porphyry central Rota, 4 Verde Antico corner disks, and intertwining braided guilloche ribbons with Byzantine gold glass smalti.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Cathedral_OpusSectile_ImperialPorphyry",
        "title": "Opus Sectile 8-Pointed Star Slabs",
        "category": "Monumental Stone Inlay",
        "desc": "Geometric Opus Sectile slabwork featuring Imperial Porphyry, Giallo Antico golden marble, and Pavonazzo violet-veined white marble cut into 8-pointed star hexagrams and lozenges.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Cathedral_BasilicaNave_BookmatchedCipollino",
        "title": "Bookmatched Cipollino Verde Nave Slabs",
        "category": "Basilica Nave Slabwork",
        "desc": "Grand 2-meter bookmatched slabs of flowing wave-veined Cipollino Verde marble flanked by black-and-gold Portoro borders with aged flush bronze divider rods.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Cathedral_ByzantineApse_GildedSmalti",
        "title": "Byzantine Apse 24k Gold Glass Smalti",
        "category": "Cathedral Vault & Apse Smalti",
        "desc": "Authentic Byzantine gold glass smalti tesserae with hand-cut micro cubes and 3D rotational facet tilts reflecting light at varied angles, bordered by cobalt lapis smalti.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Cathedral_Baptistery_TwelveFoldRosace",
        "title": "Baptistery 12-Fold Harmonic Rosace",
        "category": "Sacred Geometry Rosette",
        "desc": "Sacred 12-pointed harmonic rosette in white Carrara marble, blood-red jasper, lapis lazuli, and mother-of-pearl inlays with gilded brass frame ribbons.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Cathedral_CloisterWalk_WornTravertine",
        "title": "Cloister Walk Aged Travertine & Majolica",
        "category": "Historic Monastic Cloister",
        "desc": "Historic Roman travertine slabs with characteristic pitted cavities, micro-fossils, hand-hewn surface undulation, and corner majolica cross inlays.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    }
]

catalog = []
for s in suites_meta:
    suite_data = {
        "id": s["id"],
        "title": s["title"],
        "category": s["category"],
        "desc": s["desc"],
        "maps": {}
    }
    for ch in s["channels"]:
        img_path = cathedral_dir / f"{s['id']}_{ch}.png"
        if img_path.exists():
            with Image.open(img_path) as img:
                thumb = img.resize((320, 320), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=88)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                suite_data["maps"][ch] = f"data:image/jpeg;base64,{b64}"
    catalog.append(suite_data)

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\grand_roman_cathedral_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grand Roman Cathedral &amp; Cosmati Pavement PBR Suites</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #08090e);
      color: var(--foreground, #e5e7eb);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    .channel-badge {{
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
    }}
    .ch-BC {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .ch-N {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .ch-ORM {{ background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }}
    .ch-H {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
    .ch-AO {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}
    .ch-R {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }}
    .ch-M {{ background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }}
    .ch-Sheen {{ background: rgba(216, 180, 254, 0.25); color: #f3e8ff; border: 1px solid rgba(216, 180, 254, 0.5); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px -10px rgba(245, 158, 11, 0.25);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#10121a)] border border-[var(--border,#202433)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Imperial Roman &amp; Cosmati Heritage
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
              Egyptian Porphyry &amp; Byzantine Smalti
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight text-white">Grand Roman Cathedral &amp; Cosmati Pavement PBR Suites</h1>
          <p class="text-sm text-[var(--muted-foreground,#9ca3af)] mt-1">
            6 Monumental Cathedral Suites · 45 Master Maps @ 2048x2048 POT · Opus Sectile, Quincunx Guilloche, Bookmatched Cipollino &amp; 24k Smalti
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-amber-600 text-white shadow-sm transition">All Suites (6)</button>
          <button onclick="filterCategory('Cosmati')" id="btn-cosmati" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#10121a)] border border-[var(--border,#202433)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition">Cosmati &amp; Smalti (3)</button>
          <button onclick="filterCategory('Slab')" id="btn-slab" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#10121a)] border border-[var(--border,#202433)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition">Slabwork &amp; Rosaces (3)</button>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div id="suites-container" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Rendered by JS -->
    </div>

  </div>

  <script>
    const catalog = {catalog_json};
    let currentFilter = 'All';

    function renderSuites() {{
      const container = document.getElementById('suites-container');
      container.innerHTML = '';

      const filtered = catalog.filter(s => {{
        if (currentFilter === 'All') return true;
        if (currentFilter === 'Cosmati') return s.category.includes('Cosmati') || s.category.includes('Smalti') || s.category.includes('Inlay');
        if (currentFilter === 'Slab') return s.category.includes('Slabwork') || s.category.includes('Rosette') || s.category.includes('Cloister');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#10121a)] border border-[var(--border,#202433)] rounded-2xl p-5 shadow-sm space-y-4';
        
        let mapTabs = '';
        let mapImages = '';
        const channels = Object.keys(s.maps);
        
        channels.forEach((ch, idx) => {{
          const isFirst = idx === 0;
          mapTabs += `
            <button onclick="switchTab('${{s.id}}', '${{ch}}')" id="tab-${{s.id}}-${{ch}}" class="channel-badge ch-${{ch}} ${{isFirst ? 'ring-2 ring-amber-400/80' : 'opacity-70 hover:opacity-100'}} transition cursor-pointer">
              ${{ch}}
            </button>
          `;
          mapImages += `
            <div id="img-${{s.id}}-${{ch}}" class="relative aspect-square w-full rounded-xl overflow-hidden bg-black/60 border border-white/5 ${{isFirst ? '' : 'hidden'}}">
              <img src="${{s.maps[ch]}}" alt="${{s.id}} ${{ch}}" class="w-full h-full object-cover">
              <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/80 backdrop-blur-sm text-[10px] font-mono text-white/90">
                ${{s.id}}_${{ch}}.png (2048x2048)
              </div>
            </div>
          `;
        }});

        card.innerHTML = `
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#202433)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">${{s.category}}</span>
              <h3 class="text-lg font-bold text-white tracking-tight mt-0.5">${{s.title}}</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 font-mono text-amber-200">
              ${{channels.length}} Channels
            </span>
          </div>
          <p class="text-xs text-[var(--muted-foreground,#9ca3af)] leading-relaxed">${{s.desc}}</p>
          
          <div class="flex flex-wrap gap-1.5 pt-1">
            ${{mapTabs}}
          </div>
          
          <div class="pt-2">
            ${{mapImages}}
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function switchTab(suiteId, channel) {{
      const suite = catalog.find(s => s.id === suiteId);
      if (!suite) return;
      Object.keys(suite.maps).forEach(ch => {{
        const img = document.getElementById(`img-${{suiteId}}-${{ch}}`);
        const tab = document.getElementById(`tab-${{suiteId}}-${{ch}}`);
        if (img && tab) {{
          if (ch === channel) {{
            img.classList.remove('hidden');
            tab.classList.add('ring-2', 'ring-amber-400/80');
            tab.classList.remove('opacity-70');
          }} else {{
            img.classList.add('hidden');
            tab.classList.remove('ring-2', 'ring-amber-400/80');
            tab.classList.add('opacity-70');
          }}
        }}
      }});
    }}

    function filterCategory(cat) {{
      currentFilter = cat;
      ['all', 'cosmati', 'slab'].forEach(c => {{
        const btn = document.getElementById(`btn-${{c}}`);
        if (btn) {{
          if (c.toLowerCase() === cat.toLowerCase()) {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-amber-600 text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#10121a)] border border-[var(--border,#202433)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition';
          }}
        }}
      }});
      renderSuites();
    }}

    renderSuites();
  </script>
</body>
</html>
"""

out_html.write_text(html_content, encoding="utf-8")
print(f"Generated Grand Roman Cathedral HTML showcase: {out_html} ({out_html.stat().st_size} bytes)")
