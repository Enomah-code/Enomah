# Robot achat Livensya : mode d'emploi pas à pas

Ce robot envoie à Meta l'événement **Purchase** (achat) de chaque vente du Défi 60 jours, **une seule fois par vente**, depuis un serveur Google (Apps Script). Ton site n'envoie jamais de Purchase lui-même.

Comment il marche, en 4 lignes :
1. Quand une vente réussit, Chariow prévient le robot (c'est un « Pulse », un message automatique appelé aussi webhook).
2. Le robot relit la vente chez Chariow avec ta clé API : si la vente n'existe pas, n'est pas payée ou n'est pas le Défi 60 jours, **il n'envoie rien**. C'est sa protection contre les faux appels.
3. Il attend au plus 10 minutes un petit signal de ta page (les cookies Meta du visiteur, qui aident Meta à reconnaître l'acheteur). Avec ou sans signal, il envoie ensuite le Purchase.
4. Il note chaque vente envoyée : si Chariow renvoie le même message, il ne renvoie rien à Meta.

Fichiers du dossier :
- `Code.gs` : le robot (à coller dans Apps Script).
- `appsscript.json` : ses réglages (fuseau Africa/Lagos, accès web).
- `tests/` : le simulateur qui vérifie le robot sur ton ordinateur, sans rien envoyer (`node tests/scenarios.js`).

Compte environ 30 minutes. Ne fais aucun vrai achat pour tester.

---

## Étape 1. Créer la Google Sheet

1. Va sur https://sheets.google.com avec ton compte Google.
2. Clique sur **Vierge** (nouvelle feuille).
3. En haut à gauche, clique sur « Feuille de calcul sans titre » et renomme-la **Livensya Suivi**.

Tu n'as pas besoin de créer les onglets : le robot crée lui-même **Ventes** et **_Debug** (journal technique).

## Étape 2. Ouvrir Apps Script et coller le code

1. Dans la feuille, menu **Extensions** > **Apps Script**. Un nouvel onglet s'ouvre.
2. En haut à gauche, renomme le projet « Projet sans titre » en **Robot achat Livensya**.
3. Dans la liste des fichiers à gauche, clique sur **Code.gs**. Efface tout ce qu'il contient.
4. Ouvre le fichier `robot-achat/Code.gs` de ton dossier, copie **tout** son contenu, colle-le dans l'éditeur.
5. Clique sur l'icône de disquette (**Enregistrer le projet**) ou fais Ctrl+S.

Le fichier `appsscript.json` (facultatif mais conseillé) :
1. Clique sur la roue dentée à gauche (**Paramètres du projet**).
2. Coche **Afficher le fichier manifeste "appsscript.json" dans l'éditeur**.
3. Reviens dans l'éditeur (icône **< >** à gauche), clique sur `appsscript.json`, remplace son contenu par celui du fichier `robot-achat/appsscript.json`, enregistre.

## Étape 3. Préparer les deux clés (elles sont secrètes)

Ces deux valeurs ne vont **que** dans Apps Script. Ne les colle jamais dans un fichier du site, un message, un e-mail ou une discussion.

**A. Le jeton Meta (META_ACCESS_TOKEN)**
1. Va sur https://business.facebook.com, menu **Gestionnaire d'événements**.
2. Choisis la source de données **Livensya** (ID 5010730402487338).
3. Onglet **Paramètres**. Descends jusqu'à la partie **API Conversions**.
4. Clique sur **Générer un jeton d'accès** (le libellé exact peut varier un peu). Copie le jeton qui s'affiche.

**B. La clé API Chariow (CHARIOW_API_KEY)**
1. Va sur https://app.chariow.com et ouvre la boutique **Livensya** (ykhzgspm.mychariow.store). Important : la clé doit venir de cette boutique, sinon le robot ne trouvera pas les ventes et n'enverra rien.
2. Menu **Paramètres** > **Clés API** > **Créer une clé API**. Donne-lui le nom « Robot achat ».
3. Copie la clé tout de suite : Chariow ne l'affiche qu'une fois.

**C. Le code de test Meta (META_TEST_EVENT_CODE), seulement pour tester**
1. Gestionnaire d'événements > source **Livensya** > onglet **Tester les événements**.
2. Dans la partie **Événements du serveur** (API Conversions), copie le code de test (il ressemble à `TEST12345`).

## Étape 4. Ranger les clés dans les propriétés du script

1. Dans Apps Script, roue dentée à gauche : **Paramètres du projet**.
2. Tout en bas, **Propriétés du script** > **Ajouter une propriété du script**.
3. Ajoute ces trois lignes (nom exact à gauche, valeur à droite) :

| Propriété | Valeur |
|---|---|
| `META_ACCESS_TOKEN` | le jeton Meta (étape 3A) |
| `CHARIOW_API_KEY` | la clé Chariow (étape 3B) |
| `META_TEST_EVENT_CODE` | le code de test (étape 3C), **pendant les tests seulement** |

4. Clique sur **Enregistrer les propriétés du script**.

## Étape 5. Lancer verifierConfiguration et autoriser le robot

1. Reviens dans l'éditeur (icône **< >**).
2. En haut, dans la liste déroulante des fonctions, choisis **verifierConfiguration**, puis clique sur **Exécuter**.
3. La première fois, Google demande une autorisation :
   - clique sur **Examiner les autorisations**, choisis ton compte ;
   - un écran « Google n'a pas validé cette application » peut s'afficher : c'est normal pour un script que tu as créé toi-même. Clique sur **Paramètres avancés** puis **Accéder à Robot achat Livensya (non sécurisé)** ;
   - clique sur **Autoriser**.
   Le robot demande : lire et écrire ta feuille Livensya Suivi, appeler des sites externes (Chariow et Meta), et créer un déclencheur.
4. En bas, le **Journal d'exécution** affiche le résultat, par exemple :
   - `OK : META_ACCESS_TOKEN est rempli (…)` ;
   - `OK : CHARIOW_API_KEY est rempli (…)` ;
   - `MODE TEST ACTIF …` (normal pendant les tests) ;
   - `Fait : déclencheur « envoyerEnAttente » (toutes les 5 min) installé.`
   Le robot n'affiche jamais tes clés, seulement leur longueur.
5. Si une ligne commence par `MANQUE`, ajoute la propriété indiquée (étape 4) et relance.

Le déclencheur « envoyerEnAttente » tourne toutes les 5 minutes : il envoie les achats dont le signal de la page n'est pas arrivé après 10 minutes, et refait les essais si Chariow ou Meta étaient en panne. Tu peux le voir dans l'icône réveil à gauche (**Déclencheurs**). N'en crée pas un deuxième.

## Étape 6. Déployer en application web

1. En haut à droite : **Déployer** > **Nouveau déploiement**.
2. À côté de « Sélectionner le type », clique sur la roue dentée > **Application Web**.
3. Remplis :
   - Description : `Robot achat v1` ;
   - **Exécuter en tant que** : **Moi** (ton adresse) ;
   - **Qui a accès** : **Tout le monde**. (Chariow doit pouvoir l'appeler sans compte Google. Ce n'est pas risqué : le robot vérifie chaque vente chez Chariow avant d'envoyer quoi que ce soit.)
4. Clique sur **Déployer**, puis copie l'**URL de l'application Web**. Elle se termine par `/exec`.
5. Vérification : colle cette adresse dans ton navigateur. Tu dois voir `{"status":"ok"}`.

Si tu modifies `Code.gs` plus tard : **Déployer** > **Gérer les déploiements** > crayon > Version : **Nouvelle version** > **Déployer**. L'adresse `/exec` reste la même.

## Étape 7. Créer le Pulse dans Chariow

1. Tableau de bord Chariow de la boutique Livensya > **Automatisations** > onglet **Pulses** > **Créer un pulse**.
2. **URL du pulse** : colle l'adresse `/exec` de l'étape 6.
3. **Sélectionner un événement** : **Vente réussie**.
4. **Appliquer à un produit** : choisis **Défi 60 jours** (prd_4bisyd7x). (Le robot ignore de toute façon les autres produits.)
5. Clique sur **Créer**.

Si Chariow propose un bouton pour **envoyer un événement de test** : tu peux l'utiliser. Ce test contient une vente imaginaire, donc le robot doit la **refuser** : dans l'onglet `_Debug` de ta feuille, tu verras « Refusé : vente inconnue chez Chariow (faux appel ?). Rien envoyé à Meta. » C'est la preuve que la protection marche.

À propos de la signature Chariow : Chariow signe chaque Pulse (en-tête `x-chariow-signature`), mais Google Apps Script ne permet pas de lire les en-têtes d'un message reçu. Le robot ne peut donc pas vérifier cette signature ; il relit la vente chez Chariow à la place, ce qui protège aussi des faux achats. Tu n'as pas besoin de copier le « secret de signature » (whsec_…) du Pulse.

## Étape 8. Brancher le site

Dans `js/app.js`, tout en haut, remplace :

```js
const ROBOT_ACHAT = '';
```

par ton adresse, par exemple :

```js
const ROBOT_ACHAT = 'https://script.google.com/macros/s/AKfy…/exec';
```

Puis renvoie `js/app.js` sur ton hébergement LWS. Tu peux aussi me donner l'adresse : ce n'est pas un secret.

Tant que `ROBOT_ACHAT` est vide, la page n'envoie aucun signal ; le robot envoie quand même les achats (sans les cookies Meta, après 10 minutes).

## Étape 9. Tester sans fausse vente : testerAchatFictif

1. Vérifie que `META_TEST_EVENT_CODE` est bien rempli (étape 4).
2. Ouvre l'onglet **Tester les événements** du Gestionnaire d'événements, et garde-le ouvert.
3. Dans Apps Script, choisis la fonction **testerAchatFictif** et clique sur **Exécuter**.
4. Le journal d'exécution dit : `Achat fictif envoyé avec le code de test…`.
5. Dans **Tester les événements**, un événement **Purchase** apparaît en moins d'une minute, source **Serveur**, nommé « TEST robot achat (fictif) », valeur 3999 XOF. Clique dessus pour voir les informations envoyées (e-mail, téléphone, etc. sont hachés : c'est normal).

Sans code de test, `testerAchatFictif` refuse de partir : un achat fictif n'ira jamais dans tes vraies données.

## Étape 10. Passer en vrai

1. **Paramètres du projet** > **Propriétés du script** : supprime `META_TEST_EVENT_CODE` (ou vide sa valeur). Enregistre.
2. Relance **verifierConfiguration** : la ligne doit dire `Mode normal`.

Attention : tant que `META_TEST_EVENT_CODE` est rempli, **les vraies ventes** partent aussi avec le code de test. Elles s'affichent dans « Tester les événements » mais **ne comptent pas** pour tes publicités, et le robot ne les renverra pas. Ne laisse donc pas le mode test actif plus que le temps des essais.

## Lire la feuille Livensya Suivi

Onglet **Ventes** (une ligne par vraie vente du Défi 60 jours) :
- **Statut Meta** : « En attente du signal de la page », puis « Envoyé, events_received=1 » (Meta a bien reçu l'achat). « (mode test) » si le code de test était rempli. « Échec Meta : … » ou « Erreur Meta, nouvel essai… » en cas de souci.
- **Signal page** : « fbp fbc » si la page a transmis les cookies Meta, « non » sinon (acheteur parti avant la fin, ou `ROBOT_ACHAT` vide).
- **IP (masquée)** : seulement les deux premiers nombres, par exemple `160.155.x.x`.

Onglet **_Debug** : tout ce que le robot a reçu ou décidé (doublons ignorés, ventes refusées, réponses de Meta). Aucune clé n'y est jamais écrite.

En cas d'échec définitif (Chariow ou Meta en panne plus d'une heure), rejoue la vente depuis Chariow : **Automatisations** > **Pulses** > ton pulse > onglet **Livraisons** > rejouer. Le robot la retraite, et n'envoie toujours qu'une fois.

## À vérifier sur la première vraie vente

Ouvre l'onglet **Ventes** : la colonne **Signal page** doit indiquer « fbp » ou « fbp fbc ». Si elle dit « non » alors que l'acheteur a payé dans la fenêtre du site, regarde `_Debug` : une ligne « Signal sans vente » le lendemain veut dire que l'identifiant envoyé par la fenêtre de paiement n'est pas le même que celui du webhook. Dis-le-moi : l'achat est quand même envoyé à Meta (sans les cookies), on corrigera la correspondance.

## Surveillance

L'adresse `/exec` ouverte dans un navigateur répond `{"status":"ok"}`. Tu peux la donner à un outil de surveillance (UptimeRobot par exemple) : cet appel n'envoie rien à Meta.
