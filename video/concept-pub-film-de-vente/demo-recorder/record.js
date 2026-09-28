// Deterministic "live demo" recorder: drives the real site with a visible cursor,
// real mouse events (hover + clicks), smooth scrolling and typing, and captures
// every frame at 30 fps via HeadlessExperimental.beginFrame + virtual time.
// Usage: node record.js <site.html> <fontsDir> <outDir> [segmentName]
const puppeteer = require("puppeteer-core");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const SITE = path.resolve(process.argv[2]);
const FONTS = path.resolve(process.argv[3]);
const OUT = path.resolve(process.argv[4]);
const ONLY = process.argv[5];
const FPS = 30, FR = 1000 / FPS, VW = 1440, VH = 900, DSF = 4 / 3;
const SEGMENTS = require("./segments.js");

const fontCss = `
@font-face{font-family:"Cormorant Garamond";font-weight:300 500;font-style:normal;src:url(file://${FONTS}/cormorant-garamond-latin-500-normal.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:600 700;font-style:normal;src:url(file://${FONTS}/cormorant-garamond-latin-600-normal.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:300 400;font-style:italic;src:url(file://${FONTS}/cormorant-garamond-latin-400-italic.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:500 700;font-style:italic;src:url(file://${FONTS}/cormorant-garamond-latin-500-italic.woff2)}
@font-face{font-family:"Manrope";font-weight:200 300;src:url(file://${FONTS}/manrope-latin-300-normal.woff2)}
@font-face{font-family:"Manrope";font-weight:400 500;src:url(file://${FONTS}/manrope-latin-400-normal.woff2)}
@font-face{font-family:"Manrope";font-weight:600 800;src:url(file://${FONTS}/manrope-latin-600-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:400;src:url(file://${FONTS}/ibm-plex-mono-latin-400-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:500 600;src:url(file://${FONTS}/ibm-plex-mono-latin-500-normal.woff2)}
html{scroll-behavior:auto!important}
#__cur{position:fixed;left:0;top:0;width:0;height:0;z-index:2147483647;pointer-events:none}
#__cur svg{position:absolute;left:-3px;top:-2px;width:30px!important;height:30px!important;max-width:none!important;min-width:30px;filter:drop-shadow(0 3px 6px rgba(0,0,0,.45));transition:transform .12s cubic-bezier(.16,1,.3,1)}
#__cur.down svg{transform:scale(.86)}
#__cur i{position:absolute;left:-26px;top:-26px;width:52px;height:52px;border-radius:50%;border:2px solid #DBC796;opacity:0;transform:scale(.2)}
#__cur i.go{animation:__rip .65s cubic-bezier(.16,1,.3,1) forwards}
@keyframes __rip{0%{opacity:.95;transform:scale(.2)}100%{opacity:0;transform:scale(1.35)}}`;

