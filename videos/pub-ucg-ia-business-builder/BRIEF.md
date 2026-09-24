---
workflow: general-video
flow: companion
storyboard: no
message: "La formation IA Business Building est complète, prouvée par les avis (100 % positifs) et à 4 999 F jusqu'à dimanche 23h59."
destination: tiktok-reels-ads
aspect: "9:16"
language: fr
audience: "Francophones (Afrique de l'Ouest) intéressés par l'IA pour gagner de l'argent"
length: "2 min 41 (piloté par le script tourné)"
---

# Pub UGC — IA Business Building (EMK Blue Diamond)

## Intent
Vidéo UGC storytelling, format 9:16, qui accroche du début à la fin : rushs face caméra resserrés
(jump cuts + punch-in), sous-titres dynamiques mot à mot, bruitages, et animations plein écran
sur les passages qui présentent la formation (le visage n'y apparaît pas).

## Assets
- 13 rushs iPhone (HEVC HLG) → `assets/aroll/cXX.mp4` via `scripts/prep_aroll.py` (SDR, silences resserrés, voix -14 LUFS).
- Captures fournies : WhatsApp de M. Élie (numéro, nom et photo floutés), avis Chariow (100 %, 12 avis), avis d'Élie, certificat.
- Bruitages : bibliothèque SFX HyperFrames (voir `assets/sfx/CREDITS.md`).

## Customizations
- Prénom affiché : **M. Élie** (confirmé par le client).
- Prix : 4 999 F (offre de lancement) → 35 000 F après dimanche 23h59.

## Notes
- S6-S8 viennent d'un seul rush (IMG_9877, découpé par plages dans `prep_aroll.py`), S13 = IMG_9887 (récupérés via Drive).
- Avis réels ajoutés : MD (« même pour débutants ») et Rick (agent IA WhatsApp). Logo EMK Blue Diamond en outro.
- Pas de musique de fond pour l'instant (aucun fournisseur hors-ligne) : à fournir ou générer.
