# Money Boost 2026 — Section Plan

## Film Direction

Preset: **neo-brutalism**, portrait 1080×1920, captions disabled. This is a non-mesh preset — the project mesh default does NOT apply. Backgrounds are preset-native and consistent across the whole film: solid brand canvas (`--canvas` white or a flat brand-color fill) OR `dot-grid-bg`. Never gradient, never soft halo, never blur background. Bright/light is the baseline; the only dark scene (Scene 1 hook) is a deliberate narrative open, not a per-scene swing, and the film snaps to bright canvas from Scene 2 onward.

Palette / 60-30-10 (roles from `tokens.css`, never hex in prose): 60% canvas (white or flat brand fill per scene), 30% bold-bordered surfaces + hard `--ink` borders/dividers (the brutalist `--border-bold` / `--border-loud` + `--shadow-hard` does the structural work, not a soft surface tier), 10% accent on the one focal element — `--brand-primary` (orange) as the energy/CTA accent, `--brand-secondary` (blue) as the contrast/stability accent, deco tokens (`--deco-1..4`) only as flat sticker blocks behind hero type. Accent purpose is fixed film-wide: orange = action/urgency/money, blue = control/stability/proof. `--ink` is print-like ink on light scenes. Never neon, never purple-blue AI gradient.

Type roles (by role, never px/em): display tier (`--font-display`, Anton) for the one huge hero word per scene with tight tracking; mono (`--font-mono`, Space Mono) UPPERCASE wide-tracked for eyebrows/labels/module tags = "real-tool" metadata feel; body (`--font-body`, Inter) only for the rare supporting line, 900 weight if ever used at display size. Hierarchy is 3:1+ size jumps plus weight + case + a deco-block color contrast — legible in under one second. Voice recipe (uppercase, strip articles, noun fragments, `.`-joined, brand punchline) applies to all DOM text by default; no scene needs special text handling — narration stays natural French TTS.

Composition: "one huge thing per scene", display 200–340px-feel dominating the frame; primary visual ≥40% of the tall canvas; ≥3 depth layers (flat sticker deco block + hard-shadow framed content + corner-pins/foreground accent). Stack vertically — portrait, so any comparison/triptych becomes top/bottom bands. Vertical center anchors at y≈806 (0.42×1920). Captions disabled, so bottom band is usable. Use `corner-pins` on framed scenes. At least 3 different layout templates across the 7 scenes (Centered, Split→stacked, Full-Width-Strip-as-stack, Asymmetric).

Motion budget — ONE macro move per scene (camera-style drift/push on scene root) + at most 1–2 secondary live elements (hero breathing OR CTA glow), everything else rests. Springs by intent from `easings.js`: `EASE.entry` (back.out slam-pop) for primary hero entries, `EASE.emphasis` (expo.out) for hard arrivals, `EASE.exit` (power4.in) for departures, `EASE.drift` only for ambient breathing. Hit-and-stick — never ease-in-out for primary motion. Stagger 100–150ms between elements, total ≤500ms. Forbid yoyo / bounce.out / elastic.out. Multiplicative breathing (±2–5%) is reserved for a hero holding a live slot, not stamped everywhere.

Stillness-before-climax (0.3–0.75s pause between action and payoff) is allocated to exactly 3 scenes where narration lands a payoff: **Scene 2** (number lands), **Scene 4** (brand logo lands), **Scene 7** (CTA confirm). No other scene adds it.

