# PACK MONEY BOOST 2026 — Cinematic Gold Noir

## Film Direction

**Palette:** 60% deep near-black ground / 30% photographic stills + translucent CSS glass panels + hairline rules / 10% accent — brand-primary gold carries hero keywords, underlines, the value-stack checkmarks and the CTA button only; white (brand-costume) is the working ink for body and headlines. Gold stays rare: keyword, line, or button — never a fill. Ink/canvas read as off-black, never pure #000.
**Type:** display = single hero claims and scene core words (heavy, tight tracking); mono uppercase wide-tracked = eyebrows / scene markers / app-chip + card labels; body = supporting sentences and checklist items. Three-voice system; size jumps stay 2-3x for one-second legibility.
**Motion:** entries `EASE.entry`; large photos and the book are heavy; idle drift `EASE.drift`; emphasis `EASE.emphasis`; exits none — scenes hold the final frame. Budget per scene: ONE root-level macro motion (slow Ken-Burns zoom/pan on photo scenes, dolly/push on graphic scenes) + at most 1-2 secondary live elements (a breathing hero, a glowing chip, a CTA glow pulse). Everything else rests.
**Ambient:** NO WebGPU aurora (render target has no GPU). Base is solid off-black or a simple two-stop CSS gradient toward off-black, full-bleed every scene; on photo scenes a dark vignette + bottom-up scrim gradient seats white/gold text. A faint, sparse gold particle/dust drift is the only optional extra layer. Translucent glass panels use CSS backdrop-blur + low-opacity white, never a shader.
**Never (film-wide):** no WebGPU/liquid-glass aurora shader, no mesh gradients, no neon-on-black, no glow bloom, no purple-blue AI gradient, no bokeh balls, no nav/browser chrome, no exclamation/all-caps in body copy.
**Transitions:** crossfade (calm photo↔photo, reveals) + push-slide (montage / card cascade forward flow). Only these two repeated.
**Stillness-before-climax:** Scene 5 (book reveal) and Scene 7 (CTA) only.
**Assets:** `public/img/s1_student.jpg` → Scene 1 primary (full-frame still); `public/img/s1_phone.jpg` → Scene 1 inset detail (phone job-search). `public/img/s2_brick.jpg`, `public/img/s2_cement.jpg`, `public/img/s2_sweat.jpg`, `public/img/s2_market.jpg` → Scene 2 montage stills; `public/img/s2_coins.jpg` → Scene 2 closing payoff still. `public/img/pack_book.jpg` → Scene 5 primary reveal, reused Scene 6 (open-value) and Scene 7 (CTA) as the product anchor. Scenes 3 and 4 have no photos — pure gold/black graphic scenes.

## Scene 1: HOOK — VACANCES SANS REVENU

**Effects:** [`multi-phase-camera`, `asr-keyword-glow`, `coordinate-target-zoom`]
**Duration:** 4.08s
**Transition:** crossfade

Anxious, scroll-stopping, a held breath of frustration. Layered-depth portrait composition: `public/img/s1_student.jpg` fills the full frame as a cinematic still (~100%) under a dark vignette and bottom-up scrim; the frustrated student and phone own the lower-mid frame, white headline stacked in the upper-mid safe zone. Macro motion: slow Ken-Burns push (`multi-phase-camera`) creeping toward the phone across the whole beat. ~0.4s in, the white question "TU ES EN VACANCES ET TU CHERCHES UN REVENU ?" rises; "REVENU" catches a single gold `asr-keyword-glow` pulse on the narration stress (~1.6s). At ~2.4s a small inset of `public/img/s1_phone.jpg` (job-search results) eases up via `coordinate-target-zoom` into the lower third while the sub-line "Ne passe pas tes journées dans des jobs qui te fatiguent pour peu." fades in beneath. Hold on the frustrated frame. Eye settles on the phone, then cuts forward into the labour montage.

## Scene 2: LE PROBLÈME — TRAVAILLER PLUS, GAGNER PEU

**Effects:** [`viewport-change`, `discrete-text-sequence`, `reactive-displacement`, `asr-keyword-glow`]
**Duration:** 7.85s
**Transition:** push-slide LEFT

Heavy, fatigued, an accelerating grind that lands on injustice. Fast-montage of full-frame stills, each under dark scrim: `s2_brick.jpg` → `s2_cement.jpg` → `s2_sweat.jpg` → `s2_market.jpg` cut roughly every ~1.3s, each pushed in/out with a small Ken-Burns. Macro motion: continuous left push-pan (`viewport-change`) carrying the montage forward, photos parallaxing past. Over the first stills "BEAUCOUP TRAVAILLENT PLUS…" types in via `discrete-text-sequence`; on the market shot it is displaced by "MAIS GAGNENT TOUJOURS PEU." entering hard from the right (`reactive-displacement`), the new line shoving the old off — physical, causal. Final ~1.6s lands on `public/img/s2_coins.jpg` (coins in palm), motion stilling; the mono label "PETITE RÉMUNÉRATION" fades in low, "PEU" carrying one dim gold `asr-keyword-glow`. The injustice sits on the meagre coins; eye exits toward the reframe.

## Scene 3: LA RÉVÉLATION — TON TÉLÉPHONE, UN OUTIL

**Effects:** [`multi-phase-camera`, `orbit-3d-entry`, `svg-icon-enrichment`, `sine-wave-loop`]
**Duration:** 6.85s
**Blueprint:** composed
**Transition:** zoom-through

