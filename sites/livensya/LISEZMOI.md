# Livensya · tunnel « Défi 60 jours » · mode d'emploi

Site statique (HTML, CSS, un peu de JavaScript). Aucun serveur, aucune base de données. Poids mesuré au premier chargement sur téléphone : environ 150 Ko (moins de 500 Ko une fois toutes les images chargées ; limite fixée : 1,5 Mo).

## Ce qu'il y a dans le dossier

| Fichier | Rôle |
|---|---|
| `index.html` | La page du tunnel : héros, test de 2 minutes, résultat, histoire, méthode, contenu, jours 1/30/60, vidéo, offre, FAQ, final |
| `merci.html` | La page après paiement (non indexée par Google) |
| `css/style.css` | Tout le style (couleurs de la charte en haut du fichier) |
| `js/app.js` | Le test, le résultat, les boutons d'achat, la vidéo. **Les réglages sont en haut du fichier.** |
| `js/tracking.js` | Le Pixel Meta. **`PIXEL_ID` est en haut du fichier.** |
| `fonts/` | Les 2 polices, hébergées sur ton site (pas d'appel à Google) |
| `images/` | Photos d'Enock, logos, mockups et fonds, en WebP. `images/marque/` = les originaux fournis |
| `captures/` | Les captures téléphone (390 px) et ordinateur (1440 px) de chaque page |
| `DESIGN.md` | La direction artistique et la planche de références |

## Publier sur le sous-domaine LWS (livensya.emkbluediamond.online)

1. **Créer le sous-domaine** : espace client LWS → ton hébergement → « Sous-domaines » → ajoute `livensya` sur `emkbluediamond.online`. Note le dossier créé (souvent `/livensya/` ou `/sous-domaines/livensya/` à la racine de l'hébergement).
2. **Activer le HTTPS** : dans « SSL / Let's Encrypt », coche le sous-domaine `livensya.emkbluediamond.online`. Attends qu'il soit actif (quelques minutes à quelques heures).
3. **Envoyer les fichiers** : par le gestionnaire de fichiers LWS ou en FTP (FileZilla), copie **le contenu** du dossier `sites/livensya/` dans le dossier du sous-domaine : `index.html`, `merci.html`, `css/`, `js/`, `fonts/`, `images/`. Inutile d'envoyer `captures/`, `images/marque/`, `DESIGN.md`, `DONNEES.md` et ce fichier.
4. **Vérifier** : ouvre `https://livensya.emkbluediamond.online` sur ton téléphone, fais le test jusqu'au bout, appuie sur un bouton d'achat (tu dois arriver sur Chariow), ouvre `/merci.html`.
5. **Brancher la page merci dans Chariow** : dans le produit, réglage « redirection après achat » (ou « page de remerciement »), mets `https://livensya.emkbluediamond.online/merci.html`. Si Chariow ne le propose pas, la page reste utile : mets son lien dans l'e-mail de livraison.

Aperçu de la vidéo et du suivi : ajoute `?apercu=1` à l'adresse (la section vidéo s'affiche même vide, et les événements du Pixel s'écrivent dans la console du navigateur).

## Ce que tu peux changer toi-même (sans casser le reste)

Tout est en haut de `js/app.js` :

```js
const LIEN_PAIEMENT = 'https://ykhzgspm.mychariow.store';   // lien de paiement Chariow
const VIDEO_SRC = '';        // ex. 'videos/defi-60-jours.mp4'
const VIDEO_AFFICHE = '';    // ex. 'videos/affiche.webp'
```

- **Lien de paiement** : remplace par le lien direct du produit. Sur ta boutique, le paiement du produit est à l'adresse `https://ykhzgspm.mychariow.store/prd_4bisyd7x/checkout` : vérifie qu'il marche, puis colle-le. Les paramètres publicitaires (`utm_…`, `fbclid`) de l'adresse d'arrivée sont transmis automatiquement à Chariow.
- **Vidéo faceless** : dépose le fichier dans un dossier `videos/` (MP4 H.264, format vertical 9:16, idéalement moins de 8 Mo), puis remplis `VIDEO_SRC`. Tant que c'est vide, la section est invisible pour les visiteurs. Rien ne se charge avant le clic sur « Lire la vidéo ».
- **Textes** : directement dans `index.html` et `merci.html`. Garde le tutoiement, pas de tiret cadratin, et pas de promesse de kilos.
- **Prix** : il apparaît plusieurs fois dans `index.html` (héros, ticket de l'offre, final, barre collante) et dans la description : cherche `999`.
- **Témoignages** : un modèle commenté est prêt dans `index.html` (cherche `TÉMOIGNAGES`). À n'utiliser qu'avec de vrais retours et l'accord écrit de la personne.
- **Collecte des réponses du test** : la fonction `envoyerLead(donnees)` (en haut de `js/app.js`) est vide exprès. Aujourd'hui, aucune donnée ne quitte le téléphone (le test l'annonce aux visiteurs). Si tu la branches un jour, il faudra changer cette phrase et ta politique de confidentialité.

## Suivi Meta (Pixel), simple et sans doublon

1. Ouvre `js/tracking.js`, colle ton identifiant : `var PIXEL_ID = '123456789012345';`. Tant qu'il est vide, **rien** n'est chargé.
2. Événements envoyés (Pixel standard, rien d'autre) :

| Événement | Quand | Garde-fou |
|---|---|---|
| `PageView` | chaque page (accueil et merci) | |
| `ViewContent` | quand la section de l'offre s'affiche | une fois par page vue |
| `Lead` | fin du test | une seule fois par visiteur (drapeau `lv_lead_envoye` dans le téléphone) |
| `InitiateCheckout` | clic sur un bouton d'achat | un par clic, clics répétés en moins de 2 s ignorés |
| `Purchase` | **pas envoyé par le navigateur** | voir ci-dessous |

Chaque événement porte un `eventID` unique (ex. `Lead.8f3c…`), prêt pour la déduplication avec l'API Conversions (même nom d'événement + même `event_id` côté serveur).

3. **Jamais de jeton API Conversions dans ces fichiers** : un site statique est lisible par tout le monde.

### Proposition pour le Purchase (à mettre en place côté serveur)

Un seul envoi, côté serveur, déclenché par la vente réelle :

1. Dans Chariow, crée un **webhook (Pulse) « vente réussie »** vers un petit service à toi (fonction serverless, Make, n8n…). C'est lui, et lui seul, qui garde le jeton API Conversions.
2. À chaque vente, ce service envoie à Meta un événement `Purchase` avec `value: 3999`, `currency: 'XOF'`, l'e-mail et le téléphone de l'acheteur **hachés en SHA-256** (comme Meta l'exige), `action_source: 'website'`, et un `event_id` stable : l'identifiant de la vente Chariow (ex. `purchase.<id_vente>`), pour qu'un éventuel renvoi du webhook ne compte pas deux fois.
3. Relier au parcours : le navigateur garde l'`eventID` du dernier `InitiateCheckout` dans `localStorage` (`lv_initiate_checkout_id`). Si Chariow permet de faire passer un paramètre ou un champ personnalisé jusqu'au webhook, on pourra l'y transmettre pour réutiliser ce même identifiant. Sinon, l'identifiant de la vente suffit : il n'y a pas de Purchase navigateur, donc pas de doublon possible.
4. Pas de `Purchase` dans `merci.html` (expliqué en commentaire dans la page) : elle peut être rechargée ou ouverte sans achat.

## Ce qu'Enock doit fournir ou valider

1. **Le récit de l'histoire** (section « L'histoire derrière le défi ») : chaque phrase est à relire et corriger. Elle a été écrite à partir des seules infos connues (« à 24 ans, on me donnait 14 ans »). La citation « Je ne voulais pas devenir quelqu'un d'autre… » est une proposition : garde-la seulement si elle est vraie pour toi.
2. **L'exemple de journée** (méthode, levier 1 : 7 h bouillie et œufs, 10 h banane et arachides…) : remplace-le par une vraie journée de ton programme.
3. **Le prix barré 12 500 F** : affiche-le seulement si c'est vraiment le prix prévu après le lancement. Sinon, retire-le. Sur Chariow, la remise « renouvelée chaque jour » avec compte à rebours est une fausse urgence : je te conseille de la couper (et elle n'apparaît pas sur ce site).
4. **Le lien de paiement direct** (`/prd_4bisyd7x/checkout`) : à tester puis à coller dans `LIEN_PAIEMENT`.
5. **La garantie** : aucune n'existe aujourd'hui, le site n'en affiche donc aucune. Si tu en décides une (ex. remboursement sous 7 jours), il faut l'écrire mot pour mot et l'activer aussi sur Chariow ; des emplacements commentés sont prêts.
6. **Le visage** : tes yeux sont masqués sur les deux photos. Un vrai visage inspire beaucoup plus confiance ; c'est ton choix. Si tu les démasques, envoie les fichiers originaux.
7. **Les mockups des livres** montrent des corps générés (dont un torse musclé dans le miroir) et disent « votre ». Sur la page, ils sont légendés « visuel d'illustration ». Pour les pubs Meta : pas de mockup avec torse nu ni d'avant/après, et je te conseille à terme une couverture sans corps idéalisé.
8. **L'ID du Pixel Meta** (et plus tard le jeton API Conversions, à garder côté serveur uniquement).
9. **La vidéo faceless** (HyperFrames) quand elle sera prête.
10. **Un numéro WhatsApp** si tu veux un bouton « Une question ? » : je ne l'ai pas inventé, il n'y en a pas sur la page.
11. **Tes vrais premiers retours clients** (avec accord) pour remplir l'emplacement témoignages.
12. **Deux phrases de service** dans la carte de l'offre : « Écris-moi depuis la page contact » (c'est toi qui réponds) et « pas reçu, on règle ça avec toi ». Garde-les seulement si tu peux les tenir.
13. **Deux vraies captures de pages** de tes PDF (une journée du programme, une page du carnet) : c'est la meilleure preuve qui manque, l'emplacement est prêt (cherche `EXTRAIT` dans `index.html`).
14. **Une adresse e-mail de contact** à afficher près du bouton d'achat, avec un délai de réponse réaliste.
15. **Ton ✅** sur l'aperçu avant toute mise en ligne.
