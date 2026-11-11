// Shared helpers for every shot page. Load it BEFORE the page's own script, which defines
// `async function start()` at top level:   <script src="shot.js"></script><script>...</script>
// It exposes window.start and auto-plays once fonts and images are ready, unless the URL has
// #manual (the recorder and checker use #manual and call start() themselves).
const $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));

// Preload extra images the page swaps in later (frame sequences); call it at top level, not in
// start(). Images already in the DOM are waited for automatically.
const PRELOAD = [];
function preload(...srcs) { for (const s of srcs.flat()) { const im = new Image(); im.src = s; PRELOAD.push(im); } }

// Show / hide. .on and .out both use !important in base.css, so swap one for the other rather
// than adding a second class next to .on (which silently does nothing).
const show = el => { el.classList.remove('out'); el.classList.add('on'); };
const hide = el => { el.classList.remove('on'); el.classList.add('out'); };

// Cursor: aim at the ELEMENT, never at typed-in coordinates. Its position is measured when the
// cursor moves, so zooms, re-layouts and other stage sizes can't make a click miss. left/top is
// the arrow's tip (base.css offsets the drawing). Waits for the whole glide before returning.
async function cursorTo(target, ms = 600) {
  const c = $('cursor'), stage = c.parentElement.getBoundingClientRect();
  let x, y;
  if (target instanceof Element) {
    const r = target.getBoundingClientRect();
    x = r.left + r.width / 2 - stage.left; y = r.top + r.height / 2 - stage.top;
  } else ({ x, y } = target);   // {x, y} only for a point that isn't an element
  c.style.transition = `opacity .3s, left ${ms}ms cubic-bezier(.5,0,.2,1), top ${ms}ms cubic-bezier(.5,0,.2,1)`;
  c.style.opacity = 1; c.style.left = x + 'px'; c.style.top = y + 'px';
  await sleep(ms + 60);
}

// Clicks el, moving there first if needed. If the tip still isn't on el, logs an error, which
// makes check.cjs fail the page instead of a mis-click reaching a recording.
async function click(el) {
  const c = $('cursor');
  if (el) {
    const r = el.getBoundingClientRect();
    const on = t => t.left >= r.left && t.left <= r.right && t.top >= r.top && t.top <= r.bottom;
    if (!on(c.getBoundingClientRect()) || c.style.opacity !== '1') await cursorTo(el);
    if (!on(c.getBoundingClientRect())) console.error(`cursor missed #${el.id || el.className}`);
  }
  c.classList.add('down'); el?.classList.add('press'); await sleep(140);
  el?.classList.remove('press'); c.classList.remove('down');
}

// Types text into el a character at a time. Keep the whole string under ~1 s in a short ad
// (a 16-character URL at 55 ms is 0.9 s); slower reads as lag.
async function typeText(el, text, perChar = 55) {
  for (const ch of text) { el.textContent += ch; await sleep(perChar); }
}

// Counts a number up in el over ms (ease-out), with thousands separators.
async function countUp(el, to, ms = 700, { decimals = 0, suffix = '' } = {}) {
  const t0 = performance.now(), fmt = v => v.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
  await new Promise(done => (function tick(now) {
    const k = Math.min(1, (now - t0) / ms), v = to * (1 - Math.pow(1 - k, 3));
    el.textContent = fmt(k < 1 ? +v.toFixed(decimals) : to);
    k < 1 ? requestAnimationFrame(tick) : done();
  })(t0));
}

// Frames a native-size screenshot inside #world: puts image point (x, y) (in the screenshot's CSS
// pixels) at stage point (sx, sy), scaled by s. Defaults to the stage centre. The page sets
// `.world { transform-origin:0 0 }` and an <img> at its natural size (see SKILL.md). Animates
// with .world's transition.
function frameTo(x, y, s = 1, sx, sy) {
  const st = getComputedStyle(document.documentElement);
  sx ??= parseFloat(st.width) / 2; sy ??= parseFloat(st.height) / 2;
  $('world').style.transform = `translate(${sx - x * s}px, ${sy - y * s}px) scale(${s})`;
}

addEventListener('DOMContentLoaded', () => {
  if (typeof start !== 'function') { console.error('page has no start()'); return; }
  window.start = start;
  if (location.hash.includes('manual')) return;
  Promise.all([document.fonts.ready, ...[...document.images, ...PRELOAD].map(im => im.decode().catch(() => {}))])
    .then(() => setTimeout(start, 600));
});
