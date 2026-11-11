// Screenshots animation pages at chosen moments, for checking before recording.
//
//   node check.cjs <pages-dir> <out-dir> page:ms:ms:ms [page:ms ...]
//   e.g. node check.cjs ./anim ./chk hook:500:1800:3500 live:1000:4000
//
// start() is called WITHOUT awaiting it, then shots are taken at each ms after the call. (Awaiting
// start() only ever shows the end state.) Page errors are printed; any error means fix the page.
const { chromium } = require('./pw.cjs');
const fs = require('fs'), path = require('path');
const [pagesDir, outDir, ...specs] = process.argv.slice(2);
if (!pagesDir || !outDir || !specs.length) { console.error('usage: node check.cjs <pages-dir> <out-dir> page:ms[:ms...] ...'); process.exit(2); }
const base = 'file://' + path.resolve(pagesDir) + '/';
fs.mkdirSync(outDir, { recursive: true });
(async () => {
  const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  let errors = 0;
  p.on('pageerror', e => { errors++; console.log('PAGE ERROR', e.message); });
  // console.error from the page (e.g. click() reporting a missed button) also fails the check.
  p.on('console', m => { if (m.type() === 'error') { errors++; console.log('PAGE ERROR', m.text()); } });
  for (const spec of specs) {
    const [n, ...ts] = spec.split(':');
    await p.goto(base + n + '.html#manual');
    // Screenshot at the page's own size (1920x1080, 1080x1920, 1080x1080 ...).
    const { w, h } = await p.evaluate(() => { const cs = getComputedStyle(document.documentElement); return { w: parseFloat(cs.width), h: parseFloat(cs.height) }; });
    await p.setViewportSize({ width: Math.round(w) || 1920, height: Math.round(h) || 1080 });
    await p.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images, ...(typeof PRELOAD !== 'undefined' ? PRELOAD : [])].map(i => i.decode().catch(() => {}))]));
    await p.waitForTimeout(1200);
    await p.evaluate(() => { window.start(); });
    let at = 0;
    for (const t of ts) {
      await p.waitForTimeout(+t - at); at = +t;
      const f = path.join(outDir, `${n}-${String(t).padStart(5, '0')}.jpg`);  // padded so they sort in time order
      await p.screenshot({ path: f, quality: 70, type: 'jpeg' });
      console.log(f);
    }
  }
  // b.close() can stall with the Chrome channel; don't let it hang the run.
  await Promise.race([b.close(), new Promise(r => setTimeout(r, 5000))]);
  process.exit(errors ? 1 : 0);
})();
