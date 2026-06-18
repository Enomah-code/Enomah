# L'Art de Bien Parler — Cinematic Ebook Ad (Navy / Gold)

## Film Direction

**Palette:** 60% deep-navy ground (`--navy` / `--liquid-bg-fallback` cinematic gradient) — for photo scenes this is the navy scrim laid over the full-bleed image / for the CTA it is the literal canvas / 30% the photograph itself + white body text reading on the scrim / 10% accent: GOLD (`--gold` / `--gold-bright`) carries every serif title, the emphasised keyword in each line, hairline rules, checkmarks, and the CTA button + arrow. White is body/supporting text; gold is rare and always the focal word. Never flood gold.
**Type:** display = Playfair-role serif for the product title, scene headlines and the gold keyword (elegant high-contrast); body = Inter-role for supporting sentences and check-item labels; no mono voice in this film. Hero claims sit in display tier, supporting sentences one tier down with clear 3:1 size + weight + color contrast.
**Motion:** entries `EASE.entry`, large photo/hero blocks read as `heavy`; idle `EASE.drift`; exits none — each scene holds its final frame and the camera carries continuity. Budget: every scene gets ONE root-level macro motion — a slow Ken-Burns push/pan on the full-bleed photo (or dolly on the CTA poster) — plus at most one secondary live element (a gold keyword glow, a check stagger, or the CTA pulse). Everything else rests.
**Ambient:** real photographs are the atmosphere — full-bleed, slow Ken-Burns, with a navy scrim gradient (top-and-bottom darken) under all text for legibility; CTA scene swaps to the navy gradient ground with a faint gold-bokeh/starfield from layered radial-gradients. No shader aurora (no GPU). A faint gold hairline accent may sit per scene.
**Never (film-wide):** no WebGPU/shader aurora, no mesh gradients, no neon-on-black, no glow bloom, no purple-blue AI gradient, no decorative floating bokeh balls, no stock-icon clutter, no letterboxing or stretch-distorting the photos.
**Transitions:** crossfade + zoom-through only (calm dissolves between emotional beats; zoom-through on the camera-push moments). Scene 1 opening is a placeholder.
**Stillness-before-climax:** Scene 4 (the gold title + checks land) and Scene 6 (the pulsing CTA button lands) only.
**Assets:** `public/img/s1_stress.png` → Scene 1 primary (full-bleed); `public/img/s2_problemes.png` → Scene 2 primary (pre-labelled montage, full-bleed); `public/img/s3_frustration.png` → Scene 3 primary (full-bleed); `public/img/s4_solution.jpg` → Scene 4 primary (full-bleed); `public/img/s5_transform.jpg` → Scene 5 primary (full-bleed); `public/img/s6_poster.jpg` → Scene 6 primary (product poster, centered on navy).

## Scene 1: HOOK — BLOQUÉ

**Effects:** [`multi-phase-camera`, `asr-keyword-glow`]
**Duration:** 3.07s
**Hierarchy:** simple
**Transition:** crossfade

Anxious, frozen, breath-held — a slow tightening with one held beat, no bounce. Layered-depth composition: `public/img/s1_stress.png` fills 100% of the tall frame (the anxious man frozen as others stare), a navy scrim gradient darkening top and bottom thirds so white text reads. Primary subject is the photo; the white serif-leaning question sits in the lower-middle reading zone over the scrim, three depth layers (photo midground, scrim, text foreground). Macro motion: `multi-phase-camera` slow push-in toward the man's face across the whole beat (pull-tight, no pan). The rhetorical question "Tu as de bonnes idées mais tu n'arrives jamais à les exprimer ?" rises in; `asr-keyword-glow` gives a single restrained gold pulse to the keyword **exprimer** as the line settles — the one live element. Eye drifts inward on the push, carrying into the problem montage.

## Scene 2: LE PROBLÈME — TU PERDS TES MOYENS

**Effects:** [`viewport-change`, `asr-keyword-glow`]
**Duration:** 5.89s
**Hierarchy:** simple
**Transition:** crossfade

Mounting social stress — a continuous, slightly claustrophobic build, one take. Full-bleed composition: `public/img/s2_problemes.png` fills the frame; it is a PRE-COMPOSED montage that ALREADY carries its own labelled panels (STRESS / HÉSITATION / MANQUE DE CONFIANCE / SILENCE GÊNANT), so it is the whole subject — do NOT overlay competing big headlines on top of it. A light navy scrim only at the very top edge holds a single small gold keyword "Le problème" as an eyebrow; the montage's own labels carry the message. Macro motion: `viewport-change` slow continuous push-in (~2-4%) across the montage so the labelled panels feel like they close in. `asr-keyword-glow` lets the small gold eyebrow word warm faintly as the narration agitates — the only added motion. No big white text block over the montage; the photo speaks. Eye stays centered, pressure rising, into the frustration beat.

## Scene 3: LA FRUSTRATION — IDÉES INVISIBLES

