import base64, io, json
from pathlib import Path
from PIL import Image

houdini_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Houdini_Vibrant_PBR_Suites")

suites_meta = [
    {
        "id": "T_Houdini_DifferentialOrganza_NeonHydrangea",
        "title": "Differential Growth Neon Hydrangea Organza",
        "category": "SOP Curve Growth & Curl Normals",
        "desc": "Differential curve growth ruffle petals with 3D tangent curl-flow normals in electric Neon Hydrangea Blue, Vivid Magenta Pink, Deep Iris Violet, and cyan sheen.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Houdini_ReactionDiffusion_AmethystLapis",
        "title": "Reaction-Diffusion Amethyst & Lapis Cloisons",
        "category": "VEX Gray-Scott Enamel",
        "desc": "Gray-Scott reaction-diffusion organic labyrinth in Royal Amethyst Purple, Deep Lapis Lazuli, Hot Fuchsia Pink, and 24k rose-gold dividing ridges.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Houdini_VoronoiCrystal_PinkSapphire",
        "title": "Cellular Voronoi Pink Sapphire & Tanzanite",
        "category": "SOP Voronoi Crystal Facets",
        "desc": "Cellular Voronoi fractured crystal gems in Vivid Pink Sapphire, Tanzanite Royal Violet, and Electric Ice Blue with sharp facet normals.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Houdini_ChladniAcoustic_UltravioletVelvet",
        "title": "Chladni Acoustic Ultraviolet Velvet",
        "category": "Modal Wave Velvet Fuzz",
        "desc": "Harmonic standing-wave acoustic silk velvet with swirling pile tangency in Ultraviolet Purple, Cyan Marine Blue, and Pastel Rose.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Houdini_BaroqueAcanthus_GildedMagentaSilk",
        "title": "Baroque Acanthus Gilded Magenta Silk",
        "category": "Polar Spiral Jacquard",
        "desc": "Polar logarithmic spiral acanthus scrollwork in Gilded Magenta, Midnight Cobalt Blue, Lilac Mist, and 18k rose-gold thread.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Houdini_CathedralStainedGlass_RosaceAzurePink",
        "title": "Cathedral Rosace Royal Azure & Ruby Glass",
        "category": "Opus Vitreum Blown Glass",
        "desc": "Cathedral stained-glass rosace with blown-glass ripple displacement in Royal Azure Blue, Ruby Magenta Pink, and Deep Amethyst Violet.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
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
        img_path = houdini_dir / f"{s['id']}_{ch}.png"
        if img_path.exists():
            with Image.open(img_path) as img:
                thumb = img.resize((320, 320), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=88)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                suite_data["maps"][ch] = f"data:image/jpeg;base64,{b64}"
    catalog.append(suite_data)

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\houdini_vibrant_pbr_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Houdini Procedural PBR: Vibrant Pinks, Blues &amp; Purples</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #090814);
      color: var(--foreground, #f0eef8);
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
    .ch-BC {{ background: rgba(236, 72, 153, 0.25); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.5); }}
    .ch-N {{ background: rgba(168, 85, 247, 0.25); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.5); }}
    .ch-ORM {{ background: rgba(52, 211, 153, 0.25); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.5); }}
    .ch-H {{ background: rgba(56, 189, 248, 0.25); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.5); }}
    .ch-AO {{ background: rgba(148, 163, 184, 0.25); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.5); }}
    .ch-R {{ background: rgba(251, 191, 36, 0.25); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.5); }}
    .ch-M {{ background: rgba(244, 63, 94, 0.25); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.5); }}
    .ch-Sheen {{ background: rgba(216, 180, 254, 0.3); color: #f3e8ff; border: 1px solid rgba(216, 180, 254, 0.6); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px -10px rgba(236, 72, 153, 0.35);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#120f24)] border border-[var(--border,#261f47)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Houdini 22.0 SOP &amp; VEX Engine
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Vibrant Pink, Blue &amp; Purple Palette
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Differential Growth &amp; Reaction-Diffusion
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight text-white">Houdini Procedural PBR: Vibrant Pinks, Blues &amp; Purples</h1>
          <p class="text-sm text-[var(--muted-foreground,#a59fc4)] mt-1">
            6 Advanced Procedural Suites · 48 Master Maps @ 2048x2048 POT · Tangent Flow Normals, Dual-Lobe Sheen &amp; Packed ORM
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-sm transition">All Suites (6)</button>
          <button onclick="filterCategory('Fabric')" id="btn-fabric" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#120f24)] border border-[var(--border,#261f47)] text-[var(--muted-foreground,#a59fc4)] hover:text-white transition">Organza &amp; Velvet (3)</button>
          <button onclick="filterCategory('Structure')" id="btn-structure" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#120f24)] border border-[var(--border,#261f47)] text-[var(--muted-foreground,#a59fc4)] hover:text-white transition">Enamel &amp; Crystal (3)</button>
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
        if (currentFilter === 'Fabric') return s.category.includes('Growth') || s.category.includes('Velvet') || s.category.includes('Jacquard');
        if (currentFilter === 'Structure') return s.category.includes('Enamel') || s.category.includes('Crystal') || s.category.includes('Glass');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#120f24)] border border-[var(--border,#261f47)] rounded-2xl p-5 shadow-sm space-y-4';
        
        let mapTabs = '';
        let mapImages = '';
        const channels = Object.keys(s.maps);
        
        channels.forEach((ch, idx) => {{
          const isFirst = idx === 0;
          mapTabs += `
            <button onclick="switchTab('${{s.id}}', '${{ch}}')" id="tab-${{s.id}}-${{ch}}" class="channel-badge ch-${{ch}} ${{isFirst ? 'ring-2 ring-pink-400/90' : 'opacity-70 hover:opacity-100'}} transition cursor-pointer">
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
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#261f47)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-pink-400 uppercase tracking-wider">${{s.category}}</span>
              <h3 class="text-lg font-bold text-white tracking-tight mt-0.5">${{s.title}}</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-md bg-pink-500/10 border border-pink-500/20 font-mono text-pink-200">
              ${{channels.length}} Channels
            </span>
          </div>
          <p class="text-xs text-[var(--muted-foreground,#a59fc4)] leading-relaxed">${{s.desc}}</p>
          
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
            tab.classList.add('ring-2', 'ring-pink-400/90');
            tab.classList.remove('opacity-70');
          }} else {{
            img.classList.add('hidden');
            tab.classList.remove('ring-2', 'ring-pink-400/90');
            tab.classList.add('opacity-70');
          }}
        }}
      }});
    }}

    function filterCategory(cat) {{
      currentFilter = cat;
      ['all', 'fabric', 'structure'].forEach(c => {{
        const btn = document.getElementById(`btn-${{c}}`);
        if (btn) {{
          if (c.toLowerCase() === cat.toLowerCase()) {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#120f24)] border border-[var(--border,#261f47)] text-[var(--muted-foreground,#a59fc4)] hover:text-white transition';
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
print(f"Generated Houdini Vibrant HTML showcase: {out_html} ({out_html.stat().st_size} bytes)")
