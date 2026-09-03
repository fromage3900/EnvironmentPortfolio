import base64, io, json
from pathlib import Path
from PIL import Image

tile_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Melodia_Tilework")
lookdev_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Lookdev_Suites")

suites_meta = [
    {
        "id": "T_Melusina_BaroqueAquatic_MosaicTile",
        "title": "Melusina Baroque Aquatic Mosaic",
        "category": "Architectural Tilework",
        "desc": "Majolica glazed ceramic mosaic featuring aquatic turquoise & lapis lazuli watercolor washes, gilded 24k gold filigree borders, and central mother-of-pearl cabochons.",
        "dir": tile_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_WatercolourWave_Parquet",
        "title": "Melusina Watercolour Wave Parquet",
        "category": "Architectural Flooring",
        "desc": "Handcrafted French parquet marquetry with undulating acoustic wave bands in stained cyan pearwood, ebony navy, rose quartz satinwood, mother-of-pearl planks, and brass stave dividers.",
        "dir": tile_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Melusina_CathedralPearl_MarbleTile",
        "title": "Melusina Cathedral Pearl Marble",
        "category": "Architectural Tilework",
        "desc": "Translucent Carrara marble slabs with pastel violet/teal watercolor veining, geometric octagonal tessellations, gold leaf inlays, and pearlized mortar.",
        "dir": tile_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Lookdev_IridescentSilkVelvet",
        "title": "Iridescent Silk Velvet",
        "category": "Haute-Couture Lookdev",
        "desc": "High-fashion Infinity Nikki dress fabric with watercolor-dipped cyan-to-lilac duchess satin weave, fine warp/weft micro-normal, and soft Fresnel sheen.",
        "dir": lookdev_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Lookdev_GildedAquaticFiligree_Trim",
        "title": "Gilded Aquatic Filigree Trim",
        "category": "Prop & Ornament Lookdev",
        "desc": "Baroque cast 24k gold filigree trim with ocean wave volutes, vitreous sea-glass enamel cloisons, and subtle verdigris weathering in micro-crevices.",
        "dir": lookdev_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Lookdev_WatercolorStudio_CalibPlaster",
        "title": "Watercolor Studio Calibration Plaster",
        "category": "Lighting & Shader Calibration",
        "desc": "Clean studio lookdev surface featuring 300lb cold-press watercolor paper tooth, neutral 80% reflectance plaster, and stepped 8-patch roughness/reflectance calibration ladder.",
        "dir": lookdev_dir,
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
        img_path = s["dir"] / f"{s['id']}_{ch}.png"
        if img_path.exists():
            with Image.open(img_path) as img:
                thumb = img.resize((320, 320), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=88)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                suite_data["maps"][ch] = f"data:image/jpeg;base64,{b64}"
    catalog.append(suite_data)

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\melodia_pbr_lookdev_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Melodia PBR Texture Suites & Lookdev Showcase</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #0d0f14);
      color: var(--foreground, #e8eaed);
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
    .ch-BC {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
    .ch-N {{ background: rgba(139, 92, 246, 0.2); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.4); }}
    .ch-ORM {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .ch-H {{ background: rgba(6, 182, 212, 0.2); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.4); }}
    .ch-AO {{ background: rgba(100, 116, 139, 0.2); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.4); }}
    .ch-R {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .ch-M {{ background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4); }}
    .ch-Sheen {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.5);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#151821)] border border-[var(--border,#262a36)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              PBR Standards Compliant (2048x2048 POT)
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              Infinity Nikki &amp; Baroque Aesthetic
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight">Melodia &amp; Lookdev PBR Master Suites</h1>
          <p class="text-sm text-[var(--muted-foreground,#9aa0a6)] mt-1">
            6 Full Material Suites · 44 Discrete &amp; Packed Maps · Direct Tangent-Space Normals &amp; ORM Packing
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--primary,#3b82f6)] text-white shadow-sm transition">All Suites (6)</button>
          <button onclick="filterCategory('Tilework')" id="btn-tilework" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#151821)] border border-[var(--border,#262a36)] text-[var(--muted-foreground,#9aa0a6)] hover:text-white transition">Melusina Tilework (3)</button>
          <button onclick="filterCategory('Lookdev')" id="btn-lookdev" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#151821)] border border-[var(--border,#262a36)] text-[var(--muted-foreground,#9aa0a6)] hover:text-white transition">Lookdev &amp; Fabrics (3)</button>
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
        if (currentFilter === 'Tilework') return s.category.includes('Tilework') || s.category.includes('Flooring');
        if (currentFilter === 'Lookdev') return s.category.includes('Lookdev') || s.category.includes('Calibration');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#151821)] border border-[var(--border,#262a36)] rounded-2xl p-5 shadow-sm space-y-4';
        
        let mapTabs = '';
        let mapImages = '';
        const channels = Object.keys(s.maps);
        
        channels.forEach((ch, idx) => {{
          const isFirst = idx === 0;
          mapTabs += `
            <button onclick="switchTab('${{s.id}}', '${{ch}}')" id="tab-${{s.id}}-${{ch}}" class="channel-badge ch-${{ch}} ${{isFirst ? 'ring-2 ring-white/50' : 'opacity-70 hover:opacity-100'}} transition cursor-pointer">
              ${{ch}}
            </button>
          `;
          mapImages += `
            <div id="img-${{s.id}}-${{ch}}" class="relative aspect-square w-full rounded-xl overflow-hidden bg-black/40 border border-white/5 ${{isFirst ? '' : 'hidden'}}">
              <img src="${{s.maps[ch]}}" alt="${{s.id}} ${{ch}}" class="w-full h-full object-cover">
              <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/70 backdrop-blur-sm text-[10px] font-mono text-white/90">
                ${{s.id}}_${{ch}}.png (2048x2048)
              </div>
            </div>
          `;
        }});

        card.innerHTML = `
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#262a36)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-[var(--primary,#60a5fa)] uppercase tracking-wider">${{s.category}}</span>
              <h3 class="text-lg font-bold text-white tracking-tight mt-0.5">${{s.title}}</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-md bg-white/5 border border-white/10 font-mono text-white/80">
              ${{channels.length}} Channels
            </span>
          </div>
          <p class="text-xs text-[var(--muted-foreground,#9aa0a6)] leading-relaxed">${{s.desc}}</p>
          
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
            tab.classList.add('ring-2', 'ring-white/50');
            tab.classList.remove('opacity-70');
          }} else {{
            img.classList.add('hidden');
            tab.classList.remove('ring-2', 'ring-white/50');
            tab.classList.add('opacity-70');
          }}
        }}
      }});
    }}

    function filterCategory(cat) {{
      currentFilter = cat;
      ['all', 'tilework', 'lookdev'].forEach(c => {{
        const btn = document.getElementById(`btn-${{c}}`);
        if (btn) {{
          if (c.toLowerCase() === cat.toLowerCase()) {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--primary,#3b82f6)] text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#151821)] border border-[var(--border,#262a36)] text-[var(--muted-foreground,#9aa0a6)] hover:text-white transition';
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
print(f"Generated HTML showcase: {out_html} ({out_html.stat().st_size} bytes)")
