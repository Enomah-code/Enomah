const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const SRC = 'file://' + path.resolve(process.argv[2]);
const OUT = process.argv[3];
const F = 'file:///tmp/claude-0/-home-user-Enomah/02acd9b7-556b-5b22-bac3-911dc55fbfd2/scratchpad/video/assets/fonts/';
const FONTS = `
@font-face{font-family:"Cormorant Garamond";font-weight:400 500;font-style:normal;src:url(${F}cormorant-garamond-latin-500-normal.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:600 700;font-style:normal;src:url(${F}cormorant-garamond-latin-600-normal.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:400;font-style:italic;src:url(${F}cormorant-garamond-latin-400-italic.woff2)}
@font-face{font-family:"Cormorant Garamond";font-weight:500 700;font-style:italic;src:url(${F}cormorant-garamond-latin-500-italic.woff2)}
@font-face{font-family:"Manrope";font-weight:200 300;src:url(${F}manrope-latin-300-normal.woff2)}
@font-face{font-family:"Manrope";font-weight:400 500;src:url(${F}manrope-latin-400-normal.woff2)}
@font-face{font-family:"Manrope";font-weight:600 800;src:url(${F}manrope-latin-600-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:400;src:url(${F}ibm-plex-mono-latin-400-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:500 600;src:url(${F}ibm-plex-mono-latin-500-normal.woff2)}
*{transition:none!important}`;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox','--allow-file-access-from-files'] });
  async function page(w, h, dpr) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
    await p.goto(SRC, { waitUntil: 'load' });
    await p.addStyleTag({ content: FONTS });
    await p.evaluate(async () => { await document.fonts.load('500 40px "Cormorant Garamond"'); await document.fonts.load('italic 500 40px "Cormorant Garamond"'); await document.fonts.load('300 20px Manrope'); await document.fonts.load('400 20px Manrope'); await document.fonts.load('600 20px Manrope'); await document.fonts.load('400 20px "IBM Plex Mono"'); await document.fonts.ready; });
    await p.evaluate(() => document.querySelectorAll('[data-reveal],[data-mask],[data-grow]').forEach(e => e.classList.add('in')));
    await p.waitForTimeout(1200);
    return p;
  }
  const p = await page(1440, 900, 2);
  const view = async (sel, name, off = 0) => { await p.evaluate(([s, o]) => { const el = document.querySelector(s); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY + o); }, [sel, off]); await p.waitForTimeout(900); await p.screenshot({ path: OUT + '/v-' + name + '.png' }); };
  await view('#top', 'hero');
  await view('section.sec', 'manifeste', -40);
  await view('#prestations', 'prestations', -60);
  await view('#realisations', 'reel1', 0);
  await view('#realisations', 'reel2', 1200);
  const opts = await p.$$('#devis .opt'); for (const i of [0, 1, 3]) if (opts[i]) await opts[i].click({force:true});
  const del = await p.$$('#devis .delay'); if (del[1]) await del[1].click({force:true});
  await p.waitForTimeout(1600);
  await view('#devis', 'devis', 0);
  await view('#devis', 'devis2', 560);
  const days = await p.$$('#rendez-vous .day'); if (days[2]) await days[2].click({force:true});
  await p.waitForTimeout(300);
  const slots = await p.$$('#rendez-vous .slot:not([disabled])'); if (slots[2]) await slots[2].click({force:true});
  await view('#rendez-vous', 'rdv', -40);
  await view('#espace-client', 'auth', 0);
  await p.click('#authCta', {force:true}); await p.waitForTimeout(1500);
  await view('#espace-client', 'dash', 0);
  await view('#espace-client', 'dash2', 380);
  // full-length sections without sticky nav
  await p.addStyleTag({ content: '.nav{display:none!important}' });
  for (const [s, n] of [['#prestations','prestations'],['#devis','devis']]) { const el = await p.$(s); await el.screenshot({ path: OUT + '/s-' + n + '.png' }); }
  const m = await page(390, 844, 3);
  await m.screenshot({ path: OUT + '/m-hero.png' });
  for (const [s, n, o] of [['#devis','devis',120],['#espace-client','client',0],['#prestations','prestations',0]]) {
    await m.evaluate(([s, o]) => { const el = document.querySelector(s); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY + o); }, [s, o]);
    await m.waitForTimeout(700); await m.screenshot({ path: OUT + '/m-' + n + '.png' });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
