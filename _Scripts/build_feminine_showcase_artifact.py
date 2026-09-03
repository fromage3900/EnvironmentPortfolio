import base64, io, json
from pathlib import Path
from PIL import Image

textures_root = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\Melusina_Feminine_Iridescent_Suites")

suites_meta = [
    {
        "id": "T_Melusina_IridescentSiren_ScaleTessellation",
        "title": "Sirens' White Opal & Rose-Gold Scales",
        "category": "Haute-Couture Mermaid Scales",
        "desc": "Scalloped mermaid scale tiles in Australian white opal and pink mother-of-pearl with thin-film rainbow optical interference, rose-gold filigree rims, and dewy micro-droplets.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_SakuraLullaby_SilkOrganza",
        "title": "Sakura Lullaby Water-Organza Gown",
        "category": "Translucent Silk & Embroidery",
        "desc": "Translucent watercolor sakura petals suspended in sheer crystalline organza with floating music note ripples, micro-twill shimmer, and rose-gold thread embroidery.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_BaroqueTiara_RoseGoldFiligree",
        "title": "Baroque Tiara & Morganite Jewel Trim",
        "category": "Rococo Jewelry & Filigree",
        "desc": "Ultra-feminine rococo tiara filigree in 18k rose-gold, bezel-set pastel morganite gems, teardrop pearls, and vitreous strawberry enamel.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_PorcelainMusicBox_KintsugiLapis",
        "title": "Porcelain Music-Box with Rose-Gold Kintsugi",
        "category": "Glazed Porcelain & Ceramic",
        "desc": "Luminous white porcelain glazed with soft watercolor hydrangeas and humming musical clefs, repaired with liquid rose-gold kintsugi and diamond-dust luster coat.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_MoonlitHarbor_WaterRippleParquet",
        "title": "Blush Satinwood & Abalone Wave Parquet",
        "category": "Architectural Flooring & Marquetry",
        "desc": "Bleached blush satinwood and lilac pearwood inlaid in delicate acoustic wave ripples, accented with rainbow abalone shell and fine rose-gold ribbons.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_Melusina_EtherealVeil_StarlightChantilly",
        "title": "Starlight Bridal Chantilly Lace & Pearls",
        "category": "Translucent Bridal Lace",
        "desc": "Gossamer starlight Chantilly lace with woven aquatic blossoms, micro-pearl seed beading, delicate scalloped borders, and ethereal subsurface translucency.",
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen", "Alpha", "Mask"]
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
        img_path = textures_root / f"{s['id']}_{ch}.png"
        if img_path.exists():
            with Image.open(img_path) as img:
                thumb = img.resize((320, 320), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=88)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                suite_data["maps"][ch] = f"data:image/jpeg;base64,{b64}"
    catalog.append(suite_data)

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\melusina_feminine_iridescent_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Melusina &amp; Infinity Nikki Feminine Iridescent PBR Suites</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #0c0d14);
      color: var(--foreground, #eaeaf2);
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
    .ch-BC {{ background: rgba(244, 114, 182, 0.2); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.4); }}
    .ch-N {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .ch-ORM {{ background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }}
    .ch-H {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
    .ch-AO {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}
    .ch-R {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }}
    .ch-M {{ background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }}
    .ch-Sheen {{ background: rgba(192, 132, 252, 0.25); color: #e9d5ff; border: 1px solid rgba(192, 132, 252, 0.5); }}
    .ch-Alpha {{ background: rgba(251, 146, 60, 0.2); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.4); }}
    .ch-Mask {{ background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px -10px rgba(244, 114, 182, 0.25);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#141522)] border border-[var(--border,#26283b)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Infinity Nikki &amp; Siren Aesthetic
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Thin-Film Iridescence &amp; Rose-Gold
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight text-white">Melusina Feminine Iridescent PBR Suites</h1>
          <p class="text-sm text-[var(--muted-foreground,#9ca3af)] mt-1">
            6 Haute-Couture Suites · 50 Master Maps @ 2048x2048 POT · White Opal, Sakura Organza, Rose-Gold &amp; Dewdrops
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-pink-600 text-white shadow-sm transition">All Suites (6)</button>
          <button onclick="filterCategory('Fabric')" id="btn-fabric" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#141522)] border border-[var(--border,#26283b)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition">Silk, Lace &amp; Scales (3)</button>
          <button onclick="filterCategory('Structure')" id="btn-structure" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#141522)] border border-[var(--border,#26283b)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition">Tiara, Porcelain &amp; Parquet (3)</button>
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
        if (currentFilter === 'Fabric') return s.category.includes('Mermaid') || s.category.includes('Organza') || s.category.includes('Lace');
        if (currentFilter === 'Structure') return s.category.includes('Jewelry') || s.category.includes('Porcelain') || s.category.includes('Flooring');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#141522)] border border-[var(--border,#26283b)] rounded-2xl p-5 shadow-sm space-y-4';
        
        let mapTabs = '';
        let mapImages = '';
        const channels = Object.keys(s.maps);
        
        channels.forEach((ch, idx) => {{
          const isFirst = idx === 0;
          mapTabs += `
            <button onclick="switchTab('${{s.id}}', '${{ch}}')" id="tab-${{s.id}}-${{ch}}" class="channel-badge ch-${{ch}} ${{isFirst ? 'ring-2 ring-pink-400/80' : 'opacity-70 hover:opacity-100'}} transition cursor-pointer">
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
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#26283b)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-pink-400 uppercase tracking-wider">${{s.category}}</span>
              <h3 class="text-lg font-bold text-white tracking-tight mt-0.5">${{s.title}}</h3>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-md bg-pink-500/10 border border-pink-500/20 font-mono text-pink-200">
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
            tab.classList.add('ring-2', 'ring-pink-400/80');
            tab.classList.remove('opacity-70');
          }} else {{
            img.classList.add('hidden');
            tab.classList.remove('ring-2', 'ring-pink-400/80');
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
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-pink-600 text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#141522)] border border-[var(--border,#26283b)] text-[var(--muted-foreground,#9ca3af)] hover:text-white transition';
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
print(f"Generated Feminine Iridescent HTML showcase: {out_html} ({out_html.stat().st_size} bytes)")
