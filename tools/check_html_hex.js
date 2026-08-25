const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');
const RAW_HEX_REGEX = /(^|[^-\w])#([a-fA-F0-9]{3,4}|[a-fA-F0-9]{6}|[a-fA-F0-9]{8})(?![a-fA-F0-9])/g;

const files = fs.readdirSync(WIX_DIR).filter(f => f.endsWith('.html'));

const occurrences = [];

for (const f of files) {
  const filePath = path.join(WIX_DIR, f);
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  let inStyle = false;
  lines.forEach((line, i) => {
    if (line.includes('<style')) inStyle = true;
    let cleanLine = line.replace(/\/\*[\s\S]*?\*\//g, '');
    let m;
    while ((m = RAW_HEX_REGEX.exec(cleanLine)) !== null) {
      // Exclude anchor target links href="#..." or id="..." or SVG url(#id)
      const fullMatch = m[0].trim();
      const matchPos = m.index;
      const beforeMatch = line.slice(0, matchPos);
      if (/href=["']$/i.test(beforeMatch) || /id=["']$/i.test(beforeMatch) || /url\(["']?$/i.test(beforeMatch)) {
        continue;
      }
      occurrences.push({
        file: f,
        line: i + 1,
        inStyleTag: inStyle,
        match: fullMatch,
        text: line.trim()
      });
    }
    if (line.includes('</style>')) inStyle = false;
  });
}

console.log(`Found ${occurrences.length} hex occurrences in HTML files:`);
occurrences.forEach(o => {
  console.log(`  ${o.file}:${o.line} [${o.inStyleTag ? 'STYLE' : 'BODY'}] ${o.match} => ${o.text.substring(0, 100)}`);
});
