# Livensya · tunnel « Défi 60 jours » · mode d'emploi

Site statique (HTML, CSS, un peu de JavaScript). Aucun serveur, aucune base de données. Poids mesuré au premier chargement sur téléphone : environ 150 Ko (moins de 500 Ko une fois toutes les images chargées ; limite fixée : 1,5 Mo).

## Version 6 : le robot achat (Purchase côté serveur)
- **Nouveau dossier `robot-achat/`** : un Google Apps Script qui envoie l'événement **Purchase** à Meta (API Conversions) une seule fois par vente, depuis le webhook « Vente réussie » de Chariow. Installation pas à pas, comme pour un débutant : **`robot-achat/LISEZMOI.md`**. Détails techniques : `TRACKING.md`, section 4.
- **`js/app.js`** : nouvelle constante en haut, `const ROBOT_ACHAT = '';`. Quand tu y colles l'adresse `/exec` du robot, la page lui envoie à la fin du paiement un petit signal (identifiant d'achat et cookies Meta), une seule fois, sans retarder la redirection vers `merci.html`. Tant que c'est vide, rien n'est envoyé.
- **`confidentialite.html`** : la section 3 décrit maintenant l'achat transmis à Meta par notre serveur.
- Les secrets (jeton Meta, clé Chariow) restent dans les « Propriétés du script » d'Apps Script, jamais dans le site.

