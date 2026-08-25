const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');
const files = fs.readdirSync(WIX_DIR).filter(f => f.endsWith('.html'));

let modifiedCount = 0;

for (const f of files) {
  const filePath = path.join(WIX_DIR, f);
  let content = fs.readFileSync(filePath, 'utf-8');
  let original = content;

  // 1. Root overrides
  content = content.replace(
    /:root\s*\{\s*--surface-base:\s*#141A30;\s*--text-primary:\s*#ECEAF4;\s*--text-secondary:\s*#A9A7C0;\s*--gold:\s*#C9A86A;\s*\}/gi,
    ':root { --surface-base: var(--primitive-astral-900); --text-primary: var(--primitive-ivory-50); --text-secondary: var(--primitive-slate-300); --gold: var(--primitive-gold-500); }'
  );
  content = content.replace(/--gold:\s*#C9A86A;/gi, '--gold: var(--primitive-gold-500);');
  content = content.replace(/--gold-soft:\s*#DDC79B;/gi, '--gold-soft: var(--primitive-gold-300);');

  // 2. Fallbacks in var(...)
  content = content.replace(/#C9A86A/gi, 'var(--primitive-gold-500)');
  content = content.replace(/#DDC79B/gi, 'var(--primitive-gold-300)');
  content = content.replace(/#A9A7C0/gi, 'var(--primitive-slate-300)');
  content = content.replace(/#ffe666/gi, 'var(--primitive-gold-100)');
  content = content.replace(/#66d9ff/gi, 'var(--primitive-astral-300)');
  content = content.replace(/#ff6eb4/gi, 'var(--color-accent-tertiary)');

  // Fix any double var(var(...)) or broken syntax if any created
  content = content.replace(/var\(var\((--[a-z0-9-]+)\)\)/gi, 'var($1)');
  content = content.replace(/var\(--color-accent-primary,\s*var\(--primitive-gold-500\)\)/gi, 'var(--color-accent-primary, var(--primitive-gold-500))');
  content = content.replace(/var\(--color-text-tertiary,\s*var\(--primitive-slate-300\)\)/gi, 'var(--color-text-tertiary, var(--primitive-slate-300))');
  content = content.replace(/var\(--color-text-accent,\s*var\(--primitive-gold-500\)\)/gi, 'var(--color-text-accent, var(--primitive-gold-500))');

  // 3. Specific inline style color hexes
  content = content.replace(/style="color:#666"/gi, 'style="color:var(--primitive-slate-400)"');
  content = content.replace(/style="color:#555555"/gi, 'style="color:var(--primitive-slate-500)"');
  content = content.replace(/color:#8c8/gi, 'color:var(--primitive-status-success)');
  content = content.replace(/style="background:#F5C77E"/gi, 'style="background:var(--primitive-gold-300)"');

  // Preserve prose text mentioning hex colors in technical docs (e.g. Hex #352D40 in pipeline.html text)
  content = content.replace(/Hex var\(--primitive-plum-800\) Warm-Violet/gi, 'Hex #352D40 Warm-Violet');
  content = content.replace(/`var\(--primitive-plum-800\)/gi, '`#352D40');

  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`Cleaned inline hex in ${f}`);
    modifiedCount++;
  }
}

console.log(`Cleaned ${modifiedCount} HTML files.`);