Hopeful exhale, a luminous lift after the grind — premium and slow. Centered graphic composition on off-black: a clean CSS phone outline (rendered as a glass-edged device frame, ~45% of canvas) holds the frame center, white headline "TON TÉLÉPHONE PEUT DEVENIR TON OUTIL DE TRAVAIL." stacked above. Macro motion: slow dolly-push (`multi-phase-camera`) into the phone as the light shifts warmer. From ~1.2s three gold-rimmed glass app chips — Canva, ChatGPT, WhatsApp Business — flip in and settle into a shallow arc around/inside the phone via `orbit-3d-entry` (staggered, total <500ms); each chip's small glyph animates alive with `svg-icon-enrichment` (pulsing dot, drawing stroke). After settling, the phone and chips breathe with `sine-wave-loop` as the single live cluster. Gold appears only on the chip rims and the keyword "OUTIL." Eye rests on the lit phone, then pushes through into the services.

## Scene 4: SERVICES — CE QUE TU PEUX VENDRE

**Effects:** [`viewport-change`, `center-outward-expansion`, `press-release-spring`, `sine-wave-loop`]
**Duration:** 8.19s
**Transition:** push-slide LEFT

Confident, concrete, momentum building — four clean beats of "you could sell this." Stacked-band portrait composition (no side-by-side in tall frame): four gold-hairlined glass service cards stack vertically, each ~20% canvas height, a mono uppercase label per card — "CRÉATION DE CV", "FLYERS CANVA", "GESTION RÉSEAUX SOCIAUX", "SERVICES IA". Macro motion: gentle vertical drift/parallax on the card stack (`viewport-change`). Cards enter staggered from center outward (`center-outward-expansion`), ~1.7s apart so each lands as its service is named, total reveal pacing the 8s. As the last card seats, a soft `press-release-spring` tap pulses the "SERVICES IA" card to mark the climax of the list. Settled cards drift with `sine-wave-loop` as the one live element. Gold only on each card's thin rule and the active label. Eye travels top-to-bottom down the stack, then lifts into the golden product reveal.

## Scene 5: LE PACK — MONEY BOOST 2026

**Effects:** [`coordinate-target-zoom`, `3d-text-depth-layers`, `sine-wave-loop`, `asr-keyword-glow`]
**Duration:** 9.09s
**Blueprint:** based-on `brand-reveal-assemble-zoom`
**Transition:** zoom-through

Aspirational, luminous, the gold-lit launch moment — slow and reverent. Centered hero composition: `public/img/pack_book.jpg` (book on a gold-lit pedestal) is the primary, ~55% of canvas, on deep off-black with a soft golden floor glow. Following the assemble-zoom skeleton: the title "PACK MONEY BOOST 2026" assembles beside/above the book as a `3d-text-depth-layers` gold-and-white stack, "2026" the heaviest layer; then the camera `coordinate-target-zoom` pushes in to center the book as the companion title recenters above it. **Stillness-before-climax (~0.6s):** after the zoom settles, a held pause before the sub-line "LE SYSTÈME COMPLET POUR COMMENCER." fades in white below, "COMPLET" catching one gold `asr-keyword-glow`. The book then breathes with `sine-wave-loop` (multiplicative, on final scale) as the single live element. Eye locks on the book, carrying into its contents.

## Scene 6: VALEUR — CE QU'IL Y A DEDANS

**Effects:** [`multi-phase-camera`, `svg-path-draw`, `center-outward-expansion`, `sine-wave-loop`]
**Duration:** 6.08s
**Transition:** push-slide LEFT

Desire stacking, generous, "look how much is inside" — measured and satisfying. Asymmetric portrait composition: `public/img/pack_book.jpg` sits slightly off-center (lower/left, ~40%) as the source the value flies from; the mono eyebrow "À L'INTÉRIEUR" tops the frame. Macro motion: slow dolly-in (`multi-phase-camera`) toward the book. A five-item checklist stacks outward from the book via `center-outward-expansion` — "15 MÉTHODES", "50 SCRIPTS", "TEMPLATES CANVA", "PROMPTS IA", "PLAN D'ACTION" — staggered (total <500ms), each line led by a gold check whose stroke draws on with `svg-path-draw` as the item lands. The book breathes with `sine-wave-loop` as the one live element while the list holds for reading. Gold only on the five checkmarks and the keyword digits. Eye runs down the value stack, then drives into the CTA.

## Scene 7: CTA — TÉLÉCHARGER MAINTENANT

**Effects:** [`multi-phase-camera`, `press-release-spring`, `cursor-click-ripple`, `sine-wave-loop`]
**Duration:** 8.94s
**Hierarchy:** action
**Transition:** crossfade

Decisive, motivating, a calm confident close — the command lands clean. Centered composition: `public/img/pack_book.jpg` anchored upper-mid (~40%) as the product, the white line "CHANGE TES VACANCES, CHANGE TON AVENIR." stacked above it, and the golden CTA button "TÉLÉCHARGER MAINTENANT" owning the center-lower safe zone (captions disabled, so the lower band is usable). Macro motion: slow dolly-push (`multi-phase-camera`) settling on the button. The button enters and breathes with a gentle gold glow pulse (`sine-wave-loop`) as the live element. **Stillness-before-climax (~0.6s):** the button holds glowing and still before a cursor glides in (`cursor-click-ripple`) and a `press-release-spring` depresses it with an outward gold ripple on the click — the payoff. Book breathes faintly behind, demoted to support. Gold carries the button and ripple only. Final frame holds on the pressed CTA.
