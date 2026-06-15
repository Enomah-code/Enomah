# Pack Money Boost 2026 — Vidéo publicitaire de lancement

Vidéo publicitaire cinématique pour le lancement du produit **« Money Boost 2026 : L'accélérateur de revenus »**, disponible sur la boutique Chariow **Emk Blue Diamond** (`yevmtzhs.mychariow.shop`).

Format : **1080×1920 (9:16 vertical)**, 30 fps, ~63 s, **voix off masculine + musique** — optimisé pour WhatsApp Statut, TikTok, Reels et Facebook.

## Direction artistique

Inspirée du prototype fourni (film publicitaire sombre, premium, typographie animée mot à mot, transitions fluides, compteur animé) — fusionnée avec l'identité réelle du livre (**or & noir luxe**) et le logo officiel **EMK Blue Diamond**.

- Fond bleu nuit profond, halos bleus/dorés, poussière d'or, grain, vignette.
- Typographie : **Anton** (impact) + **Montserrat** (corps).
- Accent **or** (#F3C969) = l'argent / le premium ; **bleu électrique** = le digital.
- Assets réels : mockup du livre, **vrai logo EMK** (fond fondu en emblème lumineux), **captures de revenus clients** (preuve sociale).

## Son

- **Voix off française neuronale masculine** (Piper, `fr_FR-upmc-medium`, voix « pierre », hors-ligne) — voix **grave et posée** (~130 Hz) calquée sur la vidéo de référence (~129 Hz). Diction copiée de la référence : **phrases courtes et percutantes**, synthétisées une par une et réassemblées avec de **vraies pauses dramatiques** (~0,42 s) pour un débit lent et premium.
- **Musique** synthétisée (numpy/scipy) : pad évolutif, pluck/arp, sub, **accents synchronisés sur chaque transition de scène**, montées + impacts sur la révélation produit et le CTA.
- **Ducking** : la musique baisse automatiquement (~‑12 dB) sous la voix off pour rester intelligible et non envahissante.

## Storyboard & voix off

| Scène | À l'écran | Voix off |
|------|-----------|----------|
| Accroche | « Et si ton **téléphone**… …valait plus que ton **salaire ?** » | « Ton téléphone. Tu l'as en main toute la journée. » |
| Accroche 2 | suite | « Et s'il pouvait te rapporter… bien plus que ton salaire ? » |
| Compteur | **50 000 → 500 000 FCFA / mois** | « En Afrique, des milliers l'ont déjà compris. 50 000. 100 000. 500 000 F par mois. Avec un simple téléphone. » |
| Objections | ~~capital~~ ~~diplôme~~ ~~expérience~~ → **Juste la bonne méthode** | « Sans capital. Sans diplôme. Sans expérience. Juste la bonne méthode. » |
| Révélation | **PACK MONEY BOOST 2026** + livre | « Voici le Pack Money Boost. Ton accélérateur de revenus. » |
| Contenu | 15 services · 50 scripts · 100 idées · Plan 0→1 M | « 15 services digitaux, prêts à vendre. 50 scripts WhatsApp. 100 idées de produits. Et le plan complet. De zéro… à un million de francs. » |
| **Témoignages** | **captures de revenus réels** + ★★★★★ | « Et ça marche déjà. Voici les premiers revenus de ceux qui sont passés à l'action. » |
| **CTA** | ~~9 500~~ **4 450 FCFA · ‑53 %** · lien · logo EMK | « Aujourd'hui, c'est moins 53 %. 4 450 F. Au lieu de 9 500. L'offre est limitée. Télécharge ton pack maintenant. Le lien est juste en dessous. » |

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
# 0. Voix neuronale FR masculine (Piper, voix « pierre ») — une fois
curl -L -o /tmp/v.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-fr_FR-upmc-medium.tar.bz2
mkdir -p /tmp/upmc && tar xjf /tmp/v.tar.bz2 -C /tmp/upmc --strip-components=1
mkdir -p build/tts && cp /tmp/upmc/fr_FR-upmc-medium.onnx* build/tts/

# 1. Voix off + musique + timeline.js
python3 soundtrack.py
# 2. Rendu des images (4 workers parallèles ; la durée est lue depuis window.DURATION)
for s in 0 1 2 3; do node render.js 30 53 build/frames $s 4 & done; wait
# 3. Encodage MP4
bash build.sh
```

Dépendances : Node + Playwright (Chromium), Python (`pymupdf`, `numpy`, `scipy`, `piper-tts`, `imageio-ffmpeg`), accès réseau aux Google Fonts.

### Clonage *exact* du timbre de la vidéo de référence (XTTS-v2)

La voix par défaut (Piper « pierre ») reproduit le **registre** de la référence
(~130 Hz vs ~129 Hz) mais pas l'identité vocale exacte. Pour cloner le **timbre
précis** du speaker de la vidéo de référence, on utilise XTTS-v2 (zéro-shot).

> ⚠️ Les poids XTTS-v2 sont hébergés sur **HuggingFace**, bloqué par la politique
> réseau par défaut de cet environnement. Lancer ces commandes depuis une session
> dont l'environnement **autorise `huggingface.co`**.

```bash
pip install coqui-tts                      # moteur XTTS (PyPI, OK partout)
# `--ref` = la vidéo (ou l'audio) de référence ; l'audio est extrait/nettoyé auto.
COQUI_TOS_AGREED=1 python3 voice_clone.py --ref /chemin/vers/reference.mov
VO_USE_EXISTING=1  python3 soundtrack.py   # même script/cadence, voix clonée
for s in 0 1 2 3; do node render.js 30 0 build/frames $s 4 & done; wait
bash build.sh
```

`script_vo.py` contient le script et la cadence partagés par les deux backends
(Piper et XTTS), pour que seul le timbre change.

### Vidéo finale avec une voix clonée (ta voix ou la voix OKF) — tout-en-un

Les références vocales propres sont déjà committées dans `../okf-voice/assets/`
(`my_voice_ref.wav` = ta voix, `speaker_ref.wav` = voix OKF isolée). Un seul
script clone la voix off du promo dans la voix choisie, mixe, rend et encode :

```bash
# Ta propre voix (défaut)
bash build_promo_video.sh
# Voix OKF clonée
bash build_promo_video.sh ../okf-voice/assets/speaker_ref.wav
```

> ⚠️ Nécessite l'accès HuggingFace (poids XTTS-v2) : lancer depuis une session
> dont la politique réseau est **Full** (ou autorise `*.huggingface.co` + `*.hf.co`).

Pour comparer les deux voix avant de choisir, voir `../okf-voice/compare_voices.sh`.

### Variante format paysage 16:9 / carré 1:1

Le moteur est paramétré en 1080×1920. Adapter `html,body,#stage` dans `promo.html` et le `viewport` de `render.js`, puis repositionner les scènes.
