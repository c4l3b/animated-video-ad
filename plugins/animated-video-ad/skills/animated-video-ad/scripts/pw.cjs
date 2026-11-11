// Finds Playwright: local install first, then any global install (plain or bundled in @playwright/cli).
const { execSync } = require('child_process');
const path = require('path');
let globalRoot = '';
try { globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim(); } catch {}
const candidates = ['playwright',
  path.join(globalRoot, 'playwright'),
  path.join(globalRoot, '@playwright/cli/node_modules/playwright'),
  path.join(globalRoot, '@playwright/test/node_modules/playwright')];
for (const m of candidates) { try { module.exports = require(m); break; } catch {} }
if (!module.exports.chromium) {
  console.error('Playwright not found. Install it once: npm i -g playwright  (the scripts use your installed Chrome).');
  process.exit(2);
}
