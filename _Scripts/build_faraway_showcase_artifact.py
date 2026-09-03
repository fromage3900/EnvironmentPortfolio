import base64, io, json
from pathlib import Path
from PIL import Image

faraway_dir = Path(r"C:\EnvironmentPortfolio\BS_GodFile\Content\Textures\FarawayMother_Suites")

suites_meta = [
    {
        "id": "T_FarawayMother_Gown_CelestialSilkJacquard",
        "title": "Maternal Gown — Celestial Silk Jacquard",
        "category": "Haute-Couture Silk & Embroidery",
        "desc": "Heavy moonlit ivory silk jacquard with musical stave water-droplet damask, lilac-to-seafoam iridescent watercolor sheen, and 24k gold bullion embroidery along the hem.",
        "dir": faraway_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_FarawayMother_Veil_AquaticLullabyLace",
        "title": "Ethereal Veil — Aquatic Lullaby Lace",
        "category": "Translucent Gauze & Lace",
        "desc": "Translucent Chantilly lace interwoven with musical notes, weeping willow fronds, and pearlized sea-mist filigree with delicate alpha cutouts and micro-thread normals.",
        "dir": faraway_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Alpha", "Mask"]
    },
    {
        "id": "T_FarawayMother_Corset_GildedAcanthusBrocade",
        "title": "Structured Bodice — Gilded Acanthus Brocade",
        "category": "Baroque Bodice & Boning",
        "desc": "Structured baroque maternal bodice in ivory moiré watered silk reinforced with 24k gold filigree boning, inlaid cabochon water-opals, and aquatic scrollwork reliefs.",
        "dir": faraway_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M"]
    },
    {
        "id": "T_FarawayMother_Ornament_NacreMusicBoxJewel",
        "title": "Sacred Ornament — Nacre Music-Box Jewel",
        "category": "Jewelry, Nacre & Clockwork",
        "desc": "Carved white mother-of-pearl disc layered over celestial brass clockwork gears, 8-fold faceted aquamarine gemstone center, and pearlescent teardrops.",
        "dir": faraway_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_FarawayMother_Mantle_NightSkyVelvet",
        "title": "Ceremonial Mantle — Night-Sky Velvet",
        "category": "Outer Robes & Fuzz Velvet",
        "desc": "Deep midnight royal blue velvet washed with watercolor auroral ripples, gold-foil constellation lullaby staves, and soft anisotropic velvet fuzz.",
        "dir": faraway_dir,
        "channels": ["BC", "N", "ORM", "H", "AO", "R", "M", "Sheen"]
    },
    {
        "id": "T_FarawayMother_Cradle_CarvedAlabasterWood",
        "title": "Lullaby Cradle — Carved Limed Oak",
        "category": "Prop & Architectural Woodwork",
        "desc": "Antique bleached French oak wood with carved musical cherubs, fluted sea-shell volutes, and soft damp pearlized alabaster patina in micro-crevices.",
        "dir": faraway_dir,
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

out_html = Path(r"C:\Users\froma\.gemini\antigravity\brain\92af4173-1e1e-4ccd-aa99-852f9d8b06b9\faraway_mother_pbr_showcase.html")

catalog_json = json.dumps(catalog)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>P1 Faraway Mother — Haute-Couture PBR Material Suites</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      background: var(--background, #0b0d13);
      color: var(--foreground, #eaecef);
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
    .ch-Alpha {{ background: rgba(251, 146, 60, 0.2); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.4); }}
    .ch-Mask {{ background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); }}
    .suite-card {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .suite-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.6);
    }}
  </style>
</head>
<body class="p-6 antialiased">
  <div class="max-w-7xl mx-auto space-y-8">
    
    <!-- Header -->
    <div class="bg-[var(--card,#131620)] border border-[var(--border,#232838)] rounded-2xl p-6 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              Infinity Nikki &amp; Baroque Aesthetic Research
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              P1 Faraway Mother Material Suite (2048x2048)
            </span>
          </div>
          <h1 class="text-2xl font-bold mt-2 tracking-tight">P1 Faraway Mother — Haute-Couture PBR Suites</h1>
          <p class="text-sm text-[var(--muted-foreground,#949aa8)] mt-1">
            6 Complete Character Material Sets · 47 Channel Maps · Substrate &amp; Dual-Lobe Sheen Ready
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="filterCategory('All')" id="btn-all" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--primary,#3b82f6)] text-white shadow-sm transition">All Suites (6)</button>
          <button onclick="filterCategory('Fabric')" id="btn-fabric" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#131620)] border border-[var(--border,#232838)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition">Silk, Lace &amp; Velvet (3)</button>
          <button onclick="filterCategory('Structure')" id="btn-structure" class="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#131620)] border border-[var(--border,#232838)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition">Bodice, Jewels &amp; Cradle (3)</button>
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
        if (currentFilter === 'Fabric') return s.category.includes('Silk') || s.category.includes('Gauze') || s.category.includes('Velvet');
        if (currentFilter === 'Structure') return s.category.includes('Bodice') || s.category.includes('Jewelry') || s.category.includes('Woodwork');
        return true;
      }});

      filtered.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'suite-card bg-[var(--card,#131620)] border border-[var(--border,#232838)] rounded-2xl p-5 shadow-sm space-y-4';
        
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
          <div class="flex items-start justify-between gap-2 border-b border-[var(--border,#232838)] pb-3">
            <div>
              <span class="text-[11px] font-semibold text-[var(--primary,#60a5fa)] uppercase tracking-wider">${{s.category}}</span>
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
      ['all', 'fabric', 'structure'].forEach(c => {{
        const btn = document.getElementById(`btn-${{c}}`);
        if (btn) {{
          if (c.toLowerCase() === cat.toLowerCase()) {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--primary,#3b82f6)] text-white shadow-sm transition';
          }} else {{
            btn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[var(--card,#131620)] border border-[var(--border,#232838)] text-[var(--muted-foreground,#949aa8)] hover:text-white transition';
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
