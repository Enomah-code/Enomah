<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Concept Pub — Film de vente v2</title>
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
    
      /* live demo frames (root-level, untimed wrappers around timed videos) */
      .live { position: absolute; left: 260px; top: 46px; width: 1400px; height: 915px; z-index: 20; opacity: 0; border-radius: 14px; overflow: hidden; background: #0B0A09;
        box-shadow: 0 60px 160px rgba(0,0,0,0.6), 0 0 0 1px rgba(219,199,150,0.22); }
      .live .bar { position: absolute; left: 0; right: 0; top: 0; height: 40px; background: #1F1D18; display: flex; align-items: center; gap: 9px; padding: 0 18px; z-index: 2; }
      .live .bar i { display: block; width: 12px; height: 12px; border-radius: 50%; background: rgba(245,241,232,0.18); }
      .live .bar .url { position: absolute; left: 50%; top: 7px; width: 360px; margin-left: -180px; height: 26px; border-radius: 999px; background: rgba(245,241,232,0.07); font-family: var(--mono); font-size: 14px; letter-spacing: 0.06em; color: rgba(245,241,232,0.6); display: flex; align-items: center; justify-content: center; }
      .live .bar .onair { margin-left: auto; display: flex; align-items: center; gap: 10px; font-family: var(--mono); font-size: 13px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--gold-300); }
      .live .bar .onair b { display: block; width: 9px; height: 9px; border-radius: 50%; background: #C0392B; box-shadow: 0 0 10px rgba(192,57,43,0.8); }
      .live .vw { position: absolute; left: 0; right: 0; top: 40px; bottom: 0; overflow: hidden; }
      .live .zoom { position: absolute; inset: 0; }
      .live video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
      #tags { position: absolute; inset: 0; z-index: 30; pointer-events: none; }
      #tags .tag { position: absolute; display: inline-flex; align-items: center; gap: 14px; height: 60px; padding: 0 28px 0 18px; border-radius: 999px; white-space: nowrap;
        background: rgba(11,10,9,0.86); border: 1px solid rgba(219,199,150,0.55); color: var(--ivory); font-family: var(--sans); font-weight: 600; font-size: 23px; opacity: 0; box-shadow: 0 20px 50px rgba(0,0,0,0.45); }
      #tags .tag .n { width: 34px; height: 34px; border-radius: 50%; background: var(--gg); color: var(--noir); font-family: var(--mono); font-size: 15px; font-weight: 500; display: flex; align-items: center; justify-content: center; }
      #tags .tag.gold { background: var(--gg); color: var(--noir); border: 0; }
      .livebg { position: absolute; inset: 0; background: radial-gradient(ellipse 70% 60% at 50% 45%, rgba(181,147,78,0.16), rgba(0,0,0,0) 70%), radial-gradient(ellipse 90% 80% at 50% 38%, #1B1915 0%, var(--noir) 70%); }

      /* A — hook */
      #A .err { position: absolute; left: 0; right: 0; top: 250px; display: flex; flex-direction: column; align-items: center; gap: 34px; text-align: center; }
      #A .kick { font-family: var(--mono); font-size: 22px; letter-spacing: 0.4em; text-transform: uppercase; color: #C4553F; display: flex; align-items: center; gap: 20px; }
      #A .kick .rule { width: 60px; height: 1px; background: currentColor; display: block; }
      #A .l1 { font-size: 100px; white-space: nowrap; }
      #A .roles { position: relative; height: 230px; width: 1600px; }
      #A .role { position: absolute; left: 0; right: 0; top: 0; text-align: center; font-size: 200px; font-style: italic; color: var(--gold); line-height: 1.05; }
      #A .belief { position: absolute; left: 0; right: 0; top: 380px; text-align: center; }
      #A .belief .b1 { font-size: 118px; white-space: nowrap; position: relative; display: inline-block; }
      #A .belief .strike { position: absolute; left: 0; width: 100%; top: 54%; height: 6px; background: #B0412F; transform-origin: left center; display: block; }

      /* B — causes */
      #B .head { position: absolute; left: 150px; top: 110px; }
      #B .head h2 { margin: 22px 0 0; font-size: 84px; }
      #B .cards { position: absolute; left: 150px; right: 150px; top: 350px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 36px; }
      #B .card { position: relative; height: 540px; border-radius: 18px; background: linear-gradient(180deg, #1D1B17, #141310); border: 1px solid rgba(245,241,232,0.09); padding: 34px; overflow: hidden; }
      #B .card .num { font-family: var(--mono); font-size: 18px; letter-spacing: 0.26em; color: #C4553F; }
      #B .card .t { margin-top: 16px; font-family: var(--serif); font-size: 64px; line-height: 1; }
      #B .card .s { margin-top: 12px; font-family: var(--sans); font-weight: 300; font-size: 24px; color: var(--noir-300); line-height: 1.4; }
      #B .vig { position: absolute; left: 34px; right: 34px; bottom: 34px; height: 240px; border-radius: 12px; background: #0E0D0B; border: 1px solid rgba(245,241,232,0.07); padding: 22px; }
      #B .search { height: 50px; border-radius: 999px; border: 1px solid rgba(245,241,232,0.16); display: flex; align-items: center; padding: 0 20px; font-family: var(--sans); font-size: 19px; color: var(--noir-300); gap: 12px; }
      #B .res { margin-top: 18px; height: 16px; border-radius: 8px; background: #25231F; }
      #B .none { margin-top: 20px; font-family: var(--mono); font-size: 15px; letter-spacing: 0.14em; color: #C4553F; text-transform: uppercase; }
      #B .bub { max-width: 90%; padding: 16px 20px; border-radius: 18px 18px 18px 6px; background: #2B2925; color: #DCD6C9; font-family: var(--sans); font-size: 20px; }
      #B .seen { margin-top: 10px; font-family: var(--mono); font-size: 15px; letter-spacing: 0.1em; color: var(--noir-400); }
      #B .days { position: absolute; right: 24px; bottom: 18px; font-family: var(--serif); font-size: 86px; color: #C4553F; line-height: 1; }
      #B .days small { font-size: 30px; margin-left: 6px; }
      #B .q { padding: 12px 18px; border-radius: 16px 16px 6px 16px; background: #2B2925; color: #DCD6C9; font-family: var(--sans); font-size: 18px; margin-left: auto; width: fit-content; margin-bottom: 10px; }
      #B .pbar { position: absolute; left: 22px; right: 22px; bottom: 26px; height: 4px; background: #25231F; }
      #B .pbar i { position: absolute; left: 0; top: 0; bottom: 0; width: 40%; background: #46423A; }
      #B .pbar b { position: absolute; left: 40%; top: -34px; font-family: var(--serif); font-size: 44px; color: #C4553F; margin-left: -10px; }

      /* C — result */
      #C .wrap { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 34px; text-align: center; margin-top: -40px; }
      #C .l1 { font-size: 140px; white-space: nowrap; }
      #C .l2 { font-size: 86px; white-space: nowrap; }
      #C .arrow { width: 900px; height: 2px; position: relative; }
      #C .arrow i { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(196,85,63,0), #C4553F); transform-origin: left center; display: block; }
      #C .arrow b { position: absolute; right: -4px; top: -9px; width: 20px; height: 20px; border-top: 2px solid #C4553F; border-right: 2px solid #C4553F; transform: rotate(45deg); }

      /* D — reveal */
      #D .rays { position: absolute; left: 50%; top: 50%; width: 1700px; height: 1700px; margin: -850px 0 0 -850px; background: radial-gradient(circle, rgba(181,147,78,0.22) 0%, rgba(181,147,78,0.05) 32%, rgba(0,0,0,0) 60%); }
      #D .grp { gap: 28px; margin-top: -30px; }
      #D .kick { font-family: var(--mono); font-size: 22px; letter-spacing: 0.4em; text-transform: uppercase; color: var(--gold); }
      #D .seal { width: 140px; height: 140px; }
      #D .word { font-size: 190px; letter-spacing: -0.005em; }
      #D .sub { font-size: 58px; color: var(--noir-200); }
      #D .tags { display: flex; gap: 22px; margin-top: 18px; }

      /* E — swatches over the live hero */
      #sw { position: absolute; left: 1250px; top: 330px; z-index: 31; display: flex; flex-direction: column; gap: 26px; pointer-events: none; }
      #sw .s { display: flex; align-items: center; gap: 22px; opacity: 0; }
      #sw .c { width: 104px; height: 104px; border-radius: 50%; box-shadow: 0 0 0 1px rgba(245,241,232,0.3), 0 20px 50px rgba(0,0,0,0.5); }
      #sw .n { font-family: var(--serif); font-size: 50px; line-height: 1; color: var(--ivory); text-shadow: 0 4px 20px rgba(0,0,0,0.6); }

      /* F — sells */
      #F .noirdisc { position: absolute; inset: 0; background: radial-gradient(ellipse 90% 80% at 50% 45%, #1B1915 0%, var(--noir) 70%); }
      #F .l1 { font-size: 118px; white-space: nowrap; }
      #F .l2 { font-size: 330px; margin-top: 30px; }

      /* H — client space title card + closing line */
      #hc { position: absolute; inset: 0; z-index: 32; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 26px; text-align: center; pointer-events: none; opacity: 0; }
      #hc .k { font-family: var(--mono); font-size: 22px; letter-spacing: 0.4em; text-transform: uppercase; color: var(--gold-300); }
      #hc .t { font-family: var(--serif); font-weight: 500; font-style: italic; font-size: 200px; line-height: 1; color: var(--gold); text-shadow: 0 10px 60px rgba(0,0,0,0.7); }
      #hc .s { font-family: var(--sans); font-weight: 300; font-size: 32px; color: var(--ivory); }
      #hdim { position: absolute; inset: 0; z-index: 31; background: rgba(11,10,9,0.78); opacity: 0; pointer-events: none; }
      #hend { position: absolute; left: 1300px; top: 300px; width: 540px; z-index: 31; pointer-events: none; opacity: 0; }
      #hend .k { font-family: var(--mono); font-size: 18px; letter-spacing: 0.26em; text-transform: uppercase; color: var(--gold); opacity: 0; }
      #hend .l { margin-top: 20px; font-family: var(--serif); font-size: 74px; line-height: 1.02; color: var(--ivory); }
      #hend .z { margin-top: 36px; display: flex; flex-direction: column; gap: 14px; }
      #hend .z div { font-family: var(--sans); font-size: 26px; color: var(--noir-200); display: flex; align-items: center; gap: 14px; opacity: 0; }
      #hend .z b { font-family: var(--serif); font-size: 46px; color: var(--gold); font-weight: 500; }

    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="137">

      <!-- A · HOOK — l'erreur -->
      <section id="A" class="scene clip" data-start="@S0" data-duration="@D0" data-track-index="1">
        <div class="stage noir"><div class="cam">
          <div class="err" id="A-err">
            <div class="kick" id="A-kick"><span class="rule"></span><span>L’erreur n°1</span><span class="rule"></span></div>
            <div class="serif l1"><span class="mask"><span class="in">Voici</span></span> <span class="mask"><span class="in">l’erreur</span></span> <span class="mask"><span class="in">que</span></span> <span class="mask"><span class="in">font</span></span> <span class="mask"><span class="in">la</span></span> <span class="mask"><span class="in">plupart</span></span> <span class="mask"><span class="in">des…</span></span></div>
            <div class="roles">
              <div class="serif role" id="A-r1"><span class="mask"><span class="in">graphistes</span></span></div>
              <div class="serif role" id="A-r2"><span class="mask"><span class="in">monteurs</span></span></div>
              <div class="serif role" id="A-r3"><span class="mask"><span class="in">motion designers</span></span></div>
            </div>
          </div>
          <div class="belief" id="A-bel">
            <div class="serif b1"><span class="mask"><span class="in">Le talent</span></span> <span class="mask"><span class="in it">suffit à vendre.</span></span><span class="strike" id="A-strike"></span></div>
          </div>
        </div></div>
      </section>

      <!-- B · CAUSES -->
      <section id="B" class="scene clip" data-start="@S1" data-duration="@D1" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="head">
            <div class="eyebrow" style="color:#C4553F"><span class="rule"></span><span>Pourquoi ils perdent des clients</span></div>
            <h2 class="serif"><span class="mask"><span class="in">Trois fuites,</span></span> <span class="mask"><span class="in it">un même résultat.</span></span></h2>
          </div>
          <div class="cards">
            <div class="card" id="B-c1"><div class="num">01</div><div class="t">Introuvables</div><div class="s">Les clients ne les trouvent pas.</div>
              <div class="vig"><div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#948D7E" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>studio motion design</div><div class="res" style="width:86%"></div><div class="res" style="width:70%"></div><div class="res" style="width:78%"></div><div class="none">Votre studio : introuvable</div></div></div>
            <div class="card" id="B-c2"><div class="num">02</div><div class="t">Trop lents</div><div class="s">Un devis attendu pendant des jours.</div>
              <div class="vig"><div class="bub">Bonjour, c’est combien pour un spot de 30 s ?</div><div class="seen">Lu · en attente de réponse</div><div class="days"><span id="B-days">1</span><small>jours</small></div></div></div>
            <div class="card" id="B-c3"><div class="num">03</div><div class="t">Opaques</div><div class="s">Aucune visibilité sur la commande.</div>
              <div class="vig"><div class="q" id="B-q1">Où en est ma commande ?</div><div class="q" id="B-q2">Vous avez reçu mes retours ?</div><div class="q" id="B-q3">C’est quelle version, la bonne ?</div><div class="pbar"><i></i><b>?</b></div></div></div>
          </div>
        </div></div>
      </section>

      <!-- C · RESULT -->
      <section id="C" class="scene clip" data-start="@S2" data-duration="@D2" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="wrap">
            <div class="eyebrow" style="color:#C4553F"><span class="rule"></span><span>Résultat</span></div>
            <div class="serif l1"><span class="mask"><span class="in">Le client part</span></span> <span class="mask"><span class="in" style="color:#C4553F">chez le concurrent.</span></span></div>
            <div class="arrow"><i id="C-arrow"></i><b id="C-head"></b></div>
            <div class="serif l2"><span class="mask"><span class="in">Même quand votre travail</span></span> <span class="mask"><span class="in it">est meilleur.</span></span></div>
          </div>
        </div></div>
      </section>

      <!-- D · REVEAL -->
      <section id="D" class="scene clip" data-start="@S3" data-duration="@D3" data-track-index="1">
        <div class="stage noir"><div class="cam">
          <div class="rays" id="D-rays"></div>
          <div class="center grp" id="D-grp">
            <div class="kick" id="D-kick">La solution</div>
            <svg class="seal" id="D-seal" viewBox="0 0 120 120" fill="none"><g stroke="#B5934E" fill="#B5934E">
              <circle class="c1" cx="60" cy="60" r="54" stroke-width="1.25" fill="none" opacity="0.55"></circle><circle class="c2" cx="60" cy="60" r="46" stroke-width="1.25" fill="none"></circle>
              <path class="fv" d="M60 34 L66 60 L60 86 L54 60 Z" stroke="none"></path><path class="fh" d="M34 60 L60 54 L86 60 L60 66 Z" stroke="none" opacity="0.62"></path>
              <line class="tk" x1="60" y1="6" x2="60" y2="14" stroke-width="1.25"></line><line class="tk" x1="60" y1="106" x2="60" y2="114" stroke-width="1.25"></line><line class="tk" x1="6" y1="60" x2="14" y2="60" stroke-width="1.25"></line><line class="tk" x1="106" y1="60" x2="114" y2="60" stroke-width="1.25"></line></g></svg>
            <div class="serif word split" id="D-word">Concept Pub</div>
            <div class="serif sub" id="D-sub">Le site vitrine <span class="it">haut de gamme</span> des métiers de l’image</div>
            <div class="tags" id="D-tags"><span class="pill">Studios de création</span><span class="pill">Agences de communication</span><span class="pill">Boîtes de production</span></div>
          </div>
        </div></div>
      </section>

      <!-- E · LIVE 1 backdrop -->
      <section id="E" class="scene clip" data-start="@S4" data-duration="@D4" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam"><div class="livebg"></div></div></div>
      </section>

      <!-- F · SELLS -->
      <section id="F" class="scene clip" data-start="@S5" data-duration="@D5" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="noirdisc" id="F-disc"></div>
          <div class="center">
            <div class="serif l1" id="F-l1"><span class="mask"><span class="in">Il</span></span> <span class="mask"><span class="in">ne</span></span> <span class="mask"><span class="in">se</span></span> <span class="mask"><span class="in">contente</span></span> <span class="mask"><span class="in">pas</span></span> <span class="mask"><span class="in">de</span></span> <span class="mask"><span class="in">montrer.</span></span></div>
            <div class="serif l2 it" id="F-l2" style="color:#B5934E">Il vend.</div>
          </div>
        </div></div>
      </section>

      <!-- G · LIVE 2 backdrop -->
      <section id="G" class="scene clip" data-start="@S6" data-duration="@D6" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam"><div class="livebg"></div></div></div>
      </section>

      <!-- H · LIVE 3 backdrop -->
      <section id="H" class="scene clip" data-start="@S7" data-duration="@D7" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam"><div class="livebg"></div></div></div>
      </section>

<!-- K · BENEFITS -->
      <section id="K" class="scene clip" data-start="@S8" data-duration="@D8" data-track-index="1">
        <div class="stage ivory"><div class="edge"></div><div class="cam">
          <div class="center lines">
            <div class="serif ln" id="K-1"><span class="mask"><span class="in">Moins d’allers-retours.</span></span></div>
            <div class="serif ln it" id="K-2"><span class="mask"><span class="in">Plus de commandes.</span></span></div>
            <div class="serif ln" id="K-3"><span class="mask"><span class="in">Une image irréprochable.</span></span></div>
          </div>
        </div></div>
      </section>

      <!-- L · MOBILE -->
      <section id="L" class="scene clip" data-start="@S9" data-duration="@D9" data-track-index="1">
        <div class="stage noir"><div class="edge"></div><div class="cam">
          <div class="browser" id="L-br" style="left:260px; top:150px; width:1400px; height:919px"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio</div></div><div class="view"><img src="assets/img/v-manifeste.jpg" /></div></div>
          <div class="phone" id="L-p1" style="left:560px; top:260px"><div class="notch"></div><img src="assets/img/m-hero.jpg" /></div>
          <div class="phone" id="L-p2" style="left:810px; top:220px"><div class="notch"></div><img src="assets/img/m-devis.jpg" /></div>
          <div class="phone" id="L-p3" style="left:1060px; top:260px"><div class="notch"></div><img src="assets/img/m-client.jpg" /></div>
        </div></div>
      </section>

      <!-- M · DESIGN SYSTEM -->
      <section id="M" class="scene clip" data-start="@S10" data-duration="@D10" data-track-index="1">
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
      <section id="N" class="scene clip" data-start="@S11" data-duration="@D11" data-track-index="1">
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
      <section id="O" class="scene clip" data-start="@S12" data-duration="@D12" data-track-index="1">
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

            <!-- LIVE DEMO FRAMES — untimed wrappers, timed videos inside -->
      <div class="live" id="LV1"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio</div><div class="onair"><b></b>Démo en direct</div></div>
        <div class="vw"><div class="zoom" id="Z1"><video id="v1" src="assets/live/v1-vitrine.mp4" data-start="28.8" data-duration="20.95" data-track-index="3" muted playsinline></video></div></div></div>
      <div class="live" id="LV2"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/devis</div><div class="onair"><b></b>Démo en direct</div></div>
        <div class="vw"><div class="zoom" id="Z2"><video id="v2" src="assets/live/v2-devis-rdv.mp4" data-start="53.5" data-duration="18.35" data-track-index="3" muted playsinline></video></div></div></div>
      <div class="live" id="LV3"><div class="bar"><i></i><i></i><i></i><div class="url">conceptpub.studio/espace-client</div><div class="onair"><b></b>Démo en direct</div></div>
        <div class="vw"><div class="zoom" id="Z3"><video id="v3" src="assets/live/v3-espace-client.mp4" data-start="71.05" data-duration="25.2" data-track-index="3" muted playsinline></video></div></div></div>

      <div id="sw">
        <div class="s"><div class="c" style="background:#0B0A09"></div><div class="n">Noir</div></div>
        <div class="s"><div class="c" style="background:#FBF8F1"></div><div class="n">Ivoire</div></div>
        <div class="s"><div class="c" style="background:linear-gradient(135deg,#DBC796,#B5934E 45%,#836935)"></div><div class="n it">Or</div></div>
      </div>

      <div id="tags"></div>

      <div id="hdim"></div>
      <div id="hc"><div class="k">L’atout qui fait la différence</div><div class="t">L’espace client</div><div class="s">Inclus dans le site, prêt à l’emploi.</div></div>
      <div id="hend">
        <div class="k">Pour votre studio</div>
        <div class="z"><div id="hz1"><b>0</b> relance</div><div id="hz2"><b>0</b> fichier perdu</div></div>
        <div class="l"><span class="mask"><span class="in">Aussi pro qu’une</span></span> <span class="mask"><span class="in it">grande agence.</span></span></div>
      </div>

      <div id="caps"></div>
      <div id="flash"></div>
      <div id="vignette"></div>
      <div id="grain"></div>
      <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="137" data-track-index="8" data-volume="1"></audio>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="137" data-track-index="9" data-volume="1"></audio>
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
        tl.fromTo("#grain", { x: 0, y: 0 }, { x: -40, y: 30, duration: 0.12, ease: "steps(1)", repeat: Math.max(0, Math.floor(137 / 0.24) - 1), yoyo: true }, 0);

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
        function masks(sel, t, st = 0.08, d = 1.0) { tl.fromTo(`${sel} .mask > .in`, { yPercent: 115, rotate: 3, opacity: 0 }, { yPercent: 0, rotate: 0, opacity: 1, duration: d, ease: EX, stagger: st }, t); }
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
        const ids = ["A", "B", "C", "D", "E", "F", "G", "H", "K", "L", "M", "N", "O"];
        const kinds = { D: "iris", F: "up", K: "left", O: "iris" };
        CUTS.slice(1, -1).forEach((T, i) => { push(ids[i], T, kinds[ids[i + 1]] === "left" ? 1 : -1); wipe(ids[i + 1], T, kinds[ids[i + 1]] || "right"); });

        // ================= A · HOOK
        const hw = line("hook1").words;
        tl.fromTo("#A-kick", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, 0.35);
        $$("#A .l1 .mask > .in").forEach((el, i) => tl.fromTo(el, { yPercent: 115 }, { yPercent: 0, duration: 0.7, ease: EX }, hw[i][0] - 0.06));
        const roles = [["#A-r1", W("hook1", "graphistes"), W("hook1", "des", 1) - 0.1], ["#A-r2", W("hook1", "monteurs"), W("hook1", "des", 2) - 0.05], ["#A-r3", W("hook1", "motion"), W("hook2", "ils") - 0.3]];
        roles.forEach(([s, a, b]) => {
          tl.fromTo(`${s} .in`, { yPercent: 115, filter: "blur(8px)" }, { yPercent: 0, filter: "blur(0px)", duration: 0.55, ease: EX }, a - 0.08);
          tl.to(`${s} .in`, { yPercent: -115, duration: 0.3, ease: "power3.in" }, b);
        });
        flash(W("hook1", "l'erreur"), 0.35);
        tl.to("#A-err", { y: -80, opacity: 0, filter: "blur(10px)", duration: 0.5, ease: "power2.in" }, W("hook2", "ils") - 0.3);
        tl.fromTo("#A-bel", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("hook2", "ils") - 0.1);
        tl.fromTo("#A-bel .mask:nth-child(1) > .in", { yPercent: 115 }, { yPercent: 0, duration: 0.8, ease: EX }, W("hook2", "talent") - 0.15);
        tl.fromTo("#A-bel .mask:nth-child(2) > .in", { yPercent: 115 }, { yPercent: 0, duration: 0.8, ease: EX }, W("hook2", "suffit") - 0.1);
        tl.fromTo("#A-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.4, ease: "power3.inOut" }, W("hook2", "vendre") + 0.2);
        tl.to("#A-bel .b1", { color: "#6B6559", duration: 0.4 }, W("hook2", "vendre") + 0.35);

        // ================= B · CAUSES
        eyebrow("#B", 7.35);
        masks("#B .head h2", 7.5, 0.12);
        const bw = [W("cause", "clients") - 0.1, W("cause", "ils", 0) - 0.1, W("cause", "et") - 0.1];
        ["#B-c1", "#B-c2", "#B-c3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 120, rotateX: 18, transformPerspective: 2000 }, { opacity: 1, y: 0, rotateX: 0, duration: 1.0, ease: EX }, bw[i]));
        tl.fromTo("#B-c1 .none", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "steps(2)", repeat: 3, yoyo: true }, W("cause", "trouvent"));
        const dy = { v: 1 }, dEl = $("#B-days");
        tl.fromTo(dy, { v: 1 }, { v: 4, duration: 1.4, ease: "none", onUpdate: () => { dEl.textContent = Math.floor(dy.v + 0.001); } }, W("cause", "pendant"));
        ["#B-q1", "#B-q2", "#B-q3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, ease: "back.out(1.6)" }, W("cause", "savent") + i * 0.42));
        tl.to("#B .card", { x: 1600, opacity: 0, filter: "blur(10px)", duration: 0.7, ease: "power3.in", stagger: 0.06 }, 14.0);

        // ================= C · RESULT
        eyebrow("#C", W("result", "résultat") - 0.2);
        masks("#C .l1", W("result", "ils") - 0.05, 0.4, 0.9);
        tl.fromTo("#C-arrow", { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "expo.inOut" }, W("result", "chez") - 0.1);
        tl.fromTo("#C-head", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.5, ease: EX }, W("result", "concurrent"));
        masks("#C .l2", W("result", "même") - 0.05, 0.55, 0.9);

        // ================= D · REVEAL
        tl.fromTo("#D-kick", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("reveal", "solution") - 0.1);
        sealDraw("#D-seal", W("reveal", "s'appelle") - 0.2);
        flash(W("reveal", "concept"), 0.75);
        tl.fromTo("#D-rays", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1.1, duration: 3, ease: EX }, W("reveal", "concept"));
        tl.fromTo("#D-word .ch", { opacity: 0, yPercent: 70, filter: "blur(12px)", x: (i, e, a) => (i - (a.length - 1) / 2) * 30 }, { opacity: 1, yPercent: 0, filter: "blur(0px)", x: 0, duration: 1.3, ease: EX, stagger: 0.04 }, W("reveal", "concept") - 0.1);
        tl.fromTo("#D-sub", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.0, ease: EX }, W("for", "site"));
        [["studios"], ["agences"], ["boîtes"]].forEach(([w], i) => tl.fromTo(`#D-tags .pill:nth-child(${i + 1})`, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("for", w) - 0.1));
        tl.fromTo("#D-grp", { scale: 1.06 }, { scale: 1, duration: 9, ease: "power1.out" }, 19.5);

        // ================= LIVE FRAMES
        function liveIn(sel, t) { tl.fromTo(sel, { opacity: 0, y: 90, scale: 0.93, rotateX: 14, transformPerspective: 2600, transformOrigin: "50% 100%" }, { opacity: 1, y: 0, scale: 1, rotateX: 0, duration: 1.1, ease: EX }, t); }
        function liveOut(sel, t) { tl.to(sel, { opacity: 0, scale: 0.94, y: -30, duration: 0.6, ease: "power2.in" }, t); }
        function zoom(sel, t, origin, s, back) {
          tl.fromTo(sel, { scale: 1, transformOrigin: origin }, { scale: s, duration: 0.9, ease: "expo.inOut", immediateRender: false }, t);
          tl.to(sel, { scale: 1, duration: 0.8, ease: "expo.inOut" }, back);
        }
        liveIn("#LV1", 28.8); liveOut("#LV1", 48.95);
        liveIn("#LV2", 53.5); liveOut("#LV2", 71.05);
        liveIn("#LV3", 71.05); liveOut("#LV3", 95.45);
        tl.fromTo("#LV1 .onair b, #LV2 .onair b, #LV3 .onair b", { opacity: 1 }, { opacity: 0.25, duration: 0.6, ease: "sine.inOut", repeat: Math.floor(67 / 0.6) - 1, yoyo: true }, 28.8);

        // swatches over the live hero
        $$("#sw .s").forEach((s, i) => {
          const t = [W("look", "noir"), W("look", "ivoire"), W("look", "or")][i] - 0.1;
          tl.fromTo(s, { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.8, ease: EX }, t);
          tl.fromTo(s.querySelector(".c"), { scale: 0 }, { scale: 1, duration: 0.8, ease: "back.out(1.8)" }, t);
        });
        tl.to("#sw .s", { opacity: 0, x: 40, duration: 0.5, ease: "power2.in", stagger: 0.05 }, W("look", "maisons") + 0.4);

        // step tags over the live frames (one slot, bottom-left)
        const tagBox = $("#tags");
        function tag(label, t0, t1, opts = {}) {
          const d = document.createElement("div"); d.className = "tag" + (opts.gold ? " gold" : "");
          d.innerHTML = (opts.n ? `<span class="n">${opts.n}</span>` : "") + label;
          d.style.left = (opts.x ?? 200) + "px"; d.style.top = (opts.y ?? 866) + "px";
          tagBox.appendChild(d);
          tl.fromTo(d, { opacity: 0, x: -30, scale: 0.94 }, { opacity: 1, x: 0, scale: 1, duration: 0.5, ease: EX }, t0);
          tl.to(d, { opacity: 0, x: 20, duration: 0.3, ease: "power2.in" }, t1 - 0.3);
        }
        tag("Défilement en direct", W("scroll", "regardez"), W("reel", "vos"));
        tag("9 métiers, un seul site", W("reel", "neuf"), W("reel", "vos", 1));
        tag("Réalisations en mode cinéma", W("reel", "réalisations"), 49.0);
        tag("Prestation", W("devis1", "prestation") - 0.1, W("devis1", "règle"), { n: "01" });
        tag("Durée", W("devis1", "règle") - 0.1, W("devis1", "ajoute"), { n: "02" });
        tag("Options", W("devis1", "ajoute") - 0.1, W("devis2", "prix"), { n: "03" });
        tag("Prix recalculé en direct", W("devis2", "prix") - 0.1, W("devis3", "il"), { gold: true, x: 200, y: 86 });
        tag("Validation", W("devis3", "valide") - 0.1, W("devis3", "sans"), { n: "04" });
        tag("Zéro appel", W("devis3", "sans") - 0.1, W("rdv", "il"), { gold: true });
        tag("Rendez-vous en ligne", W("rdv", "réserve") - 0.1, 71.0, { n: "05" });
        tag("Connexion client", W("client2", "connecte") - 0.1, W("client2", "retrouve"));
        tag("Toutes les commandes, au même endroit", W("client2", "retrouve") - 0.1, W("client3", "les"));
        tag("En cours · avancement", W("client3", "projets") - 0.1, W("client4", "les"), { n: "01" });
        tag("Livrées · fichiers à télécharger", W("client4", "livrées") - 0.1, W("client5", "et"), { n: "02" });
        tag("Devis · validation en un clic", W("client5", "devis") - 0.1, W("client6", "plus"), { n: "03" });

        // zooms on the key moments
        zoom("#Z2", W("devis2", "prix") - 0.2, "79% 26%", 1.32, W("devis3", "il") - 0.2);
        zoom("#Z3", W("client3", "avancement") - 0.3, "30% 64%", 1.25, W("client4", "les") - 0.5);
        zoom("#Z3", W("client4", "fichiers") - 0.3, "86% 66%", 1.3, W("client5", "et") - 0.25);

        // client space: title card, then closing line
        tl.fromTo("#hdim", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out" }, W("client1", "et") - 0.2);
        tl.fromTo("#hc", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("client1", "et") - 0.1);
        tl.fromTo("#hc .k", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: EX }, W("client1", "l'atout") - 0.1);
        tl.fromTo("#hc .t", { opacity: 0, scale: 1.25, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.9, ease: EX }, W("client1", "l'espace") - 0.15);
        tl.fromTo("#hc .s", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: EX }, W("client1", "client") + 0.1);
        flash(W("client1", "l'espace"), 0.45);
        tl.to("#hc", { opacity: 0, scale: 0.96, duration: 0.5, ease: "power2.in" }, W("client2", "votre") - 0.25);
        tl.to("#hdim", { opacity: 0, duration: 0.6, ease: "power2.inOut" }, W("client2", "votre") - 0.25);
        tl.to("#LV3", { x: -250, scale: 0.74, duration: 1.1, ease: "expo.inOut" }, W("client6", "plus") - 0.2);
        tl.fromTo("#hend", { opacity: 0 }, { opacity: 1, duration: 0.01 }, W("client6", "plus"));
        tl.fromTo("#hend .k", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.7, ease: EX }, W("client6", "plus") + 0.3);
        tl.fromTo("#hz1", { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.7, ease: EX }, W("client6", "relances") - 0.1);
        tl.fromTo("#hz2", { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.7, ease: EX }, W("client6", "fichiers") - 0.1);
        masks("#hend .l", W("client6", "votre") - 0.1, 0.5);
        tl.to("#hend", { opacity: 0, duration: 0.5, ease: "power2.in" }, 95.45);

        // ================= F · SELLS
        masks("#F-l1", W("sells", "ce") - 0.1, 0.1, 0.9);
        tl.fromTo("#F-disc", { clipPath: "circle(0% at 50% 62%)" }, { clipPath: "circle(90% at 50% 62%)", duration: 0.9, ease: "expo.inOut" }, W("sells", "il") - 0.35);
        tl.to("#F-l1", { color: "#948D7E", y: -40, scale: 0.82, duration: 0.9, ease: "expo.inOut" }, W("sells", "il") - 0.35);
        tl.fromTo("#F-l2", { opacity: 0, scale: 1.5, filter: "blur(18px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.8, ease: EX }, W("sells", "il") - 0.05);
        flash(W("sells", "vend"), 0.8);

        // ================= K · BENEFITS
        const kw = [W("benef", "moins"), W("benef", "plus"), W("benef", "une")];
        ["#K-1", "#K-2", "#K-3"].forEach((s, i) => {
          tl.fromTo(`${s} .mask > .in`, { yPercent: 115 }, { yPercent: 0, duration: 0.9, ease: EX }, kw[i] - 0.1);
          if (i < 2) tl.to(`${s}`, { opacity: 0.28, duration: 0.6 }, kw[i + 1] - 0.1);
        });
        tl.to("#K-1, #K-2", { opacity: 1, duration: 0.6 }, W("benef", "irr") + 0.3);
        tl.fromTo("#K .lines", { scale: 1.06 }, { scale: 1, duration: 5.5, ease: "power1.out" }, 95.5);

        // ================= L · MOBILE
        browserIn("#L-br", 100.8, { y: 100, rx: 8 });
        tl.to("#L-br", { opacity: 0.35, scale: 0.9, duration: 1.0, ease: "expo.inOut" }, W("mobile", "écrans") - 0.3);
        const lp = [["#L-p1", -12, W("mobile", "écrans")], ["#L-p2", 0, W("mobile", "élégant")], ["#L-p3", 12, W("mobile", "mobile")]];
        lp.forEach(([s, r, t]) => tl.fromTo(s, { y: 700, rotate: r * 2, opacity: 0 }, { y: 0, rotate: r * 0.5, opacity: 1, duration: 1.1, ease: EX }, t - 0.2));
        tl.to("#L-br", { opacity: 1, scale: 1, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);
        tl.to("#L-p1, #L-p2, #L-p3", { y: 120, scale: 0.72, duration: 1.0, ease: "expo.inOut", stagger: 0.05 }, W("mobile", "grand") - 0.2);
        tl.to("#L-p1", { x: -470, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);
        tl.to("#L-p3", { x: 470, duration: 1.0, ease: "expo.inOut" }, W("mobile", "grand") - 0.2);

        // ================= M · DESIGN SYSTEM
        eyebrow("#M", 105.65);
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
        eyebrow("#N", 117.65);
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
        tl.fromTo("#O .grp", { scale: 1.04 }, { scale: 1, duration: 8, ease: "power1.out" }, 128.2);
        tl.to("#O .cam", { opacity: 0, duration: 1.0, ease: "power2.in" }, 135.8);

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
