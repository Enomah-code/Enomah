# Suivi Meta de Livensya (Pixel 5010730402487338)

Simple, fiable, sans doublon. Navigateur uniquement pour l'instant. Le Purchase viendra plus tard du serveur.

## 1. Plan des événements

| Événement | Quand il part | Pages | Source | eventID | Paramètres |
|---|---|---|---|---|---|
| PageView | à l'ouverture de la page, 1 fois | les 5 pages | navigateur (`js/tracking.js`) | `PageView.<uuid>` | aucun |
| ViewContent | quand l'offre (`#offre`) apparaît à l'écran, 1 fois par page vue | accueil | navigateur (`js/app.js`) | `ViewContent.<uuid>` | content_ids `prd_4bisyd7x`, content_type `product`, content_name `Défi 60 jours`, value `3999`, currency `XOF` |
| Lead | fin du test, 1 seule fois par visiteur (drapeau `lv_lead_envoye`) | accueil | navigateur | `Lead.<uuid>` | content_name `Test 2 minutes` |
| InitiateCheckout | clic sur le bouton d'achat du widget Chariow, ou départ vers la page de paiement Chariow (bouton de repli, ou widget pas prêt après 6 s) | accueil | navigateur | `InitiateCheckout.<uuid>` | mêmes paramètres que ViewContent |
| Purchase | **jamais dans le navigateur** | aucune | futur : serveur (API Conversions, webhook de vente Chariow) | `purchaseId` Chariow | value `3999`, currency `XOF` |

Merci et pages légales : PageView seulement. Le message de fin de paiement (`chariow-purchase-completed`) ne déclenche aucun événement : il range `lv_purchase_id` et envoie vers `merci.html?achat=<id>`.

## 2. Règles anti-doublon (déjà en place)

