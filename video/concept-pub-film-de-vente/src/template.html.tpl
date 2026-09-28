<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Concept Pub — Film de vente</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Cormorant Garamond"; font-weight: 500; font-style: normal; src: url("assets/fonts/cormorant-garamond-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "Cormorant Garamond"; font-weight: 600; font-style: normal; src: url("assets/fonts/cormorant-garamond-latin-600-normal.woff2") format("woff2"); }
      @font-face { font-family: "Cormorant Garamond"; font-weight: 500; font-style: italic; src: url("assets/fonts/cormorant-garamond-latin-500-italic.woff2") format("woff2"); }
      @font-face { font-family: "Manrope"; font-weight: 300; src: url("assets/fonts/manrope-latin-300-normal.woff2") format("woff2"); }
      @font-face { font-family: "Manrope"; font-weight: 400; src: url("assets/fonts/manrope-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "Manrope"; font-weight: 600; src: url("assets/fonts/manrope-latin-600-normal.woff2") format("woff2"); }
      @font-face { font-family: "IBM Plex Mono"; font-weight: 400; src: url("assets/fonts/ibm-plex-mono-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "IBM Plex Mono"; font-weight: 500; src: url("assets/fonts/ibm-plex-mono-latin-500-normal.woff2") format("woff2"); }
      :root {
        --noir: #0B0A09; --noir-800: #1F1D18; --noir-700: #2E2B24; --noir-600: #46423A; --noir-500: #6B6559; --noir-400: #948D7E; --noir-300: #BBB4A6; --noir-200: #DCD6C9;
        --ivory: #FBF8F1; --gold: #B5934E; --gold-300: #DBC796; --gold-400: #C7AC6F; --gold-700: #836935; --gold-800: #5E4A24; --danger: #9B3B2E;
        --gg: linear-gradient(135deg, #DBC796 0%, #B5934E 42%, #836935 100%);
        --serif: "Cormorant Garamond", Georgia, serif; --sans: "Manrope", system-ui, sans-serif; --mono: "IBM Plex Mono", ui-monospace, monospace;
      }
      * { box-sizing: border-box; }
      body { margin: 0; background: var(--noir); color: var(--ivory); font-family: var(--sans); }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--noir); }
      #grain { position: absolute; inset: -60px; pointer-events: none; z-index: 60; opacity: 0.07; mix-blend-mode: overlay;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.2 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); }
      #vignette { position: absolute; inset: 0; pointer-events: none; z-index: 59; background: radial-gradient(ellipse 78% 72% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.38) 100%); }
      #flash { position: absolute; inset: 0; z-index: 58; pointer-events: none; opacity: 0; background: radial-gradient(ellipse at 50% 50%, rgba(219,199,150,0.5), rgba(181,147,78,0) 70%); }

      .scene { position: absolute; inset: 0; }
      .stage { position: absolute; inset: 0; overflow: hidden; }
      .stage.noir { background: radial-gradient(ellipse 90% 80% at 50% 38%, #1B1915 0%, var(--noir) 70%); color: var(--ivory); }
      .stage.ivory { background: radial-gradient(ellipse 90% 80% at 50% 38%, #FFFDF8 0%, var(--ivory) 60%, #F1ECDF 100%); color: var(--noir); }
      .cam { position: absolute; inset: 0; }
      .edge { position: absolute; top: 0; bottom: 0; left: 0; width: 12px; background: var(--gg); z-index: 5; box-shadow: 0 0 60px 10px rgba(181,147,78,0.35); opacity: 0; }
      .abs { position: absolute; }
      .eyebrow { font-family: var(--mono); font-size: 20px; letter-spacing: 0.28em; text-transform: uppercase; color: var(--gold); display: flex; align-items: center; gap: 20px; white-space: nowrap; }
      .eyebrow .rule { display: block; width: 56px; height: 1px; background: currentColor; transform-origin: left center; }
      .ivory .eyebrow { color: var(--gold-800); }
      .serif { font-family: var(--serif); font-weight: 500; letter-spacing: -0.02em; line-height: 1; }
      .it { font-style: italic; color: var(--gold); }
      .ivory .it { color: var(--gold-700); }
      .mask { display: inline-block; overflow: hidden; vertical-align: top; padding: 0 0.05em 0.14em; margin-bottom: -0.14em; }
      .mask > .in { display: inline-block; }
      .ch { display: inline-block; }
      .center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }

      /* browser + phone frames */
      .browser { position: absolute; border-radius: 14px; overflow: hidden; background: #0B0A09; box-shadow: 0 60px 140px rgba(0,0,0,0.55), 0 0 0 1px rgba(245,241,232,0.12); }
      .ivory .browser { box-shadow: 0 50px 120px rgba(60,45,20,0.22), 0 0 0 1px rgba(11,10,9,0.08); }
      .browser .bar { position: absolute; left: 0; right: 0; top: 0; height: 44px; background: #1F1D18; display: flex; align-items: center; gap: 9px; padding: 0 18px; z-index: 2; }
      .browser .bar i { display: block; width: 12px; height: 12px; border-radius: 50%; background: rgba(245,241,232,0.18); }
      .browser .bar .url { position: absolute; left: 50%; top: 9px; width: 340px; margin-left: -170px; height: 26px; border-radius: 999px; background: rgba(245,241,232,0.07); font-family: var(--mono); font-size: 14px; letter-spacing: 0.06em; color: rgba(245,241,232,0.55); display: flex; align-items: center; justify-content: center; }
      .browser .view { position: absolute; top: 44px; left: 0; right: 0; bottom: 0; overflow: hidden; }
      .browser .view img { position: absolute; left: 0; top: 0; width: 100%; display: block; }
      .phone { position: absolute; width: 300px; height: 650px; border-radius: 46px; background: #0B0A09; border: 9px solid #26231D; overflow: hidden; box-shadow: 0 50px 110px rgba(0,0,0,0.6), 0 0 0 1px rgba(219,199,150,0.25); }
      .phone img { position: absolute; left: 0; top: 0; width: 100%; display: block; }
      .phone .notch { position: absolute; left: 50%; top: 10px; width: 96px; height: 26px; margin-left: -48px; border-radius: 20px; background: #000; z-index: 2; }
      .pill { display: inline-flex; align-items: center; gap: 14px; height: 64px; padding: 0 30px; border-radius: 999px; border: 1px solid rgba(219,199,150,0.5); font-family: var(--sans); font-size: 24px; white-space: nowrap; }
      .ivory .pill { border-color: rgba(131,105,53,0.45); }
      .pill.gold { background: var(--gg); color: var(--noir); border: 0; font-weight: 600; }
      .chk { width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid rgba(245,241,232,0.25); position: relative; flex: 0 0 auto; }
      .chk .f { position: absolute; inset: -1.5px; border-radius: 50%; background: var(--gg); }
      .chk svg { position: absolute; inset: 0; width: 100%; height: 100%; }

      /* captions */
      #caps { position: absolute; left: 0; right: 0; bottom: 46px; height: 60px; z-index: 55; pointer-events: none; }
      #caps .cap { position: absolute; left: 50%; top: 0; transform: translateX(-50%); white-space: nowrap; height: 58px; padding: 0 28px; border-radius: 999px; display: flex; align-items: center;
        background: rgba(11,10,9,0.62); color: #FBF8F1; font-family: var(--sans); font-weight: 400; font-size: 29px; letter-spacing: 0.005em; opacity: 0; box-shadow: 0 0 0 1px rgba(219,199,150,0.14); }

      /* A — hook */
      #A .ring { position: absolute; left: 50%; top: 50%; width: 840px; height: 840px; margin: -470px 0 0 -420px; }
      #A .p1 { gap: 30px; margin-top: -90px; }
      #A .p1 .l1 { font-size: 76px; color: var(--noir-300); }
      #A .p1 .big { font-size: 250px; }
      #A .p2 { gap: 26px; margin-top: -90px; }
      #A .p2 .a { position: relative; font-size: 110px; color: var(--noir-400); }
      #A .p2 .a .strike { position: absolute; left: -2%; right: -2%; top: 52%; height: 5px; background: var(--danger); transform-origin: left center; }
      #A .p2 .b { font-size: 200px; }

      /* B — pain */
      #B .card { position: absolute; border-radius: 14px; background: #1A1916; border: 1px solid rgba(245,241,232,0.08); filter: grayscale(1); }
      #B .folio { left: 170px; top: 150px; width: 600px; height: 400px; padding: 30px; }
      #B .folio .ph { height: 180px; border-radius: 8px; background: #2A2825; }
      #B .folio .ln { height: 14px; border-radius: 7px; background: #2A2825; margin-top: 18px; }
      #B .folio .tag { position: absolute; right: 24px; top: 24px; font-family: var(--mono); font-size: 16px; letter-spacing: 0.2em; color: #948D7E; padding: 8px 12px; border: 1px solid #46423A; border-radius: 4px; }
      #B .folio .cap2 { position: absolute; left: 30px; bottom: 26px; font-family: var(--mono); font-size: 16px; letter-spacing: 0.12em; color: #6B6559; }
      #B .bub { position: absolute; right: 170px; max-width: 620px; padding: 22px 28px; border-radius: 22px 22px 6px 22px; background: #2B2925; color: #DCD6C9; font-family: var(--sans); font-size: 27px; line-height: 1.35; }
      #B .bub small { display: block; margin-top: 8px; font-family: var(--mono); font-size: 14px; letter-spacing: 0.1em; color: #6B6559; text-align: right; }
      #B .mail { position: absolute; left: 300px; width: 640px; height: 84px; border-radius: 14px; background: #201E1A; border: 1px solid rgba(245,241,232,0.08); display: flex; align-items: center; gap: 20px; padding: 0 26px; font-family: var(--sans); font-size: 23px; color: #BBB4A6; }
      #B .mail b { font-weight: 600; color: #DCD6C9; }
      #B .mail .ic { width: 38px; height: 38px; border-radius: 8px; border: 1.5px solid #6B6559; flex: 0 0 auto; position: relative; }
      #B .mail .ic::after { content: ""; position: absolute; left: 6px; right: 6px; top: 9px; height: 12px; border-left: 1.5px solid #6B6559; border-bottom: 1.5px solid #6B6559; transform: skewY(-28deg) rotate(-45deg) scale(0.7); }
      #B .mail .dot { margin-left: auto; width: 12px; height: 12px; border-radius: 50%; background: var(--danger); }

      /* C — reveal */
      #C .rays { position: absolute; left: 50%; top: 50%; width: 1700px; height: 1700px; margin: -850px 0 0 -850px; background: radial-gradient(circle, rgba(181,147,78,0.22) 0%, rgba(181,147,78,0.05) 32%, rgba(0,0,0,0) 60%); }
      #C .grp { gap: 30px; }
      #C .seal { width: 150px; height: 150px; }
      #C .word { font-size: 190px; letter-spacing: -0.005em; }
      #C .sub { font-size: 58px; color: var(--noir-200); }
      #C .tags { display: flex; gap: 22px; margin-top: 18px; }

      /* D — look */
      #D .swatches { position: absolute; left: 1430px; top: 230px; display: flex; flex-direction: column; gap: 44px; }
      #D .sw { display: flex; align-items: center; gap: 28px; }
      #D .sw .c { width: 132px; height: 132px; border-radius: 50%; box-shadow: 0 0 0 1px rgba(245,241,232,0.18); }
      #D .sw .n { font-family: var(--serif); font-size: 58px; line-height: 1; }
      #D .sw .h { margin-top: 8px; font-family: var(--mono); font-size: 17px; letter-spacing: 0.2em; color: var(--noir-400); }
      #D .title { left: 150px; top: 96px; }

      /* E — services */
      #E .left { left: 140px; top: 170px; width: 520px; }
      #E .nine { margin-top: 36px; font-size: 330px; line-height: 0.9; color: var(--gold-700); font-style: italic; }
      #E .met { margin-top: 34px; font-size: 86px; }
      #E .chips { left: 140px; top: 690px; width: 560px; display: flex; flex-wrap: wrap; gap: 16px; }

      /* F — reel */
      #F .bars { position: absolute; left: 0; right: 0; height: 170px; background: #000; z-index: 4; }

      /* G — sells */
      #G .noirdisc { position: absolute; inset: 0; background: radial-gradient(ellipse 90% 80% at 50% 45%, #1B1915 0%, var(--noir) 70%); }
      #G .l1 { font-size: 118px; white-space: nowrap; }
      #G .l2 { font-size: 330px; margin-top: 30px; }

      /* H — devis */
      #H .left { left: 140px; top: 150px; width: 560px; }
      #H .left h2 { margin: 26px 0 0; font-size: 92px; }
      #H .list { margin-top: 50px; display: flex; flex-direction: column; gap: 22px; }
      #H .row { display: flex; align-items: center; gap: 24px; font-family: var(--serif); font-size: 50px; }
      #H .min { left: 140px; top: 790px; display: flex; align-items: baseline; gap: 26px; }
      #H .min .n { font-size: 124px; color: var(--gold); font-style: italic; }
      #H .min .t { font-family: var(--mono); font-size: 19px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--noir-400); line-height: 1.7; }

      /* I — rdv */
      #I .right { left: 1320px; top: 250px; width: 500px; }
      #I .right h2 { margin: 26px 0 0; font-size: 96px; }
      #I .opts { margin-top: 50px; display: flex; flex-direction: column; gap: 20px; align-items: flex-start; }

      /* J — client */
      #J .left { left: 140px; top: 170px; width: 500px; }
      #J .left h2 { margin: 26px 0 0; font-size: 80px; }
      #J .co { margin-top: 56px; display: flex; flex-direction: column; gap: 34px; }
      #J .co .it2 { display: flex; flex-direction: column; gap: 12px; }
      #J .co .k { font-family: var(--mono); font-size: 18px; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold); }
      #J .co .v { font-family: var(--serif); font-size: 46px; line-height: 1; }
      #J .co .bar { width: 380px; height: 3px; background: rgba(245,241,232,0.12); }
      #J .co .bar i { display: block; height: 100%; width: 100%; background: var(--gg); transform-origin: left center; }

      /* K — benefits */
      #K .lines { gap: 34px; margin-top: -60px; }
      #K .ln { font-size: 150px; white-space: nowrap; }

      /* M — design system */
      #M .title { left: 140px; top: 96px; }
      #M .title h2 { margin: 22px 0 0; font-size: 84px; }
      #M .grid { position: absolute; left: 140px; right: 140px; top: 330px; height: 580px; display: grid; grid-template-columns: 1.25fr 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 26px; }
      #M .panel { position: relative; border-radius: 16px; background: #FFFFFF; border: 1px solid #E6E0D3; box-shadow: 0 20px 60px rgba(60,45,20,0.08); padding: 28px 32px; overflow: hidden; }
      #M .panel .k { font-family: var(--mono); font-size: 16px; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold-800); }
      #M .sws { display: flex; gap: 12px; margin-top: 26px; }
      #M .sws i { display: block; width: 58px; height: 150px; border-radius: 8px; box-shadow: inset 0 0 0 1px rgba(11,10,9,0.08); }
      #M .aa { display: flex; align-items: flex-end; gap: 30px; margin-top: 30px; }
      #M .aa .big { font-size: 130px; line-height: 1; }
      #M .aa .fams { font-family: var(--sans); font-size: 19px; line-height: 1.9; color: var(--noir-500); padding-bottom: 12px; }
      #M .comps { margin-top: 22px; display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
      #M .btn { height: 52px; padding: 0 24px; border-radius: 999px; display: inline-flex; align-items: center; font-family: var(--sans); font-weight: 600; font-size: 18px; }
      #M .btn.n { background: var(--noir); color: var(--ivory); }
      #M .btn.g { background: var(--gg); color: var(--noir); }
      #M .btn.o { border: 1px solid #DCD6C9; color: var(--noir); font-weight: 400; }
      #M .sw2 { width: 64px; height: 36px; border-radius: 999px; background: var(--gold); position: relative; }
      #M .sw2::after { content: ""; position: absolute; right: 4px; top: 4px; width: 28px; height: 28px; border-radius: 50%; background: #fff; }
      #M .inp { width: 250px; height: 52px; border-radius: 6px; border: 1.5px solid #DCD6C9; font-family: var(--sans); font-size: 17px; color: var(--noir-400); display: flex; align-items: center; padding: 0 16px; }
      #M .brand { position: relative; height: 110px; margin-top: 18px; }
      #M .brand .w { position: absolute; left: 0; top: 0; font-size: 76px; white-space: nowrap; }
      #M .brand .w2 { color: var(--gold-700); font-style: italic; }
      #M .svc { font-family: var(--sans); font-size: 19px; color: var(--noir-500); display: flex; gap: 10px; flex-wrap: wrap; }
      #M .svc span { padding: 6px 14px; border-radius: 999px; border: 1px solid #E6E0D3; }
      #M .price { position: relative; height: 120px; margin-top: 30px; }
      #M .price .p { position: absolute; left: 0; top: 0; font-size: 92px; white-space: nowrap; }
      #M .price .p small { font-family: var(--mono); font-size: 22px; letter-spacing: 0.1em; color: var(--noir-500); margin-left: 10px; }

      /* N — offer */
      #N .title { left: 150px; top: 110px; }
      #N .title h2 { margin: 24px 0 0; font-size: 90px; }
      #N .cards { position: absolute; left: 150px; right: 150px; top: 390px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 36px; }
      #N .card { position: relative; height: 470px; border-radius: 18px; background: linear-gradient(180deg, #1F1D18, #151410); border: 1px solid rgba(245,241,232,0.1); overflow: hidden; }
      #N .card .thumb { position: absolute; left: 30px; right: 30px; top: 30px; height: 250px; border-radius: 10px; overflow: hidden; background: #0B0A09; }
      #N .card .thumb img { width: 100%; display: block; }
      #N .card .num { position: absolute; left: 34px; top: 312px; font-family: var(--mono); font-size: 18px; letter-spacing: 0.26em; color: var(--gold); }
      #N .card .t { position: absolute; left: 32px; right: 32px; top: 350px; font-size: 58px; }
      #N .weeks { gap: 40px; }
      #N .weeks .l { font-size: 104px; white-space: nowrap; }
      #N .prog { width: 900px; display: flex; align-items: center; gap: 26px; }
      #N .prog .tr { flex: 1; height: 3px; background: rgba(245,241,232,0.12); }
      #N .prog .tr i { display: block; height: 100%; width: 100%; background: var(--gg); transform-origin: left center; }
      #N .prog .pc { font-family: var(--mono); font-size: 24px; letter-spacing: 0.1em; color: var(--gold); width: 90px; text-align: right; }
      #N .plate { margin-top: 20px; height: 120px; padding: 0 50px; border-radius: 16px; border: 1px dashed rgba(219,199,150,0.6); display: flex; align-items: center; font-size: 84px; }
      #N .plate .caret { display: inline-block; width: 3px; height: 76px; background: var(--gold); margin-left: 8px; }

      /* O — outro */
      #O .rays { position: absolute; left: 50%; top: 50%; width: 1700px; height: 1700px; margin: -850px 0 0 -850px; background: radial-gradient(circle, rgba(181,147,78,0.22) 0%, rgba(181,147,78,0.05) 32%, rgba(0,0,0,0) 60%); }
      #O .grp { gap: 28px; margin-top: -40px; }
      #O .seal { width: 140px; height: 140px; }
      #O .word { font-size: 176px; }
      #O .rule { width: 64px; height: 1px; background: var(--gg); }
      #O .tag { font-style: italic; font-size: 66px; padding: 0 0.05em 0.1em; background: linear-gradient(100deg, #836935 0%, #B5934E 30%, #F4ECD8 50%, #B5934E 70%, #836935 100%); background-size: 300% 100%; background-position: 100% 0; -webkit-background-clip: text; background-clip: text; color: transparent; }
      #O .meta { font-family: var(--mono); font-size: 19px; letter-spacing: 0.24em; text-transform: uppercase; color: var(--noir-400); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="108">

      <!-- A · HOOK -->
      <section id="A" class="scene clip" data-start="@S0" data-duration="@D0" data-track-index="1">
        <div class="stage noir"><div class="cam">
          <svg class="ring" viewBox="0 0 840 840" fill="none">
            <circle cx="420" cy="420" r="400" stroke="rgba(245,241,232,0.08)" stroke-width="1.5"></circle>
            <circle id="A-ring" cx="420" cy="420" r="400" stroke="#B5934E" stroke-width="2" transform="rotate(-90 420 420)" stroke-dasharray="2513.3" stroke-dashoffset="2513.3"></circle>
          </svg>
          <div class="center p1" id="A-p1">
            <div class="serif l1"><span class="mask"><span class="in">Un</span></span> <span class="mask"><span class="in">client</span></span> <span class="mask"><span class="in">vous</span></span> <span class="mask"><span class="in">juge</span></span> <span class="mask"><span class="in">en</span></span></div>
            <div class="serif big"><span class="mask"><span class="in">3</span></span> <span class="mask"><span class="in it">secondes.</span></span></div>
          </div>
          <div class="center p2" id="A-p2">
            <div class="serif a"><span class="mask"><span class="in">Pas sur votre talent.</span></span><span class="strike" id="A-strike"></span></div>
            <div class="serif b"><span class="mask"><span class="in">Sur votre</span></span> <span class="mask"><span class="in it">site.</span></span></div>
          </div>
        </div></div>
      </section>

      <!-- B · PAIN -->
      <section id="B" class="scene clip" data-start="@S1" data-duration="@D1" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam" id="B-cam">
          <div class="card folio" id="B-folio"><div class="ph"></div><div class="ln" style="width:80%"></div><div class="ln" style="width:60%"></div><div class="ln" style="width:70%"></div>
            <div class="tag" id="B-fige">FIGÉ</div><div class="cap2">Portfolio · mis à jour en 2019</div></div>
          <div class="bub" style="top:150px">Bonjour, c’est combien pour une affiche ?<small>09:12</small></div>
          <div class="bub" style="top:300px">Vous m’envoyez le devis quand ?<small>11:40</small></div>
          <div class="bub" style="top:450px">Je relance pour le devis…<small>Hier · 18:05</small></div>
          <div class="mail" style="top:640px"><span class="ic"></span><span><b>RE: RE: RE:</b> fichiers finaux (v7)</span><span class="dot"></span></div>
          <div class="mail" style="top:745px; left:380px"><span class="ic"></span><span><b>Échec d’envoi</b> — pièce jointe trop lourde</span><span class="dot"></span></div>
          <div class="mail" style="top:850px; left:460px"><span class="ic"></span><span><b>Client</b> — c’est laquelle, la dernière version ?</span><span class="dot"></span></div>
        </div></div>
      </section>

      <!-- C · REVEAL -->
      <section id="C" class="scene clip" data-start="@S2" data-duration="@D2" data-track-index="1">
        <div class="stage noir"><div class="cam">
          <div class="rays" id="C-rays"></div>
          <div class="center grp" id="C-grp">
            <svg class="seal" id="C-seal" viewBox="0 0 120 120" fill="none"><g stroke="#B5934E" fill="#B5934E">
              <circle class="c1" cx="60" cy="60" r="54" stroke-width="1.25" fill="none" opacity="0.55"></circle><circle class="c2" cx="60" cy="60" r="46" stroke-width="1.25" fill="none"></circle>
              <path class="fv" d="M60 34 L66 60 L60 86 L54 60 Z" stroke="none"></path><path class="fh" d="M34 60 L60 54 L86 60 L60 66 Z" stroke="none" opacity="0.62"></path>
              <line class="tk" x1="60" y1="6" x2="60" y2="14" stroke-width="1.25"></line><line class="tk" x1="60" y1="106" x2="60" y2="114" stroke-width="1.25"></line><line class="tk" x1="6" y1="60" x2="14" y2="60" stroke-width="1.25"></line><line class="tk" x1="106" y1="60" x2="114" y2="60" stroke-width="1.25"></line></g></svg>
            <div class="serif word split" id="C-word">Concept Pub</div>
            <div class="serif sub" id="C-sub">Le site vitrine <span class="it">haut de gamme</span> des métiers de l’image</div>
            <div class="tags" id="C-tags"><span class="pill">Studios de création</span><span class="pill">Agences de communication</span><span class="pill">Boîtes de production</span></div>
          </div>
        </div></div>
      </section>

      <!-- D · LOOK -->
      <section id="D" class="scene clip" data-start="@S3" data-duration="@D3" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="abs title" id="D-title"><div class="eyebrow"><span class="rule"></span><span>Direction artistique</span></div></div>
          <div class="browser" id="D-br" style="left:300px; top:150px; width:1320px; height:869px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio</div></div><div class="view"><img src="assets/img/v-hero.jpg" /></div></div>
          <div class="swatches" id="D-sw">
            <div class="sw"><div class="c" style="background:#0B0A09"></div><div><div class="n">Noir</div><div class="h">#0B0A09</div></div></div>
            <div class="sw"><div class="c" style="background:#FBF8F1"></div><div><div class="n">Ivoire</div><div class="h">#FBF8F1</div></div></div>
            <div class="sw"><div class="c" style="background:linear-gradient(135deg,#DBC796,#B5934E 45%,#836935)"></div><div><div class="n it">Or</div><div class="h">#B5934E</div></div></div>
          </div>
        </div></div>
      </section>

      <!-- E · SERVICES -->
      <section id="E" class="scene clip" data-start="@S4" data-duration="@D4" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="abs left">
            <div class="eyebrow"><span class="rule"></span><span>Prestations</span></div>
            <div class="serif nine" id="E-nine">9</div>
            <div class="serif met"><span class="mask"><span class="in">métiers,</span></span> <span class="mask"><span class="in it">un site</span></span></div>
          </div>
          <div class="abs chips" id="E-chips"><span class="pill">Affiches</span><span class="pill">Tournage</span><span class="pill">Motion design</span><span class="pill">Podcast</span></div>
          <div class="browser" id="E-br" style="left:790px; top:140px; width:1000px; height:669px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/prestations</div></div><div class="view"><img id="E-img" src="assets/img/s-prestations.jpg" /></div></div>
        </div></div>
      </section>

      <!-- F · REEL -->
      <section id="F" class="scene clip" data-start="@S5" data-duration="@D5" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="browser" id="F-br" style="left:260px; top:110px; width:1400px; height:919px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/realisations</div></div>
            <div class="view"><img id="F-i1" src="assets/img/v-reel1.jpg" /><img id="F-i2" src="assets/img/v-reel2.jpg" /></div></div>
          <div class="bars" id="F-top" style="top:0"></div><div class="bars" id="F-bot" style="bottom:0"></div>
        </div></div>
      </section>

      <!-- G · SELLS -->
      <section id="G" class="scene clip" data-start="@S6" data-duration="@D6" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="noirdisc" id="G-disc"></div>
          <div class="center">
            <div class="serif l1" id="G-l1"><span class="mask"><span class="in">Il</span></span> <span class="mask"><span class="in">ne</span></span> <span class="mask"><span class="in">se</span></span> <span class="mask"><span class="in">contente</span></span> <span class="mask"><span class="in">pas</span></span> <span class="mask"><span class="in">de</span></span> <span class="mask"><span class="in">montrer.</span></span></div>
            <div class="serif l2 it" id="G-l2" style="color:#B5934E">Il vend.</div>
          </div>
        </div></div>
      </section>

      <!-- H · DEVIS -->
      <section id="H" class="scene clip" data-start="@S7" data-duration="@D7" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="abs left">
            <div class="eyebrow"><span class="rule"></span><span>Devis instantané</span></div>
            <h2 class="serif"><span class="mask"><span class="in">Le prix,</span></span> <span class="mask"><span class="in it">en direct.</span></span></h2>
            <div class="list">
              <div class="row"><div class="chk"><div class="f"></div><svg viewBox="0 0 40 40"><path d="M12 20.5 L18 26 L28 15" fill="none" stroke="#0B0A09" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>Prestation</div>
              <div class="row"><div class="chk"><div class="f"></div><svg viewBox="0 0 40 40"><path d="M12 20.5 L18 26 L28 15" fill="none" stroke="#0B0A09" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>Durée</div>
              <div class="row"><div class="chk"><div class="f"></div><svg viewBox="0 0 40 40"><path d="M12 20.5 L18 26 L28 15" fill="none" stroke="#0B0A09" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>Options</div>
              <div class="row"><div class="chk"><div class="f"></div><svg viewBox="0 0 40 40"><path d="M12 20.5 L18 26 L28 15" fill="none" stroke="#0B0A09" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>Délai</div>
            </div>
          </div>
          <div class="abs min" id="H-min"><div class="serif n">1 min</div><div class="t"><div>pour une estimation</div><div>zéro appel</div></div></div>
          <div class="browser" id="H-br" style="left:760px; top:120px; width:1030px; height:688px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/devis</div></div><div class="view"><img id="H-img" src="assets/img/s-devis.jpg" /></div></div>
        </div></div>
      </section>

      <!-- I · RDV -->
      <section id="I" class="scene clip" data-start="@S8" data-duration="@D8" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="browser" id="I-br" style="left:130px; top:150px; width:1120px; height:744px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/rendez-vous</div></div><div class="view"><img id="I-img" src="assets/img/v-rdv.jpg" /></div></div>
          <div class="abs right">
            <div class="eyebrow"><span class="rule"></span><span>Rendez-vous</span></div>
            <h2 class="serif"><span class="mask"><span class="in">Il réserve</span></span> <span class="mask"><span class="in it">lui-même.</span></span></h2>
            <div class="opts"><span class="pill" id="I-o1">Visio · 20 min</span><span class="pill gold" id="I-o2">Au studio</span></div>
          </div>
        </div></div>
      </section>

      <!-- J · CLIENT -->
      <section id="J" class="scene clip" data-start="@S9" data-duration="@D9" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="abs left">
            <div class="eyebrow"><span class="rule"></span><span>Espace client</span></div>
            <h2 class="serif"><span class="mask"><span class="in">Tout, au même</span></span> <span class="mask"><span class="in it">endroit.</span></span></h2>
            <div class="co">
              <div class="it2" id="J-c1"><div class="k">01 · Avancement</div><div class="v">Étape par étape</div><div class="bar"><i id="J-bar"></i></div></div>
              <div class="it2" id="J-c2"><div class="k">02 · Validations</div><div class="v">En un clic</div></div>
              <div class="it2" id="J-c3"><div class="k">03 · Fichiers livrés</div><div class="v">Par format</div></div>
            </div>
          </div>
          <div class="browser" id="J-br" style="left:700px; top:130px; width:1090px; height:725px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/espace-client</div></div>
            <div class="view"><img id="J-i1" src="assets/img/v-auth.jpg" /><img id="J-i2" src="assets/img/v-dash.jpg" /><img id="J-i3" src="assets/img/v-dash2.jpg" /></div></div>
        </div></div>
      </section>

      <!-- K · BENEFITS -->
      <section id="K" class="scene clip" data-start="@S10" data-duration="@D10" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="center lines">
            <div class="serif ln" id="K-1"><span class="mask"><span class="in">Moins d’allers-retours.</span></span></div>
            <div class="serif ln it" id="K-2"><span class="mask"><span class="in">Plus de commandes.</span></span></div>
            <div class="serif ln" id="K-3"><span class="mask"><span class="in">Une image irréprochable.</span></span></div>
          </div>
        </div></div>
      </section>

      <!-- L · MOBILE -->
      <section id="L" class="scene clip" data-start="@S11" data-duration="@D11" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="browser" id="L-br" style="left:260px; top:150px; width:1400px; height:919px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio</div></div><div class="view"><img src="assets/img/v-manifeste.jpg" /></div></div>
          <div class="phone" id="L-p1" style="left:560px; top:260px"><div class="notch"></div><img src="assets/img/m-hero.jpg" /></div>
          <div class="phone" id="L-p2" style="left:810px; top:220px"><div class="notch"></div><img src="assets/img/m-devis.jpg" /></div>
          <div class="phone" id="L-p3" style="left:1060px; top:260px"><div class="notch"></div><img src="assets/img/m-client.jpg" /></div>
        </div></div>
      </section>

      <!-- M · DESIGN SYSTEM -->
      <section id="M" class="scene clip" data-start="@S12" data-duration="@D12" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="abs title">
            <div class="eyebrow"><span class="rule"></span><span>Design system</span></div>
            <h2 class="serif"><span class="mask"><span class="in">Un système complet,</span></span> <span class="mask"><span class="in it">à votre image.</span></span></h2>
          </div>
          <div class="grid">
            <div class="panel" id="M-p1"><div class="k">Couleurs</div><div class="sws">
              <i style="background:#0B0A09"></i><i style="background:#1F1D18"></i><i style="background:#6B6559"></i><i style="background:#DCD6C9"></i><i style="background:#FBF8F1"></i><i style="background:#836935"></i><i id="M-acc" style="background:#B5934E"></i><i style="background:#DBC796"></i></div></div>
            <div class="panel" id="M-p2"><div class="k">Typographies</div><div class="aa"><div class="serif big">Aa</div><div class="fams">Cormorant Garamond<br />Manrope<br />IBM Plex Mono</div></div></div>
            <div class="panel" id="M-p3"><div class="k">Composants</div><div class="comps"><span class="btn g">Commander</span><span class="btn n">Voir</span><span class="sw2"></span><span class="inp">vous@exemple.com</span><span class="btn o">Podcasts</span></div></div>
            <div class="panel" id="M-p4"><div class="k">Votre logo</div><div class="brand"><div class="serif w" id="M-w1">Concept Pub</div><div class="serif w w2" id="M-w2">Votre Studio</div></div></div>
            <div class="panel" id="M-p5"><div class="k">Vos prestations</div><div class="svc" style="margin-top:26px"><span>Affiches</span><span>Identité</span><span>Montage</span><span>Publicités</span><span>Podcasts</span><span>Motion</span><span>Tournage</span></div></div>
            <div class="panel" id="M-p6"><div class="k">Vos tarifs</div><div class="price"><div class="serif p" id="M-pr1">449 000<small>FCFA</small></div><div class="serif p" id="M-pr2">€ 1 250<small>HT</small></div></div></div>
          </div>
        </div></div>
      </section>

      <!-- N · OFFER -->
      <section id="N" class="scene clip" data-start="@S13" data-duration="@D13" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div id="N-a">
            <div class="abs title"><div class="eyebrow"><span class="rule"></span><span>Ce que vous obtenez</span></div>
              <h2 class="serif"><span class="mask"><span class="in">Trois actifs,</span></span> <span class="mask"><span class="in it">prêts à l’emploi.</span></span></h2></div>
            <div class="cards">
              <div class="card" id="N-c1"><div class="thumb"><img src="assets/img/v-hero.jpg" /></div><div class="num">01</div><div class="serif t">Le site</div></div>
              <div class="card" id="N-c2"><div class="thumb" style="background:#FBF8F1; display:flex; gap:10px; padding:26px; align-items:stretch"><i style="flex:1;border-radius:6px;background:#0B0A09"></i><i style="flex:1;border-radius:6px;background:#6B6559"></i><i style="flex:1;border-radius:6px;background:#DCD6C9"></i><i style="flex:1;border-radius:6px;background:#836935"></i><i style="flex:1;border-radius:6px;background:#B5934E"></i><i style="flex:1;border-radius:6px;background:#DBC796"></i></div><div class="num">02</div><div class="serif t">Le système graphique</div></div>
              <div class="card" id="N-c3"><div class="thumb" style="display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 50%,#2E2B24,#0B0A09 70%)"><svg width="110" height="110" viewBox="0 0 120 120" fill="none"><g stroke="#B5934E" fill="#B5934E"><circle cx="60" cy="60" r="54" stroke-width="1.25" fill="none" opacity="0.55"></circle><circle cx="60" cy="60" r="46" stroke-width="1.25" fill="none"></circle><path d="M50 40 L80 60 L50 80 Z" stroke="none"></path></g></svg></div><div class="num">03</div><div class="serif t">Le film de présentation</div></div>
            </div>
          </div>
          <div class="center weeks" id="N-b">
            <div class="serif l"><span class="mask"><span class="in">Des semaines de conception,</span></span> <span class="mask"><span class="in it">déjà faites.</span></span></div>
            <div class="prog"><div class="tr"><i id="N-bar"></i></div><div class="pc" id="N-pc">0 %</div></div>
            <div class="serif plate" id="N-plate"><span id="N-name"></span><span class="caret" id="N-caret"></span></div>
          </div>
        </div></div>
      </section>

      <!-- O · OUTRO -->
      <section id="O" class="scene clip" data-start="@S14" data-duration="@D14" data-track-index="1">
        <div class="stage noir"><div class="cam">
          <div class="rays" id="O-rays"></div>
          <div class="center grp">
            <svg class="seal" id="O-seal" viewBox="0 0 120 120" fill="none"><g stroke="#B5934E" fill="#B5934E">
              <circle class="c1" cx="60" cy="60" r="54" stroke-width="1.25" fill="none" opacity="0.55"></circle><circle class="c2" cx="60" cy="60" r="46" stroke-width="1.25" fill="none"></circle>
              <path class="fv" d="M60 34 L66 60 L60 86 L54 60 Z" stroke="none"></path><path class="fh" d="M34 60 L60 54 L86 60 L60 66 Z" stroke="none" opacity="0.62"></path>
              <line class="tk" x1="60" y1="6" x2="60" y2="14" stroke-width="1.25"></line><line class="tk" x1="60" y1="106" x2="60" y2="114" stroke-width="1.25"></line><line class="tk" x1="6" y1="60" x2="14" y2="60" stroke-width="1.25"></line><line class="tk" x1="106" y1="60" x2="114" y2="60" stroke-width="1.25"></line></g></svg>
            <div class="serif word split" id="O-word">Concept Pub</div>
            <div class="rule" id="O-rule"></div>
            <div class="serif tag" id="O-tag">L’image qui fait vendre.</div>
            <div class="pill gold" id="O-cta" style="margin-top:22px; height:80px; padding:0 44px; font-size:26px">Réservez votre démonstration
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0B0A09" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>
            <div class="meta" id="O-meta">Site vitrine · Design system · Film de présentation</div>
          </div>
        </div></div>
      </section>

      <div id="caps"></div>
      <div id="flash"></div>
      <div id="vignette"></div>
      <div id="grain"></div>
      <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="108" data-track-index="8" data-volume="1"></audio>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="108" data-track-index="9" data-volume="1"></audio>
    </div>

    <script>
      (function () {
        const TIMING = /*TIMING*/;
        const CUTS = /*CUTS*/;
        const $ = (s) => document.querySelector(s);
        const $$ = (s) => Array.from(document.querySelectorAll(s));
        const EX = "expo.out";
        const line = (id) => TIMING.find((l) => l.id === id);
        // start time of the n-th word in a line whose text starts with `w`
        const W = (id, w, n = 0) => {
          const l = line(id); const hits = l.words.filter((x) => x[2].toLowerCase().replace(/[.,…]/g, "").startsWith(w.toLowerCase()));
          return (hits[n] || l.words[0])[0];
        };

        $$(".split").forEach((el) => { const t = el.textContent; el.textContent = ""; for (const c of t) { const s = document.createElement("span"); s.className = "ch"; s.textContent = c === " " ? " " : c; el.appendChild(s); } });

        const tl = gsap.timeline({ paused: true });
        tl.fromTo("#grain", { x: 0, y: 0 }, { x: -40, y: 30, duration: 0.12, ease: "steps(1)", repeat: Math.max(0, Math.floor(108 / 0.24) - 1), yoyo: true }, 0);

        // ---------- helpers
        function wipe(id, T, kind = "right") {
          const st = `#${id} .stage`, edge = `#${id} .edge`;
          const from = { right: "inset(0 0 0 100%)", left: "inset(0 100% 0 0)", up: "inset(100% 0 0 0)", iris: "circle(0% at 50% 50%)" }[kind];
          const to = kind === "iris" ? "circle(80% at 50% 50%)" : "inset(0 0 0 0%)";
          tl.fromTo(st, { clipPath: from }, { clipPath: to, duration: kind === "iris" ? 1.0 : 0.75, ease: "expo.inOut" }, T - 0.5);
          if (kind === "right") tl.fromTo(edge, { x: 1920, opacity: 1 }, { x: -12, duration: 0.75, ease: "expo.inOut" }, T - 0.5);
          if (kind === "left") tl.fromTo(edge, { x: -12, opacity: 1 }, { x: 1920, duration: 0.75, ease: "expo.inOut" }, T - 0.5);
          if (kind === "right" || kind === "left") tl.set(edge, { opacity: 0 }, T + 0.3);
          tl.fromTo(`#${id} .cam`, { scale: 1.1 }, { scale: 1, duration: 1.5, ease: EX }, T - 0.5);
        }
        function push(id, T, dir = -1) { tl.to(`#${id} .cam`, { xPercent: 12 * dir, scale: 0.94, opacity: 0.3, duration: 0.75, ease: "expo.inOut" }, T - 0.5); }
        function masks(sel, t, st = 0.08, d = 1.0) { tl.fromTo(`${sel} .mask > .in`, { yPercent: 115, rotate: 3 }, { yPercent: 0, rotate: 0, duration: d, ease: EX, stagger: st }, t); }
        function eyebrow(sel, t) {
          tl.fromTo(`${sel} .eyebrow .rule`, { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: EX }, t);
          tl.fromTo(`${sel} .eyebrow span:not(.rule)`, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.9, ease: EX }, t + 0.1);
        }
        function flash(t, o = 0.8) { tl.fromTo("#flash", { opacity: o }, { opacity: 0, duration: 0.7, ease: "power2.out" }, t); }
        function browserIn(sel, t, o = {}) { tl.fromTo(sel, { y: o.y ?? 180, rotateX: o.rx ?? 16, opacity: 0, transformPerspective: 2400, transformOrigin: "50% 100%" }, { y: 0, rotateX: 0, opacity: 1, duration: 1.3, ease: EX }, t); }
        function sealDraw(sel, t) {
          tl.set(`${sel} .c1, ${sel} .c2`, { strokeDasharray: 400, strokeDashoffset: 400 }, 0);
          tl.to(`${sel} .c2`, { strokeDashoffset: 0, duration: 1.1, ease: "expo.inOut" }, t);
          tl.to(`${sel} .c1`, { strokeDashoffset: 0, duration: 1.2, ease: "expo.inOut" }, t + 0.1);
          tl.fromTo(`${sel} .fv`, { scaleY: 0, transformOrigin: "60px 60px" }, { scaleY: 1, duration: 0.8, ease: EX }, t + 0.4);
          tl.fromTo(`${sel} .fh`, { scaleX: 0, transformOrigin: "60px 60px" }, { scaleX: 1, duration: 0.8, ease: EX }, t + 0.5);
          tl.fromTo(`${sel} .tk`, { opacity: 0 }, { opacity: 1, duration: 0.4, stagger: 0.05 }, t + 0.6);
          tl.fromTo(sel, { rotate: -90, scale: 0.6 }, { rotate: 0, scale: 1, duration: 1.6, ease: EX }, t);
        }
        function check(rowSel, t) {
          tl.fromTo(`${rowSel} .f`, { scale: 0 }, { scale: 1, duration: 0.45, ease: "back.out(2.4)" }, t);
          tl.fromTo(`${rowSel} path`, { strokeDasharray: 30, strokeDashoffset: 30 }, { strokeDashoffset: 0, duration: 0.4, ease: "power2.out" }, t + 0.12);
        }

        // scene transitions
        const ids = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"];
        const kinds = { C: "iris", G: "up", K: "left", O: "iris", M: "right" };
        CUTS.slice(1, -1).forEach((T, i) => { push(ids[i], T, kinds[ids[i + 1]] === "left" ? 1 : -1); wipe(ids[i + 1], T, kinds[ids[i + 1]] || "right"); });

        // ================= A · HOOK
        tl.fromTo("#A-p1 .l1 .mask > .in", { yPercent: 115 }, { yPercent: 0, duration: 0.7, ease: EX, stagger: 0.13 }, W("hook1", "un") - 0.05);
        tl.fromTo("#A-p1 .big .mask > .in", { yPercent: 115, scale: 1.3 }, { yPercent: 0, scale: 1, duration: 0.9, ease: EX, stagger: 0.12 }, W("hook1", "trois") - 0.05);
        flash(W("hook1", "trois"), 0.5);
        tl.to("#A-ring", { strokeDashoffset: 0, duration: 3.0, ease: "none" }, W("hook1", "trois"));
        tl.fromTo("#A .ring", { scale: 0.9, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.2, ease: EX }, W("hook1", "trois") - 0.2);
        tl.to("#A-p1", { y: -60, opacity: 0, filter: "blur(10px)", duration: 0.5, ease: "power2.in" }, W("hook2", "pas") - 0.35);
        tl.fromTo("#A-p2", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("hook2", "pas") - 0.1);
        tl.fromTo("#A-p2 .a .mask > .in", { yPercent: 115 }, { yPercent: 0, duration: 0.8, ease: EX }, W("hook2", "pas") - 0.05);
        tl.fromTo("#A-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "power3.inOut" }, W("hook2", "talent") + 0.25);
        tl.fromTo("#A-p2 .b .mask > .in", { yPercent: 115, scale: 1.2 }, { yPercent: 0, scale: 1, duration: 1.0, ease: EX, stagger: 0.14 }, W("hook2", "sur", 1) - 0.05);
        tl.to("#A .ring", { scale: 1.08, duration: 3, ease: "none" }, 4);

        // ================= B · PAIN
        const shake = (sel, t, d) => { // seeded jitter, finite
          let s = 7; const r = () => ((s = (s * 16807) % 2147483647) / 2147483647 - 0.5);
          const n = Math.floor(d / 0.09); for (let i = 0; i < n; i++) tl.to(sel, { x: r() * 6, y: r() * 6, rotate: r() * 0.6, duration: 0.09, ease: "none" }, t + i * 0.09);
        };
        tl.fromTo("#B-folio", { opacity: 0, y: 60, rotate: -3 }, { opacity: 1, y: 0, rotate: -2, duration: 0.9, ease: EX }, W("pain", "portfolio") - 0.1);
        tl.fromTo("#B-fige", { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(3)" }, W("pain", "fig"));
        $$("#B .bub").forEach((b, i) => tl.fromTo(b, { opacity: 0, y: 40, scale: 0.92, transformOrigin: "100% 100%" }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.6)" }, W("pain", "devis") - 0.1 + i * 0.42));
        $$("#B .mail").forEach((m, i) => tl.fromTo(m, { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: 0.55, ease: EX }, W("pain", "fichiers") - 0.1 + i * 0.35));
        shake("#B-cam", W("pain", "fichiers"), 1.8);
        tl.to("#B-cam", { x: 0, y: 0, rotate: 0, duration: 0.1 }, W("pain", "fichiers") + 1.85);
        tl.to("#B .card, #B .bub, #B .mail", { x: 1500, opacity: 0, filter: "blur(14px)", duration: 0.9, ease: "power3.in", stagger: 0.05 }, W("pain", "partent") - 0.05);

        // ================= C · REVEAL
        sealDraw("#C-seal", W("reveal", "voici"));
        flash(W("reveal", "concept"), 0.7);
        tl.fromTo("#C-rays", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1.1, duration: 3, ease: EX }, W("reveal", "concept"));
        tl.fromTo("#C-word .ch", { opacity: 0, yPercent: 70, filter: "blur(12px)", x: (i, e, a) => (i - (a.length - 1) / 2) * 30 }, { opacity: 1, yPercent: 0, filter: "blur(0px)", x: 0, duration: 1.3, ease: EX, stagger: 0.04 }, W("reveal", "concept") - 0.1);
        tl.fromTo("#C-sub", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.0, ease: EX }, W("for", "site"));
        tl.fromTo("#C-tags .pill:nth-child(1)", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("for", "studios") - 0.1);
        tl.fromTo("#C-tags .pill:nth-child(2)", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("for", "agences") - 0.1);
        tl.fromTo("#C-tags .pill:nth-child(3)", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("for", "boîtes") - 0.1);
        tl.fromTo("#C-grp", { scale: 1.06 }, { scale: 1, duration: 8, ease: "power1.out" }, 14.5);

        // ================= D · LOOK
        browserIn("#D-br", 23.3, { y: 260, rx: 26 });
        eyebrow("#D", W("look", "direction") - 0.2);
        tl.fromTo("#D-br img", { scale: 1.0 }, { scale: 1.08, duration: 3.5, ease: "none" }, W("look", "l'image"));
        tl.to("#D-br", { x: -200, scale: 0.8, duration: 1.1, ease: "expo.inOut" }, W("look", "noir") - 0.45);
        $$("#D .sw").forEach((s, i) => tl.fromTo(s, { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.8, ease: EX }, [W("look", "noir"), W("look", "ivoire"), W("look", "or")][i] - 0.1));
        $$("#D .sw .c").forEach((c, i) => tl.fromTo(c, { scale: 0 }, { scale: 1, duration: 0.8, ease: "back.out(1.8)" }, [W("look", "noir"), W("look", "ivoire"), W("look", "or")][i] - 0.1));
        flash(W("look", "or"), 0.35);

        // ================= E · SERVICES
        eyebrow("#E", 31.5);
        tl.fromTo("#E-nine", { yPercent: 40, opacity: 0, scale: 1.3 }, { yPercent: 0, opacity: 1, scale: 1, duration: 1.0, ease: EX }, W("services", "neuf") - 0.1);
        masks("#E .met", W("services", "métiers"), 0.12);
        browserIn("#E-br", 31.6);
        tl.fromTo("#E-img", { y: 0 }, { y: -(1000 * 1616 / 1680 - 625), duration: 5.2, ease: "power2.inOut" }, 32.4);
        $$("#E-chips .pill").forEach((p, i) => tl.fromTo(p, { opacity: 0, y: 30, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(2)" }, [W("services", "l'affiche"), W("services", "tournage"), W("services", "motion"), W("services", "podcast")][i] - 0.05));

        // ================= F · REEL
        browserIn("#F-br", 37.5, { y: 120, rx: 10 });
        tl.fromTo("#F-i2", { xPercent: 100 }, { xPercent: 0, duration: 1.1, ease: "expo.inOut" }, W("reel", "défilent") - 0.1);
        tl.fromTo("#F-i1", { xPercent: 0 }, { xPercent: -30, duration: 1.1, ease: "expo.inOut" }, W("reel", "défilent") - 0.1);
        tl.fromTo("#F-top", { yPercent: -100 }, { yPercent: 0, duration: 0.9, ease: "expo.inOut" }, W("reel", "comme"));
        tl.fromTo("#F-bot", { yPercent: 100 }, { yPercent: 0, duration: 0.9, ease: "expo.inOut" }, W("reel", "comme"));
        tl.fromTo("#F-br", { scale: 1 }, { scale: 1.1, duration: 3, ease: "power1.inOut" }, 38.4);

        // ================= G · SELLS
        masks("#G-l1", W("sells", "ce") - 0.1, 0.1, 0.9);
        tl.fromTo("#G-disc", { clipPath: "circle(0% at 50% 62%)" }, { clipPath: "circle(90% at 50% 62%)", duration: 0.9, ease: "expo.inOut" }, W("sells", "il") - 0.35);
        tl.to("#G-l1", { color: "#948D7E", y: -40, scale: 0.82, duration: 0.9, ease: "expo.inOut" }, W("sells", "il") - 0.35);
        tl.fromTo("#G-l2", { opacity: 0, scale: 1.5, filter: "blur(18px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.8, ease: EX }, W("sells", "il") - 0.05);
        flash(W("sells", "vend"), 0.8);

        // ================= H · DEVIS
        eyebrow("#H", 45.0);
        masks("#H .left h2", 45.1, 0.12);
        browserIn("#H-br", 45.1);
        tl.fromTo("#H-img", { y: 0 }, { y: -(1030 * 2302 / 1680 - 644), duration: 9.0, ease: "power1.inOut" }, 46.2);
        const hw = [W("devis", "prestation"), W("devis", "durée"), W("devis", "options"), W("devis", "délai")];
        $$("#H .row").forEach((r, i) => { tl.fromTo(r, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.6, ease: EX }, hw[i] - 0.15); });
        $$("#H .row").forEach((r, i) => check(`#H .row:nth-child(${i + 1})`, hw[i]));
        tl.fromTo("#H-min", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.9, ease: EX }, W("devis", "une") - 0.1);
        tl.fromTo("#H-min .n", { scale: 1.4, transformOrigin: "0% 100%" }, { scale: 1, duration: 0.9, ease: EX }, W("devis", "une") - 0.1);

        // ================= I · RDV
        browserIn("#I-br", 55.9, { y: 140, rx: 10 });
        eyebrow("#I", 56.2);
        masks("#I .right h2", W("rdv", "réserve") - 0.1, 0.14);
        tl.fromTo("#I-img", { scale: 1, transformOrigin: "22% 55%" }, { scale: 1.45, duration: 3.6, ease: "power2.inOut" }, 56.6);
        tl.fromTo("#I-o1", { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: EX }, W("rdv", "visio") - 0.1);
        tl.fromTo("#I-o2", { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: EX }, W("rdv", "studio") - 0.15);

        // ================= J · CLIENT
        eyebrow("#J", 59.8);
        masks("#J .left h2", 60.0, 0.12);
        browserIn("#J-br", 59.7);
        tl.fromTo("#J-i2", { opacity: 0, scale: 1.04 }, { opacity: 1, scale: 1, duration: 0.7, ease: EX }, W("client", "espace"));
        tl.fromTo("#J-i3", { opacity: 0, yPercent: 20 }, { opacity: 1, yPercent: 0, duration: 1.0, ease: "expo.inOut" }, W("client", "validations") - 0.3);
        const jw = [W("client", "l'avancement"), W("client", "validations"), W("client", "fichiers")];
        ["#J-c1", "#J-c2", "#J-c3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.7, ease: EX }, jw[i] - 0.1));
        tl.fromTo("#J-bar", { scaleX: 0 }, { scaleX: 0.64, duration: 1.4, ease: EX }, jw[0] + 0.2);

        // ================= K · BENEFITS
        const kw = [W("benef", "moins"), W("benef", "plus"), W("benef", "une")];
        ["#K-1", "#K-2", "#K-3"].forEach((s, i) => {
          tl.fromTo(`${s} .mask > .in`, { yPercent: 115 }, { yPercent: 0, duration: 0.9, ease: EX }, kw[i] - 0.1);
          if (i < 2) tl.to(`${s}`, { opacity: 0.28, duration: 0.6 }, kw[i + 1] - 0.1);
        });
        tl.to("#K-1, #K-2", { opacity: 1, duration: 0.6 }, W("benef", "irr") + 0.3);
        tl.fromTo("#K .lines", { scale: 1.06 }, { scale: 1, duration: 5.5, ease: "power1.out" }, 66.0);

        // ================= L · MOBILE
        browserIn("#L-br", 71.3, { y: 100, rx: 8 });
        tl.to("#L-br", { opacity: 0.35, scale: 0.9, duration: 1.0, ease: "expo.inOut" }, W("mobile", "écrans") - 0.3);
        const lp = [["#L-p1", -12, W("mobile", "écrans")], ["#L-p2", 0, W("mobile", "élégant")], ["#L-p3", 12, W("mobile", "mobile")]];
        lp.forEach(([s, r, t]) => tl.fromTo(s, { y: 700, rotate: r * 2, opacity: 0 }, { y: 0, rotate: r * 0.5, opacity: 1, duration: 1.1, ease: EX }, t - 0.2));
        tl.to("#L-br", { opacity: 1, scale: 1, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);
        tl.to("#L-p1, #L-p2, #L-p3", { y: 120, scale: 0.72, duration: 1.0, ease: "expo.inOut", stagger: 0.05 }, W("mobile", "grand") - 0.2);
        tl.to("#L-p1", { x: -470, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);
        tl.to("#L-p3", { x: 470, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);

        // ================= M · DESIGN SYSTEM
        eyebrow("#M", 76.2);
        masks("#M .title h2", W("ds", "repose"), 0.12);
        const mw = [W("ds", "couleurs"), W("ds", "typographies"), W("ds", "composants"), W("ds", "logo"), W("ds", "prestations"), W("ds", "tarifs")];
        ["#M-p1", "#M-p2", "#M-p3", "#M-p4", "#M-p5", "#M-p6"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 60, scale: 0.95 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: EX }, mw[i] - 0.2));
        tl.fromTo("#M-p1 .sws i", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.8, ease: EX, stagger: 0.05 }, mw[0]);
        tl.fromTo("#M-w2", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.8, ease: EX }, mw[3] + 0.5);
        tl.to("#M-w1", { yPercent: -110, opacity: 0, duration: 0.6, ease: "power3.in" }, mw[3] + 0.4);
        tl.fromTo("#M-p5 .svc span", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: EX, stagger: 0.07 }, mw[4]);
        tl.fromTo("#M-pr2", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.8, ease: EX }, W("ds", "tout") - 0.1);
        tl.to("#M-pr1", { yPercent: -110, opacity: 0, duration: 0.6, ease: "power3.in" }, W("ds", "tout") - 0.2);
        tl.to("#M-acc", { backgroundColor: "#3F5A6B", duration: 0.6 }, W("ds", "personnalise"));
        tl.to("#M-acc", { backgroundColor: "#B5934E", duration: 0.6 }, W("ds", "zéro"));
        tl.to("#M .grid", { scale: 0.97, duration: 0.5, ease: "power2.inOut", yoyo: true, repeat: 1 }, W("ds", "sans"));

        // ================= N · OFFER
        eyebrow("#N", 88.3);
        masks("#N .title h2", W("offer", "vous") + 0.1, 0.12);
        const nw = [W("offer", "site"), W("offer", "système"), W("offer", "film")];
        ["#N-c1", "#N-c2", "#N-c3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 120, rotateX: 20, transformPerspective: 2000 }, { opacity: 1, y: 0, rotateX: 0, duration: 1.0, ease: EX }, nw[i] - 0.2));
        tl.to("#N-a", { opacity: 0, y: -60, scale: 0.96, duration: 0.6, ease: "power2.in" }, W("weeks", "des") - 0.4);
        masks("#N-b .l", W("weeks", "des") - 0.05, 0.14);
        tl.fromTo("#N-b .prog", { opacity: 0 }, { opacity: 1, duration: 0.5 }, W("weeks", "des"));
        const pc = { v: 0 }, pcEl = $("#N-pc");
        tl.fromTo("#N-bar", { scaleX: 0 }, { scaleX: 1, duration: 1.8, ease: "power2.inOut" }, W("weeks", "semaines"));
        tl.fromTo(pc, { v: 0 }, { v: 100, duration: 1.8, ease: "power2.inOut", onUpdate: () => { pcEl.textContent = Math.round(pc.v) + " %"; } }, W("weeks", "semaines"));
        tl.fromTo("#N-plate", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: EX }, W("weeks", "il") - 0.1);
        const nm = "Votre studio", nEl = $("#N-name"), ty = { v: 0 };
        tl.fromTo(ty, { v: 0 }, { v: nm.length, duration: 0.9, ease: "none", onUpdate: () => { nEl.textContent = nm.slice(0, Math.floor(ty.v)); } }, W("weeks", "mettre"));
        tl.fromTo("#N-caret", { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "steps(1)", repeat: 7, yoyo: true }, W("weeks", "il"));

        // ================= O · OUTRO
        sealDraw("#O-seal", W("sign", "concept") - 0.2);
        flash(W("sign", "concept"), 0.7);
        tl.fromTo("#O-rays", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1.1, duration: 3, ease: EX }, W("sign", "concept"));
        tl.fromTo("#O-word .ch", { opacity: 0, yPercent: 70, filter: "blur(12px)" }, { opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 1.1, ease: EX, stagger: 0.04 }, W("sign", "concept") - 0.1);
        tl.fromTo("#O-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "expo.inOut" }, W("sign", "l'image") - 0.4);
        tl.fromTo("#O-tag", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1.0, ease: EX }, W("sign", "l'image") - 0.1);
        tl.fromTo("#O-tag", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.8, ease: "power2.inOut" }, W("sign", "vendre"));
        tl.fromTo("#O-cta", { opacity: 0, y: 30, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 1.0, ease: EX }, W("cta", "réservez") - 0.1);
        tl.to("#O-cta", { boxShadow: "0 0 80px rgba(219,199,150,0.55)", duration: 0.8, ease: "sine.inOut", yoyo: true, repeat: 3 }, W("cta", "démonstration"));
        tl.fromTo("#O-meta", { opacity: 0 }, { opacity: 1, duration: 1.0 }, W("cta", "dès"));
        tl.fromTo("#O .grp", { scale: 1.04 }, { scale: 1, duration: 8, ease: "power1.out" }, 99.0);
        tl.to("#O .cam", { opacity: 0, duration: 1.0, ease: "power2.in" }, 106.8);

        // ================= CAPTIONS (chunked on punctuation, timed by words)
        const caps = $("#caps");
        TIMING.forEach((l) => {
          const chunks = l.text.split(/(?<=[,.:…?!])\s+/).map((c) => c.trim()).filter(Boolean);
          let wi = 0;
          chunks.forEach((c, ci) => {
            const n = c.split(/\s+/).filter((tok) => /[\p{L}\p{N}]/u.test(tok)).length;
            const w0 = l.words[wi], w1 = l.words[Math.min(l.words.length - 1, wi + n - 1)];
            wi += n;
            if (!w0) return;
            const start = w0[0] - 0.08, end = ci === chunks.length - 1 ? l.end + 0.15 : (l.words[wi] ? l.words[wi][0] - 0.1 : w1[0] + w1[1]);
            const d = document.createElement("div"); d.className = "cap"; d.textContent = c; caps.appendChild(d);
            tl.fromTo(d, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.18, ease: "power2.out" }, start);
            tl.to(d, { opacity: 0, duration: 0.14, ease: "power2.in" }, Math.max(start + 0.3, end));
          });
        });

        window.__timelines["main"] = tl;
      })();
    </script>
  </body>
</html>
