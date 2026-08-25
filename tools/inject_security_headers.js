const fs = require('fs');
const path = require('path');

const WIX_DIR = path.join(__dirname, '..', 'wix');
const SECURITY_TAGS = `<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https: http://127.0.0.1:* ws://127.0.0.1:*; img-src 'self' data: blob: https:; media-src 'self' data: blob: https:;" />
<meta http-equiv="X-Content-Type-Options" content="nosniff" />
<meta name="referrer" content="strict-origin-when-cross-origin" />`;

const files = fs.readdirSync(WIX_DIR).filter(f => f.endsWith('.html'));

let injectedCount = 0;
for (const f of files) {
  const filePath = path.join(WIX_DIR, f);
  let content = fs.readFileSync(filePath, 'utf-8');

  if (!content.includes('Content-Security-Policy')) {
    // Inject after viewport meta tag if present, else after <head>
    if (content.includes('<meta name="viewport"')) {
      content = content.replace(
        /(<meta name="viewport"[^>]*>)/i,
        `$1\n${SECURITY_TAGS}`
      );
    } else if (content.includes('<head>')) {
      content = content.replace('<head>', `<head>\n${SECURITY_TAGS}`);
    } else if (content.includes('<HEAD>')) {
      content = content.replace('<HEAD>', `<HEAD>\n${SECURITY_TAGS}`);
    }
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`Injected security headers into ${f}`);
    injectedCount++;
  }
}

console.log(`Total injected: ${injectedCount}`);
