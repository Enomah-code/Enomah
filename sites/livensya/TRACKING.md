# Suivi Meta de Livensya (Pixel 5010730402487338)

Simple, fiable, sans doublon. PageView, ViewContent, Lead et InitiateCheckout partent du navigateur. Le Purchase part uniquement du serveur : le « robot achat » (Google Apps Script, dossier `robot-achat/`).

## 1. Plan des événements

| Événement | Quand il part | Pages | Source | eventID | Paramètres |
|---|---|---|---|---|---|
| PageView | à l'ouverture de la page, 1 fois | les 5 pages | navigateur (`js/tracking.js`) | `PageView.<uuid>` | aucun |
| ViewContent | quand l'offre (`#offre`) apparaît à l'écran, 1 fois par page vue | accueil | navigateur (`js/app.js`) | `ViewContent.<uuid>` | content_ids `prd_4bisyd7x`, content_type `product`, content_name `Défi 60 jours`, value `3999`, currency `XOF` |
| Lead | fin du test, 1 seule fois par visiteur (drapeau `lv_lead_envoye`) | accueil | navigateur | `Lead.<uuid>` | content_name `Test 2 minutes` |
| InitiateCheckout | clic sur le bouton d'achat du widget Chariow, ou départ vers la page de paiement Chariow (bouton de repli, ou widget pas prêt après 6 s) | accueil | navigateur | `InitiateCheckout.<uuid>` | mêmes paramètres que ViewContent |
| Purchase | vente réussie chez Chariow (Pulse « Vente réussie »), vérifiée par relecture de la fiche Chariow ; envoi dès le signal de la page, ou au plus tard 10 à 15 min après le webhook | aucune (serveur) | **serveur seul** : robot achat (API Conversions v25.0) | ID de la vente Chariow (`sal_…`) | value = montant payé (3999), currency `XOF`, content_ids `prd_4bisyd7x`, content_type `product`, content_name `Défi 60 jours`, order_id ; user_data : em, ph, fn, ln, country, external_id hachés SHA-256, client_ip_address et client_user_agent du paiement (fiche Chariow), fbp et fbc (signal de la page) |

Merci et pages légales : PageView seulement. Le message de fin de paiement (`chariow-purchase-completed`) ne déclenche aucun événement Meta : il range `lv_purchase_id`, envoie une fois au robot le signal `{purchaseId, _fbp, _fbc, _userAgent, _eventSourceUrl}` (seulement si `ROBOT_ACHAT` est rempli dans `js/app.js`), puis redirige vers `merci.html?achat=<id>`.

## 2. Règles anti-doublon (déjà en place)

