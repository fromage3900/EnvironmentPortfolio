/**
 * Comprehensive Empirical Adversarial Challenge & Stress Test Harness
 * Evaluates Milestones 2 & 3:
 * 1. melodia-mahou-flourish.js runtime safety, boundary conditions, edge cases, particle throttle & capping, memory leak resistance, reduced-motion behavior, and idempotency.
 * 2. melodia-mahou-flourish.css design token compliance, variable resolution against melodia-tokens.css, pointer-events safety, z-index hierarchy, and viewport layout constraints.
 * 3. Cross-page integration across all 13 showcase HTML files in wix/.
 * 4. Milestone 2 & Milestone 3 acceptance criteria compliance.
 */

const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const WIX_DIR = path.join(REPO_ROOT, 'wix');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
const failures = [];

function assert(condition, testName, details = '') {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  [PASS] ${testName}`);
  } else {
    failedTests++;
    console.error(`  [FAIL] ${testName} — ${details}`);
    failures.push({ testName, details });
  }
}

console.log('================================================================');
console.log('MELODIA MILESTONES 2 & 3 EMPIRICAL ADVERSARIAL CHALLENGE HARNESS');
console.log('================================================================\n');

// -------------------------------------------------------------
// SECTION 1: CSS TOKEN RESOLUTION & POINTER-EVENTS AUDIT
// -------------------------------------------------------------
console.log('--- SUITE 1: CSS TOKEN RESOLUTION & POINTER-EVENTS AUDIT ---');

const tokensCssPath = path.join(WIX_DIR, 'melodia-tokens.css');
const flourishCssPath = path.join(WIX_DIR, 'melodia-mahou-flourish.css');

const tokensCss = fs.readFileSync(tokensCssPath, 'utf8');
const flourishCss = fs.readFileSync(flourishCssPath, 'utf8');

// Extract all token definitions from melodia-tokens.css
const definedTokens = new Set();
const defRegex = /(--[a-zA-Z0-9_-]+)\s*:/g;
let m;
while ((m = defRegex.exec(tokensCss)) !== null) {
  definedTokens.add(m[1]);
}

// Extract all var(--...) used in melodia-mahou-flourish.css
const varUsageRegex = /var\(\s*(--[a-zA-Z0-9_-]+)(?:\s*,\s*([^)]+))?\)/g;
const usedVars = [];
while ((m = varUsageRegex.exec(flourishCss)) !== null) {
  usedVars.push({ varName: m[1], fallback: m[2] });
}

// Known local variables or standard CSS custom props allowed
const localAllowed = new Set(['--tx', '--ty']);

let unresolvedCount = 0;
usedVars.forEach(({ varName, fallback }) => {
  const isDefined = definedTokens.has(varName) || localAllowed.has(varName) || Boolean(fallback);
  if (!isDefined) {
    unresolvedCount++;
    console.error(`    Unresolved CSS token: ${varName}`);
  }
});

assert(unresolvedCount === 0, 'All CSS custom properties in melodia-mahou-flourish.css resolve to tokens or fallbacks', `Found ${unresolvedCount} unresolved tokens`);

// Check for raw hex colors in melodia-mahou-flourish.css
const rawHexMatches = flourishCss.match(/#[0-9a-fA-F]{3,8}\b/g) || [];
assert(rawHexMatches.length === 0, 'Zero raw hex colors in melodia-mahou-flourish.css', `Found raw hex: ${rawHexMatches.join(', ')}`);

// Check for raw rgba/rgb colors in melodia-mahou-flourish.css
const rawRgbMatches = flourishCss.match(/rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+/g) || [];
assert(rawRgbMatches.length === 0, 'Zero raw rgb/rgba color values in melodia-mahou-flourish.css', `Found raw rgb: ${rawRgbMatches.join(', ')}`);

// Check pointer-events safety on all ambient classes
const pointerEventsNoneClasses = [
  '.mahou-flourish-stage',
  '.mahou-lens-flare',
  '.mahou-sigil-ring',
  '.mahou-ribbon-spiral',
  '.mahou-sparks',
  '.mahou-spark',
  '.mahou-henshin-burst',
  '.mahou-burst-shards',
  '.mahou-trail-particle'
];

pointerEventsNoneClasses.forEach(className => {
  const escaped = className.replace('.', '\\.');
  const classBlockRegex = new RegExp(`${escaped}\\s*\\{[^}]*\\}`, 'g');
  const blocks = flourishCss.match(classBlockRegex) || [];
  const hasPointerEventsNone = blocks.some(b => b.includes('pointer-events: none'));
  assert(hasPointerEventsNone, `Pointer-events safety: ${className} has pointer-events: none`);
});

// Check reduced motion media query presence
assert(flourishCss.includes('@media (prefers-reduced-motion: reduce)'), 'melodia-mahou-flourish.css includes @media (prefers-reduced-motion: reduce) block');

// Check stage overflow containment
assert(flourishCss.includes('overflow: hidden'), '.mahou-flourish-stage specifies overflow: hidden to prevent horizontal page scrolling');


// -------------------------------------------------------------
// SECTION 2: JAVASCRIPT EMULATION & RUNTIME STRESS TESTING
// -------------------------------------------------------------
console.log('\n--- SUITE 2: JAVASCRIPT EMULATION & RUNTIME STRESS TESTING ---');

function createMockDom(initialHtml = '<div class="hero"><h1>Title</h1><button class="button primary">CTA</button></div>', prefersMotion = false) {
  class MockElement {
    constructor(tagName) {
      this.tagName = tagName.toUpperCase();
      this.className = '';
      this.style = {};
      this.attributes = {};
      this.children = [];
      this.parentNode = null;
      this.textContent = '';
      this._listeners = {};
    }
    setAttribute(k, v) { this.attributes[k] = String(v); }
    getAttribute(k) { return this.attributes[k] || null; }
    hasAttribute(k) { return k in this.attributes; }
    removeAttribute(k) { delete this.attributes[k]; }
    appendChild(child) {
      if (child.parentNode) child.parentNode.removeChild(child);
      child.parentNode = this;
      this.children.push(child);
      return child;
    }
    removeChild(child) {
      const idx = this.children.indexOf(child);
      if (idx !== -1) {
        this.children.splice(idx, 1);
        child.parentNode = null;
      }
      return child;
    }
    querySelector(sel) {
      return this.querySelectorAll(sel)[0] || null;
    }
    querySelectorAll(sel) {
      const results = [];
      function match(el) {
        if (sel === ':scope > .mahou-flourish-stage') {
          return el.className.split(/\s+/).includes('mahou-flourish-stage');
        }
        if (sel.startsWith('.')) {
          const cls = sel.slice(1);
          return el.className.split(/\s+/).includes(cls);
        }
        if (sel.startsWith('[') && sel.endsWith(']')) {
          const attr = sel.slice(1, -1).split('=')[0];
          return el.hasAttribute(attr);
        }
        return false;
      }
      function traverse(node, isDirectChild) {
        for (const c of node.children) {
          if (sel.startsWith(':scope >')) {
            if (isDirectChild && match(c)) results.push(c);
          } else if (match(c)) {
            results.push(c);
          }
          traverse(c, false);
        }
      }
      traverse(this, true);
      return results;
    }
    closest(sel) {
      let curr = this;
      while (curr) {
        if (curr.className && curr.className.split(/\s+/).includes(sel.replace('.', ''))) return curr;
        if (curr.attributes && curr.attributes[sel.replace(/[\[\]]/g, '')]) return curr;
        curr = curr.parentNode;
      }
      return null;
    }
    addEventListener(evt, fn, opts) {
      if (!this._listeners[evt]) this._listeners[evt] = [];
      this._listeners[evt].push({ fn, opts });
    }
    dispatchEvent(evtName, evtData = {}) {
      if (this._listeners[evtName]) {
        const list = [...this._listeners[evtName]];
        list.forEach(l => {
          l.fn({ target: this, ...evtData });
          if (l.opts && l.opts.once) {
            this._listeners[evtName] = this._listeners[evtName].filter(item => item !== l);
          }
        });
      }
    }
    get classList() {
      const self = this;
      return {
        add(...classes) {
          const set = new Set(self.className.split(/\s+/).filter(Boolean));
          classes.forEach(c => set.add(c));
          self.className = Array.from(set).join(' ');
        },
        remove(...classes) {
          const set = new Set(self.className.split(/\s+/).filter(Boolean));
          classes.forEach(c => set.delete(c));
          self.className = Array.from(set).join(' ');
        },
        contains(cls) {
          return self.className.split(/\s+/).includes(cls);
        }
      };
    }
    set innerHTML(html) {
      this._innerHTML = html;
      this.children = [];
      const tagRegex = /<([a-z0-9-]+)([^>]*)>(.*?)<\/\1>|<([a-z0-9-]+)([^>]*)\/>/gi;
      let match;
      while ((match = tagRegex.exec(html)) !== null) {
        const tag = match[1] || match[4];
        const attrs = match[2] || match[5];
        const child = new MockElement(tag);
        if (attrs) {
          const classMatch = attrs.match(/class="([^"]+)"/);
          if (classMatch) child.className = classMatch[1];
          const styleMatch = attrs.match(/style="([^"]+)"/);
          if (styleMatch) child.setAttribute('style', styleMatch[1]);
        }
        child.parentNode = this;
        this.children.push(child);
      }
    }
    get innerHTML() {
      return this._innerHTML || '';
    }
  }

  const doc = {
    readyState: 'complete',
    body: new MockElement('body'),
    createElement(tag) {
      return new MockElement(tag);
    },
    querySelector(sel) {
      return this.body.querySelector(sel);
    },
    querySelectorAll(sel) {
      return this.body.querySelectorAll(sel);
    },
    addEventListener: () => {}
  };

  const hero = new MockElement('section');
  hero.className = 'hero';
  hero.parentNode = doc.body;
  doc.body.children.push(hero);

  const kicker = new MockElement('div');
  kicker.className = 'magazine-kicker';
  kicker.parentNode = hero;
  hero.children.push(kicker);

  const btn = new MockElement('button');
  btn.className = 'button primary';
  btn.parentNode = hero;
  hero.children.push(btn);

  let simulatedTime = 1000; // Simulated time offset past throttle window
  const mockWindow = {
    innerWidth: 1920,
    innerHeight: 1080,
    performance: {
      now: () => {
        simulatedTime += 60; // Advance 60ms each call
        return simulatedTime;
      }
    },
    matchMedia: (query) => ({
      matches: query.includes('prefers-reduced-motion') ? prefersMotion : false
    }),
    getComputedStyle: (el) => el.style || { position: 'static' },
    requestAnimationFrame: (cb) => { cb(); return 1; },
    cancelAnimationFrame: () => {},
    addEventListener: (evt, fn) => {
      if (!mockWindow._listeners) mockWindow._listeners = {};
      if (!mockWindow._listeners[evt]) mockWindow._listeners[evt] = [];
      mockWindow._listeners[evt].push(fn);
    },
    document: doc,
    MelodiaMahouFlourish: undefined,
    _listeners: {}
  };

  return { window: mockWindow, document: doc, hero, kicker, btn };
}

// Load melodia-mahou-flourish.js source code
const flourishJsPath = path.join(WIX_DIR, 'melodia-mahou-flourish.js');
const flourishJsSource = fs.readFileSync(flourishJsPath, 'utf8');

// Test 2.1: Execution in standard DOM environment
{
  const mock = createMockDom();
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  runFn(mock.window, mock.document, mock.window, mock.window.performance);

  const MMF = mock.window.MelodiaMahouFlourish;
  assert(Boolean(MMF), 'MelodiaMahouFlourish exports to global object');
  assert(typeof MMF.init === 'function', 'MMF.init is a function');
  assert(typeof MMF.mount === 'function', 'MMF.mount is a function');
  assert(typeof MMF.trigger === 'function', 'MMF.trigger is a function');
  assert(typeof MMF.burst === 'function', 'MMF.burst is a function');

  // Verify that mountHeroFlourish mounted a stage inside hero
  const stage = mock.hero.querySelector('.mahou-flourish-stage');
  assert(Boolean(stage), 'Stage element .mahou-flourish-stage mounted into .hero');
  assert(stage.getAttribute('aria-hidden') === 'true', 'Stage element has aria-hidden="true"');
  assert(stage.classList.contains('is-mounted'), 'Stage element has is-mounted class');
  assert(stage.classList.contains('is-active'), 'Stage element has is-active class');

  // Test idempotency: Calling mountHeroFlourish again should not create duplicate
  const secondStage = MMF.mount(mock.hero);
  assert(secondStage === null, 'Second call to mount() is idempotent and returns null');
  const stageCount = mock.hero.querySelectorAll('.mahou-flourish-stage').length;
  assert(stageCount === 1, 'Exactly one .mahou-flourish-stage exists in hero after duplicate mount');
}

// Test 2.2: Empty DOM environment without .hero or [data-mahou-stage]
{
  const mock = createMockDom();
  mock.document.body.children = [];
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  
  let didThrow = false;
  try {
    runFn(mock.window, mock.document, mock.window, mock.window.performance);
    mock.window.MelodiaMahouFlourish.init();
  } catch (err) {
    didThrow = true;
  }
  assert(!didThrow, 'MMF.init() runs safely without error in empty DOM without .hero');
}

// Test 2.3: Adversarial Parameters: burst() with invalid/null inputs
{
  const mock = createMockDom();
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  runFn(mock.window, mock.document, mock.window, mock.window.performance);
  const MMF = mock.window.MelodiaMahouFlourish;

  let noCrash = true;
  try {
    MMF.burst(undefined, undefined);
    MMF.burst(null, null);
    MMF.burst('invalid', NaN);
    MMF.burst(-9999, 99999);
    MMF.triggerHenshin(null);
    MMF.triggerHenshin(undefined);
  } catch (e) {
    noCrash = false;
  }
  assert(noCrash, 'MMF.burst() and MMF.triggerHenshin() safely handle undefined, null, NaN, and out-of-bounds parameters');
}

// Test 2.4: Transformation triggers & particle burst DOM lifecycle
{
  const mock = createMockDom();
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  runFn(mock.window, mock.document, mock.window, mock.window.performance);
  const MMF = mock.window.MelodiaMahouFlourish;

  MMF.burst(500, 300);
  const bursts = mock.document.body.children.filter(c => c.className.includes('mahou-henshin-burst'));
  assert(bursts.length >= 1, 'MMF.burst() creates a burst element in document.body');
  assert(bursts[0].getAttribute('aria-hidden') === 'true', 'Burst element has aria-hidden="true"');

  MMF.triggerHenshin(mock.hero);
  const heroBursts = mock.hero.children.filter(c => c.className.includes('mahou-henshin-burst'));
  assert(heroBursts.length === 1, 'MMF.triggerHenshin() mounts henshin burst in target container');
}

// Test 2.5: Pointer trail throttling & particle boundary stress test
{
  const mock = createMockDom();
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  runFn(mock.window, mock.document, mock.window, mock.window.performance);

  const pointerListeners = mock.window._listeners['pointermove'] || [];
  assert(pointerListeners.length > 0, 'pointermove event listener registered');

  // Fire 1,000 pointermove events
  for (let i = 0; i < 1000; i++) {
    pointerListeners.forEach(fn => fn({ clientX: 100 + (i % 50), clientY: 200 + (i % 50) }));
  }

  const trailParticles = mock.document.body.children.filter(c => c.className.includes('mahou-trail-particle'));
  assert(trailParticles.length <= 16, `Active trail particles cap strictly respected (found: ${trailParticles.length}, max allowed: 16)`);
  assert(trailParticles.length > 0, `Pointer trail generated ${trailParticles.length} particles upon simulated movement`);
}

// Test 2.6: Reduced motion mode suppresses particles and bursts
{
  const mock = createMockDom('<div class="hero"></div>', true); // prefersMotion = true
  const runFn = new Function('window', 'document', 'global', 'performance', flourishJsSource);
  runFn(mock.window, mock.document, mock.window, mock.window.performance);
  const MMF = mock.window.MelodiaMahouFlourish;

  MMF.burst(100, 100);
  MMF.triggerHenshin(mock.hero);

  const bursts = mock.document.body.children.filter(c => c.className.includes('mahou-henshin-burst'));
  const heroBursts = mock.hero.children.filter(c => c.className.includes('mahou-henshin-burst'));

  assert(bursts.length === 0, 'Reduced-motion suppresses MMF.burst()');
  assert(heroBursts.length === 0, 'Reduced-motion suppresses MMF.triggerHenshin()');
}


// -------------------------------------------------------------
// SECTION 3: CROSS-PAGE INTEGRATION AUDIT ACROSS ALL 13 PAGES
// -------------------------------------------------------------
console.log('\n--- SUITE 3: CROSS-PAGE INTEGRATION & QUALITY AUDIT ---');

const showcasePages = [
  'index.html',
  'melodia-melusina.html',
  'surreal-architecture.html',
  'pipeline.html',
  'sakura-case-study.html',
  'recruiter-one-sheet.html',
  'application-hub.html',
  'space-cathedral.html',
  'cosmic-orrery.html',
  'pcg-system-impact.html',
  'melodia-stage-character.html',
  'geometry-nodes.html',
  'melodia-gameplay-loop.html'
];

showcasePages.forEach(page => {
  const filePath = path.join(WIX_DIR, page);
  assert(fs.existsSync(filePath), `File exists: ${page}`);

  const html = fs.readFileSync(filePath, 'utf8');

  // Check script tag for melodia-mahou-flourish.js
  const hasFlourishScript = /<script\s+[^>]*src=["'](?:\.\/|\/)?melodia-mahou-flourish\.js["']/i.test(html);
  assert(hasFlourishScript, `${page} includes melodia-mahou-flourish.js script tag`);

  // Check stylesheet tag for melodia-mahou-flourish.css
  const hasFlourishCss = /<link\s+[^>]*href=["'](?:\.\/|\/)?melodia-mahou-flourish\.css["']/i.test(html);
  assert(hasFlourishCss, `${page} includes melodia-mahou-flourish.css stylesheet tag`);

  // Check stylesheet tag for melodia-magical-girl.css
  const hasMgCss = /<link\s+[^>]*href=["'](?:\.\/|\/)?melodia-magical-girl\.css["']/i.test(html);
  assert(hasMgCss, `${page} includes melodia-magical-girl.css stylesheet tag`);
});

// Milestone 2 & 3 specific acceptance criteria:
console.log('\n--- SUITE 4: MILESTONE 2 & 3 ACCEPTANCE CRITERIA AUDIT ---');

let pagesWithMgLoaded = 0;
let pagesWithGameUiHoverOrCards = 0;
let pagesWithMahouModule = 0;

showcasePages.forEach(page => {
  const filePath = path.join(WIX_DIR, page);
  const html = fs.readFileSync(filePath, 'utf8');

  if (html.includes('melodia-magical-girl.js') || html.includes('melodia-magical-girl.css')) {
    pagesWithMgLoaded++;
  }
  if (html.includes('mg-ribbon-card') || html.includes('game-ui-filigree-divider') || html.includes('game-ui-skill-chip')) {
    pagesWithGameUiHoverOrCards++;
  }
  if (html.includes('melodia-mahou-flourish.js')) {
    pagesWithMahouModule++;
  }
});

assert(pagesWithMgLoaded >= 5, `Magical girl micro-interactions loaded on >= 4 pages beyond gameplay-loop (actual: ${pagesWithMgLoaded} pages)`);
assert(pagesWithGameUiHoverOrCards >= 6, `Game UI hover states & cards present on >= 6 pages (actual: ${pagesWithGameUiHoverOrCards} pages)`);
assert(pagesWithMahouModule >= 2, `Mahou flourish creative element integrated on >= 2 pages (actual: ${pagesWithMahouModule} pages)`);

// Summary
console.log('\n================================================================');
console.log(`HARNESS AUDIT COMPLETE: ${totalTests} Total Tests | ${passedTests} Passed | ${failedTests} Failed`);
console.log('================================================================\n');

if (failedTests > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
