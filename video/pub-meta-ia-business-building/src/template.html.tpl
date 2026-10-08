<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>IA Business Building — Pub Meta UGC</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Jakarta"; font-weight: 500; src: url("assets/fonts/plus-jakarta-sans-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "Jakarta"; font-weight: 700; src: url("assets/fonts/plus-jakarta-sans-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Jakarta"; font-weight: 800; src: url("assets/fonts/plus-jakarta-sans-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Jakarta"; font-weight: 800; font-style: italic; src: url("assets/fonts/plus-jakarta-sans-latin-800-italic.woff2") format("woff2"); }
      :root {
        --navy: #0A1440; --navy-2: #050B26; --navy-3: #13205C; --blue: #5B7CFF; --blue-2: #8EA5FF;
        --gold: #E2B33C; --gold-2: #F5D27A; --gold-3: #B8891F; --white: #FFFFFF; --mist: #EEF2FF; --ink: #0A1033; --muted: #8C97C9; --red: #FF5A5F; --green: #2BD07E;
      }
      * { box-sizing: border-box; }
      body { margin: 0; background: var(--navy-2); font-family: "Jakarta", system-ui, sans-serif; color: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--navy-2); }
      .scene { position: absolute; inset: 0; }
      .stage { position: absolute; inset: 0; overflow: hidden; }
      .dark { background: radial-gradient(ellipse 120% 70% at 30% 20%, #1A2B7A 0%, var(--navy) 38%, var(--navy-2) 100%); color: #fff; }
      .light { background: radial-gradient(ellipse 120% 70% at 70% 25%, #FFFFFF 0%, #F1F4FF 55%, #E2E8FF 100%); color: var(--ink); }
      .blob { position: absolute; width: 900px; height: 900px; border-radius: 50%; filter: blur(120px); opacity: 0.55; }
      .dark .blob { background: radial-gradient(circle, rgba(91,124,255,0.55), rgba(91,124,255,0) 70%); }
      .light .blob { background: radial-gradient(circle, rgba(226,179,60,0.35), rgba(226,179,60,0) 70%); }
      .grid { position: absolute; inset: 0; opacity: 0.07; background-image: linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px); background-size: 90px 90px; mask-image: radial-gradient(ellipse at 50% 40%, #000 20%, transparent 75%); }
      .light .grid { background-image: linear-gradient(rgba(10,16,51,1) 1px, transparent 1px), linear-gradient(90deg, rgba(10,16,51,1) 1px, transparent 1px); opacity: 0.05; }

      /* kinetic text — the voice, word by word */
      .kt { position: absolute; left: 90px; right: 90px; font-weight: 800; letter-spacing: -0.035em; line-height: 1.04; }
      .kt .w { display: inline-block; opacity: 0; margin-right: 0.22em; }
      .kt .g { color: var(--gold); }
      .kt .b { color: var(--blue-2); }
      .light .kt .b { color: #3D5CF0; }
      .light .kt .g { color: #946B0E; }
      .light .kt .r { color: #C92A30; }
      .kt .r { color: var(--red); }
      .kt .sm { font-size: 0.5em; font-weight: 700; letter-spacing: -0.01em; }
      .kicker { position: absolute; left: 90px; font-weight: 700; font-size: 30px; letter-spacing: 0.02em; color: var(--muted); }
      .light .kicker { color: #5F6AA3; }
      .brandtag { position: absolute; left: 90px; top: 210px; display: flex; align-items: center; gap: 16px; font-weight: 800; font-size: 30px; letter-spacing: 0.01em; }
      .brandtag .d { width: 46px; height: 46px; }

      /* cards & mockups */
      .card { position: absolute; border-radius: 34px; background: #fff; color: var(--ink); box-shadow: 0 40px 100px rgba(5,11,38,0.45); }
      .dark .card.glass { background: rgba(255,255,255,0.06); color: #fff; border: 1.5px solid rgba(255,255,255,0.14); box-shadow: 0 40px 100px rgba(0,0,0,0.35); backdrop-filter: blur(10px); }
      .pill { display: inline-flex; align-items: center; gap: 14px; height: 76px; padding: 0 32px; border-radius: 999px; font-weight: 700; font-size: 30px; white-space: nowrap; }

      /* S1 revenue card */
      #s1card { left: 90px; right: 90px; top: 980px; height: 470px; padding: 44px; }
      #s1card .k { font-weight: 700; font-size: 28px; color: var(--muted); }
      #s1card .v { margin-top: 10px; font-weight: 800; font-size: 120px; letter-spacing: -0.04em; }
      #s1card .bars { position: absolute; left: 44px; right: 44px; bottom: 44px; height: 170px; display: flex; align-items: flex-end; gap: 22px; }
      #s1card .bars i { flex: 1; border-radius: 10px; background: rgba(255,255,255,0.14); height: 12px; display: block; }
      #s1card .bars i.on { background: var(--red); }
      #s1chat { left: 90px; right: 200px; top: 760px; padding: 26px 32px; border-radius: 30px 30px 30px 8px; font-weight: 500; font-size: 30px; }

      /* S2 orbit */
      .orbit { position: absolute; left: 50%; top: 1210px; width: 640px; height: 640px; margin: -320px 0 0 -320px; }

      /* reveal */
      #rev { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 34px; text-align: center; }
      #rev .emb { width: 300px; height: 380px; }
      #rev .t1 { font-weight: 700; font-size: 34px; letter-spacing: 0.24em; color: var(--blue-2); }
      #rev .t2 { font-weight: 800; font-size: 104px; line-height: 0.98; letter-spacing: -0.035em; }
      #rev .t2 .g { color: var(--gold); }
      #rev .chips { display: flex; gap: 16px; }
      #rev .chips span { height: 64px; padding: 0 26px; border-radius: 999px; border: 2px solid rgba(142,165,255,0.6); display: flex; align-items: center; font-weight: 700; font-size: 26px; }
      #gcirc { position: absolute; left: 50%; top: 50%; width: 2600px; height: 2600px; margin: -1300px 0 0 -1300px; border-radius: 50%; background: var(--gold); z-index: 40; pointer-events: none; }

      /* S3 chat agent */
      #chat { left: 90px; right: 90px; top: 760px; height: 760px; overflow: hidden; }
      #chat .hd { height: 120px; background: #0F1B55; color: #fff; display: flex; align-items: center; gap: 22px; padding: 0 34px; border-radius: 34px 34px 0 0; }
      #chat .av { width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, var(--gold-2), var(--gold-3)); display: flex; align-items: center; justify-content: center; font-weight: 800; color: var(--ink); font-size: 28px; }
      #chat .nm { font-weight: 800; font-size: 32px; }
      #chat .st { font-weight: 500; font-size: 22px; color: var(--green); display: flex; align-items: center; gap: 10px; }
      #chat .st b { width: 12px; height: 12px; border-radius: 50%; background: var(--green); display: block; }
      #chat .clock { margin-left: auto; font-weight: 800; font-size: 36px; color: var(--gold-2); }
      #chat .bd { position: absolute; top: 120px; left: 0; right: 0; bottom: 0; background: #EEF1FA; padding: 30px; display: flex; flex-direction: column; gap: 18px; }
      #chat .m { max-width: 78%; padding: 20px 26px; border-radius: 26px; font-weight: 500; font-size: 28px; line-height: 1.3; opacity: 0; }
      #chat .m.in { background: #fff; border-radius: 26px 26px 26px 8px; align-self: flex-start; }
      #chat .m.out { background: #DCE4FF; border-radius: 26px 26px 8px 26px; align-self: flex-end; }
      #chat .m small { display: block; margin-top: 6px; font-size: 18px; color: #4A5488; text-align: right; }
      #chat .pay { display: inline-flex; margin-top: 12px; height: 56px; padding: 0 24px; border-radius: 999px; background: var(--ink); color: #fff; align-items: center; font-weight: 700; font-size: 24px; }
      #chat .typing { align-self: flex-end; background: #DCE4FF; border-radius: 26px; padding: 22px 26px; display: flex; gap: 8px; opacity: 0; }
      #chat .typing i { width: 12px; height: 12px; border-radius: 50%; background: #5B6BB0; display: block; }
      #badge24 { position: absolute; right: 70px; top: 700px; z-index: 3; height: 92px; padding: 0 34px; border-radius: 999px; background: var(--gold); color: var(--ink); display: flex; align-items: center; font-weight: 800; font-size: 40px; box-shadow: 0 20px 50px rgba(226,179,60,0.45); }

      /* S4 site + mobile money */
      #site { left: 90px; right: 90px; top: 720px; height: 820px; overflow: hidden; }
      #site .bar { height: 64px; background: #E8ECFA; display: flex; align-items: center; gap: 10px; padding: 0 24px; border-radius: 34px 34px 0 0; }
      #site .bar i { width: 14px; height: 14px; border-radius: 50%; background: #B8C0E0; display: block; }
      #site .bar .u { margin-left: 16px; height: 38px; flex: 1; border-radius: 999px; background: #fff; display: flex; align-items: center; padding: 0 20px; font-weight: 500; font-size: 22px; color: #5F6AA3; }
      #site .hero { height: 300px; background: linear-gradient(135deg, #13205C, #2B44C8); color: #fff; padding: 40px; }
      #site .hero .a { font-weight: 800; font-size: 54px; letter-spacing: -0.03em; line-height: 1.02; }
      #site .hero .c { margin-top: 22px; display: inline-flex; height: 64px; padding: 0 30px; border-radius: 999px; background: var(--gold); color: var(--ink); align-items: center; font-weight: 800; font-size: 26px; }
      #site .sheet { position: absolute; left: 0; right: 0; bottom: 0; height: 460px; background: #fff; border-radius: 34px 34px 0 0; box-shadow: 0 -20px 50px rgba(10,16,51,0.15); padding: 36px 40px; }
      #site .sheet .k { font-weight: 700; font-size: 26px; color: #5F6AA3; }
      #site .sheet .amt { font-weight: 800; font-size: 64px; letter-spacing: -0.03em; margin-top: 6px; }
      #site .ops { margin-top: 26px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
      #site .op { height: 82px; border-radius: 20px; border: 2px solid #DCE2F7; display: flex; align-items: center; gap: 14px; padding: 0 22px; font-weight: 800; font-size: 26px; }
      #site .op i { width: 40px; height: 40px; border-radius: 12px; display: block; flex: 0 0 auto; }
      #site .op.sel { border-color: var(--blue); background: #EEF2FF; }
      #paid { position: absolute; left: 50%; top: 880px; margin-left: -230px; width: 460px; height: 110px; border-radius: 999px; background: var(--green); color: #fff; display: flex; align-items: center; justify-content: center; gap: 16px; font-weight: 800; font-size: 40px; z-index: 4; box-shadow: 0 30px 70px rgba(43,208,126,0.45); opacity: 0; }

      /* S5 app */
      #phone { position: absolute; left: 50%; top: 760px; width: 470px; height: 900px; margin-left: -235px; border-radius: 70px; background: #0A1033; border: 14px solid #1D2766; box-shadow: 0 50px 120px rgba(10,16,51,0.4); overflow: hidden; }
      #phone .scr { position: absolute; inset: 0; background: linear-gradient(180deg, #1B2A80, #0A1440); padding: 90px 40px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 34px 26px; align-content: start; }
      #phone .ic { width: 110px; height: 110px; border-radius: 28px; background: rgba(255,255,255,0.12); }
      #phone .ic.mine { background: linear-gradient(135deg, var(--gold-2), var(--gold-3)); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 40px; color: var(--ink); box-shadow: 0 0 0 4px rgba(255,255,255,0.8); }
      #phone .lbl { position: absolute; left: 0; right: 0; bottom: 120px; text-align: center; font-weight: 800; font-size: 34px; color: #fff; opacity: 0; }
      #phone .prog { position: absolute; left: 70px; right: 70px; bottom: 90px; height: 10px; border-radius: 5px; background: rgba(255,255,255,0.18); }
      #phone .prog i { display: block; height: 100%; border-radius: 5px; background: var(--gold); transform-origin: left center; transform: scaleX(0); }
      #nocode { position: absolute; right: 80px; top: 1260px; width: 210px; height: 210px; border-radius: 50%; background: #fff; box-shadow: 0 30px 70px rgba(10,16,51,0.25); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 72px; color: var(--ink); z-index: 3; opacity: 0; }
      #nocode::after { content: ""; position: absolute; left: 30px; right: 30px; top: 50%; height: 12px; margin-top: -6px; background: var(--red); border-radius: 6px; transform: rotate(-35deg) scaleX(var(--s, 0)); }

      /* S6 ring */
      #ring { position: absolute; left: 50%; top: 1150px; width: 620px; height: 620px; margin: -310px 0 0 -310px; }
      #ring .num { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
      #ring .num b { font-weight: 800; font-size: 210px; letter-spacing: -0.05em; line-height: 0.9; }
      #ring .num span { font-weight: 700; font-size: 38px; color: var(--muted); }
      #lessons { position: absolute; left: 90px; right: 90px; top: 1520px; display: flex; justify-content: center; gap: 18px; }

      /* S7 certificate + clients */
      #cert { left: 110px; right: 110px; top: 760px; height: 560px; padding: 50px; background: linear-gradient(160deg, #FFFDF6, #FFF6DD); border: 3px solid var(--gold); text-align: center; }
      #cert .in { position: absolute; inset: 22px; border: 1.5px solid rgba(184,137,31,0.5); border-radius: 22px; }
      #cert .k { font-weight: 700; font-size: 24px; letter-spacing: 0.3em; color: var(--gold-3); margin-top: 40px; }
      #cert .t { font-weight: 800; font-size: 54px; letter-spacing: -0.02em; margin-top: 26px; color: var(--ink); line-height: 1.05; }
      #cert .n { font-weight: 500; font-size: 30px; color: #5F6AA3; margin-top: 26px; }
      #cert .seal { position: absolute; right: 60px; bottom: 50px; width: 120px; height: 120px; border-radius: 50%; background: radial-gradient(circle, var(--gold-2), var(--gold-3)); display: flex; align-items: center; justify-content: center; font-weight: 800; color: var(--ink); font-size: 36px; }
      #clients { position: absolute; left: 90px; right: 90px; top: 1390px; display: flex; flex-direction: column; gap: 18px; }
      #clients .c { height: 96px; border-radius: 26px; background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.14); display: flex; align-items: center; gap: 22px; padding: 0 26px; font-weight: 700; font-size: 30px; opacity: 0; }
      #clients .c i { width: 56px; height: 56px; border-radius: 50%; display: block; flex: 0 0 auto; }
      #clients .c em { margin-left: auto; font-style: normal; color: var(--green); font-weight: 800; }

      /* S8 price */
      #cmp { position: absolute; left: 90px; right: 90px; top: 900px; height: 700px; display: flex; align-items: flex-end; gap: 60px; justify-content: center; }
      #cmp .col { width: 360px; display: flex; flex-direction: column; align-items: center; gap: 24px; }
      #cmp .bar { width: 100%; border-radius: 26px 26px 0 0; transform-origin: 50% 100%; }
      #cmp .lab { font-weight: 800; font-size: 34px; text-align: center; }
      #cmp .val { font-weight: 800; font-size: 54px; letter-spacing: -0.03em; white-space: nowrap; }
      #cmp .ag .bar { height: 560px; background: linear-gradient(180deg, #FF8A8D, var(--red)); }
      #cmp .us .bar { height: 70px; background: linear-gradient(180deg, var(--gold-2), var(--gold)); }
      #old { opacity: 0; position: relative; font-weight: 700; font-size: 44px; color: #6A74A8; }
      #old::after { content: ""; position: absolute; left: -6px; right: -6px; top: 52%; height: 6px; background: var(--red); transform: scaleX(var(--s, 0)); transform-origin: left center; }

      /* S9 proof */
      #proof { position: absolute; left: 90px; right: 90px; top: 740px; text-align: left; }
      #proof .big { font-weight: 800; font-size: 300px; letter-spacing: -0.06em; line-height: 0.85; color: var(--gold); }
      #proof .lab { font-weight: 800; font-size: 60px; letter-spacing: -0.02em; margin-top: 10px; }
      #flags { position: absolute; left: 90px; right: 90px; top: 1210px; display: flex; flex-wrap: wrap; gap: 18px; }
      #flags .pill { background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.2); opacity: 0; }
      #flags .pill i { width: 40px; height: 28px; border-radius: 6px; display: block; overflow: hidden; }
      #shield { position: absolute; left: 90px; right: 90px; top: 1420px; height: 150px; border-radius: 34px; background: rgba(43,208,126,0.12); border: 2px solid rgba(43,208,126,0.6); display: flex; align-items: center; gap: 28px; padding: 0 36px; opacity: 0; }
      #shield svg { width: 80px; height: 80px; flex: 0 0 auto; }
      #shield b { font-weight: 800; font-size: 40px; }
      #shield span { display: block; font-weight: 500; font-size: 26px; color: #BFE9D2; margin-top: 4px; }

      /* S10 end card */
      #end { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; padding-top: 250px; gap: 40px; text-align: center; }
      #end .logo { width: 240px; height: 240px; }
      #end .thumb { width: 760px; height: 760px; border-radius: 40px; overflow: hidden; box-shadow: 0 50px 120px rgba(0,0,0,0.5), 0 0 0 3px rgba(226,179,60,0.6); }
      #end .thumb img { width: 100%; height: 100%; display: block; }
      #end .price { display: flex; align-items: baseline; gap: 26px; }
      #end .price b { font-weight: 800; font-size: 96px; color: var(--gold); letter-spacing: -0.04em; }
      #end .price s { font-weight: 700; font-size: 46px; color: var(--muted); }
      #end .cta { height: 130px; padding: 0 64px; border-radius: 999px; background: var(--gold); color: var(--ink); display: flex; align-items: center; gap: 22px; font-weight: 800; font-size: 46px; box-shadow: 0 30px 80px rgba(226,179,60,0.5); }
      #end .meta { font-weight: 700; font-size: 28px; color: var(--muted); }
      #tap { position: absolute; left: 0; top: 0; width: 90px; height: 90px; border-radius: 50%; background: rgba(255,255,255,0.85); border: 4px solid #fff; z-index: 5; opacity: 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }

      #flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 50; pointer-events: none; }
      #grain { position: absolute; inset: -60px; pointer-events: none; z-index: 60; opacity: 0.06; mix-blend-mode: overlay;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.2 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); }
      #prog { position: absolute; left: 0; top: 0; height: 8px; width: 100%; background: var(--gold); transform-origin: left center; z-index: 55; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="@DUR">

      <!-- S1 · HOOK -->
      <section id="S1" class="scene clip" data-start="@S0" data-duration="@D0" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:-200px;top:-150px"></div><div class="grid"></div>
          <div class="kt" id="k1" data-line="h1" style="top:300px; font-size:104px">Tu utilises <span class="b">l'IA…</span> mais elle ne te rapporte <span class="g">pas un franc ?</span></div>
          <div class="card glass" id="s1chat">« Écris-moi un poème sur le café »</div>
          <div class="card glass" id="s1card"><div class="k">Revenus générés avec l'IA · ce mois</div><div class="v" id="s1v">0 F</div>
            <div class="bars"><i></i><i></i><i></i><i></i><i></i><i></i><i class="on"></i></div></div>
        </div>
      </section>

      <!-- S2 · PROBLEM -->
      <section id="S2" class="scene clip" data-start="@S1" data-duration="@D1" data-track-index="1">
        <div class="stage dark"><div class="blob" style="right:-300px;top:200px"></div><div class="grid"></div>
          <div class="kt" id="k2" data-line="h2" style="top:300px; font-size:104px">Le problème, ce n'est <span class="g">pas toi.</span></div>
          <div class="kt" id="k3" data-line="h3" style="top:560px; font-size:78px; color:#C9D3FF">Personne ne t'a montré comment <span class="g">construire</span> avec.</div>
          <svg class="orbit" id="orbit" viewBox="0 0 640 640" fill="none">
            <circle cx="320" cy="320" r="300" stroke="rgba(142,165,255,0.35)" stroke-width="2"/>
            <circle cx="320" cy="320" r="200" stroke="rgba(142,165,255,0.2)" stroke-width="2" stroke-dasharray="6 12"/>
            <circle id="odot" cx="320" cy="20" r="18" fill="#E2B33C"/>
            <g transform="translate(320 320)"><path d="M0 -110 L80 0 L0 110 L-80 0 Z" fill="none" stroke="#E2B33C" stroke-width="5"/><path d="M0 -70 L50 0 L0 70 L-50 0 Z" fill="none" stroke="#E2B33C" stroke-width="3" opacity="0.7"/><text x="0" y="16" text-anchor="middle" font-family="Jakarta" font-weight="800" font-size="44" fill="#E2B33C">IA</text></g>
          </svg>
        </div>
      </section>

      <!-- S2b · REVEAL -->
      <section id="R" class="scene clip" data-start="@S2" data-duration="@D2" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:100px;top:500px"></div><div class="grid"></div>
          <div id="rev">
            <svg class="emb" id="emb" viewBox="0 0 300 380" fill="none">
              <path class="e1" d="M150 10 L290 190 L150 370 L10 190 Z" stroke="#E2B33C" stroke-width="5"/>
              <path class="e2" d="M150 70 L245 190 L150 310 L55 190 Z" stroke="#E2B33C" stroke-width="3" opacity="0.8"/>
              <circle class="e3" cx="150" cy="190" r="58" fill="#13205C" stroke="#5B7CFF" stroke-width="4"/>
              <text class="e4" x="150" y="210" text-anchor="middle" font-family="Jakarta" font-weight="800" font-size="56" fill="#E2B33C">IA</text>
            </svg>
            <div class="t1" id="revk">CERTIFICATION</div>
            <div class="t2" id="revt"><span class="g">IA</span> BUSINESS<br />BUILDING</div>
            <div class="chips" id="revc"><span>Agents IA</span><span>Sites</span><span>Apps</span></div>
          </div>
        </div>
      </section>

      <!-- S3 · AGENT WHATSAPP -->
      <section id="S3" class="scene clip" data-start="@S3" data-duration="@D3" data-track-index="1">
        <div class="stage light"><div class="blob" style="right:-200px;top:-100px"></div><div class="grid"></div>
          <div class="kicker" style="top:250px">01 · Ton agent IA</div>
          <div class="kt" id="k4" data-line="s1" data-from="tu" style="top:310px; font-size:84px">Tu crées ton <span class="b">agent WhatsApp</span> qui vend <span class="g">à ta place</span></div>
          <div id="badge24">24h/24</div>
          <div class="card" id="chat">
            <div class="hd"><div class="av">IA</div><div><div class="nm">Ta Boutique</div><div class="st"><b></b>Agent IA · en ligne</div></div><div class="clock" id="clk">03:12</div></div>
            <div class="bd">
              <div class="m in" id="m1">Bonsoir, la robe bleue est encore dispo ?<small>03:12</small></div>
              <div class="typing" id="typ"><i></i><i></i><i></i></div>
              <div class="m out" id="m2">Oui ! Il en reste 2 en taille M. Je vous la réserve ?<small>03:12 ✓✓</small></div>
              <div class="m in" id="m3">Oui, je prends.<small>03:13</small></div>
              <div class="m out" id="m4">Parfait. Voici votre lien de paiement :<div class="pay">Payer 15 000 F →</div><small>03:13 ✓✓</small></div>
            </div>
          </div>
        </div>
      </section>

      <!-- S4 · SITE + MOBILE MONEY -->
      <section id="S4" class="scene clip" data-start="@S4" data-duration="@D4" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:-200px;top:300px"></div><div class="grid"></div>
          <div class="kicker" style="top:250px">02 · Ton site pro</div>
          <div class="kt" id="k5" data-line="s2" style="top:310px; font-size:84px">Ton <span class="g">site pro,</span> avec le paiement <span class="b">Mobile Money</span> intégré.</div>
          <div class="card" id="site">
            <div class="bar"><i></i><i></i><i></i><div class="u">tonbusiness.com</div></div>
            <div class="hero"><div class="a">Ta marque.<br />Ton site.</div><div class="c">Commander →</div></div>
            <div class="sheet" id="sheet">
              <div class="k">Paiement sécurisé</div><div class="amt">15 000 F</div>
              <div class="ops">
                <div class="op" id="op1"><i style="background:#FFCC00"></i>MTN MoMo</div>
                <div class="op"><i style="background:#0066B3"></i>Moov Money</div>
                <div class="op"><i style="background:#FF7900"></i>Orange Money</div>
                <div class="op"><i style="background:#1DC8FF"></i>Wave</div>
              </div>
            </div>
          </div>
          <div id="paid"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>Paiement reçu</div>
          <div id="tap4" class="tapdot" style="position:absolute;left:0;top:0;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,0.8);border:4px solid #fff;opacity:0;z-index:5"></div>
        </div>
      </section>

      <!-- S5 · APP + NO CODE -->
      <section id="S5" class="scene clip" data-start="@S5" data-duration="@D5" data-track-index="1">
        <div class="stage light"><div class="blob" style="left:200px;top:600px"></div><div class="grid"></div>
          <div class="kicker" style="top:250px">03 · Ton application</div>
          <div class="kt" id="k6" data-line="s3" style="top:310px; font-size:84px">Et ton <span class="b">application.</span> Sans écrire <span class="g">une seule ligne</span> de code.</div>
          <div id="phone"><div class="scr"><div class="ic"></div><div class="ic"></div><div class="ic"></div><div class="ic"></div><div class="ic mine" id="myapp">IA</div><div class="ic"></div><div class="ic"></div><div class="ic"></div><div class="ic"></div></div>
            <div class="lbl" id="plbl">Installée ✓</div><div class="prog"><i id="pbar"></i></div></div>
          <div id="nocode">&lt;/&gt;</div>
        </div>
      </section>

      <!-- S6 · FORMAT -->
      <section id="S6" class="scene clip" data-start="@S6" data-duration="@D6" data-track-index="1">
        <div class="stage dark"><div class="blob" style="right:-200px;top:500px"></div><div class="grid"></div>
          <div class="kt" id="k7" data-line="f1" style="top:300px; font-size:96px"><span class="g">8 modules,</span> 57 leçons, depuis ton <span class="b">téléphone.</span></div>
          <svg id="ring" viewBox="0 0 620 620" fill="none">
            <circle cx="310" cy="310" r="280" stroke="rgba(255,255,255,0.1)" stroke-width="18"/>
            <circle id="ringarc" cx="310" cy="310" r="280" stroke="#E2B33C" stroke-width="18" stroke-linecap="round" transform="rotate(-90 310 310)" stroke-dasharray="1759.3" stroke-dashoffset="1759.3"/>
          </svg>
          <div id="ringnum" style="position:absolute;left:50%;top:1150px;width:620px;height:620px;margin:-310px 0 0 -310px;display:flex;flex-direction:column;align-items:center;justify-content:center">
            <b id="rn" style="font-weight:800;font-size:220px;letter-spacing:-0.05em;line-height:0.9">0</b><span id="ru" style="font-weight:700;font-size:40px;color:#8C97C9">modules</span></div>
          <div id="lessons"><span class="pill" style="background:rgba(255,255,255,0.08);border:1.5px solid rgba(255,255,255,0.2)">Accès à vie</span><span class="pill" style="background:rgba(255,255,255,0.08);border:1.5px solid rgba(255,255,255,0.2)">À ton rythme</span></div>
        </div>
      </section>

      <!-- S7 · CERTIFICATE + CLIENTS -->
      <section id="S7" class="scene clip" data-start="@S7" data-duration="@D7" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:-100px;top:700px"></div><div class="grid"></div>
          <div class="kt" id="k8" data-line="f2" style="top:280px; font-size:76px">Et à la fin : ton <span class="g">certificat,</span> et ton plan pour décrocher <span class="b">tes 3 premiers clients.</span></div>
          <div class="card" id="cert"><div class="in"></div><div class="k">CERTIFICAT DE RÉUSSITE</div><div class="t">IA Business Building</div><div class="n">décerné à <b style="color:#0A1033">Ton Nom</b></div><div class="n" style="font-size:24px;margin-top:40px">EMK Blue Diamond</div><div class="seal">✓</div></div>
          <div id="clients">
            <div class="c"><i style="background:#5B7CFF"></i>Client n°1 · Site vitrine<em>✓</em></div>
            <div class="c"><i style="background:#E2B33C"></i>Client n°2 · Agent WhatsApp<em>✓</em></div>
            <div class="c"><i style="background:#2BD07E"></i>Client n°3 · Automatisation<em>✓</em></div>
          </div>
        </div>
      </section>

      <!-- S8 · PRICE -->
      <section id="S8" class="scene clip" data-start="@S8" data-duration="@D8" data-track-index="1">
        <div class="stage light"><div class="blob" style="right:-100px;top:200px"></div><div class="grid"></div>
          <div class="kt" id="k9" data-line="p1" style="top:280px; font-size:76px">Une agence te facture jusqu'à <span class="r">500 000 F</span> pour un site.</div>
          <div class="kt" id="k10" data-line="p2" style="top:560px; font-size:64px; color:#3A4478">Ici, tu apprends à le faire <span class="b">toi-même.</span></div>
          <div id="cmp">
            <div class="col ag" id="colag"><div class="val" style="color:#E04449">500 000 F</div><div class="bar"></div><div class="lab">Agence</div></div>
            <div class="col us" id="colus"><div id="old">35 000 F</div><div class="val" id="newp" style="color:#0A1033">35 000 F</div><div class="bar"></div><div class="lab">La formation</div></div>
          </div>
        </div>
      </section>

      <!-- S9 · PROOF + GUARANTEE -->
      <section id="S9" class="scene clip" data-start="@S9" data-duration="@D9" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:-200px;top:400px"></div><div class="grid"></div>
          <div class="kicker" style="top:250px">Ils ont déjà rejoint la formation</div>
          <div id="proof"><div class="big"><span id="cnt">0</span>+</div><div class="lab">inscrits</div></div>
          <div id="flags">
            <span class="pill"><i style="background:linear-gradient(90deg,#F77F00 33%,#fff 33% 66%,#009E60 66%)"></i>Côte d'Ivoire</span>
            <span class="pill"><i style="background:linear-gradient(90deg,#007A5E 33%,#CE1126 33% 66%,#FCD116 66%)"></i>Cameroun</span>
            <span class="pill"><i style="background:linear-gradient(90deg,#008751 40%,transparent 40%),linear-gradient(180deg,#FCD116 50%,#E8112D 50%)"></i>Bénin</span>
          </div>
          <div id="shield"><svg viewBox="0 0 24 24" fill="none" stroke="#2BD07E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/></svg><div><b>Satisfait ou remboursé</b><span>7 jours · sans question piège</span></div></div>
        </div>
      </section>

      <!-- S10 · END CARD -->
      <section id="S10" class="scene clip" data-start="@S10" data-duration="@D10" data-track-index="1">
        <div class="stage dark"><div class="blob" style="left:100px;top:300px"></div><div class="grid"></div>
          <div id="end">
            <div class="thumb" id="ethumb"><img src="assets/thumb.jpg" /></div>
            <div class="price" id="eprice"><b>4 999 F</b><s>35 000 F</s></div>
            <div class="cta" id="ecta">Rejoindre la formation →</div>
            <div class="meta" id="emeta">Mobile Money ou carte · Accès immédiat · Garantie 7 jours</div>
          </div>
          <div id="tap"></div>
        </div>
      </section>

      <div id="gcirc"></div>
      <div id="flash"></div>
      <div id="grain"></div>
      <div id="prog"></div>
      <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="@DUR" data-track-index="8" data-volume="1"></audio>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="@DUR" data-track-index="9" data-volume="1"></audio>
    </div>

    <script>
      (function () {
        const TIMING = /*TIMING*/;
        const CUTS = /*CUTS*/;
        const DUR = CUTS[CUTS.length - 1];
        const $ = (s) => document.querySelector(s);
        const $$ = (s) => Array.from(document.querySelectorAll(s));
        const EX = "expo.out";
        const norm = (s) => s.toLowerCase().replace(/[’]/g, "'").replace(/[^\p{L}\p{N}' ]/gu, "").trim();
        const line = (id) => TIMING.find((l) => l.id === id);
        const W = (id, w, n = 0) => { const l = line(id); const h = l.words.filter((x) => norm(x[2]).split(" ").includes(norm(w)) || norm(x[2]).startsWith(norm(w))); return (h[n] || l.words[0])[0]; };

        const tl = gsap.timeline({ paused: true });
        tl.fromTo("#grain", { x: 0, y: 0 }, { x: -40, y: 30, duration: 0.12, ease: "steps(1)", repeat: Math.max(0, Math.floor(DUR / 0.24) - 1), yoyo: true }, 0);
        tl.fromTo("#prog", { scaleX: 0 }, { scaleX: 1, duration: DUR, ease: "none" }, 0);

        // kinetic text: split each block into words; time every word on the matching spoken word
        $$(".kt").forEach((el) => {
          const l = line(el.dataset.line);
          // wrap words, preserving accent spans
          const nodes = Array.from(el.childNodes); el.innerHTML = "";
          nodes.forEach((n) => {
            const cls = n.nodeType === 1 ? n.className : "";
            const txt = n.textContent;
            txt.split(/\s+/).filter(Boolean).forEach((t) => { const s = document.createElement("span"); s.className = "w " + cls; s.textContent = t; el.appendChild(s); el.appendChild(document.createTextNode(" ")); });
          });
          let j = 0;
          if (el.dataset.from) { const k = l.words.findIndex((x) => norm(x[2]) === norm(el.dataset.from)); if (k >= 0) j = k; }
          el.querySelectorAll(".w").forEach((s) => {
            const w = norm(s.textContent).split(" ")[0];
            let t = null;
            for (let k = j; k < Math.min(l.words.length, j + 4); k++) {
              const toks = norm(l.words[k][2]).split(" ");
              if (toks.includes(w) || norm(l.words[k][2]) === w) { t = l.words[k][0]; j = toks[toks.length - 1] === w ? k + 1 : k; break; }
            }
            if (t === null) t = (l.words[Math.min(j, l.words.length - 1)] || l.words[0])[0];
            tl.fromTo(s, { opacity: 0, y: 26, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }, t - 0.05);
          });
        });

        // scene transitions: quick push + zoom (UGC energy)
        const ids = ["S1", "S2", "R", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"];
        CUTS.slice(1, -1).forEach((T, i) => {
          if (ids[i + 1] === "R") return; // gold circle handles this one
          tl.fromTo(`#${ids[i + 1]} .stage`, { yPercent: 100 }, { yPercent: 0, duration: 0.45, ease: "expo.out" }, T - 0.12);
          tl.to(`#${ids[i]} .stage`, { yPercent: -18, scale: 0.94, opacity: 0.4, duration: 0.45, ease: "expo.out" }, T - 0.12);
        });
        $$(".blob").forEach((b, i) => tl.fromTo(b, { x: 0, y: 0 }, { x: i % 2 ? -160 : 160, y: i % 2 ? 120 : -80, duration: 8, ease: "sine.inOut" }, Math.max(0, CUTS[Math.min(i, CUTS.length - 2)] - 0.3)));

        // S1
        tl.fromTo("#s1chat", { opacity: 0, y: 40, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.6)" }, W("h1", "l'ia"));
        tl.fromTo("#s1card", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.6, ease: EX }, W("h1", "mais") - 0.1);
        tl.fromTo("#s1card .bars i", { height: 12 }, { height: (i) => [40, 70, 30, 90, 55, 20, 12][i], duration: 0.6, ease: EX, stagger: 0.05 }, W("h1", "rapporte") - 0.3);
        tl.to("#s1card .bars i", { height: 12, duration: 0.4, ease: "power3.in", stagger: 0.03 }, W("h1", "franc") - 0.1);
        tl.fromTo("#s1v", { color: "#FFFFFF" }, { color: "#FF5A5F", duration: 0.2 }, W("h1", "franc"));
        tl.fromTo("#s1card", { x: 0 }, { x: 14, duration: 0.05, repeat: 5, yoyo: true, ease: "none" }, W("h1", "franc") + 0.05);

        // S2
        tl.fromTo("#orbit", { opacity: 0, scale: 0.7, rotate: -40 }, { opacity: 1, scale: 1, rotate: 0, duration: 1.0, ease: EX }, W("h2", "le"));
        tl.fromTo("#orbit", { rotate: 0 }, { rotate: 120, duration: 4, ease: "none" }, W("h2", "le") + 1.0);
        tl.to("#k2", { opacity: 0.35, duration: 0.4 }, W("h3", "personne") - 0.1);

        // gold circle → reveal
        const TR = CUTS[2];
        tl.set("#gcirc", { scale: 0 }, 0);
        tl.fromTo("#gcirc", { scale: 0 }, { scale: 1, duration: 0.5, ease: "power3.in" }, TR - 0.5);
        tl.to("#gcirc", { scale: 0, duration: 0.55, ease: "power3.out", transformOrigin: "50% 50%" }, TR + 0.02);
        tl.fromTo("#emb .e1", { strokeDasharray: 1000, strokeDashoffset: 1000 }, { strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut" }, TR + 0.05);
        tl.fromTo("#emb .e2", { strokeDasharray: 700, strokeDashoffset: 700 }, { strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }, TR + 0.2);
        tl.fromTo("#emb .e3, #emb .e4", { opacity: 0, scale: 0.4, transformOrigin: "150px 190px" }, { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(2)" }, TR + 0.4);
        tl.fromTo("#revk", { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 0.6, ease: EX }, W("s1", "certification") - 0.05);
        tl.fromTo("#revt", { opacity: 0, y: 50, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: EX }, W("s1", "ia") - 0.05);
        tl.fromTo("#revc span", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: EX, stagger: 0.12 }, W("s1", "building"));
        tl.fromTo("#flash", { opacity: 0.6 }, { opacity: 0, duration: 0.5, immediateRender: false }, TR);

        // S3 agent
        tl.fromTo("#chat", { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.6, ease: EX }, CUTS[3] - 0.1);
        tl.fromTo("#m1", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.6)" }, W("s1", "agent") - 0.2);
        tl.fromTo("#typ", { opacity: 0 }, { opacity: 1, duration: 0.15 }, W("s1", "whatsapp"));
        tl.fromTo("#typ i", { y: 0 }, { y: -8, duration: 0.18, ease: "sine.inOut", stagger: 0.08, repeat: 3, yoyo: true }, W("s1", "whatsapp"));
        tl.to("#typ", { opacity: 0, height: 0, padding: 0, duration: 0.1 }, W("s1", "vend") - 0.05);
        tl.fromTo("#m2", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.6)" }, W("s1", "vend") - 0.05);
        tl.fromTo("#m3", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.6)" }, W("s1", "place"));
        tl.fromTo("#m4", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.6)" }, W("s1", "24") + 0.1);
        tl.fromTo("#badge24", { opacity: 0, scale: 0.5, rotate: -10 }, { opacity: 1, scale: 1, rotate: -4, duration: 0.5, ease: "back.out(2.5)" }, W("s1", "24") - 0.05);
        tl.fromTo("#clk", { opacity: 0.4 }, { opacity: 1, duration: 0.3, repeat: 3, yoyo: true }, W("s1", "agent"));

        // S4 site
        tl.fromTo("#site", { opacity: 0, y: 140, rotateX: 18, transformPerspective: 2000 }, { opacity: 1, y: 0, rotateX: 0, duration: 0.6, ease: EX }, CUTS[4] - 0.1);
        tl.fromTo("#sheet", { yPercent: 100 }, { yPercent: 0, duration: 0.5, ease: EX }, W("s2", "paiement") - 0.15);
        tl.fromTo("#site .op", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: EX, stagger: 0.08 }, W("s2", "mobile") - 0.1);
        tl.fromTo("#tap4", { opacity: 0, scale: 1.6, x: 300, y: 1420 }, { opacity: 1, scale: 1, x: 260, y: 1360, duration: 0.3, ease: EX }, W("s2", "money"));
        tl.to("#tap4", { scale: 0.8, duration: 0.1, yoyo: true, repeat: 1 }, W("s2", "intégré") - 0.1);
        tl.to("#op1", { borderColor: "#5B7CFF", backgroundColor: "#EEF2FF", duration: 0.15 }, W("s2", "intégré") - 0.05);
        tl.to("#tap4", { opacity: 0, duration: 0.2 }, W("s2", "intégré") + 0.2);
        tl.fromTo("#paid", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.5)" }, W("s2", "intégré") + 0.15);

        // S5 app
        tl.fromTo("#phone", { opacity: 0, y: 200, rotate: 6 }, { opacity: 1, y: 0, rotate: 0, duration: 0.6, ease: EX }, CUTS[5] - 0.1);
        tl.fromTo("#myapp", { scale: 0, rotate: -30 }, { scale: 1, rotate: 0, duration: 0.5, ease: "back.out(2.5)" }, W("s3", "application"));
        tl.fromTo("#pbar", { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "power2.inOut" }, W("s3", "application") + 0.1);
        tl.fromTo("#plbl", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: EX }, W("s3", "application") + 1.0);
        tl.fromTo("#nocode", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }, W("s3", "écrire"));
        tl.fromTo("#nocode", { "--s": 0 }, { "--s": 1, duration: 0.3, ease: "power3.out" }, W("s3", "code") - 0.05);

        // S6 ring
        tl.fromTo("#ringarc", { strokeDashoffset: 1759.3 }, { strokeDashoffset: 0, duration: 1.0, ease: "power2.out" }, CUTS[6]);
        const rn = $("#rn"), ru = $("#ru"), o6 = { v: 0 };
        tl.fromTo(o6, { v: 0 }, { v: 8, duration: 0.8, ease: "power2.out", onUpdate: () => { rn.textContent = Math.round(o6.v); } }, W("f1", "8"));
        const o6b = { v: 8 };
        tl.fromTo(o6b, { v: 8 }, { v: 57, duration: 0.8, ease: "power2.out", immediateRender: false, onUpdate: () => { rn.textContent = Math.round(o6b.v); ru.textContent = "leçons"; } }, W("f1", "57"));
        tl.fromTo("#lessons .pill", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: EX, stagger: 0.12 }, W("f1", "téléphone") - 0.1);

        // S7 cert + clients
        tl.fromTo("#cert", { opacity: 0, rotateY: -70, transformPerspective: 2000 }, { opacity: 1, rotateY: 0, duration: 0.7, ease: EX }, W("f2", "certificat") - 0.1);
        tl.fromTo("#cert .seal", { scale: 0, rotate: -90 }, { scale: 1, rotate: 0, duration: 0.5, ease: "back.out(2.5)" }, W("f2", "certificat") + 0.4);
        tl.fromTo("#flash", { opacity: 0.35 }, { opacity: 0, duration: 0.4, immediateRender: false }, W("f2", "certificat"));
        $$("#clients .c").forEach((c, i) => tl.fromTo(c, { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.35, ease: EX }, W("f2", "premiers") - 0.1 + i * 0.22));

        // S8 price
        tl.fromTo("#colag .bar", { scaleY: 0 }, { scaleY: 1, duration: 0.7, ease: EX }, W("p1", "500"));
        tl.fromTo("#colag .val, #colag .lab", { opacity: 0 }, { opacity: 1, duration: 0.3 }, W("p1", "500"));
        tl.fromTo("#colus", { opacity: 0 }, { opacity: 1, duration: 0.3 }, W("p2", "ici"));
        tl.fromTo("#colus .bar", { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: EX }, W("p2", "ici"));
        const np = $("#newp"), o8 = { v: 35000 };
        tl.fromTo(o8, { v: 35000 }, { v: 4999, duration: 1.2, ease: "power3.inOut", onUpdate: () => { np.textContent = Math.round(o8.v).toLocaleString("fr-FR").replace(/ | /g, " ") + " F"; } }, W("p2", "4"));
        tl.to("#newp", { color: "#B8891F", scale: 1.15, duration: 0.3, ease: "back.out(3)" }, W("p2", "4") + 1.2);
        tl.fromTo("#old", { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, W("p2", "35"));
        tl.fromTo("#old", { "--s": 0 }, { "--s": 1, duration: 0.3, ease: "power3.out" }, W("p2", "35") + 0.25);
        tl.to("#k9", { opacity: 0.35, duration: 0.4 }, W("p2", "ici") - 0.1);

        // S9 proof
        const cnt = $("#cnt"), o9 = { v: 0 };
        tl.fromTo(o9, { v: 0 }, { v: 100, duration: 1.0, ease: "power3.out", onUpdate: () => { cnt.textContent = Math.round(o9.v); } }, W("sp", "100"));
        tl.fromTo("#proof", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.4, ease: EX }, W("sp", "déjà") - 0.1);
        $$("#flags .pill").forEach((p, i) => tl.fromTo(p, { opacity: 0, y: 24, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)" }, [W("sp", "côte"), W("sp", "cameroun"), W("sp", "bénin")][i] - 0.08));
        tl.fromTo("#shield", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.45, ease: EX }, W("g", "satisfait") - 0.1);

        // S10 end card
        tl.fromTo("#ethumb", { opacity: 0, scale: 0.85, y: 60 }, { opacity: 1, scale: 1, y: 0, duration: 0.6, ease: EX }, CUTS[10] - 0.1);
        tl.fromTo("#eprice", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: EX }, CUTS[10] + 0.2);
        tl.fromTo("#ecta", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2.2)" }, W("cta", "clique") - 0.05);
        tl.fromTo("#emeta", { opacity: 0 }, { opacity: 1, duration: 0.4 }, W("cta", "commence"));
        tl.fromTo("#tap", { opacity: 0, x: 760, y: 1500, scale: 1.4 }, { opacity: 1, x: 500, y: 1240, scale: 1, duration: 0.45, ease: EX }, W("cta", "lien") - 0.2);
        tl.to("#tap", { scale: 0.75, duration: 0.12, yoyo: true, repeat: 1 }, W("cta", "lien") + 0.3);
        tl.to("#ecta", { scale: 0.95, duration: 0.12, yoyo: true, repeat: 1 }, W("cta", "lien") + 0.3);
        tl.to("#ecta", { boxShadow: "0 0 0 24px rgba(226,179,60,0.0), 0 30px 80px rgba(226,179,60,0.7)", duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut" }, W("cta", "commence"));

        window.__timelines["main"] = tl;
      })();
    </script>
  </body>
</html>