Transition vocabulary — 2 types repeated film-wide: **push-slide** (directional, matches the brutalist hard-directional energy and the script's slide beats) and **zoom-through** (the Scene 4 push-through-the-split reveal + high-energy snaps). Direction alternates across seams. Scene 1 is the open (no incoming transition).

Ambient system: sparse — either a static `dot-grid-bg` or 2–3 flat deco sticker blocks per scene; NO floating particle clouds, NO mesh, NO gradient swell. Aliveness comes from the single macro camera move plus the hero's entry, not from many independent oscillators.

Film negative list: no gradients, no crossfade/blur transitions, no soft drop-shadows (only hard offset `--shadow-hard`), no mesh background, no neon-on-black, no purple-blue AI gradient, no nav bars / scrollbars / browser chrome (Scene 7 cursor+button is the one intentional UI element), no generic decorative blobs replacing content, no per-scene dark/light swings.

Asset coverage: `assetCandidates` is empty for every scene — there are NO real product assets. Build all visuals from brand-native type, flat deco sticker blocks, hard-bordered frames, corner-pins, and brutalist iconography (simple bold-stroke SVG glyphs for modules/benefits). Social proof (Scene 6) uses brutalist avatar placeholders (bold-bordered circles), not fabricated photos. Money/results framing stays typographic, not faked screenshots.

## Scene 1: HOOK — 2026 ARRIVE
**Effects:** `hacker-flip-3d`, `multi-phase-camera`, `3d-text-depth-layers`
**Duration:** 6.0
**Blueprint:** composed
**SFX:**
- `glitch-1.mp3` at 0.2s — hard-cut accent on the "2026 ARRIVE" punch-in, decay bleeds forward
- `impact-bass-1.mp3` at 0.6s — headline slam landing

The one dark scene — deliberate night-frame open, not a per-scene swing. Centered template. Background: near-black `--ink` flat ground (the brutalist dark open) with a faint `dot-grid-bg` overlay; this is the single exception, film snaps bright at Scene 2. Hero: "2026" in mega display tier decodes via `hacker-flip-3d`, then "ARRIVE" slams under it as a `3d-text-depth-layers` stack so the glowing-phone-light feel reads as cold extruded type. Macro move: slow `multi-phase-camera` push-in (pull-back → settle) for unease. A small mono UPPERCASE eyebrow holds the rhetorical-question fragment beneath. Hero holds the live breathing slot ±2%. Corner-pins frame the dark card. The fear question is carried by stillness and the cold extrusion, not by extra motion.

## Scene 2: CHIFFRE CHOC — 365 JOURS
**Effects:** `counting-dynamic-scale`, `center-outward-expansion`, `multi-phase-camera`, `svg-icon-enrichment`
**Duration:** 5.0
**Blueprint:** based-on hook-counter-burst
**Transition:** zoom-through
Hard snap from dark to bright — flat brand canvas, `dot-grid-bg`. based-on `hook-counter-burst`: role (statistic) + trigger (dramatic number) fit directly. Centered template, one huge thing. "365" counts up with `counting-dynamic-scale` (font grows with the value) to fill the vertical frame, "JOURS" mono label locked beneath. A few enriched calendar/clock SVG glyphs (`svg-icon-enrichment` — ticking hand) expand outward from center via `center-outward-expansion`, then rest. Macro: `multi-phase-camera` (0.92→1.0→1.08). Deco sticker block (one `--deco` color) sits flat behind the number for brutalist contrast. **stillness-before-climax** 0.5s: the count finishes, everything freezes, only the camera drifts, then "JOURS" snaps in — the number lands before the label confirms.

## Scene 3: PROBLÈME — SUBIR ou BOOSTER ?
**Effects:** `split-tilt-cards`, `sine-wave-loop`, `reactive-displacement`
**Duration:** 6.5
**Blueprint:** based-on comparison-split-cards
**Transition:** push-slide DOWN
based-on `comparison-split-cards`, adapted to portrait → top/bottom stacked bands (no side-by-side in a tall frame). Top band = passive drift (scroll/spend, blue-leaning, lower-energy, slight `--ink` desaturated feel); bottom band = active control (manage/invest, orange-leaning, sharper). Each band is a hard-bordered surface with `--shadow-hard`; bands enter from opposite edges via `push-slide`-style opposing motion and a light `reactive-displacement` so the seam feels physical. Bicolor "SUBIR ou BOOSTER ?" lands on the seam — "SUBIR" blue, "BOOSTER" orange, forcing the binary. Macro: slow vertical dolly across the seam. One `sine-wave-loop` float on the seam headline only; bands rest. Corner-pins frame both bands.

## Scene 4: SOLUTION — MONEY BOOST 2026
**Effects:** `discrete-text-sequence`, `coordinate-target-zoom`, `center-outward-expansion`, `sine-wave-loop`
**Duration:** 10.0
**Blueprint:** composed
**Transition:** zoom-through
Camera pushes through the prior split into center — `zoom-through` carries it. Composed: brand assemble + module cascade, no single blueprint covers "logo + 5 stacked module tags". Centered → then asymmetric stack. "MONEY BOOST 2026" wordmark assembles via `discrete-text-sequence` (display tier, orange+blue split lockup) with `coordinate-target-zoom` settling it dead-center on the bright canvas. Then 4–5 module tags (Business en ligne / Finances / Investissement / IA) stagger-drop as mono UPPERCASE hard-bordered chips stacked below via `center-outward-expansion`, 100–150ms apart, total ≤500ms, then rest. Each chip a flat `--deco` sticker. Macro: gentle settle-drift after the push. Hero wordmark holds breathing slot ±3%. **stillness-before-climax** 0.6s: wordmark assembles and freezes, only the drift continues, THEN the module chips cascade — the brand lands before the value stack confirms.

## Scene 5: BÉNÉFICES — CE QUE TU OBTIENS
**Effects:** `dynamic-content-sequencing`, `context-sensitive-cursor`, `asr-keyword-glow`
**Duration:** 9.0
**Blueprint:** based-on messaging-multi-phrase
**Transition:** push-slide UP
based-on `messaging-multi-phrase`: role (sequential statements) + trigger (multiple phrases, dual-color) fit. Full-width-strip-as-vertical-stack template: four benefit lines slide up and stack on one bright surface, eye building downward — "STRATÉGIES CONCRÈTES", "OUTILS PRÊTS", "ACCOMPAGNEMENT", "COMPÉTENCES → ARGENT". `dynamic-content-sequencing` computes per-line timing from content length; each line types/reveals with a `context-sensitive-cursor` whose accent flips (blue label → orange payoff word). The final line's money payoff word gets `asr-keyword-glow` emphasis. Each line is a hard-bordered band with offset `--shadow-hard`; the active line is full-contrast, prior lines demote one step (the supporting rail). Macro: slow upward dolly following the stack growth. Lines rest once landed; no extra floats.

## Scene 6: PREUVE SOCIALE — ILS L'ONT DÉJÀ FAIT
**Effects:** `avatar-cloud-network`, `vertical-spring-ticker`, `coordinate-target-zoom`
**Duration:** 5.5
**Blueprint:** based-on proof-logo-chain
**Transition:** push-slide DOWN
**Hierarchy:** social-proof, multi-act
**PrimarySubjectTimeline:** 0.0–2.2s primary = avatar-cloud cluster assembling (the proof building); 2.2–5.5s primary = "ILS L'ONT DÉJÀ FAIT" headline, avatars + ticker demote to supporting background rail.
**Handoff:** the avatar cluster and result ticker compact and demote to a lower-contrast supporting background rail outside the headline's safe zone as the headline zooms to primary; nothing competes with the call-to-identify.

based-on `proof-logo-chain` (social-proof role, "they already did it" trigger), adapted: no real photos exist, so use brutalist avatar placeholders. `avatar-cloud-network` arranges bold-bordered avatar circles in a compact portrait cluster connected to a center hub, staggering in as the "community". A `vertical-spring-ticker` rolls 2–3 short result fragments (slot-machine) as supporting proof. Bold "ILS L'ONT DÉJÀ FAIT" headline overlays as the primary — `coordinate-target-zoom` lands the eye on it; the avatar cluster + ticker are explicitly the supporting/demoted background rail behind the headline, lower contrast, smaller, outside the headline bbox. Macro: slow push-in onto the headline. Hard-bordered frame, corner-pins.

## Scene 7: CTA + URGENCE — PLACES LIMITÉES
**Effects:** `physics-press-reaction`, `cursor-click-ripple`, `scale-swap-transition`, `hacker-flip-3d`
**Duration:** 9.0
**Blueprint:** based-on cta-morph-press
**Transition:** zoom-through
**Hierarchy:** action, multi-act
**PrimarySubjectTimeline:** 0.0–4.0s primary = "REJOINDRE MAINTENANT" CTA button + cursor (the action); 4.0–9.0s primary = "INSCRIPTIONS OUVERTES" end-card headline (the payoff), button demotes.
**Handoff:** after the click confirms, the CTA button compacts and demotes via scale-swap as the end-card headline scales to primary; the scarcity proof line sits as a supporting rail below, outside the headline bbox, never competing with the confirm.

based-on `cta-morph-press` (cursor clicks button, brand-to-action). Hard-cut feel into a bright bicolor end card (flat blue/orange split fill — brutalist, NOT a gradient). Phase 1: "REJOINDRE MAINTENANT" button (hard-bordered, orange, `--shadow-hard`) sits center; a cursor enters via spring path and presses it through `physics-press-reaction` + `cursor-click-ripple`. **stillness-before-climax** 0.5s: cursor lands, both compress, hold still on the pressed beat. Phase 2: the press triggers `scale-swap-transition` — "PLACES LIMITÉES" `hacker-flip-3d` decodes into "INSCRIPTIONS OUVERTES" (urgency → open), the payoff. Signature line sits mono UPPERCASE below. Centered template, one huge confirm. Macro: slow push-in onto the end card. CTA holds the one live slot (glow pulse pre-click); after confirm, the headline holds and everything else rests.
