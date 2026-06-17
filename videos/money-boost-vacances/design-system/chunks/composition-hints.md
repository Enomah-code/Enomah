# Composition hints — Liquid Glass

**Runtime prerequisites — read first**

Liquid glass scenes will NOT render in a default Puppeteer/Chrome stable. Before
authoring or rendering a liquid-glass composition you must:

1. **Install one of the liquid-glass runtime blocks** to get
   `lib/liquid-glass.iife.js` and the three.js dependencies wired:

   ```bash
   npx hyperframes add liquid-glass-widgets
   # OR pick another:  liquid-glass-notification | liquid-glass-context-menu
   #                   liquid-glass-media-controls | ios26-liquid-glass
   #                   macos-tahoe-liquid-glass    | vfx-liquid-glass
   ```

   You only need one — they all ship the same `lib/liquid-glass.iife.js`.

2. **Use a WebGPU-capable browser for rendering**: Brave or Chrome Canary
   with WebGPU enabled. Set:

   ```bash
   export PRODUCER_HEADLESS_SHELL_PATH=/path/to/brave-or-canary
   ```

   The engine auto-passes `--enable-unsafe-webgpu`. See
   `/hyperframes-animation` → `adapters/typegpu.md` for the full setup.

3. **Verify before authoring**: `npx hyperframes doctor` should report
   `webgpu: ok`. If it says `unsupported`, fall back to a different preset
   — liquid-glass will silently render as blank panels otherwise.

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

**Aurora shader — copy verbatim from registry**

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

**Color discipline**

- Canvas is the **aurora**, not a flat fill. Never set `body { background: var(--canvas); }`
  in a liquid-glass scene — the canvas variable is overridden to the deep
  base purple that the aurora needs as a blackpoint.
- Brand accent appears as: aurora hot zone tint, pill dots, button gradients,
  album-art conic gradients. Never as a glass panel fill.

**Atmosphere**

- **Transitions between scenes**: hold the aurora across scenes (single
  composition-wide `uTime` driver). Panels slide off the bottom on scene N,
  rise from the bottom on scene N+1. The aurora doesn't blink.
