# Type-roles atlas — Liquid Glass

Phase 4b scene worker reads this when text outside §6 components is needed (hero displays, ledes, pill rows, CTA buttons, …). Workflow: pick role by id → paste the CSS rule into scene `<style>` with `s<N>-` prefix on the class names → wrap content using the prefixed class. Family tokens (`var(--font-*)`) resolve to brand DNA at scene-render time.

## type-role: display-cover

- family: display · px: 96–180 · weight: 800
- leading: 0.95 · tracking: -0.01em · case: sentence
- purpose: cover hero on aurora — type sits on glass card or floats directly on the aurora

```css
.t-trole-display-cover {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: clamp(96px, 12vw, 180px);
  line-height: 0.95;
  letter-spacing: -0.01em;
  color: rgba(255, 255, 255, 0.98);
  text-shadow: 0 4px 32px rgba(0, 0, 0, 0.5);
}
```

Sample:

```html
<div class="t-trole-display-cover">{BRAND_NAME}</div>
```

## type-role: headline

- family: display · px: 56–96 · weight: 700
- leading: 1 · tracking: -0.01em · case: sentence
- purpose: primary slide headline on glass panel

```css
.t-trole-headline {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: clamp(56px, 6vw, 96px);
  line-height: 1;
  letter-spacing: -0.01em;
  color: rgba(255, 255, 255, 0.98);
  text-shadow: var(--text-shadow-glass);
}
```

Sample:

```html
<div class="t-trole-headline">Design together</div>
```

## type-role: statement

- family: display · px: 40–64 · weight: 650
- leading: 1.1 · tracking: 0 · case: sentence
- purpose: long-form quoted statement on glass — wraps across panels

```css
.t-trole-statement {
  display: inline-block;
  font-family: var(--font-display);
  font-weight: 650;
  font-size: clamp(40px, 4vw, 64px);
  line-height: 1.1;
  letter-spacing: 0;
  color: rgba(255, 255, 255, 0.96);
  text-shadow: var(--text-shadow-glass);
  max-width: 26ch;
}
```

Sample:

```html
<div class="t-trole-statement">Light passes through. Surfaces stay weightless.</div>
```

## type-role: stat-value

- family: display · px: 64–120 · weight: 800
- leading: 1 · tracking: -0.02em · case: sentence
- purpose: hero numeral inside widget glass card — numbers-as-nouns voice

```css
.t-trole-stat-value {
  display: inline-block;
  font-family: var(--font-display);
  font-weight: 800;
  font-size: clamp(64px, 8vw, 120px);
  line-height: 1;
  letter-spacing: -0.02em;
  color: rgba(255, 255, 255, 0.98);
  text-shadow: var(--text-shadow-glass);
}
```

Sample:

```html
<div class="t-trole-stat-value">48ms</div>
```

## type-role: h3

- family: display · px: 28–44 · weight: 650
- leading: 1.15 · tracking: 0 · case: sentence
- purpose: sub-headline / panel title

```css
.t-trole-h3 {
  font-family: var(--font-display);
  font-weight: 650;
  font-size: clamp(28px, 2.8vw, 44px);
  line-height: 1.15;
  color: rgba(255, 255, 255, 0.96);
  text-shadow: var(--text-shadow-glass);
}
```

Sample:

```html
<div class="t-trole-h3">Panel title</div>
```

## type-role: lead

- family: body · px: 26–36 · weight: 600
- leading: 1.45 · tracking: 0 · case: sentence
- purpose: lead paragraph on glass — heavier than usual to survive refraction

```css
.t-trole-lead {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: clamp(26px, 2.4vw, 36px);
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.94);
  text-shadow: var(--text-shadow-glass);
  max-width: 44ch;
  margin: 0;
}
```

Sample:

```html
<p class="t-trole-lead">The lead carries one idea per panel. Heavier weight than usual — refraction softens edges.</p>
```

## type-role: label-eyebrow

- family: body · px: 24–28 · weight: 650
- leading: 1.2 · tracking: 0.18em · case: upper
- purpose: uppercase tracked label above a headline (panel eyebrow / section label)

```css
.t-trole-label-eyebrow {
  display: inline-block;
  font-family: var(--font-body);
  font-weight: 650;
  font-size: clamp(24px, 1.6vw, 28px);
  line-height: 1.2;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.78);
  text-shadow: var(--text-shadow-glass);
}
```

Sample:

```html
<div class="t-trole-label-eyebrow">Featured panel</div>
```

## type-role: label-mono

- family: mono · px: 24–28 · weight: 550
- leading: 1.3 · tracking: 0.06em · case: upper
- purpose: metadata chrome / slide counter — JetBrains Mono, soft white, wide-tracked caps

```css
.t-trole-label-mono {
  display: inline-block;
  font-family: var(--font-mono);
  font-weight: 550;
  font-size: clamp(24px, 1.6vw, 28px);
  line-height: 1.3;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.74);
}
```

Sample:

```html
<div class="t-trole-label-mono">01 / Surfaces</div>
```

## type-role: pill

- family: body · px: 24–28 · weight: 600
- leading: 1 · tracking: 0.04em · case: upper
- purpose: gradient pill chip on glass — brand-primary→secondary fill, white text

```css
.t-trole-pill {
  display: inline-block;
  padding: 10px 22px;
  border-radius: 999px;
  background: linear-gradient(120deg, var(--brand-primary), var(--brand-secondary));
  color: rgba(255, 255, 255, 0.98);
  font-family: var(--font-body);
  font-weight: 600;
  font-size: clamp(24px, 1.6vw, 28px);
  line-height: 1;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.32),
    0 8px 22px rgba(0, 0, 0, 0.3);
}
```

Sample:

```html
<div><span class="t-trole-pill">Live now</span></div>
```

## type-role: unit-suffix

- family: mono · px: 28–44 · weight: 550
- leading: 1 · tracking: 0 · case: sentence
- purpose: unit appended to a stat-value (ms / GB / %) — sits at ~30-40% of the numeral

```css
.t-trole-unit-suffix {
  font-family: var(--font-mono);
  font-weight: 550;
  font-size: clamp(28px, 3vw, 44px);
  line-height: 1;
  color: rgba(255, 255, 255, 0.72);
  margin-left: 0.18em;
}
```

Sample:

```html
<div><span class="t-trole-stat-value">48</span><span class="t-trole-unit-suffix">ms</span></div>
```
