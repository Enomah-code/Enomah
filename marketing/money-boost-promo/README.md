# Pack Money Boost 2026 — Vidéo publicitaire de lancement

Vidéo publicitaire cinématique pour le lancement du produit **« Money Boost 2026 : L'accélérateur de revenus »**, disponible sur la boutique Chariow **Emk Blue Diamond** (`yevmtzhs.mychariow.shop`).

Format : **1080×1920 (9:16 vertical)**, 30 fps, ~43 s — optimisé pour WhatsApp Statut, TikTok, Reels et Facebook (les canaux ciblés par le produit lui‑même).

## Direction artistique

Inspirée du prototype fourni (film publicitaire sombre, premium, typographie blanche animée mot à mot, transitions fluides, compteur animé) — fusionnée avec l'identité réelle du livre (**or & noir luxe**).

- Fond bleu nuit profond dégradé, halos bleus/dorés, poussière d'or flottante, grain et vignette.
- Typographie : **Anton** (impact) + **Montserrat** (corps).
- Accent **or** (#F3C969) = l'argent / le premium ; accent **bleu électrique** = le digital.
- Mockup 3D réel du livre extrait de la couverture officielle (`assets/book_hero.png`).

## Storyboard (texte à l'écran)

| Temps | Scène | Message |
|------|-------|---------|
| 0–3.6 s | Accroche 1 | « Et si ton **téléphone**… » |
| 3.6–7.2 s | Accroche 2 | « …valait plus que ton **salaire ?** » |
| 7.2–11.8 s | Compteur | « jusqu'à **50 000 → 500 000 FCFA / mois** » avec un simple téléphone |
| 11.8–16.2 s | Objections | ~~Pas de capital~~ ~~Pas de diplôme~~ ~~Pas d'expérience~~ → **Juste la bonne méthode.** |
| 16.2–21.6 s | Révélation produit | Badge *Édition Bestseller 2026* · **PACK MONEY BOOST 2026** · *L'accélérateur de revenus* + livre |
| 21.6–29.4 s | Contenu | 15 services · 50 scripts WhatsApp · 100 idées · Plan 0→1 M FCFA · Bonus communauté |
| 29.4–33.6 s | Outils + preuve | WhatsApp · Canva · ChatGPT (gratuits) + ★★★★★ + témoignage |
| 33.6–43 s | **CTA** | ~~9 500~~ **4 450 FCFA · -53% Offre limitée** · « Télécharge ton pack maintenant » · `yevmtzhs.mychariow.shop` · Emk Blue Diamond |

Toutes les données (prix 9 500 → 4 450 FCFA, -53 %, contenus, témoignages, canaux de paiement, URL) proviennent de la fiche produit Chariow et du livre PDF.

## Fichiers

- `promo.html` — composition animée (moteur déterministe `window.seek(t)`).
- `render.js` — capture image par image via Playwright/Chromium (shardé pour le parallélisme).
- `audio.py` — bande sonore cinématique synthétisée (numpy/scipy, sans samples).
- `build.sh` — encodage final frames + audio → MP4.
- `assets/book_hero.png` — mockup 3D du livre (extrait de la couverture officielle).
- `money-boost-2026-promo.mp4` — **rendu final**.
- `money-boost-2026-poster.jpg` — image d'accroche (vignette).

## Régénérer

```bash
# 1. Rendu des images (4 workers parallèles)
for s in 0 1 2 3; do node render.js 30 43 build/frames $s 4 & done; wait
# 2. Bande sonore
python3 audio.py
# 3. Encodage MP4
bash build.sh
```

Dépendances : Node + Playwright (Chromium), Python (`pymupdf`, `numpy`, `scipy`, `imageio-ffmpeg`), accès réseau aux Google Fonts.

### Variante format paysage 16:9

Le moteur est paramétré en 1080×1920. Pour une version 16:9 (YouTube/site), adapter les dimensions dans `promo.html` (`html,body,#stage`, `viewport` dans `render.js`) et repositionner les scènes.
