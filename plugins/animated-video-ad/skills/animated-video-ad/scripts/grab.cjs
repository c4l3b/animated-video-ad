// Screenshots the real product (a local HTML file or a URL) for use in shot pages: the full view
// and any elements by CSS selector, at 2x or 3x so zooming in stays sharp. Also prints each
// element's box in CSS pixels, for frameTo() and marks.
//
//   node grab.cjs <file-or-url> <out-dir> [--size 1280x800] [--scale 3] [--wait 800] [name=selector ...]
//   e.g. node grab.cjs shelfie.html anim/shots --size 1000x640 goal=.goal streak=.streak logo="header .logo"
//
// Writes <out-dir>/full.png plus <name>.png per selector. For a site behind a login, ask the person
// for screenshots instead; don't sign in for them.
const { chromium } = require('./pw.cjs');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const [w, h] = opt('--size', '1280x800').split('x').map(Number);
const scale = +opt('--scale', '3'), wait = +opt('--wait', '800');
const [src, outDir, ...shots] = args;
if (!src || !outDir) { console.error('usage: node grab.cjs <file-or-url> <out-dir> [--size WxH] [--scale N] [--wait ms] [name=selector ...]'); process.exit(2); }
const url = /^[a-z]+:\/\//i.test(src) ? src : 'file://' + path.resolve(src);
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  p.on('pageerror', e => console.error('page error:', e.message));
  await p.goto(url, { waitUntil: 'networkidle' }).catch(() => p.goto(url));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(wait);
  await p.screenshot({ path: path.join(outDir, 'full.png') });
  console.log(`full.png  ${w}x${h} CSS px @${scale}x`);
  let failed = 0;
  for (const spec of shots) {
    const i = spec.indexOf('='), name = spec.slice(0, i), sel = spec.slice(i + 1);
    const el = await p.$(sel);
    if (!el) { console.error(`no element for ${name}=${sel}`); failed++; continue; }
    await el.screenshot({ path: path.join(outDir, name + '.png') });
    const r = await el.boundingBox();
    console.log(`${name}.png  ${sel}  x=${Math.round(r.x)} y=${Math.round(r.y)} w=${Math.round(r.width)} h=${Math.round(r.height)}`);
  }
  await Promise.race([b.close(), new Promise(r => setTimeout(r, 5000))]);
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
