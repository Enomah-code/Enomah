# Livensya · tunnel « Défi 60 jours » · mode d'emploi

Site statique (HTML, CSS, un peu de JavaScript). Aucun serveur, aucune base de données. Poids mesuré au premier chargement sur téléphone : environ 150 Ko (moins de 500 Ko une fois toutes les images chargées ; limite fixée : 1,5 Mo).

## Version 2 (retours d'Enock)
- **Narrateur** : la page ne parle plus d'Enock. Le narrateur est le personnage du livre. Son prénom est dans **une seule constante**, `PRENOM_NARRATEUR` en haut de `js/app.js` (valeur : `'David'`, le narrateur du livre), et la même ligne en bas de `merci.html`. Tous les éléments `data-prenom` se remplissent seuls. Si tu laisses `''`, le texte devient neutre (« L'auteur du défi ») et la phrase « Moi, c'est … » disparaît.
- **Histoire** : l'histoire de David (préface du livre), réécrite à la 1re personne, avec la mention « L'histoire de David est inspirée de situations réelles. »
- **Prix** : il n'apparaît que dans la carte de l'offre (3 999 F, barré 12 500 F), après « Ce que tu reçois ». Tous les autres boutons disent « Commencer le défi » ou « Faire le défi avec moi ».
- **Contact** : WhatsApp https://wa.me/22995726957 (+229 95 72 69 57) et contact@emkbluediamond.online, en pastilles avec icônes (logo WhatsApp, enveloppe), sans prénom ni signature, dans la carte de l'offre, la FAQ, la page merci et le pied de page.
- **Aucune garantie** de remboursement n'est mentionnée nulle part.
- **La confidence du test** (question sur la remarque la plus blessante) n'est jamais enregistrée ni envoyée : elle sert seulement à adapter le résultat sur le téléphone.

## Ce qu'il y a dans le dossier

| Fichier | Rôle |
|---|---|
| `index.html` | La page du tunnel : héros, test de 2 minutes, résultat, histoire, méthode, contenu, jours 1/30/60, vidéo, offre, FAQ, final |
| `merci.html` | La page après paiement (non indexée par Google) |
| `css/style.css` | Tout le style (couleurs de la charte en haut du fichier) |
| `js/app.js` | Le test, le résultat, les boutons d'achat, la vidéo. **Les réglages sont en haut du fichier.** |
| `js/tracking.js` | Le Pixel Meta. **`PIXEL_ID` est en haut du fichier.** |
| `fonts/` | Les 2 polices, hébergées sur ton site (pas d'appel à Google) |
| `images/` | Photos avant/après, logos, mockups et fonds, en WebP. `images/marque/` = les originaux fournis |
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

- **Prénom du narrateur** : `const PRENOM_NARRATEUR = 'David';` (et la même ligne dans `merci.html`).
- **Lien de paiement** : remplace par le lien direct du produit. Sur ta boutique, le paiement du produit est à l'adresse `https://ykhzgspm.mychariow.store/prd_4bisyd7x/checkout` : vérifie qu'il marche, puis colle-le. Les paramètres publicitaires (`utm_…`, `fbclid`) de l'adresse d'arrivée sont transmis automatiquement à Chariow.
- **Vidéo faceless** : dépose le fichier dans un dossier `videos/` (MP4 H.264, format vertical 9:16, idéalement moins de 8 Mo), puis remplis `VIDEO_SRC`. Tant que c'est vide, la section est invisible pour les visiteurs. Rien ne se charge avant le clic sur « Lire la vidéo ».
- **Textes** : directement dans `index.html` et `merci.html`. Garde le tutoiement, pas de tiret cadratin, et pas de promesse de kilos.
- **Prix** : une seule fois, dans la carte de l'offre de `index.html` : cherche `999`.
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
1. **L'histoire de David** telle qu'écrite sur la page (réécriture à la 1re personne de la préface du livre). Âge non cité dans l'histoire ; le héros garde « 24 ans, on m'en donnait 14 » comme demandé, alors que le livre dit 26 ans.
2. **La question du miroir** : le livre écrit « sa question n'a pas été : « Qu'est-ce que je fais mal depuis tout ce temps ? » ». J'ai compris « a été » (c'est elle qui mène à la méthode). Vérifie la phrase du livre, elle semble contenir une coquille.
3. **Les photos avant/après** sont présentées comme celles de David (« Moi, à 24 ans »), alors que David est un personnage « inspiré de situations réelles ». Une partie des visiteurs prendra ces photos pour celles d'un vrai client : à toi de décider si tu gardes cette présentation, ou si tu ajoutes une légende du type « photos réelles d'avant et d'après ».
4. **Les phrases de David dans le test** (« Moi aussi, j'ai entendu ces phrases », « le jour où une personne que j'appréciais m'a dit qu'elle me voyait comme un frère », « Moi aussi, j'ai eu des jours sans motivation », « Pour moi non plus, ça n'a pas marché ») : alignées sur le livre (préface et carnet du jour 52).
5. **Le prix barré 12 500 F** : à garder seulement si c'est vraiment le prix prévu après le lancement. Sur Chariow, couper le compte à rebours « renouvelé chaque jour » (fausse urgence).
6. **Le lien de paiement direct** (`/prd_4bisyd7x/checkout`) : à confirmer puis à coller dans `LIEN_PAIEMENT`.
7. **Deux vraies captures de pages** des PDF (emplacement `EXTRAIT` prêt).
8. **Les mockups des livres** (corps générés, « votre », « ENOCK M. ») : légendés « visuel d'illustration ». Pas de torse nu ni d'avant/après dans les pubs Meta.
9. **L'ID du Pixel Meta** (le jeton API Conversions reste côté serveur).
10. **La vidéo faceless**, puis de vrais témoignages avec accord.
11. **Ton ✅** sur l'aperçu avant toute mise en ligne.
