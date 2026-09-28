# Concept Pub — Film de présentation

Vidéo motion design de 48 s (1920×1080, 30 i/s, H.264 + AAC) pour le site Concept Pub, construite sur le design system « Concept Pub » (noir, ivoire, or antique · Cormorant Garamond, Manrope, IBM Plex Mono).

- `concept-pub-presentation.mp4` — la vidéo finale
- `poster.jpg` — image d'affiche (attribut `poster` du lecteur)
- `index.html` — composition HyperFrames (HTML + GSAP), source éditable
- `make_audio.py` — bande-son procédurale (numpy/scipy) → `assets/soundtrack.wav`

## Déroulé

| Temps | Scène |
|---|---|
| 0 – 4,5 s | Mots-flash (Affiches, Publicités, Podcasts, Motion, Tournage) puis révélation du sceau et du logo |
| 4,5 – 9 s | « L'image qui fait vendre. » |
| 9 – 15,5 s | Les 9 prestations en défilement rapide |
| 15,5 – 22,5 s | Réalisations : carrousel de 6 projets |
| 22,5 – 26,5 s | « Une marque ne se raconte pas, elle se regarde. » |
| 26,5 – 31,5 s | Chiffres clés (180+, 48 h, 9, 4K) |
| 31,5 – 37 s | Méthode en 4 étapes |
| 37 – 42,5 s | Devis instantané |
| 42,5 – 48 s | Signature, CTA et contact |

## Modifier et re-rendre

```bash
python3 make_audio.py                      # regénère la musique (optionnel)
npx hyperframes@latest check               # validation
npx hyperframes@latest render --quality high -o concept-pub-presentation.mp4
```

Requiert Node 22+, FFmpeg et Chrome headless (`npx hyperframes browser ensure`).

## Intégration sur le site

```html
<video src="concept-pub-presentation.mp4" poster="poster.jpg"
       autoplay muted loop playsinline preload="metadata"></video>
```
