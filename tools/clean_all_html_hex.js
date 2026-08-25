const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');
const files = fs.readdirSync(WIX_DIR).filter(f => f.endsWith('.html'));

const replacements = [
  { target: /style="color:#999"/gi, replace: 'style="color:var(--primitive-slate-400)"' },
  { target: /style="color:#666"/gi, replace: 'style="color:var(--primitive-slate-400)"' },
  { target: /style="color:#555555"/gi, replace: 'style="color:var(--primitive-slate-500)"' },
  { target: /style="color:#fff"/gi, replace: 'style="color:var(--primitive-ivory-50)"' }
];

let modified = 0;
for (const f of files) {
  const filePath = path.join(WIX_DIR, f);
  let content = fs.readFileSync(filePath, 'utf-8');
  let original = content;

  for (const r of replacements) {
    content = content.replace(r.target, r.replace);
  }

  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`Cleaned ${f}`);
    modified++;
  }
}

console.log(`Cleaned total ${modified} files.`);
