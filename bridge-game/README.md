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

## Déploiement web

Le jeu est déployé automatiquement sur **GitHub Pages** via
`.github/workflows/deploy-bridge-game.yml` à chaque push sur `main` touchant `bridge-game/`
(ou manuellement via "Run workflow"). Voir ce fichier pour le pipeline complet.

## Application mobile native (Android / iOS)

Le jeu est aussi emballé en application native avec [Capacitor](https://capacitorjs.com/) : le
même code web tourne dans une coque native, verrouillée en **paysage** (le pont se joue mieux en
largeur). Config : `capacitor.config.ts`. Projets natifs générés : `android/` et `ios/`.

### Android — testable dès maintenant

```bash
npm run android:build-debug   # build web (base "/") + sync Capacitor + gradlew assembleDebug
```

Produit un APK debug installable directement (sideload) :
`android/app/build/outputs/apk/debug/app-debug.apk`. Transférez-le sur un téléphone Android et
ouvrez-le (autoriser "sources inconnues" si demandé) — aucun compte développeur requis pour ce
test.

Pour ouvrir le projet dans Android Studio à la place : `npx cap open android`.

### iOS — nécessite un Mac

La compilation iOS nécessite **Xcode**, qui ne tourne que sur macOS. Le projet `ios/App` est prêt
(icônes, splash screen, orientation paysage déjà configurés) ; sur un Mac avec Xcode installé :

```bash
npm run build:capacitor && npx cap sync ios
npx cap open ios   # ouvre Xcode ; Run sur un simulateur ou un appareil connecté
```

### Régénérer les icônes / splash screens

Sources vectorielles dans `resources/` (`icon-foreground.svg`, `icon-background.svg`,
`icon.svg`, `splash.svg`). `@capacitor/assets` prend des PNG en entrée : après avoir modifié un
`.svg`, reconvertissez-le en PNG à la bonne taille (1024×1024 pour les icônes, 2732×2732 pour le
splash — n'importe quel outil SVG→PNG convient : Inkscape, `rsvg-convert`, ou une capture d'écran
du SVG dans un navigateur) en écrasant le fichier `.png` correspondant dans `resources/`, puis
relancez la génération d'assets :

```bash
npx capacitor-assets generate --ios --android
```

### Publication sur les stores (à faire par vous)

Cette partie exige vos propres comptes et votre propre signature — impossible à faire à votre
place :

**Google Play**
1. Compte [Play Console](https://play.google.com/console) (frais unique ~25 $).
2. Générer un **App Bundle signé** : `cd android && ./gradlew bundleRelease`, avec un keystore de
   release que vous créez et conservez précieusement (`keytool -genkeypair ...` — sa perte empêche
   toute mise à jour future de l'app).
3. Créer la fiche Play Console (captures d'écran, description, classification de contenu) et
   soumettre le `.aab` à la revue.

**Apple App Store**
1. Compte [Apple Developer Program](https://developer.apple.com/programs/) (99 $/an).
2. Dans Xcode (`npx cap open ios`) : configurer l'équipe de signature, archiver
   (*Product → Archive*), puis distribuer via App Store Connect.
3. Créer la fiche App Store Connect (captures d'écran, description, classification) et soumettre à
   la revue.
