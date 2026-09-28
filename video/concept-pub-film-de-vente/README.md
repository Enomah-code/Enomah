# Concept Pub — Film de vente

Film de 2 min 17 (1920×1080, voix off française, musique, sous-titres) qui sert à vendre le site Concept Pub à un prestataire des métiers de l'image. Il contient une **démonstration en direct** filmée sur le vrai site : curseur, clics, défilement, prix recalculé et espace client.

- `concept-pub-film-de-vente.mp4`, la vidéo finale
- `SCRIPT-DE-VENTE.md`, qui contient le script complet : voix off minutée, déroulé du rendez-vous commercial, objections et messages de prospection
- `src/template.html.tpl` et `build.py`, qui produisent la composition HyperFrames `index.html`
- `vo/`, avec le texte de la voix off (`lines.py`), la synthèse vocale et le minutage mot à mot (`gen.py` → `timing.json` et `assets/voice.wav`)
- `make_music.py`, la musique procédurale, atténuée automatiquement sous la voix
- `demo-recorder/`, l'enregistreur de démonstration (`record.js`) et sa chorégraphie (`segments.js`) : chaque clic et chaque défilement est calé sur un mot de la voix
- `assets/live/`, les trois séquences filmées sur le site : vitrine, devis et rendez-vous, espace client

## Régénérer

```bash
# voix off (après modification de vo/lines.py)
cd vo && python3 gen.py && cd ..
python3 make_music.py

# démonstration en direct (Chrome headless, rendu image par image à 30 i/s)
cd demo-recorder && npm i puppeteer-core@23
node record.js "<chemin>/Concept Pub - Vitrine.html" <dossier des polices woff2> ../assets/live
cd ..

# composition et rendu
python3 build.py
npx hyperframes@latest check
npx hyperframes@latest render --quality high -o concept-pub-film-de-vente.mp4
```

Si le texte change de longueur, ajustez les temps de coupe (`CUTS` dans `build.py`), les temps de départ des vidéos dans `src/template.html.tpl` (`data-start` de `v1`, `v2`, `v3`) et la chorégraphie dans `segments.js`.

Pour changer de voix, lancez `gen.py` avec `VOICE=fr-FR-HenriNeural` (voix masculine) ou `VOICE=fr-FR-VivienneMultilingualNeural` (voix féminine).
