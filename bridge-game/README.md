# 🌉 Architecte de Ponts

Jeu de stratégie où vous concevez, construisez et testez des ponts capables de résister à un
trafic toujours plus lourd — marchands, voitures, camions puis convois complets.

## Gameplay

1. **Construction** — reliez les deux falaises avec des segments de **route** (obligatoires pour
   le passage des véhicules) et renforcez la structure avec des poutres de **bois**, **acier** ou
   **câbles**, chacune avec son propre coût et sa propre résistance. Le budget est limité.
2. **Test** — un moteur physique réel ([Matter.js](https://brm.io/matter-js/)) simule le pont : les
   poutres se déforment et **cassent** si la contrainte dépasse la résistance du matériau.
3. **Trafic** — des véhicules traversent un par un ou en convoi. Le pont est validé si tous
   arrivent de l'autre côté sans que la structure ne s'effondre.
4. **Progression** — 8 niveaux avec des gouffres de plus en plus larges et des véhicules de plus
   en plus lourds (charrette → automobile → camion → poids lourd → transporteur géant), débloqués
   et notés (⭐ jusqu'à 3, selon l'efficacité budgétaire) au fil de la progression, sauvegardée en
   local.

## Développement

```bash
npm install
npm run dev       # serveur de développement (http://localhost:5173)
npm run typecheck # vérification TypeScript stricte
npm run build     # build de production dans dist/
npm run preview   # prévisualiser le build de production
```

## Stack technique

- **TypeScript** + **Vite** — build rapide, aucun framework UI (DOM natif pour les menus/HUD,
  Canvas 2D pour le rendu du jeu).
- **Matter.js** — moteur physique 2D pour la structure du pont (contraintes/ressorts cassables)
  et les véhicules (châssis + roues motorisées).
- Progression et scores sauvegardés via `localStorage`, aucun backend requis.

## Déploiement

Le jeu est déployé automatiquement sur **GitHub Pages** via
`.github/workflows/deploy-bridge-game.yml` à chaque push sur `main` touchant `bridge-game/`
(ou manuellement via "Run workflow"). Voir ce fichier pour le pipeline complet.
