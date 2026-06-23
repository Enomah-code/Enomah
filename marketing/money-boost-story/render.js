// Deterministic frame renderer for the Money Boost video (sharded for parallelism).
// Usage: node render.js <fps> <outDir> <shardIndex> <shardCount>
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const FPS = parseInt(process.argv[2] || '30', 10);
const OUT = process.argv[3] || path.join(__dirname, 'build', 'frames');
const SHARD = parseInt(process.argv[4] || '0', 10);
const SHARDS = parseInt(process.argv[5] || '1', 10);
const HTML = 'file://' + path.join(__dirname, 'promo.html');
const W = 1080, H = 1920;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto(HTML, { waitUntil: 'load' });
  await page.waitForFunction('window.__ready === true', { timeout: 30000 });

  const dur = await page.evaluate(() => window.DURATION);
  const total = Math.round(FPS * dur);
  const t0 = Date.now();
  let done = 0;
  for (let i = SHARD; i < total; i += SHARDS) {
    await page.evaluate((tt) => window.seek(tt), i / FPS);
    const name = path.join(OUT, 'f_' + String(i).padStart(5, '0') + '.jpg');
    await page.screenshot({ path: name, type: 'jpeg', quality: 95, clip: { x: 0, y: 0, width: W, height: H } });
    done++;
    if (done % 25 === 0) {
      const el = (Date.now() - t0) / 1000;
      process.stdout.write(`[shard ${SHARD}] ${done} frames (${el.toFixed(1)}s, ${(done/Math.max(el,0.01)).toFixed(2)} fps)\n`);
    }
  }
  await browser.close();
  console.log(`[shard ${SHARD}] DONE ${done} frames in ${((Date.now()-t0)/1000).toFixed(1)}s`);
})();
