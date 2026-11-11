// Records animation pages to MP4 (30 fps, H.264 CRF 16) at each page's own size.
//
//   node record.cjs <pages-dir> <out-dir> page=outName=ms[,page=outName=ms...]
//   e.g. node record.cjs ./anim ./clips hook=01-hook-anim=4200,end=08-end-card-anim=3600
//
// Each page is opened with #manual (so it doesn't auto-play), images are decoded, then recording
// starts and window.start() is called. ms = how long to record; make it the animation length plus
// ~1 s of held end frame so the editor has room to trim.
//
// Size: each page's <html> width and height (set by --w/--h in base.css) decide the clip size,
// so 1920x1080, 1080x1920 and 1080x1080 pages all record at their own size.
//
// How it works: CDP screencast frames with their real timestamps -> ffmpeg concat with per-frame
// durations -> constant 30 fps. Two things that bit us before and are handled here:
//  - Without Emulation.setDeviceMetricsOverride the screencast captures a shorter frame (993 px of
//    1080) and ffmpeg stretches it, so every clip looks squashed and loses its bottom 8%.
//  - The first frame's timestamp can predate the recording; it's clamped so the clip doesn't open
//    on a long static frame.
const { chromium } = require('./pw.cjs');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const [pagesDir, outDir, jobsArg] = process.argv.slice(2);
if (!pagesDir || !outDir || !jobsArg) {
  console.error('usage: node record.cjs <pages-dir> <out-dir> page=outName=ms[,...]');
  process.exit(2);
}
const JOBS = jobsArg.split(',').map(s => s.split('='));
const base = 'file://' + path.resolve(pagesDir) + '/';
fs.mkdirSync(outDir, { recursive: true });

// The page's design size: <html>'s CSS width/height (base.css sets them from --w/--h). Even numbers
// because H.264 needs them.
async function pageSize(page) {
  const { w, h } = await page.evaluate(() => { const cs = getComputedStyle(document.documentElement); return { w: parseFloat(cs.width), h: parseFloat(cs.height) }; });
  const even = n => Math.round(n / 2) * 2;
  return { W: even(w) || 1920, H: even(h) || 1080 };
}

async function record(ctx, page, out, ms, W, H) {
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false, screenWidth: W, screenHeight: H });
  const frames = [], t0 = Date.now() / 1000;
  cdp.on('Page.screencastFrame', f => {
    frames.push({ t: Math.max(t0, f.metadata.timestamp), d: f.data });
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: W, maxHeight: H });
  await page.evaluate(() => { window.start(); });
  await page.waitForTimeout(ms);
  // Nudge a repaint so the final held state is captured, then stop.
  await page.mouse.move(5, 5); await page.waitForTimeout(300);
  await cdp.send('Page.stopScreencast');

  const dir = out + '.frames';
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
  const end = Date.now() / 1000;
  let list = '';
  frames.forEach((f, i) => {
    const n = `${String(i).padStart(6, '0')}.jpg`;
    fs.writeFileSync(path.join(dir, n), Buffer.from(f.d, 'base64'));
    const next = i + 1 < frames.length ? frames[i + 1].t : end;
    list += `file '${n}'\nduration ${Math.max(0.001, next - f.t).toFixed(4)}\n`;
  });
  // The concat demuxer may ignore the last entry's duration, so the last image is listed again;
  // depending on the ffmpeg version that plays its hold twice, so -t pins the clip to the real
  // recorded time either way. (Without -t, clips came out ~1.5 s too long.)
  list += `file '${String(frames.length - 1).padStart(6, '0')}.jpg'\n`;
  fs.writeFileSync(path.join(dir, 'list.txt'), list);
  const total = (end - frames[0].t).toFixed(3);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'), '-t', total,
    '-vf', `scale=${W}:${H}:flags=lanczos,fps=30,format=yuv420p`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
    '-movflags', '+faststart', out]);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log('wrote', out, `${W}x${H}`, `(${frames.length} frames)`);
}

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', args: ['--window-size=2000,2000'] })
    .catch(() => chromium.launch({ args: ['--window-size=2000,2000'] }));
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.error('page error:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('page error:', m.text()); });
  for (const [name, out, ms] of JOBS) {
    await page.goto(base + name + '.html#manual');
    const { W, H } = await pageSize(page);
    await page.setViewportSize({ width: W, height: H });
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => Promise.all([...document.images, ...(typeof PRELOAD !== 'undefined' ? PRELOAD : [])].map(i => i.decode().catch(() => {}))));
    await page.waitForTimeout(1500);
    await record(ctx, page, path.join(outDir, out + '.mp4'), +ms, W, H);
  }
  // browser.close() can stall with the Chrome channel; don't let it hang the run.
  await Promise.race([browser.close(), new Promise(r => setTimeout(r, 5000))]);
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