1. Un seul fichier de suivi (`js/tracking.js`), un seul `init`, un seul chargement de `fbevents.js` par page. Ne colle jamais le « code de base » Meta dans les pages : il ferait doublon.
2. `fbq.disablePushState = true` : un clic sur un lien interne (`#offre`, `#contenu`) ou le bouton Retour ne crée plus de PageView en plus. (Option officielle Meta : [doc SPA](https://developers.facebook.com/docs/meta-pixel/implementation/tag_spa).)
3. InitiateCheckout : seul le bouton d'achat du widget compte (pas la croix qui ferme la fenêtre de paiement) ; les clics répétés en moins de 2 s sont ignorés ; un bouton « Commencer le défi » cliqué deux fois pendant le chargement du widget ne compte qu'une fois ; le repli après 6 s ne part que si le widget n'a pas été ouvert.
4. Lead : drapeau dans le téléphone, il ne repart pas si le test est refait ou la page rechargée.
5. Pas de Purchase sur `merci.html` (page rechargeable, partageable), ni nulle part dans le navigateur. Le Purchase n'a qu'une source, le robot : pas de déduplication navigateur/serveur à gérer.
6. Pas de deuxième intégration Meta : ni Pixel dans les réglages Chariow, ni plugin, ni Google Tag Manager, ni événements créés avec l'« Outil de configuration des événements » de Meta. À vérifier une fois (voir 3.4). Avec le robot, c'est encore plus important : un Pixel réglé dans Chariow enverrait son propre Purchase, avec un autre event_id, donc compté deux fois.
7. Robot achat : une seule entrée par ID de vente dans ses propriétés (`vente_<id>`), sous verrou. Webhook renvoyé, deuxième Pulse, signal répété, rechargement de la page : rien ne repart. Le signal de la page part une seule fois par achat (drapeau `lv_signal_achat` + garde dans la page) et ne crée jamais d'achat à lui seul.

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

## 4. Le Purchase côté serveur : le robot achat

Code : `robot-achat/Code.gs`. Installation pas à pas : `robot-achat/LISEZMOI.md`.

**Déroulé d'une vente**
1. Chariow envoie le Pulse « Vente réussie » (`successful.sale`) à l'adresse `/exec` du robot.
2. Le robot ignore tout ce qui n'est pas le produit `prd_4bisyd7x` de la boutique Livensya (contrôle par `store.id` = `store_6is731jk2ybk` ; l'adresse `ykhzgspm.mychariow.store` ne sert que si l'id manque, et ne bloque pas).
3. Il relit la fiche de la vente (`GET https://api.chariow.com/v1/sales/<id>`, clé `CHARIOW_API_KEY` ; les ids réels ressemblent à `SALEPEBV79QCZDIA6PJ`). Payée si statut `completed`, `settled`, `success`, `paid`, ou paiement `success`. Refus, rien envoyé : vente inconnue (faux appel), autre produit, autre boutique, statut `failed`, `cancelled`, `abandoned`, `refunded`, `expired`, paiement `failed`/`cancelled`, vente de plus de 7 jours. Statut inconnu, produit absent de la fiche, Chariow en panne : nouvel essai toutes les 5 min pendant 1 h, puis « Échec » visible dans l'onglet Ventes (rejouable depuis Chariow). Vente d'affilié (fiche : `channel` = `affiliate` ou `store_affiliate` rempli) : pas envoyée (`ENVOYER_VENTES_AFFILIES = false`), ligne « Vente affilié, non envoyée ». Si la fiche ne dit rien, le champ `affiliate` du webhook décide, mais sans rien mémoriser : un faux webhook « affilié » ne bloque jamais la vraie vente.
4. Il attend le signal de la page (cookies `_fbp`, `_fbc`) au plus 10 min, puis envoie le Purchase, avec ou sans fbp/fbc. Déclencheur `envoyerEnAttente` toutes les 5 min.
5. Réponse de Meta lue (`events_received` >= 1, sinon pas compté comme envoyé). Meta injoignable, 5xx, 429 ou `events_received` 0 : jusqu'à 12 essais (1 h). Jeton refusé (HTTP 401/403, erreurs 190/102) : la vente attend sans compter les essais, « En attente : jeton Meta refusé ». Autre erreur (400…) : pas de relance, « Échec Meta ». Après un envoi réussi, l'onglet Ventes passe à « Envoyé » avant l'état mémorisé ; si la mémoire ne peut pas être écrite, le robot tente une écriture minimale, journalise, et la ligne « Envoyé » de l'onglet Ventes empêche tout renvoi. États terminés effacés après 10 jours (au-delà de 7 jours, une vente est de toute façon refusée).

**Pourquoi pas la signature du webhook** : Chariow signe chaque Pulse (en-tête `x-chariow-signature`, HMAC-SHA256 du corps brut, [doc Chariow Pulse Security](https://chariow.dev/en/guides/pulse-security)). Mais Apps Script ne transmet pas les en-têtes HTTP à `doPost` ([doc Google, objet événement](https://developers.google.com/apps-script/guides/web)). La relecture de la fiche par l'API remplace donc la signature : un faux appel ne peut au pire que provoquer l'envoi d'une vraie vente Livensya payée, une seule fois.

**Correspondance (EMQ)** : e-mail, prénom, nom, téléphone (`customer.phone.number` + `dial_code`) et pays de la fiche Chariow (téléphone et pays du webhook en secours, seulement si l'e-mail du webhook est celui de la fiche), hachés SHA-256 après normalisation ([règles Meta](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters)) : e-mail en minuscules sans espaces ; téléphone en chiffres avec indicatif (`+229 01 97 00 00 00` donne `2290197000000`, numéro sans indicatif connu : non envoyé) ; prénom et nom en minuscules sans espaces ni ponctuation ; pays en 2 lettres minuscules. En clair : IP du paiement (validée, publique, sinon écartée), navigateur du paiement, fbp, fbc. `event_time` = heure de la vente en secondes, jamais dans le futur (min(completed_at, maintenant)) ; value = `amount.value` de la fiche dès que c'est un nombre >= 0 (3999 seulement s'il manque), currency = `amount.currency` si 3 lettres majuscules (sinon XOF). Navigateur inconnu : envoi quand même, noté dans `_Debug` (vente de plus de 7 jours : non envoyée, [limite Meta](https://developers.facebook.com/docs/marketing-api/conversions-api/using-the-api)).

**Correspondance purchaseId / ID de vente** : le widget envoie `purchaseId` et ouvre `https://<boutique>/purchase/<purchaseId>` (code du widget). L'API Checkout de Chariow appelle `purchase.id` l'identifiant de vente `sal_…` ([doc Checkout](https://chariow.dev/en/guides/checkout)). Les deux devraient donc être identiques, **à confirmer sur la première vraie vente**. Si ce n'est pas le cas : aucun doublon ni perte, le Purchase part sans fbp/fbc après 10 min, et `_Debug` affiche « Signal sans vente » 24 h après. Pas de correspondance par e-mail possible : la page ne connaît pas l'e-mail de l'acheteur.

**Code de test** : `META_TEST_EVENT_CODE` sert **uniquement** à `testerAchatFictif()`, qui refuse de partir sans lui. Les vraies ventes ne portent **jamais** `test_event_code`.

**Secrets** : `META_ACCESS_TOKEN` et `CHARIOW_API_KEY` dans les Propriétés du script uniquement. Jamais dans le site, jamais écrits dans la feuille (filtre `sansSecret_`), jamais affichés par `verifierConfiguration` (seulement leur longueur). IP masquée (`160.155.x.x`) dans la feuille.

**Choix de simplicité** : pas d'IP depuis la page (pas d'ipify) : l'IP vient de la fiche Chariow. Fenêtre de paiement acceptée seulement depuis `https://ykhzgspm.mychariow.store` (adresse construite par le widget). Risque résiduel : si Meta reçoit un achat mais que la réponse se perd (exception réseau), une relance peut le doubler, Meta ne garantissant pas la déduplication entre deux envois serveur.

### Procédure de test (une fois installé)
1. Simulateur sur ordinateur, sans réseau : `node sites/livensya/robot-achat/tests/scenarios.js` (128 vérifications, toutes OK au 9 octobre 2026).
2. Apps Script : `verifierConfiguration`, puis `testerAchatFictif` avec `META_TEST_EVENT_CODE` rempli ; l'onglet « Tester les événements » doit montrer 1 Purchase, source Serveur, « TEST robot achat (fictif) ».
3. Pulse Chariow : le bouton de test éventuel doit donner « Refusé : vente inconnue chez Chariow » dans `_Debug`.
4. Première vraie vente : onglet Ventes, « Envoyé, events_received=1 » et colonne Signal page. Puis, dans le Gestionnaire d'événements, « Vue d'ensemble » > Purchase : source **Serveur** seule, 1 par vente. Si un Purchase **Navigateur** apparaît aussi, c'est une deuxième source (Pixel réglé dans Chariow, ou « événements automatiques » de Meta qui devineraient un achat sur `merci.html`) : ne change rien toi-même, dis-le-moi et on décidera ensemble.
5. Jamais d'achat réel pour tester.

## 5. Audit du 9 octobre 2026

Vérifié avec Chromium (Playwright), connect.facebook.net bloqué (aucun événement réel envoyé), widget Chariow et page de paiement simulés en local.
Corrigé : PageView en double sur liens internes et bouton Retour ; InitiateCheckout à la fermeture de la fenêtre de paiement ; double InitiateCheckout possible pendant le chargement du widget ; InitiateCheckout du repli coupé par la redirection immédiate.
Verdict : OK pour le navigateur, sous réserve du point 3.4 (aucun Pixel dans Chariow).

## 6. Audit du robot achat (9 octobre 2026)

Vérifié : simulateur Node (128 vérifications, fiche au format réel de Chariow, statut `settled` ; en plus : verrou occupé, écriture impossible après un envoi réussi, exception réseau et events_received 0, abandon puis rejeu, statut inconnu, produit absent, montant 0, devise objet, affiliés (fiche et webhook forgé), heure future, purge à 10 jours, fbp/fbc/URL invalides ; et : vente valide, webhook renvoyé, signal avant/après/absent, autre produit/boutique, faux webhook, IP invalides, mode test, achat fictif refusé sans code, pannes Chariow et Meta, jeton oublié, secrets absents des journaux), et `js/app.js` dans Chromium sans réseau (tout bloqué, faux widget) : redirection vers `merci.html?achat=…` intacte, 1 seul signal (sendBeacon, ou repli fetch), aucun signal quand `ROBOT_ACHAT` est vide, aucun nouveau signal après rechargement, messages venant d'autres origines (`evil.mychariow.store`, `checkout.chariow.com`) ignorés.
Relecture par un auditeur indépendant : faite (demandée par le coordinateur), 16 corrections appliquées (statuts réels, code de test réservé à l'achat fictif, purge à 10 jours, écriture protégée, boutique par store.id, montant, jeton refusé, affiliés, heure, file d'attente, origine du widget). Une nouvelle relecture de ces corrections reste conseillée.
Verdict provisoire : OK, sous réserve de la relecture indépendante et de la confirmation purchaseId = ID de vente sur la première vente.
