const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');

// 1. melodia-navigation-constellation.html
const navPath = path.join(WIX_DIR, 'melodia-navigation-constellation.html');
let navContent = fs.readFileSync(navPath, 'utf-8');
const navHeadAndStyle = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https: http://127.0.0.1:* ws://127.0.0.1:*; img-src 'self' data: blob: https:; media-src 'self' data: blob: https:;" />
<meta http-equiv="X-Content-Type-Options" content="nosniff" />
<meta name="referrer" content="strict-origin-when-cross-origin" />
<title>Melodia Constellation Navigation</title>
<link rel="stylesheet" href="melodia-luxury-type.css">
<style>
  :root {
    --surface-base: var(--primitive-astral-900);
    --surface-raised: var(--primitive-astral-700);
    --gold: var(--primitive-gold-500);
    --gold-soft: var(--primitive-gold-300);
    --text-primary: var(--primitive-ivory-50);
    --text-secondary: var(--primitive-slate-300);
    --border-gold: rgba(201, 168, 106, 0.3);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-body), system-ui, sans-serif;
    background: var(--surface-base);
    color: var(--text-primary);
    width: 100%;
    min-height: 500px;
  }`;
navContent = navHeadAndStyle + '\n' + navContent.slice(navContent.indexOf('.nav-container {'));
fs.writeFileSync(navPath, navContent, 'utf-8');

// 2. melodia-breakdown-card.html
const bdcPath = path.join(WIX_DIR, 'melodia-breakdown-card.html');
let bdcContent = fs.readFileSync(bdcPath, 'utf-8');
bdcContent = bdcContent.replace('#141A30', 'var(--primitive-astral-900)');
bdcContent = bdcContent.replace('#1C2340', 'var(--primitive-astral-700)');
bdcContent = bdcContent.replace('#241B2E', 'var(--primitive-plum-800)');
bdcContent = bdcContent.replace('#ECEAF4', 'var(--primitive-ivory-50)');
bdcContent = bdcContent.replace('#3C5C9E', 'var(--primitive-astral-500)');
bdcContent = bdcContent.replace('#A85751', 'var(--primitive-status-error)');
fs.writeFileSync(bdcPath, bdcContent, 'utf-8');

// 3. melodia-gallery-grid.html
const mggPath = path.join(WIX_DIR, 'melodia-gallery-grid.html');
let mggContent = fs.readFileSync(mggPath, 'utf-8');
mggContent = mggContent.replace('#141A30', 'var(--primitive-astral-900)');
mggContent = mggContent.replace('#1C2340', 'var(--primitive-astral-700)');
mggContent = mggContent.replace('#241B2E', 'var(--primitive-plum-800)');
mggContent = mggContent.replace('#ECEAF4', 'var(--primitive-ivory-50)');
mggContent = mggContent.replace('#3C5C9E', 'var(--primitive-astral-500)');
fs.writeFileSync(mggPath, mggContent, 'utf-8');

console.log('Fixed embed components.');
