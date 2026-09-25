# Stone Edits — portfolio motion design

Six e-commerce videos for fictional brands. Source of truth: the production brief (`stone-edits-briefs-motion-design.md`, supplied separately).

## Layout

```
_shared/            neutral kit shared by every project
  brand/            Stone Edits logo (SVG split into S / E / blade, PNG) + end-card template
  fonts/            Google Fonts, local woff2 (render never hits the network)
  sfx/              sound effects (Pixabay Content License, see CREDITS.md)
  vendor/           GSAP, bundled locally
  polish.js         grain, vignette, beat grid, seeded PRNG, safe-zone guides
  build.py          syncs the kit into a project (assets/ + compositions/se-endcard.html)
  render.sh         final render: 60 fps, 16 Mb/s H.264, AAC 320 kb/s 48 kHz, metadata stripped
  endcard-preview/  standalone preview of the end card
02-showcase-lumen/  project 02 — done (photo-based, see assets/img/CREDITS.md)
livrables/          rendered MP4 / posters (not versioned)
```

## Commands

```bash
python3 _shared/build.py 02-showcase-lumen                       # sync shared kit
(cd 02-showcase-lumen && npx hyperframes check)                   # lint + runtime + layout + contrast
_shared/render.sh 02-showcase-lumen StoneEdits_02_Showcase_Lumen_1x1          # signature version
_shared/render.sh 02-showcase-lumen StoneEdits_02_Showcase_Lumen_1x1 --clean  # client version, no end card
```

## Decisions (client feedback, 2026-09-25)

- **Product visuals must be photorealistic.** Code-drawn products (SVG/CSS) are rejected for the portfolio.
  The client's Gemini key is free-tier (image/video/music quota 0), so the client chose **royalty-free stock only**.
  Method: one high-resolution hero photo per product (Pexels), cut out with rembg/BiRefNet, graded to the
  project palette, background rebuilt; every shot is a camera move on that photo; screens are replaced by the
  fictional brand UI through a perspective (homography) transform. Photo prep scripts live next to each project.
- Stock photos must carry no real brand, logo or recognisable face.
- **Logo animation:** a "blade clash" opener (blades strike and split to reveal the video) plus
  the same effect in the closing card, while keeping the brief's 1.5 s end card.
- Defaults from brief §E apply: French text, signature on, cleaning (04), robot (05), bag + stock (06), euros.
- Music: no royalty-free music provider is available in this environment; sound effects are
  mixed in, music cues are listed per project in `audio-cues.md`.
