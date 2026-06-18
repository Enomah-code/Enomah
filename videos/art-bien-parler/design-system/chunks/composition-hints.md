# Composition hints — Liquid Glass (CSS-only / no-GPU mode)

> ## ⚠ MANDATORY CREATIVE-DIRECTION OVERRIDE — READ FIRST
>
> **This project renders on a target with NO GPU. WebGPU shaders are FORBIDDEN.**
> Do NOT install the liquid-glass IIFE runtime, do NOT add the Three.js aurora
> `<canvas>` layers, do NOT set `PRODUCER_HEADLESS_SHELL_PATH`. Any WebGPU pass
> renders as blank panels here.
>
> **Use the CSS-only fallback exclusively:**
> - Ground: navy cinematic gradient via `--liquid-bg-fallback`
>   (`linear-gradient(160deg, #0B1B2E, #0d1b2a, #08131f)`), plus optional
>   subtle starfield/bokeh built from layered `radial-gradient` dots and a
>   faint gold glow. NO animated shader.
> - Glass surfaces: plain `<div>` panels styled with
>   `background: rgba(255,255,255,0.06)`, `backdrop-filter: blur(14px)`,
>   `border: 1px solid var(--lg-rim-edge)`, inset highlight via the
>   `--lg-rim-*` tokens, and `box-shadow` for depth. Put text directly inside
>   (no separate IIFE text-overlay dance — that pattern only matters for the
>   shader path).
> - Use the shipped `components/aurora-bg-fallback.html` as the background base.
>   IGNORE `components/liquid-stage.html`'s two `<canvas>` elements and the
>   "Aurora shader — copy verbatim" section below — they require WebGPU.
>
> **Brand surface for this video (overrides the inferred palette):**
> deep NAVY ground (`#0B1B2E` / `#0d1b2a`), premium GOLD hero accent
> (`--gold` `#C9A24B`, `--gold-bright` `#D4AF37`) for titles, keywords, hairline
> rules, checkmarks and CTA, WHITE (`#FFFFFF`) for body/supporting text.
> Display type is **Playfair Display** (elegant high-contrast serif); body is
> **Inter**. Several scenes are full-bleed cinematic PHOTOS — lay a navy scrim
> (`linear-gradient` from `rgba(11,27,46,.85)` to transparent) under
> white/gold text for legibility. Mood: emotional, inspiring, classy, confident,
> lots of negative space.

**Runtime prerequisites (CSS-only path — the WebGPU steps below are DISABLED for this project):**

The original liquid-glass preset assumes a WebGPU runtime. For this no-GPU build
all three steps below are intentionally skipped — they are kept only for
reference. Author with the CSS fallback described in the override box above.

1. ~~Install a liquid-glass runtime block (`npx hyperframes add ...`)~~ — SKIP (no GPU).
2. ~~Set `PRODUCER_HEADLESS_SHELL_PATH` to a WebGPU browser~~ — SKIP (no GPU).
3. ~~`npx hyperframes doctor` → `webgpu: ok`~~ — N/A; expect `unsupported`, which
   is fine because we never invoke the shader.

**Stage structure**

- Every scene starts with the `liquid-stage` component (§F). The two canvases
  - text-overlay layer are non-negotiable; the IIFE looks for them by id.
- Glass panels go inside `#glass-canvas` as empty `<div class="glass-panel ... liquid-glass">`.
  The `liquid-glass` class is the IIFE hook — without it the panel won't be
  picked up. **Don't put text inside the glass div** — text lives in a sibling
  `.text-overlay` div absolutely positioned to overlap the panel.
- The text-overlay div itself MUST stay transparent (no background, no border,
  no box-shadow). The glass card visuals come from the IIFE pass underneath;
  the overlay only carries text + small icons + gradient pills. Adding a
  background to the overlay creates a visible rectangle that breaks the
  illusion the moment IIFE renders. (The `.stat-text` / `.showcase-text`
  inset highlights in §F are an intentional exception — they fake the **inner
  rim** of the glass card itself, not the body.)

**Aurora shader — DISABLED for this project (no GPU)**

> The WebGPU/Three.js aurora below is NOT used in this build. Replace it with the
> CSS navy gradient + starfield from `aurora-bg-fallback.html`. The verbatim-copy
> instructions are retained for reference only.

The Three.js aurora shader is byte-identical across all 8 registry liquid-glass
blocks. **Do not let an LLM rewrite it.** When authoring a scene:

1. Copy the entire `<script>` block (vs string + fs string + Three.js
   renderer/scene/camera/uniforms/quad setup + the `requestGlassRender` /
   `lg.waitForInit()` block) from:
   `registry/blocks/liquid-glass-widgets/liquid-glass-widgets.html` lines 485-601.
2. Keep `uTime` driven by your GSAP timeline (`tl.eventCallback("onUpdate",
() => requestGlassRender(tl.time()))`) — already wired in the source.
3. The `vec3 base = mix(vec3(0.10, 0.02, 0.22), vec3(0.04, 0.10, 0.25), …)`
   line is the only place to retint the aurora toward a brand color — replace
   those two vec3 stops with desaturated versions of `--brand-primary` /
   `--brand-secondary` if you want brand-tinted aurora. Don't touch the snoise
   functions or the ridge math.

**Density & focus**

- **2-4 glass surfaces per scene maximum.** More than that and the refraction
  passes start to mush each other.
- **Surfaces don't overlap.** A small chip _next to_ a card is fine; a chip
  _on_ a card produces a refraction double-bounce that reads as broken.
- **Brand color lives in the aurora and the accent strokes**, not the glass
  tint. Glass stays neutral (white at low opacity). To bring brand color
  forward, push the aurora warm/cool stops toward `--brand-primary` /
  `--brand-secondary` in the shader — don't paint the glass.

**Typography on glass**

- **Body weight ≥ 550.** Thinner reads as smudge through the refraction.
- **Always include `text-shadow: var(--text-shadow-glass)`** on labels —
  the glass refracts and softens edges, the shadow restores legibility.
- **Min text size 14px**, ideally 16-22px. Anything smaller disappears.
- For light-tinted glass (menu archetype): use `--ink-on-light-glass`
  (near-black with a subtle white text-shadow). The IIFE shader inverts
  the perceived contrast on menu panels.

**Color discipline (CSS-only navy/gold)**

- Canvas is the **navy cinematic gradient** (`--liquid-bg-fallback`), optionally
  with a subtle gold-bokeh / starfield built from layered radial-gradients.
  Deep navy `#0B1B2E` is the blackpoint — never a white fill.
- GOLD (`--gold` / `--gold-bright`) is the hero accent: serif titles, emphasised
  keywords, hairline rules, checkmarks, pill borders, and the CTA gradient
  (`--brand-gradient`). WHITE is body/supporting text.
- Keep glass panels neutral (white at low opacity) with a faint gold rim on
  hero/CTA surfaces only. Don't flood panels with gold — gold is the accent,
  navy is the ground, white carries the reading.
- Over full-bleed photos: drop a navy scrim gradient before any text so white
  and gold stay legible.

**Atmosphere**

- **Transitions between scenes**: hold the aurora across scenes (single
  composition-wide `uTime` driver). Panels slide off the bottom on scene N,
  rise from the bottom on scene N+1. The aurora doesn't blink.
