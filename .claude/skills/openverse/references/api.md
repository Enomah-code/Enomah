# Openverse API — référence rapide

Base : `https://api.openverse.org/v1/` — pas de clé requise pour un usage normal (quota plus élevé avec un jeton gratuit).
Docs officielles : https://api.openverse.org/v1/

## Endpoints
- `GET /v1/images/` — recherche d'images.
- `GET /v1/audio/` — recherche audio (musiques, ambiances, bruitages/SFX).
- `GET /v1/images/{id}/` et `GET /v1/audio/{id}/` — détail d'un média.
- `GET /v1/images/{id}/related/` — médias similaires.
- `POST /v1/auth_tokens/register/` puis `POST /v1/auth_tokens/token/` — obtenir un jeton (optionnel, pour plus de débit).

## Paramètres de recherche utiles
- `q` — mots-clés.
- `page`, `page_size` (max 20 sans jeton).
- `license` — codes exacts, séparés par des virgules : `cc0`, `pdm`, `by`, `by-sa`, `by-nc`, `by-nd`, `by-nc-sa`, `by-nc-nd`.
- `license_type` — raccourci : `commercial`, `modification`, ou `commercial,modification`.
- `source` — ex. `flickr`, `wikimedia`, `freesound`, `jamendo`…
- `extension` — `jpg`, `png`, `svg`, `mp3`, `ogg`, `wav`…
- `category` — images : `photograph`, `illustration`, `digitized_artwork`… ; audio : `music`, `sound_effect`, `podcast`, `audiobook`…
- `creator`, `tags`, `title` — filtres ciblés.

## Champs de résultat importants
- `url` — lien direct du média (à télécharger).
- `foreign_landing_url` — page d'origine.
- `license`, `license_version`, `license_url` — la licence.
- `attribution` — **texte d'attribution prêt à coller** (à mettre dans les crédits).
- `creator`, `creator_url`, `source`, `title`.
- `thumbnail` — vignette.
- audio en plus : `duration`, `bit_rate`, `sample_rate`, `genres`, `audio_set`.

## Licences — ce qu'elles imposent
- `cc0`, `pdm` : **domaine public**, aucune obligation (idéal, zéro contrainte).
- `by` : crédit obligatoire.
- `by-sa` : crédit + partage à l'identique (ShareAlike).
- `by-nc*` : **pas d'usage commercial** → éviter pour une vidéo/pub commerciale.
- `by-nd*` : pas de modification (ne pas découper/retravailler) → mauvais pour du montage.
→ Pour une pub ou un produit vendu : filtrer `license_type=commercial,modification`, et privilégier `cc0`/`pdm`.

## Exemple complet (images commerciales modifiables)
```bash
curl -s "https://api.openverse.org/v1/images/?q=abstract%20gradient&license_type=commercial,modification&page_size=10" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['title'],'|',r['license'],'|',r['url'],'|',r['attribution'][:80]) for r in d['results']]"
```

## Télécharger proprement (pour un montage)
1. Récupérer `url` (fichier) + `attribution`.
2. Télécharger le fichier dans le dossier d'assets du projet.
3. Noter l'attribution dans un fichier `CREDITS` / le générique si la licence est `by*`/`*sa`.