const ease = {
  inOutCubic: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  inOutQuint: (x) => (x < 0.5 ? 16 * x ** 5 : 1 - Math.pow(-2 * x + 2, 5) / 2),
  outExpo: (x) => (x === 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  linear: (x) => x,
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await puppeteer.launch({
    executablePath: "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell", headless: "shell",
    args: ["--no-sandbox", "--deterministic-mode", "--enable-begin-frame-control", "--disable-new-content-rendering-timeout", "--run-all-compositor-stages-before-draw",
      "--disable-threaded-animation", "--disable-threaded-scrolling", "--disable-checker-imaging", "--disable-image-animation-resync", "--hide-scrollbars", "--allow-file-access-from-files", "--font-render-hinting=none"],
  });
  const bc = await b.target().createCDPSession();
  const { targetId } = await bc.send("Target.createTarget", { url: "about:blank", enableBeginFrameControl: true, width: VW, height: VH });
  const target = await b.waitForTarget((t) => t._targetId === targetId);
  const p = await target.page();
  const c = await p.createCDPSession();
  await c.send("Emulation.setDeviceMetricsOverride", { width: VW, height: VH, deviceScaleFactor: DSF, mobile: false });

  let T = 0;
  const begin = (shot) => { T += FR; return c.send("HeadlessExperimental.beginFrame", { frameTimeTicks: 1e10 + T, interval: FR, ...(shot ? { screenshot: { format: "jpeg", quality: 93 } } : {}) }); };
  await p.setRequestInterception(true);
  p.on("request", (r) => (/^https?:/.test(r.url()) ? r.abort() : r.continue()));
  const nav = p.goto("file://" + SITE, { waitUntil: "load", timeout: 60000 });
  let loaded = false; nav.then(() => (loaded = true), (e) => { console.error("nav", e.message); loaded = true; });
  const race = (pr, ms) => Promise.race([pr.catch(() => ({})), new Promise((r) => setTimeout(() => r({}), ms))]);
  while (!loaded) { await race(begin(false), 1000); await new Promise((r) => setTimeout(r, 15)); }
  await p.addStyleTag({ content: fontCss });
  await p.evaluate(() => {
    const d = document.createElement("div"); d.id = "__cur";
    d.innerHTML = '<i></i><svg viewBox="0 0 24 24"><path d="M4 2.5 L4 19.5 L8.6 15.4 L11.6 22 L14.6 20.7 L11.7 14.2 L18 14.2 Z" fill="#fff" stroke="#0B0A09" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    document.body.appendChild(d);
  });
  for (let i = 0; i < 20; i++) { await race(begin(false), 1000); await new Promise((r) => setTimeout(r, 30)); }
  await p.evaluate(async () => { for (const f of ['500 40px "Cormorant Garamond"', 'italic 500 40px "Cormorant Garamond"', "300 20px Manrope", "400 20px Manrope", "600 20px Manrope", '400 20px "IBM Plex Mono"']) await document.fonts.load(f); });
  await c.send("Emulation.setVirtualTimePolicy", { policy: "pause" });
  const adv = () => new Promise((r) => { c.once("Emulation.virtualTimeBudgetExpired", r); c.send("Emulation.setVirtualTimePolicy", { policy: "advance", budget: FR }); });
  const step = async (shot) => { await adv(); return begin(shot); };

  // ---- page-side helpers
  const rectOf = (tg) => p.evaluate((tg) => {
    let els = Array.from(document.querySelectorAll(tg.sel));
    if (tg.text) els = els.filter((e) => e.textContent.trim().toLowerCase().includes(tg.text.toLowerCase()));
    if (tg.visible) els = els.filter((e) => e.offsetParent !== null);
    const e = els[tg.i || 0]; if (!e) return null;
    const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height };
  }, tg);
  const docY = (tg) => p.evaluate((tg) => { const e = document.querySelector(tg.sel); return e ? e.getBoundingClientRect().top + window.scrollY : 0; }, tg);
  const setCursor = (x, y) => p.evaluate((x, y) => { const d = document.getElementById("__cur"); d.style.transform = `translate(${x}px,${y}px)`; }, x, y);
  const mouse = (type, x, y, extra = {}) => { c.send("Input.dispatchMouseEvent", { type, x, y, button: extra.button || "none", buttons: extra.buttons || 0, clickCount: extra.clickCount || 0 }).catch(() => {}); };

  const cur = { x: VW * 0.72, y: VH + 60, down: false };

  for (const seg of SEGMENTS) {
    if (ONLY && seg.name !== ONLY) continue;
    // ---- set up state (not recorded)
    if (seg.setup) await p.evaluate(seg.setup);
    if (seg.startScroll) { const y = (await docY(seg.startScroll)) + (seg.startScroll.off || 0); await p.evaluate((y) => window.scrollTo(0, y), y); }
    if (seg.cursor) { cur.x = seg.cursor[0]; cur.y = seg.cursor[1]; }
    await setCursor(cur.x, cur.y); await mouse("mouseMoved", cur.x, cur.y);
    for (let i = 0; i < 6; i++) await step(false);

    const ff = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-", "-vf", "scale=1920:1200:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", String(FPS), path.join(OUT, seg.name + ".mp4")], { stdio: ["pipe", "inherit", "inherit"] });
    const n = Math.round(seg.dur * FPS);
    // resolve actions lazily at their start time
    const acts = seg.actions.map((a) => ({ ...a, done: false, started: false }));
    const t0 = Date.now();
    for (let f = 0; f < n; f++) {
      const t = f / FPS;
      for (const a of acts) {
        if (t < a.t || a.done) continue;
        if (!a.started) {
          a.started = true;
          if (a.type === "move") {
            const r = await rectOf(a.to);
            a.from = { x: cur.x, y: cur.y };
            a.dst = r ? { x: r.x + r.w * (a.to.fx ?? 0.5) + (a.to.dx || 0), y: r.y + r.h * (a.to.fy ?? 0.5) + (a.to.dy || 0) } : { x: a.to.x, y: a.to.y };
          }
          if (a.type === "scroll") {
            a.fromY = await p.evaluate(() => window.scrollY);
            a.toY = a.y !== undefined ? a.y : (await docY(a.to)) + (a.to.off || 0);
          }
          if (a.type === "drag") {
            const r = await rectOf({ sel: a.sel });
            const pos = (v) => r.x + 9 + ((v - a.min) / (a.max - a.min)) * (r.w - 18);
            a.fx = pos(a.from); a.tx = pos(a.to); a.y = r.y + r.h / 2; a.lastV = a.from;
            cur.x = a.fx; cur.y = a.y; await setCursor(cur.x, cur.y);
            await mouse("mouseMoved", cur.x, cur.y); await mouse("mousePressed", cur.x, cur.y, { button: "left", buttons: 1, clickCount: 1 });
            await p.evaluate(() => document.getElementById("__cur").classList.add("down"));
          }
          if (a.type === "click") {
            await p.evaluate(() => { const d = document.getElementById("__cur"); d.classList.add("down"); const i = d.querySelector("i"); i.classList.remove("go"); void i.offsetWidth; i.classList.add("go"); });
            await mouse("mousePressed", cur.x, cur.y, { button: "left", buttons: 1, clickCount: 1 });
            a.releaseAt = t + 0.1;
          }
          if (a.type === "eval") { await p.evaluate(a.js); a.done = true; continue; }
          if (a.type === "type") { a.typed = 0; }
        }
        const k = Math.min(1, (t - a.t) / (a.dur || 1e-6));
        if (a.type === "move") {
          const e = ease[a.ease || "inOutCubic"](k);
          if (a.to.sel) { const r = await rectOf(a.to); if (r) a.dst = { x: r.x + r.w * (a.to.fx ?? 0.5) + (a.to.dx || 0), y: r.y + r.h * (a.to.fy ?? 0.5) + (a.to.dy || 0) }; }
          // slight arc for a natural hand movement
          const arc = Math.sin(Math.PI * e) * (a.arc ?? -30);
          cur.x = a.from.x + (a.dst.x - a.from.x) * e; cur.y = a.from.y + (a.dst.y - a.from.y) * e + arc;
          await setCursor(cur.x, cur.y); await mouse("mouseMoved", cur.x, cur.y);
          if (k >= 1) a.done = true;
        } else if (a.type === "scroll") {
          const e = ease[a.ease || "inOutQuint"](k);
          await p.evaluate((y) => window.scrollTo(0, y), a.fromY + (a.toY - a.fromY) * e);
          if (k >= 1) a.done = true;
        } else if (a.type === "drag") {
          const e = ease.inOutCubic(k); cur.x = a.fx + (a.tx - a.fx) * e;
          await setCursor(cur.x, cur.y); await mouse("mouseMoved", cur.x, cur.y, { button: "left", buttons: 1 });
          if (k >= 1) { await mouse("mouseReleased", cur.x, cur.y, { button: "left", buttons: 0, clickCount: 1 }); await p.evaluate(() => document.getElementById("__cur").classList.remove("down")); a.done = true; }
        } else if (a.type === "click") {
          if (t >= a.releaseAt) { await mouse("mouseReleased", cur.x, cur.y, { button: "left", buttons: 0, clickCount: 1 }); await p.evaluate(() => document.getElementById("__cur").classList.remove("down")); a.done = true; }
        } else if (a.type === "type") {
          const want = Math.floor(k * a.text.length);
          while (a.typed < want) { c.send("Input.insertText", { text: a.text[a.typed] }).catch(() => {}); a.typed++; }
          if (k >= 1) a.done = true;
        }
      }
      const r = await step(true);
      if (r.screenshotData) last = r.screenshotData;
      if (last) ff.stdin.write(Buffer.from(last, "base64"));
    }
    ff.stdin.end();
    await new Promise((r) => ff.on("close", r));
    console.log(`segment ${seg.name}: ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
let last = null;
