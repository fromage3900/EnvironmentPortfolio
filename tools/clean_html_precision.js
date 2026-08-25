const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');

// 1. Restore pcg-system-impact.html
const pcgPath = path.join(WIX_DIR, 'pcg-system-impact.html');
let pcgContent = fs.readFileSync(pcgPath, 'utf-8');

const pcgHeader = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https: http://127.0.0.1:* ws://127.0.0.1:*; img-src 'self' data: blob: https:; media-src 'self' data: blob: https:;" />
<meta http-equiv="X-Content-Type-Options" content="nosniff" />
<meta name="referrer" content="strict-origin-when-cross-origin" />
<title>L_FallenMoon — PCG scatter survey</title>
<meta name="description" content="Procedural generation systems breakdown - density heatmaps, world placement, and hero graph plan/section drawings from a stylized UE5 environment portfolio.">
<meta property="og:title" content="L_FallenMoon — PCG scatter survey">
<meta property="og:description" content="Procedural generation systems breakdown for a stylized UE5 environment portfolio.">
<meta property="og:type" content="article">
<style>*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0}img,canvas{max-width:100%}</style>
</head>
<body>
<style>
:root{
  --ground: var(--primitive-astral-900); --surface: var(--primitive-astral-700); --surface-2: var(--primitive-plum-900); --line: var(--color-border-subtle);
  --ink: var(--primitive-ivory-50); --muted: var(--primitive-slate-300); --accent: var(--primitive-astral-300);
  --good: var(--primitive-status-success); --warn: var(--primitive-gold-300);
}
@media (prefers-color-scheme: light){
  :root{ --ground: var(--primitive-ivory-100); --surface: var(--primitive-ivory-50); --surface-2: var(--primitive-ivory-200); --line: var(--primitive-ivory-300);
         --ink: var(--primitive-plum-800); --muted: var(--primitive-plum-500); --accent: var(--primitive-astral-500); --good: var(--primitive-status-success); --warn: var(--primitive-status-warning); }
}
:root[data-theme="dark"]{
  --ground: var(--primitive-astral-900); --surface: var(--primitive-astral-700); --surface-2: var(--primitive-plum-900); --line: var(--color-border-subtle);
  --ink: var(--primitive-ivory-50); --muted: var(--primitive-slate-300); --accent: var(--primitive-astral-300); --good: var(--primitive-status-success); --warn: var(--primitive-gold-300);
}
:root[data-theme="light"]{
  --ground: var(--primitive-ivory-100); --surface: var(--primitive-ivory-50); --surface-2: var(--primitive-ivory-200); --line: var(--primitive-ivory-300);
  --ink: var(--primitive-plum-800); --muted: var(--primitive-plum-500); --accent: var(--primitive-astral-500); --good: var(--primitive-status-success); --warn: var(--primitive-status-warning);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}`;

pcgContent = pcgHeader + '\n' + pcgContent.slice(pcgContent.indexOf('.wrap{max-width:1120px'));
fs.writeFileSync(pcgPath, pcgContent, 'utf-8');
console.log('Fixed pcg-system-impact.html');
