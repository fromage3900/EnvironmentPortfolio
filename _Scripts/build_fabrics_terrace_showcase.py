import base64, io, json
from pathlib import Path
from PIL import Image

fabric_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\HauteCouture_Iridescent_Fabrics")
terrace_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Stylized_Terrace_Tilework")

suites_meta = [
    # 4 Fabrics
    {
        "id": "T_Fabric_IridescentDuchessSatin_ChampagneRose",
        "title": "Champagne-Rose Duchess Satin",
        "category": "Haute-Couture Silk Satin",
        "desc": "Heavy 400g duchess silk satin with dual-color iridescent warp/weft (Champagne Gold x Rose Quartz), micro-twill striations, and anisotropic sheen.",
        "dir": fabric_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Fabric_ChromaticJacquard_AcanthusBrocade",
        "title": "Chromatic Jacquard & Gold Bullion Brocade",
        "category": "Metallic Embroidery Brocade",
        "desc": "Heavy metallic brocade with raised 24k gold bullion acanthus embroidery over cyan-to-lilac iridescent silk jacquard background.",
        "dir": fabric_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Fabric_OpalescentChiffon_Plisse",
        "title": "Opalescent Plissé Micro-Pleated Chiffon",
        "category": "Translucent Sheer Chiffon",
        "desc": "Fine micro-pleated (plissé) semi-sheer chiffon with iridescent white-opal luster, translucent drape, and micro-fold normals.",
        "dir": fabric_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Fabric_AquaticVelvet_CrushedFuzz",
        "title": "Aquatic Crushed Velvet Fuzz",
        "category": "Crushed Silk Velvet",
        "desc": "Crushed aquatic silk velvet with multidirectional pile fuzz, deep indigo/seafoam chromatic sheen, and tactile micro-fiber relief.",
        "dir": fabric_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    # 4 Terrace Tiles
    {
        "id": "T_Terrace_WaterOrgan_MajolicaTile",
        "title": "Water-Organ Floral Majolica Tiles",
        "category": "Glazed Terrace Ceramic",
        "desc": "Glazed Moroccan/Portuguese majolica ceramic terrace tiles with musical water-organ motifs, hand-painted pastel turquoise and peach floral medallions, beveled mortar, and glossy pooled enamel.",
        "dir": terrace_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Terrace_SunkenPlaza_MarbleTessellation",
        "title": "Sunken Plaza Rose Marble & Brass",
        "category": "Architectural Plaza Marble",
        "desc": "Concentric terrace plaza tiles combining Carrara rose marble, sea-mist celadon tiles, and flush brushed-brass geometric borders.",
        "dir": terrace_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Terrace_MossyGrotto_GlazedTerracotta",
        "title": "Mossy Grotto Glazed Terracotta",
        "category": "Weathered Terracotta Pavers",
        "desc": "Weathered Mediterranean terracotta terrace tiles with damp watercolor moss in grout lines, dewy sheen, and clay grain.",
        "dir": terrace_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_Terrace_PetalFountain_HexMosaic",
        "title": "Petal Fountain Pearl Hex Mosaic",
        "category": "Fountain Basin Mosaic",
        "desc": "Micro-hexagonal mosaic tiles arranged in a radiating cherry blossom / siren scale fountain basin with mother-of-pearl tesserae and water-worn grout.",
        "dir": terrace_dir,
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

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\fabrics_terrace_pbr_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Haute-Couture Fabrics &amp; Stylized Terrace Tilework</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #0a0c12);
      color: var(--foreground, #e8eaf0);
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
    .ch-BC {{ background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4); }}
    .ch-N {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .ch-ORM {{ background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }}
    .ch-H {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
    .ch-AO {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}
    .ch-R {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }}
    .ch-M {{ background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }}
    .ch-Sheen {{ background: rgba(192, 132, 252, 0.25); color: #e9d5ff; border: 1px solid rgba(192, 132, 252, 0.5); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px -10px rgba(0, 0, 0, 0.7);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#12141f)] border border-[var(--border,#222536)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Infinity Nikki Haute-Couture Weave
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Stylized Terrace &amp; Water Gardens
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight text-white">Iridescent Fabrics &amp; Stylized Terrace Tilework</h1>
          <p class="text-sm text-[var(--muted-foreground,#949aa8)] mt-1">
            8 Master Material Suites · 60 Channel Maps @ 2048x2048 POT · Duchess Satin, Bullion Jacquard, Majolica &amp; Terracotta
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-rose-600 text-white shadow-sm transition">All Suites (8)</button>
          <button onclick="filterCategory('Fabric')" id="btn-fabric" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#12141f)] border border-[var(--border,#222536)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition">Iridescent Fabrics (4)</button>
          <button onclick="filterCategory('Terrace')" id="btn-terrace" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#12141f)] border border-[var(--border,#222536)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition">Terrace Tilework (4)</button>
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
        if (currentFilter === 'Fabric') return s.id.includes('Fabric');
        if (currentFilter === 'Terrace') return s.id.includes('Terrace');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#12141f)] border border-[var(--border,#222536)] rounded-2xl p-5 shadow-sm space-y-4';
        
        let mapTabs = '';
        let mapImages = '';
        const channels = Object.keys(s.maps);
        
        channels.forEach((ch, idx) => {{
          const isFirst = idx === 0;
          mapTabs += `
            <button onclick="switchTab('${{s.id}}', '${{ch}}')" id="tab-${{s.id}}-${{ch}}" class="channel-badge ch-${{ch}} ${{isFirst ? 'ring-2 ring-rose-400/80' : 'opacity-70 hover:opacity-100'}} transition cursor-pointer">
              ${{ch}}
            </button>
          `;
          mapImages += `
            <div id="img-${{s.id}}-${{ch}}" class="relative aspect-square w-full rounded-xl overflow-hidden bg-black/50 border border-white/5 ${{isFirst ? '' : 'hidden'}}">
              <img src="${{s.maps[ch]}}" alt="${{s.id}} ${{ch}}" class="w-full h-full object-cover">
              <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/75 backdrop-blur-sm text-[10px] font-mono text-white/90">
                ${{s.id}}_${{ch}}.png (2048x2048)
              </div>
            </div>
          `;
        }});

        card.innerHTML = `
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#222536)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">${{s.category}}</span>
              <h3 class="text-lg font-bold text-white tracking-tight mt-0.5">${{s.title}}</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-md bg-white/5 border border-white/10 font-mono text-white/80">
              ${{channels.length}} Channels
            </span>
          </div>
          <p class="text-xs text-[var(--muted-foreground,#949aa8)] leading-relaxed">${{s.desc}}</p>
          
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
            tab.classList.add('ring-2', 'ring-rose-400/80');
            tab.classList.remove('opacity-70');
          }} else {{
            img.classList.add('hidden');
            tab.classList.remove('ring-2', 'ring-rose-400/80');
            tab.classList.add('opacity-70');
          }}
        }}
      }});
    }}

    function filterCategory(cat) {{
      currentFilter = cat;
      ['all', 'fabric', 'terrace'].forEach(c => {{
        const btn = document.getElementById(`btn-${{c}}`);
        if (btn) {{
          if (c.toLowerCase() === cat.toLowerCase()) {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-rose-600 text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#12141f)] border border-[var(--border,#222536)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition';
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
print(f"Generated Fabrics & Terrace HTML showcase: {out_html} ({out_html.stat().st_size} bytes)")
