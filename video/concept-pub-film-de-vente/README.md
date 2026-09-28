# Concept Pub — Film de vente

Film de 1 min 48 (1920×1080, voix off française, musique, sous-titres) qui sert à vendre le site Concept Pub à un prestataire des métiers de l'image.

- `concept-pub-film-de-vente.mp4`, la vidéo finale
- `SCRIPT-DE-VENTE.md`, qui contient le script complet : voix off minutée, déroulé du rendez-vous commercial, objections et messages de prospection
- `index.html`, la composition HyperFrames générée (ne pas modifier à la main : éditer `src/template.html.tpl` puis lancer `python3 build.py`)
- `vo/`, avec le texte de la voix off (`lines.py`), la synthèse vocale (`gen.py`, voix `fr-FR-RemyMultilingualNeural`) et le minutage mot à mot (`words.py` → `timing.json`)
- `make_music.py`, la musique procédurale, atténuée automatiquement sous la voix
- `assets/img/`, les captures réelles du site (produites par `capture-site.js`)

## Modifier le texte et régénérer

```bash
# 1. éditer vo/lines.py, puis :
cd vo && python3 gen.py && python3 words.py && cd ..
ffmpeg -y -i vo/voice.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 assets/voice.wav
python3 make_music.py
# 2. ajuster les temps de scène (CUTS dans build.py) si les phrases changent de longueur
python3 build.py
npx hyperframes@latest check
npx hyperframes@latest render --quality high -o concept-pub-film-de-vente.mp4
```

Pour changer de voix, lancez `gen.py` avec `VOICE=fr-FR-HenriNeural` (voix masculine) ou `VOICE=fr-FR-VivienneMultilingualNeural` (voix féminine).