1. Un seul fichier de suivi (`js/tracking.js`), un seul `init`, un seul chargement de `fbevents.js` par page. Ne colle jamais le « code de base » Meta dans les pages : il ferait doublon.
2. `fbq.disablePushState = true` : un clic sur un lien interne (`#offre`, `#contenu`) ou le bouton Retour ne crée plus de PageView en plus. (Option officielle Meta : [doc SPA](https://developers.facebook.com/docs/meta-pixel/implementation/tag_spa).)
3. InitiateCheckout : seul le bouton d'achat du widget compte (pas la croix qui ferme la fenêtre de paiement) ; les clics répétés en moins de 2 s sont ignorés ; un bouton « Commencer le défi » cliqué deux fois pendant le chargement du widget ne compte qu'une fois ; le repli après 6 s ne part que si le widget n'a pas été ouvert.
4. Lead : drapeau dans le téléphone, il ne repart pas si le test est refait ou la page rechargée.
5. Pas de Purchase sur `merci.html` (page rechargeable, partageable).
6. Pas de deuxième intégration Meta : ni Pixel dans les réglages Chariow, ni plugin, ni Google Tag Manager, ni événements créés avec l'« Outil de configuration des événements » de Meta. À vérifier une fois (voir 3.4).

## 3. Vérifier une fois le site en ligne (lecture seule, rien à modifier)

**3.1 Meta Pixel Helper (sur ordinateur, Chrome)**
1. Installe l'extension « Meta Pixel Helper » depuis le Chrome Web Store.
2. Ouvre https://livensya.emkbluediamond.online/ puis clique sur l'icône de l'extension.
3. Attendu : un seul Pixel (5010730402487338), un seul PageView. Aucune alerte « Pixel chargé plusieurs fois ».
4. Descends jusqu'à l'offre : un ViewContent apparaît, un seul. Clique sur « D'abord, voir ce que tu reçois » ou un autre lien interne : pas de nouveau PageView.
5. Ouvre `cgv.html`, `mentions-legales.html`, `confidentialite.html`, `merci.html` : un seul PageView chacune, rien d'autre.

**3.2 Outil « Tester les événements »**
1. Va sur business.facebook.com, menu « Gestionnaire d'événements ».
2. Choisis la source de données « Livensya » (ID 5010730402487338), onglet « Tester les événements ».
3. Dans « Événements du navigateur », tape l'adresse du site et clique « Ouvrir le site web ».
4. Fais le parcours : ouvre la page, descends jusqu'à l'offre, termine le test, clique sur « Commencer le défi », puis **ferme la fenêtre de paiement sans payer**.
5. Attendu dans la liste : 1 PageView, 1 ViewContent, 1 Lead, 1 InitiateCheckout. Aucun Purchase. Fermer la fenêtre de paiement n'ajoute rien.

Ne fais aucun vrai achat pour tester. Les événements de cet onglet sont des visites réelles de ton navigateur : c'est normal et sans risque.

**3.3 Les jours suivants (onglet « Vue d'ensemble »)**
Clique sur chaque événement : la colonne « Navigateur » doit être seule, et le nombre de PageView doit rester proche du nombre de visites (pas le double).

**3.4 Pas de deuxième source**
1. Dans Chariow, réglages de la boutique (Intégrations ou Pixel) : aucun Pixel Meta renseigné. Sinon Chariow enverrait ses propres InitiateCheckout et Purchase depuis la page de paiement : doublon, et un Purchase navigateur interdit par nos règles. Je n'ai pas pu le vérifier depuis mon environnement.
2. Dans le Gestionnaire d'événements, « Paramètres » de la source : regarde seulement, ne change rien. Les « événements automatiques » restent comme ils sont.

## 4. Le futur Purchase côté serveur (ce qu'il faudra)

1. Un petit service (Apps Script, serverless, Make...) qui reçoit le webhook « vente réussie » de Chariow et envoie un seul Purchase à l'API Conversions. Le jeton reste dans ce service (propriétés du script ou secret), jamais dans le site.
2. `event_id` = l'identifiant de la vente Chariow, toujours le même pour une vente. Vérifie que le `purchaseId` du widget (`lv_purchase_id`, `merci.html?achat=`) est bien le même que l'identifiant reçu dans le webhook.
3. Un journal des ventes déjà envoyées : si Chariow renvoie le webhook, on n'envoie pas une deuxième fois (Meta ne garantit la déduplication qu'entre navigateur et serveur, dans les 48 h : [doc déduplication](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events)).
4. Champs : `event_name: Purchase`, `event_time` en secondes, `action_source: website`, `event_source_url`, `custom_data` (value 3999, currency XOF, content_ids `prd_4bisyd7x`).
5. Correspondance (EMQ) : e-mail et téléphone hachés en SHA-256 après normalisation (minuscules sans espaces ; téléphone avec indicatif, ex. 229...). En plus si possible : `fbp` (cookie `_fbp`) et `fbc` (cookie `_fbc`, créé depuis `fbclid`), `client_user_agent`, `client_ip_address`. Le webhook Chariow ne les a sans doute pas : il faudra les faire passer (champ personnalisé Chariow, ou envoi depuis `merci.html` avec le `purchaseId`).
6. Tests uniquement avec un `test_event_code` (onglet « Tester les événements »), jamais de faux achat dans les vraies données. Version de la Graph API à vérifier au moment de coder.
7. Mettre à jour `confidentialite.html` (section 3) quand ce sera en place.

## 5. Audit du 9 octobre 2026

Vérifié avec Chromium (Playwright), connect.facebook.net bloqué (aucun événement réel envoyé), widget Chariow et page de paiement simulés en local.
Corrigé : PageView en double sur liens internes et bouton Retour ; InitiateCheckout à la fermeture de la fenêtre de paiement ; double InitiateCheckout possible pendant le chargement du widget ; InitiateCheckout du repli coupé par la redirection immédiate.
Verdict : OK pour le navigateur, sous réserve du point 3.4 (aucun Pixel dans Chariow).
