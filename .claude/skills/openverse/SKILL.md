---
name: openverse
description: "Trouver des médias libres de droits (images, photos, illustrations, audio, musiques et bruitages/SFX) via Openverse — le moteur de recherche de plus de 800 millions d'œuvres sous licences ouvertes (Creative Commons et domaine public). À utiliser dès qu'un montage vidéo, un motion design, une vidéo promo, une miniature, une page ou un visuel a besoin d'une image, d'un son d'ambiance, d'une musique ou d'un bruitage libre de droits, ou quand il faut vérifier la licence et l'attribution d'un média. Déclencheurs : image libre, photo gratuite, musique libre de droits, bruitage, SFX, son d'ambiance, banque de sons, banque d'images, Creative Commons, domaine public, média libre, Openverse."
---

# Openverse — médias libres de droits (images + audio)

Openverse est un moteur de recherche de médias sous **licences ouvertes** (Creative Commons + domaine public) :
images et audio (dont musiques, ambiances et bruitages). Gratuit, API publique, **sans clé** pour un usage normal.
C'est le « magasin » où aller chercher un visuel ou un son réutilisable pour un montage, une vidéo ou une page.

## Règle d'or : la licence et l'attribution
Chaque résultat porte une **licence** (ex. `by`, `by-sa`, `cc0`, `pdm`) et une **attribution** prête à coller.
Toujours :
1. **Vérifier la licence** avant d'utiliser (certaines imposent le crédit `by`, le partage à l'identique `sa`, ou interdisent le commercial `nc`).
2. **Garder l'attribution** fournie par l'API (champ `attribution`) et l'ajouter au générique/crédits de la vidéo ou de la page.
3. Préférer `cc0` / `pdm` (domaine public, aucune contrainte) quand on veut zéro obligation.
Détails : `references/api.md` (section licences).

## Chercher (API, sans clé)
Base : `https://api.openverse.org/v1/`
- **Images** : `GET /v1/images/?q=<mots-clés>&license_type=commercial&page_size=20`
- **Audio** (musiques, ambiances, bruitages) : `GET /v1/audio/?q=<mots-clés>&page_size=20`

Exemple (bruitage « whoosh » utilisable en commercial) :
```bash
curl -s "https://api.openverse.org/v1/audio/?q=whoosh&license_type=commercial&page_size=10" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['title'],'|',r['license'],'|',r['url']) for r in d['results']]"
```
Filtres utiles : `license=cc0,pdm` (domaine public), `license_type=commercial` ou `commercial,modification`,
`source=`, `extension=`, `category=` (pour l'audio : `music`, `sound_effect`, …). Voir `references/api.md`.
Pour plus de débit, un jeton gratuit s'obtient via `/v1/auth_tokens/register/` (optionnel).

## Dans la chaîne de montage vidéo (lien HyperFrames)
Openverse est la **source de médias** de la chaîne :
1. **HyperFrames / Remotion / GSAP** → fabriquent les visuels et l'animation.
2. **`openverse`** (ce skill) → va chercher images + sons/bruitages **libres de droits**.
3. **`real-sound`** → place et mixe ces vrais sons sur le montage (il sait déjà sourcer Freesound/Mixkit ; Openverse est une source de plus, souvent en CC0).
4. **`earshot`** → écoute/vérifie que le son tombe juste (synchro, niveaux) avant de livrer.

Donc : quand `real-sound` cherche un bruitage ou une ambiance, Openverse est une source à privilégier pour du
libre de droits ; et toute image d'un montage/vignette peut venir d'ici avec sa licence en règle.

## À retenir
- Vérifier la licence et conserver l'attribution — toujours.
- Audio **et** images dans la même recherche d'esprit (`/v1/audio/` et `/v1/images/`).
- Gratuit, local-friendly : ce ne sont que des requêtes HTTP, rien à installer.
