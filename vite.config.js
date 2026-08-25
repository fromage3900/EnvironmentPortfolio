import { defineConfig } from 'vite';
import { createReadStream, cpSync, existsSync, statSync } from 'fs';
import { extname, isAbsolute, relative as relativePath, resolve } from 'path';

const ROOT = __dirname;
const GENERATED_ROOT = resolve(ROOT, 'generated');
const DEPLOY_ROOT = resolve(ROOT, 'my-site-deploy');

const GENERATED_MIME_TYPES = {
  '.avif': 'image/avif',
  '.gif': 'image/gif',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webm': 'video/webm',
  '.webp': 'image/webp',
};

function generatedAssetBridge() {
  return {
    name: 'melodia-generated-asset-bridge',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const requestPath = decodeURIComponent((req.url || '').split('?')[0]);
        const prefix = '/generated/';
        if (!requestPath.startsWith(prefix)) {
          next();
          return;
        }

        const assetPath = resolve(GENERATED_ROOT, requestPath.slice(prefix.length));
        const assetRelativePath = relativePath(GENERATED_ROOT, assetPath);
        if (
          !assetRelativePath ||
          assetRelativePath.startsWith('..') ||
          isAbsolute(assetRelativePath)
        ) {
          next();
          return;
        }

        let stats;
        try {
          stats = statSync(assetPath);
        } catch {
          next();
          return;
        }
        if (!stats.isFile()) {
          next();
          return;
        }

        res.statusCode = 200;
        res.setHeader(
          'Content-Type',
          GENERATED_MIME_TYPES[extname(assetPath).toLowerCase()] ||
            'application/octet-stream',
        );
        res.setHeader('Content-Length', String(stats.size));
        res.setHeader('Cache-Control', 'no-cache');
        if (req.method === 'HEAD') {
          res.end();
          return;
        }

        createReadStream(assetPath)
          .on('error', () => {
            if (!res.headersSent) res.statusCode = 500;
            res.end();
          })
          .pipe(res);
      });
    },
    writeBundle() {
      if (!existsSync(GENERATED_ROOT)) return;
      cpSync(GENERATED_ROOT, resolve(DEPLOY_ROOT, 'generated'), {
        force: true,
        recursive: true,
      });
    },
  };
}

// Single source of truth: pages[] in content/site-manifest.json.
// Add new recruiter-visible pages there first, then mirror here.
const PAGES = [
  'index',
  'recruiter-one-sheet',
  'hiring-dossier',
  'resume',
  'application-hub',
  'sakura-case-study',
  'space-cathedral',
  'melodia-stage-character',
  'pcg-system-impact',
  'cosmic-orrery',
  'hero-renders',
  'shader-breakdowns',
  'world-bible',
  'melodia-gameplay-loop',
  'ornament-kitbash',
  'zbrush-breakdown',
  'geometry-nodes',
  'sdf-material-gallery',
  'touchdesigner-architecture',
  'production-roadmap',
  'pipeline',
  'melodia-melusina',
  'melodia-atelier-lab',
];

const input = Object.fromEntries(
  PAGES.map((slug) => [slug, resolve(ROOT, `wix/${slug}.html`)]),
);

export default defineConfig({
  root: 'wix',
  publicDir: '../public',
  plugins: [generatedAssetBridge()],
  build: {
    outDir: '../my-site-deploy',
    emptyOutDir: false,
    rollupOptions: { input },
  },
  server: {
    port: 3000,
    strictPort: true,
    // Large/locked DCC files under wix/models can EBUSY-crash the watcher.
    watch: {
      ignored: ['**/models/**', '**/*.fbx', '**/*.blend', '**/*.blend1'],
    },
    proxy: {
      '/mcp': 'http://127.0.0.1:9316',
      '/blender': 'http://127.0.0.1:9317',
    },
  },
});