**Effects:** [`multi-phase-camera`, `asr-keyword-glow`]
**Duration:** 4.91s
**Hierarchy:** simple
**Transition:** zoom-through

Regret and loss — a sinking beat, slower, heavier than Scene 2. Layered-depth composition: `public/img/s3_frustration.png` full-bleed (another presents confidently / people applaud / the main character looks down, regretful); navy scrim weighted to the lower third under the line. White serif line "Tes idées restent invisibles…" sits low-center over the scrim, the ellipsis trailing the regret; gold carries only the keyword **invisibles**. Macro motion: `multi-phase-camera` does a slow push that settles on the downcast main character (focus drifts from the applauded speaker to him). `asr-keyword-glow` fades **invisibles** up as the line lands — one live element, everything else still. Eye pushes through toward the turn, zoom-through into the solution reveal.

## Scene 4: LA SOLUTION — L'EBOOK

**Effects:** [`multi-phase-camera`, `svg-path-draw`, `asr-keyword-glow`, `sine-wave-loop`]
**Duration:** 8.17s
**Hierarchy:** simple
**Transition:** zoom-through

The turn — hope arrives, luminous and premium; a confident slow build with a held breath before the title locks. Centered/hero composition: `public/img/s4_solution.jpg` full-bleed (confident man in tux holding the book), gentle navy scrim top and bottom. Phase 1 (~0–2s): photo pushes in, the gold serif title "L'ART DE BIEN PARLER" rises in display tier with "Maîtriser l'éloquence" one tier below in white. Phase 2 (~2–5.5s): four gold check items stagger in down the lower reading zone — Confiance, Éloquence, Persuasion, Prise de parole — each checkmark drawn live with `svg-path-draw` (total stagger ≤500ms), the line warming via `asr-keyword-glow` on the spoken benefit words. **stillness-before-climax** (~0.5s) after the title rises, before the first check draws, letting the promise breathe. Macro motion: `multi-phase-camera` slow push on the book; the title block gets a subtle `sine-wave-loop` breathing as the one live hero. Photo subject stays primary; checks are supporting. Eye climbs the check list, zoom-through into the transformation.

## Scene 5: LA TRANSFORMATION

**Effects:** [`multi-phase-camera`, `asr-keyword-glow`]
**Duration:** 5.27s
**Hierarchy:** simple
**Transition:** crossfade

Empowerment — uplifting, expansive, the after-state; a confident rising glide. Layered-depth composition: `public/img/s5_transform.jpg` full-bleed (the man now speaking with a mic to an attentive audience), navy scrim weighted low under the line so the lit stage stays bright. White serif line "Prends enfin la parole avec confiance" sits low-center; gold carries the keyword **confiance**. Macro motion: `multi-phase-camera` slow forward travelling/push toward the speaker, echoing the narration's future-pacing — the room opens up as we move in. `asr-keyword-glow` lifts **confiance** as the line resolves — the one live element. Whitespace stays generous over the audience. Eye rides the forward push, crossfading toward the CTA poster.

## Scene 6: CTA — TÉLÉCHARGE

**Effects:** [`coordinate-target-zoom`, `press-release-spring`, `svg-icon-enrichment`, `sine-wave-loop`]
**Duration:** 4.12s
**Hierarchy:** action
**Blueprint:** based-on `cta-morph-press`

**PrimarySubjectTimeline:** 0–1.6s poster image primary (centered, scaling in); 1.6–4.12s the gold "TÉLÉCHARGER MAINTENANT" button is primary with the animated arrow, poster demotes to a held backdrop, brand mark "eMoneyMind Pro" a small supporting line.
**Handoff:** When the CTA button locks, the poster stops moving and recedes one step (it becomes the held backdrop, not a competing subject); the button owns the center safe zone. Camera push does not count as the handoff — the poster's motion stop and contrast drop do.

Motivation and urgency — a decisive, premium close; energetic but classy, resolving to stillness then black. Centered composition on the navy gradient ground (not a photo bleed): a faint gold-bokeh/starfield from layered radial-gradients is the ambient. `public/img/s6_poster.jpg` (full product poster — title, "Télécharge maintenant ton Ebook !", price 35.000 → 1.999 FCFA) scales in large and centered via `coordinate-target-zoom`. Below it, a pulsing GOLD "TÉLÉCHARGER MAINTENANT" button with an animated gold arrow pointing to it (`svg-icon-enrichment` drives the arrow's nudging motion), and the small "eMoneyMind Pro" brand mark as a text line — its bottom edge held above the lower safe area. The button enters and presses/settles via `press-release-spring`, then idles with a `sine-wave-loop` gold glow-pulse as the one live element (the on-screen copy "📘 Télécharge ton Ebook maintenant" / "Commence ta transformation aujourd'hui"). **stillness-before-climax** (~0.4s) after the poster lands and before the button pulses, so the call to action lands as a beat. The whole frame fades toward black at the very end. Eye locks on the pulsing button — final destination.
