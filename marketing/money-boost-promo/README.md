# Pack Money Boost 2026 — Vidéo publicitaire de lancement

Vidéo publicitaire cinématique pour le lancement du produit **« Money Boost 2026 : L'accélérateur de revenus »**, disponible sur la boutique Chariow **Emk Blue Diamond** (`yevmtzhs.mychariow.shop`).

Format : **1080×1920 (9:16 vertical)**, 30 fps, ~52 s, **voix off + musique** — optimisé pour WhatsApp Statut, TikTok, Reels et Facebook.

## Direction artistique

Inspirée du prototype fourni (film publicitaire sombre, premium, typographie animée mot à mot, transitions fluides, compteur animé) — fusionnée avec l'identité réelle du livre (**or & noir luxe**) et le logo officiel **EMK Blue Diamond**.

- Fond bleu nuit profond, halos bleus/dorés, poussière d'or, grain, vignette.
- Typographie : **Anton** (impact) + **Montserrat** (corps).
- Accent **or** (#F3C969) = l'argent / le premium ; **bleu électrique** = le digital.
- Assets réels : mockup du livre, **vrai logo EMK** (fond fondu en emblème lumineux), **captures de revenus clients** (preuve sociale).

## Son

- **Voix off française neuronale** (Piper, `fr_FR-siwis-medium`, hors-ligne) — une réplique par scène, calée sur les visuels.
- **Musique** synthétisée (numpy/scipy) : pad évolutif, pluck/arp, sub, **accents synchronisés sur chaque transition de scène**, montées + impacts sur la révélation produit et le CTA.
- **Ducking** : la musique baisse automatiquement (~‑12 dB) sous la voix off pour rester intelligible et non envahissante.

## Storyboard & voix off

| Scène | À l'écran | Voix off |
|------|-----------|----------|
| Accroche | « Et si ton **téléphone**… …valait plus que ton **salaire ?** » | idem |
| Compteur | **50 000 → 500 000 FCFA / mois** | « En Afrique, des milliers de personnes gagnent de 50 000 à 500 000 F par mois, avec un simple téléphone. » |
| Objections | ~~capital~~ ~~diplôme~~ ~~expérience~~ → **Juste la bonne méthode** | « Sans capital. Sans diplôme. Sans expérience. Juste la bonne méthode. » |
| Révélation | **PACK MONEY BOOST 2026** + livre | « Voici le Pack Money Boost, l'accélérateur de revenus. » |
| Contenu | 15 services · 50 scripts · 100 idées · Plan 0→1 M | « 15 services… 50 scripts WhatsApp… 100 idées… le plan complet de 0 à 1 million. » |
| **Témoignages** | **captures de revenus réels** + ★★★★★ | « Et ça marche déjà. Voici les premiers revenus de ceux qui sont passés à l'action. » |
| **CTA** | ~~9 500~~ **4 450 FCFA · ‑53 %** · lien · logo EMK | « Aujourd'hui ‑50 % : 4 450 F au lieu de 9 500. Offre limitée. Télécharge ton pack maintenant. » |

Toutes les données proviennent de la fiche produit Chariow et du livre PDF.

## Pipeline

- `promo.html` — composition animée (moteur déterministe `window.seek(t)`).
- `timeline.js` — bornes de scènes + durée totale (généré par `soundtrack.py`, calé sur la voix off).
- `render.js` — capture image par image via Playwright/Chromium (shardé).
- `soundtrack.py` — voix off (Piper) + musique synchronisée + ducking → `build/soundtrack.wav` + `timeline.js`.
- `build.sh` — encodage final frames + son → MP4.
- `assets/` — mockup livre, logo EMK (transparent), captures de revenus, affiche.
- `money-boost-2026-promo.mp4` — **rendu final** · `money-boost-2026-poster.jpg` — vignette.

## Régénérer

```bash
# 0. Voix neuronale FR (Piper) — une fois
curl -L -o /tmp/v.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-fr_FR-siwis-medium.tar.bz2
tar xjf /tmp/v.tar.bz2 -C /tmp
mkdir -p build/tts && cp /tmp/vits-piper-fr_FR-siwis-medium/fr_FR-siwis-medium.onnx* build/tts/

# 1. Voix off + musique + timeline.js
python3 soundtrack.py
# 2. Rendu des images (4 workers parallèles ; la durée est lue depuis window.DURATION)
for s in 0 1 2 3; do node render.js 30 53 build/frames $s 4 & done; wait
# 3. Encodage MP4
bash build.sh
```

Dépendances : Node + Playwright (Chromium), Python (`pymupdf`, `numpy`, `scipy`, `piper-tts`, `imageio-ffmpeg`), accès réseau aux Google Fonts.

### Variante format paysage 16:9 / carré 1:1

Le moteur est paramétré en 1080×1920. Adapter `html,body,#stage` dans `promo.html` et le `viewport` de `render.js`, puis repositionner les scènes.