## Version 5 : contact discret, pages légales, Pixel actif, retour sur merci.html
- **Domaine** : https://livensya.emkbluediamond.online/ (adresse canonique et Open Graph de `index.html`, adresse de chaque page légale).
- **Contact sans coordonnées affichées** : partout (carte de l'offre, FAQ, page merci, pied de page, pages légales), seulement deux petits boutons « WhatsApp » et « E-mail ». Le numéro et l'adresse ne s'affichent plus en texte.
  - WhatsApp (22995726957) avec un message déjà écrit : « Bonjour, je vous écris au sujet du programme Défi 60 Jours (Livensya). J'ai une question : ».
  - E-mail : **livensya@emkbluediamond.online** (remplace l'ancienne adresse « contact@ »), objet prérempli « Question sur le Défi 60 Jours (Livensya) ».
  - Les liens sont écrits en dur dans le HTML, déjà encodés. Pour changer le message, encode le nouveau texte (par ex. avec `encodeURIComponent` dans la console du navigateur) et remplace-le dans **toutes** les pages (cherche `wa.me` et `mailto`).
- **Pied de page** (toutes les pages) : « © 2026 Livensya by EMK Blue Diamond · Cotonou, Bénin », liens vers les pages légales du site et les deux boutons de contact.
- **Pages légales** : `mentions-legales.html`, `cgv.html`, `confidentialite.html`, au style du site, non indexées (`noindex, follow`), « Dernière mise à jour : octobre 2026 ». Elles chargent `js/tracking.js` (PageView seulement). Pas de garantie « satisfait ou remboursé » : produit numérique livré tout de suite, pas de remboursement après l'envoi de l'accès, accès renvoyé en cas de problème technique. Si tu changes le prix, change-le aussi dans `cgv.html` (cherche `3 999`).
- **Logos des moyens de paiement** (`images/paiement/`) sous le prix : MTN MoMo, Moov Money, Orange Money, Wave, Visa, Mastercard, en couleurs d'origine.
- **Bouton du widget plus calme** : `data-cta-animation="none"` (valeur lue dans le code du widget Chariow : avec `none`, aucune animation n'est lancée ; sans l'attribut, le widget peut appliquer son animation par défaut).
- **Pixel Meta actif** : `PIXEL_ID = '5010730402487338'` dans `js/tracking.js`. Logique inchangée (voir plus bas).
- **Après l'achat dans le widget** : voir « Après l'achat » ci-dessous.

## Après l'achat : retour sur merci.html
1. À la fin d'un paiement dans la fenêtre du widget, Chariow envoie à la page un message `chariow-purchase-completed` qui contient le `purchaseId`.
2. `js/app.js` l'écoute (origine vérifiée : `https://…mychariow.store` ou `https://…chariow.com`, forme du message vérifiée), garde l'identifiant dans le téléphone (`localStorage`, clé `lv_purchase_id`), envoie une fois le signal au robot achat si `ROBOT_ACHAT` est rempli (version 6), et envoie l'acheteur vers **`PAGE_APRES_ACHAT`** (en haut de `js/app.js`, valeur : `'merci.html'`), avec `?achat=<purchaseId>`.
3. Le widget, qui sinon redirigeait vers sa page d'achat Chariow (`…/purchase/<id>`), ne reçoit plus ce message (écoute prioritaire). **Aucun événement Meta n'est envoyé par la page à ce moment** : le Purchase part du robot achat (serveur).
4. **Côté Chariow** : pour un produit « téléchargeable », Chariow ne propose pas de redirection après achat ; l'acheteur reçoit l'accès à son espace client Chariow. Quand le paiement se termine hors du widget (lien de repli `LIEN_PAIEMENT`), il reste donc sur Chariow : le robot envoie quand même le Purchase (sans les cookies Meta, après 10 minutes).
5. À tester avec un vrai paiement : on n'a pas pu payer depuis notre environnement de test. Le comportement a été vérifié avec un message simulé.

## Version 4 : fidèle au livre et paiement sans quitter la page
- **Âge et phrases du livre** : David a 26 ans (« J'ai 26 ans, mais on me prend encore pour un lycéen »). Plus aucune mention « 24 ans / 14 ans ». Titre de l'histoire : « On dirait que tu n'as pas changé depuis le lycée. » La 3e phrase barrée du héros devient « Tu es toujours aussi maigre… ». Photos légendées « Avant » / « Aujourd'hui », fichiers renommés `photo-avant-*` et `photo-aujourdhui-*`.
- **Widget de paiement Chariow (style « tap »)** dans la carte de l'offre, à la place du bouton :
  - c'est un bouton « Commencer le défi » aux couleurs du site qui ouvre le paiement Chariow dans une fenêtre, par-dessus la page ;
  - le script (`widget.min.js` + `widget.min.css`, environ 110 Ko) n'est chargé qu'une fois, quand on approche de « Ce que tu reçois », ou au premier clic d'achat ; rien au chargement de la page ;
  - tous les autres boutons d'achat (héros, histoire, résultat, final, barre collante) font défiler doucement jusqu'à l'offre puis ouvrent le paiement tout seuls ;
  - si le widget n'a pas pu se charger après 6 s (réseau, bloqueur), on ouvre la page de paiement Chariow (`LIEN_PAIEMENT`, https://ykhzgspm.mychariow.store/prd_4bisyd7x/checkout, vérifiée) ;
  - sans JavaScript, un bouton classique vers cette même page reste visible.
- **Pourquoi « tap » et pas « frame »** : « frame » affiche directement tout le formulaire de paiement dans la page (un grand cadre, chargé d'office, sans bouton) : plus lourd en 3G et moins rassurant avant d'avoir lu l'offre. « tap » montre un bouton et n'ouvre le paiement qu'au clic, dans une fenêtre (presque plein écran sur téléphone, fermable par une croix).
- **Réglages du widget** (attributs de `#chariow-widget` dans `index.html`) : `data-style="tap"`, `data-primary-color="#16402A"` (vert forêt, plus de vert citron), `data-background-color="#FFFCF6"`, `data-locale="fr"`, `data-custom-cta-text="Commencer le défi"`, `data-cta-width="md"` (56 px, plus facile à toucher que `xs`), animation `none` depuis la version 5 (avant : « shine »). Le CSS du site retouche seulement le bouton (pilule, police, couleur), rien d'autre.
- **Suivi** : `InitiateCheckout` part au clic sur le bouton du widget (une fois par clic, clics répétés en moins de 2 s ignorés, `eventID` unique). Toujours **pas de Purchase dans le navigateur**.
- **Après l'achat** : depuis la version 5, l'acheteur est renvoyé vers `merci.html?achat=<id>` (voir « Après l'achat » plus haut). Avant, le widget redirigeait vers la page d'achat Chariow.
- **Pour la future API Conversions** : à la fin du paiement, le widget reçoit un message `chariow-purchase-completed` qui contient le `purchaseId`. C'est cet identifiant qui servira d'`event_id` au Purchase envoyé côté serveur (webhook de vente Chariow), pour qu'il ne compte jamais deux fois.

## Version 2 (retours d'Enock)
- **Narrateur** : la page ne parle plus d'Enock. Le narrateur est le personnage du livre. Son prénom est dans **une seule constante**, `PRENOM_NARRATEUR` en haut de `js/app.js` (valeur : `'David'`, le narrateur du livre), et la même ligne en bas de `merci.html`. Tous les éléments `data-prenom` se remplissent seuls. Si tu laisses `''`, le texte devient neutre (« L'auteur du défi ») et la phrase « Moi, c'est … » disparaît.
- **Histoire** : l'histoire de David (préface du livre), réécrite à la 1re personne, avec la mention « L'histoire de David est inspirée de situations réelles. »
- **Prix** : il n'apparaît que dans la carte de l'offre (3 999 F, barré 12 500 F), après « Ce que tu reçois ». Tous les autres boutons disent « Commencer le défi » ou « Faire le défi avec moi ».
- **Contact** : depuis la version 5, deux boutons « WhatsApp » et « E-mail » (livensya@emkbluediamond.online), sans coordonnées affichées en texte (voir plus haut).
- **Aucune garantie** de remboursement n'est mentionnée nulle part.
- **La confidence du test** (question sur la remarque la plus blessante) n'est jamais enregistrée ni envoyée : elle sert seulement à adapter le résultat sur le téléphone.

## Ce qu'il y a dans le dossier

| Fichier | Rôle |
|---|---|
| `index.html` | La page du tunnel : héros, test de 2 minutes, résultat, histoire, méthode, contenu, jours 1/30/60, vidéo, offre, FAQ, final |
| `merci.html` | La page après paiement (non indexée par Google) |
| `mentions-legales.html`, `cgv.html`, `confidentialite.html` | Les pages légales (non indexées) |
| `css/style.css` | Tout le style (couleurs de la charte en haut du fichier) |
| `js/app.js` | Le test, le résultat, les boutons d'achat, la vidéo. **Les réglages sont en haut du fichier.** |
| `js/tracking.js` | Le Pixel Meta. **`PIXEL_ID` est en haut du fichier.** |
| `robot-achat/` | Le robot achat (Google Apps Script) : envoie le Purchase à Meta depuis le serveur. **Ne pas envoyer sur LWS** : il se colle dans Apps Script (voir son `LISEZMOI.md`) |
| `fonts/` | Les 2 polices, hébergées sur ton site (pas d'appel à Google) |
| `images/` | Photos avant/après, logos, mockups et fonds, en WebP. `images/marque/` = les originaux fournis. `images/paiement/` = logos des moyens de paiement |
| `captures/` | Les captures téléphone (390 px) et ordinateur (1440 px) de chaque page |
| `DESIGN.md` | La direction artistique et la planche de références |

## Publier sur le sous-domaine LWS (livensya.emkbluediamond.online)

1. **Créer le sous-domaine** : espace client LWS → ton hébergement → « Sous-domaines » → ajoute `livensya` sur `emkbluediamond.online`. Note le dossier créé (souvent `/livensya/` ou `/sous-domaines/livensya/` à la racine de l'hébergement).
2. **Activer le HTTPS** : dans « SSL / Let's Encrypt », coche le sous-domaine `livensya.emkbluediamond.online`. Attends qu'il soit actif (quelques minutes à quelques heures).
3. **Envoyer les fichiers** : par le gestionnaire de fichiers LWS ou en FTP (FileZilla), copie **le contenu** du dossier `sites/livensya/` dans le dossier du sous-domaine : `index.html`, `merci.html`, `mentions-legales.html`, `cgv.html`, `confidentialite.html`, `css/`, `js/`, `fonts/`, `images/`. Inutile d'envoyer `captures/`, `images/marque/`, `robot-achat/`, `DESIGN.md`, `DONNEES.md`, `TRACKING.md` et ce fichier.
4. **Vérifier** : ouvre `https://livensya.emkbluediamond.online` sur ton téléphone, fais le test jusqu'au bout, appuie sur un bouton d'achat (tu dois arriver sur Chariow), ouvre `/merci.html` et les trois pages légales (liens du pied de page).
5. **Brancher la page merci dans Chariow** : dans le produit, réglage « redirection après achat » (ou « page de remerciement »), mets `https://livensya.emkbluediamond.online/merci.html`. Si Chariow ne le propose pas, la page reste utile : mets son lien dans l'e-mail de livraison.

Aperçu de la vidéo et du suivi : ajoute `?apercu=1` à l'adresse (la section vidéo s'affiche même vide, et les événements du Pixel s'écrivent dans la console du navigateur).

## Ce que tu peux changer toi-même (sans casser le reste)

Tout est en haut de `js/app.js` :

```js
const LIEN_PAIEMENT = 'https://ykhzgspm.mychariow.store/prd_4bisyd7x/checkout';   // repli si le widget ne charge pas
const PAGE_APRES_ACHAT = 'merci.html';  // où envoyer l'acheteur après un paiement réussi dans le widget
const ROBOT_ACHAT = '';      // adresse /exec du robot achat (pas un secret) ; vide = aucun signal
const VIDEO_SRC = '';        // ex. 'videos/defi-60-jours.mp4'
const VIDEO_AFFICHE = '';    // ex. 'videos/affiche.webp'
```

- **Prénom du narrateur** : `const PRENOM_NARRATEUR = 'David';` (et la même ligne dans `merci.html`).
- **Lien de repli** : `LIEN_PAIEMENT` pointe déjà vers la page de paiement du produit. Les paramètres publicitaires (`utm_…`, `fbclid`) de l'adresse d'arrivée sont transmis automatiquement à Chariow.
- **Vidéo faceless** : dépose le fichier dans un dossier `videos/` (MP4 H.264, format vertical 9:16, idéalement moins de 8 Mo), puis remplis `VIDEO_SRC`. Tant que c'est vide, la section est invisible pour les visiteurs. Rien ne se charge avant le clic sur « Lire la vidéo ».
- **Textes** : directement dans `index.html` et `merci.html`. Garde le tutoiement, pas de tiret cadratin, et pas de promesse de kilos.
- **Prix** : une seule fois, dans la carte de l'offre de `index.html` : cherche `999`.
- **Témoignages** : un modèle commenté est prêt dans `index.html` (cherche `TÉMOIGNAGES`). À n'utiliser qu'avec de vrais retours et l'accord écrit de la personne.
- **Collecte des réponses du test** : la fonction `envoyerLead(donnees)` (en haut de `js/app.js`) est vide exprès. Aujourd'hui, aucune donnée ne quitte le téléphone (le test l'annonce aux visiteurs). Si tu la branches un jour, il faudra changer cette phrase et ta politique de confidentialité.

## Suivi Meta (Pixel), simple et sans doublon

Plan complet, règles anti-doublon et vérifications : voir `TRACKING.md`.

1. Le Pixel est **actif** : `var PIXEL_ID = '5010730402487338';` dans `js/tracking.js`. Pour tout couper, mets `''` : plus rien n'est chargé. Les « événements automatiques » de Meta restent sur le réglage par défaut. La politique de confidentialité décrit ce suivi : si tu ajoutes un autre outil, mets-la à jour.
2. Événements envoyés (Pixel standard, rien d'autre) :

| Événement | Quand | Garde-fou |
|---|---|---|
| `PageView` | chaque page (accueil, merci, pages légales) | |
| `ViewContent` | quand la section de l'offre s'affiche | une fois par page vue |
| `Lead` | fin du test | une seule fois par visiteur (drapeau `lv_lead_envoye` dans le téléphone) |
| `InitiateCheckout` | clic sur un bouton d'achat | un par clic, clics répétés en moins de 2 s ignorés |
| `Purchase` | **pas envoyé par le navigateur** : envoyé par le robot achat (serveur) | une fois par vente (journal du robot) |

Chaque événement porte un `eventID` unique (ex. `Lead.8f3c…`), prêt pour la déduplication avec l'API Conversions (même nom d'événement + même `event_id` côté serveur).

3. **Jamais de jeton API Conversions dans ces fichiers** : un site statique est lisible par tout le monde.

### Le Purchase : envoyé par le robot achat (serveur)

1. Chariow prévient le robot à chaque vente réussie (Pulse « Vente réussie »). Le robot relit la vente chez Chariow avant tout envoi : un faux appel n'envoie rien.
2. Il envoie un seul `Purchase` à Meta : `event_id` = identifiant de la vente Chariow, valeur 3999 XOF, e-mail, téléphone, prénom, nom et pays **hachés en SHA-256**, adresse IP et navigateur du paiement, et les cookies Meta (`_fbp`, `_fbc`) si la page les lui a transmis.
3. Pas de `Purchase` dans `merci.html` (expliqué en commentaire dans la page) : elle peut être rechargée ou ouverte sans achat.
4. Installation : `robot-achat/LISEZMOI.md`. Tant que le robot n'est pas installé, aucun Purchase n'arrive chez Meta (le reste du suivi marche normalement).

## Ce qu'Enock doit fournir ou valider
1. **L'histoire de David** telle qu'écrite sur la page (réécriture à la 1re personne de la préface du livre). Âge aligné sur le livre : 26 ans.
2. **La question du miroir** : le livre écrit « sa question n'a pas été : « Qu'est-ce que je fais mal depuis tout ce temps ? » ». J'ai compris « a été » (c'est elle qui mène à la méthode). Vérifie la phrase du livre, elle semble contenir une coquille.
3. **Les photos avant/après** sont présentées comme celles de David (« Moi, c'est David… Voici comment j'étais »), alors que David est un personnage « inspiré de situations réelles ». Une partie des visiteurs prendra ces photos pour celles d'un vrai client : à toi de décider si tu gardes cette présentation, ou si tu ajoutes une légende du type « photos réelles d'avant et d'après ».
4. **Les phrases de David dans le test** (« Moi aussi, j'ai entendu ces phrases », « le jour où une personne que j'appréciais m'a dit qu'elle me voyait comme un frère », « Moi aussi, j'ai eu des jours sans motivation », « Pour moi non plus, ça n'a pas marché ») : alignées sur le livre (préface et carnet du jour 52).
5. **Le prix barré 12 500 F** : à garder seulement si c'est vraiment le prix prévu après le lancement. Sur Chariow, couper le compte à rebours « renouvelé chaque jour » (fausse urgence).
6. **Un vrai test de paiement** sur ton téléphone (le paiement s'ouvre bien dans la fenêtre, Mobile Money passe, et tu arrives sur la page d'achat Chariow). Depuis notre environnement de test, le contenu du paiement est bloqué par Cloudflare : on a vérifié l'ouverture de la fenêtre, pas le formulaire.
7. **Deux vraies captures de pages** des PDF (emplacement `EXTRAIT` prêt).
8. **Les mockups des livres** (corps générés, « votre », « ENOCK M. ») : légendés « visuel d'illustration ». Pas de torse nu ni d'avant/après dans les pubs Meta.
9. **Les pages légales** (`mentions-legales.html`, `cgv.html`, `confidentialite.html`) : relis-les, surtout l'absence de remboursement, la phrase sur un double débit, et les durées de conservation. Le Pixel est branché (ID 5010730402487338) ; le jeton API Conversions reste côté serveur.
10. **La vidéo faceless**, puis de vrais témoignages avec accord.
11. **Ton ✅** sur l'aperçu avant toute mise en ligne.
12. **Installer le robot achat** (`robot-achat/LISEZMOI.md`), puis me donner l'adresse `/exec` (ou la coller toi-même dans `ROBOT_ACHAT`). Sur la première vraie vente, regarde la colonne « Signal page » de l'onglet Ventes.

## Ce que le navigateur garde (téléphone de l'acheteur)
- `lv_initiate_checkout_id` : eventID du dernier InitiateCheckout.
- `lv_purchase_id` : identifiant d'achat Chariow reçu à la fin du paiement dans le widget. Aussi présent dans l'adresse `merci.html?achat=<id>`.
- `lv_signal_achat` (version 6) : identifiant du dernier achat déjà signalé au robot, pour ne jamais le signaler deux fois.
