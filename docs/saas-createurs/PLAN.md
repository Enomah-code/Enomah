# Plan directeur — SaaS « vitrine + devis + espace client » pour créatifs du numérique

> Nom de code provisoire : **Studio OS** (à remplacer par le nom définitif).
> Point de départ : la maquette *Concept Pub — Vitrine complète* (handoff Claude Design) et son design system.
> Statut : plan de A à Z, avant toute ligne de code. **Révision 2** intégrée ci-dessous. Les chiffres (prix, délais) sont des hypothèses à valider.

---

## Révision 2 (30 septembre 2026) — prime sur le reste du document

Retours après la première lecture. Quand une section plus bas contredit ce bloc, **c'est ce bloc qui fait foi**.
Page de comparaison des modèles économiques (avec simulateur) : https://claude.ai/artifact/P5gGFGuS1LcY6xFJj2UeXo

### R1. Livraison protégée (garantie livraison ↔ paiement)
- Avant **paiement total** : filigrane dynamique au nom et à la référence du client, aucun bouton de téléchargement / partage / lien public, résolution réduite, jamais la source, vidéo en streaming DRM (Widevine / FairPlay / PlayReady), images converties en vidéo DRM, liens signés courts, clic droit désactivé.
- Application mobile (plus tard) : `FLAG_SECURE` sur Android (capture et enregistrement bloqués), détection `UIScreen.isCaptured` sur iOS pour masquer le contenu.
- Après paiement total : HD sans filigrane, téléchargements par format, sources, liens de partage, facture finale.
- Limite à assumer : aucun site ne bloque l'enregistrement d'écran à 100 % (Chrome desktop en DRM logiciel, ou un autre téléphone qui filme). D'où trois couches : DRM + filigrane nominatif traçable + **séquestre** (garantie financière, plan B).

### R2. Marketplace
- `plateforme.com/explorer` : catégories, sous-catégories, filtres (prix, délai, note, pays, langue, disponibilité, vérifié), tris, comparaison côte à côte de 3 créateurs, fiche créateur.
- Jauges : note /5 avec sous-notes (qualité, communication, délais, rapport qualité-prix), taux de réussite (livré et validé sans litige perdu / commandes acceptées), respect des délais, réactivité (temps de réponse chat), taux de réachat, niveaux (Nouveau, Confirmé, Expert, Élite).
- Intégrité : avis uniquement sur commande payée et livrée, moyenne bayésienne, pondération des 12 derniers mois, détection d'auto-commande (même moyen de paiement / appareil), droit de réponse, modération, mise en avant temporaire des nouveaux.
- Nouvelles tables : `reviews(order_id UNIQUE, ratings jsonb, text, reply)`, `creator_scores(tenant_id, rating_bayes, success_rate, on_time_rate, response_time, repeat_rate, level, computed_at)`, `categories`, `favorites`.

### R3. Modèle économique — deux plans comparés
- **Plan A — abonnement** : 0 / 9 900 / 24 900 FCFA par mois, 0 % de commission, le créateur encaisse lui-même. Pas de séquestre possible.
- **Plan B — commission (recommandé)** : accès gratuit et ouvert à tous ; 15 % sur les ventes du mois jusqu'à 1 000 000 FCFA, 10 % au-delà (paliers marginaux, pas d'effet de seuil). Égalité avec le plan Pro à 66 000 FCFA de ventes mensuelles.
- Recommandation : plan B, car il est le seul compatible avec paiements par la plateforme, séquestre, jauges vérifiées et accès sans barrière. Plus tard : abonnement Pro facultatif à commission réduite (ex. 5 %) pour retenir les gros vendeurs ; frais de service client facultatifs (3–5 %) pour couvrir les frais de paiement.

### R4. Paiements par la plateforme (si plan B)
- Les fonds sont détenus par un **partenaire agréé marketplace** (Stripe Connect, Mangopay, Adyen for Platforms ; Flutterwave, Paystack, FedaPay, CinetPay pour le Mobile Money), piloté par notre serveur. Jamais sur un compte personnel (activité réglementée).
- Séquestre : paiement total (ou jalon) à l'acceptation → fonds bloqués → livraison → validation (ou auto-validation à J+7 sans réponse) → libération vers le solde du créateur moins commission → reversement hebdomadaire ou à la demande. Litige → médiation sur preuves. Non-livraison après délai + grâce → remboursement possible.
- Vérification d'identité des créateurs (KYC) par le partenaire, lutte anti-blanchiment, déclarations fiscales des vendeurs selon les pays (ex. DAC7 dans l'UE).
- Avec le plan A, la section 4.1 reste valable et le flux B se limite au modèle « compte du créateur ».

### R5. Compte client unique
- Un seul compte par client pour toute la plateforme (`compte.plateforme.com`), toutes commandes chez tous les créateurs. Habillé aux couleurs du créateur quand on arrive depuis sa vitrine (connexion unique entre domaines par redirection vers le domaine de la plateforme).
- Un créateur ne voit que ses propres commandes et échanges avec ce client.
- **Chat** temps réel (Supabase Realtime) : fil par projet, pièces jointes, accusés de lecture, e-mail si hors ligne, traduction automatique, signalement des échanges de coordonnées avant paiement.
- Nouvelle commande et paiements depuis le compte.
- Modèle de données : `clients` devient global (`customers`), relation `customer_tenant(customer_id, tenant_id, first_order_at)` ; `conversations(customer_id, tenant_id, project_id?)`, `messages(conversation_id, …, read_at)`.

### R6. Relances
- E-mail : pour chaque relance, le créateur choisit **Automatique** (réglages par défaut de la section 6), **Personnalisé** (délai, nombre, objet, texte avec variables) ou **Désactivé**. Les e-mails transactionnels indispensables (reçus, confirmation, sécurité) partent toujours.
- **WhatsApp : aucun message n'est jamais envoyé par la plateforme.** Le créateur connecte son propre compte (WhatsApp Business Cloud API avec son numéro, Twilio, 360dialog, Wati, ou Zapier / Make / n8n via webhooks) ; les messages partent de son compte. Le bouton `wa.me` sur la vitrine reste possible (c'est le client qui écrit).

### R7. International dès la conception
- Langues : FR et EN au lancement (i18n dès la phase 0), puis ES, PT, AR. Traduction du chat.
- Devises : affichage dans la devise du client, encaissement dans celle du créateur, reversement dans sa devise.
- Moyens de paiement par pays (cartes, Apple/Google Pay, PayPal, virements, Mobile Money). Fuseaux horaires, formats locaux, TVA et mentions par pays.

### R8. Équipe et agents IA (un agent par poste, supervisés)

| Poste | Mission | Skills d'appui |
|---|---|---|
| Chef de projet (superviseur) | Découpe, distribue, suit délais, temps et coût par agent, rapport quotidien | `cs-project-manager`, `sprint-plan`, `sprint-health` |
| Chef de produit | Spécifications, priorités, user stories | `cs-product-manager`, `prd`, `user-story` |
| Architecte logiciel | Architecture, décisions écrites, modèle de données | `senior-architect`, `database-schema-designer` |
| Designer UI/UX | Écrans créateur, client, marketplace ; design system | `ui-ux-pro-max`, `ui-design-system`, `ux-researcher-designer` |
| Développeur front-end | Vitrines, éditeur, compte client, marketplace | `senior-frontend`, `a11y-audit` |
| Développeur back-end | API, devis, projets, comptes, isolation | `senior-backend`, `api-design-reviewer` |
| Ingénieur paiements | Séquestre, commissions, reversements, factures, devises | `stripe-integration-expert`, `senior-backend` |
| Ingénieur marketplace | Recherche, classement, jauges, anti-fraude des avis | `senior-data-engineer`, `senior-backend` |
| Ingénieur temps réel | Chat, notifications, traduction | `senior-fullstack` |
| Ingénieur médias et protection | Stockage, streaming, DRM, filigranes | `senior-backend`, `senior-computer-vision` |
| Développeur mobile | Apps iOS/Android, blocage des captures | `senior-fullstack` |
| DevOps | Hébergement, CI/CD, surveillance, sauvegardes | `senior-devops`, `ci-cd-pipeline-builder`, `observability-designer` |
| Testeur QA | Tests automatiques et manuels | `senior-qa`, `tdd-guide`, `webapp-testing` |
| Relecteur de code | Revue avant chaque fusion | `code-reviewer`, `adversarial-reviewer` |
| Expert sécurité | Audits, tests d'intrusion, paiements et données | `senior-security`, `security-pen-testing` |
| Juriste et conformité | CGU, données, KYC, fiscalité internationale | `general-counsel-advisor`, `gdpr-dsgvo-expert` |
| Finance et tarification | Modèle, commissions, trésorerie | `cfo-advisor`, `pricing-strategy`, `financial-analyst` |
| Marketing et SEO | Acquisition créateurs et clients, SEO marketplace | `marketing-strategy-pmm`, `seo-audit`, `programmatic-seo` |
| Rédacteur multilingue | Textes, e-mails, aide, traductions | `copywriting`, `email-sequence` |
| Support et confiance | Aide, modération des avis, médiation des litiges | `customer-success-manager` |

Surveillance : toi au sommet (priorités, validation de fin de phase) → chef de projet (distribution, temps et coût par agent, rapport quotidien) → agents, chacun sur sa branche et son périmètre. Rien n'est fusionné sans relecteur de code + QA (+ sécurité pour paiements et données). Tableau de suivi partagé. **À doubler par des humains** : avocat, expert-comptable, développeur senior pour la relecture des paiements.

### R10. Décisions prises (30 septembre 2026)
- **Modèle : plan B (commission)** retenu. Pas d'abonnement obligatoire ; la section 4.1 (abonnements, relances de renouvellement) est abandonnée.
- **Société basée au Bénin** : zone UEMOA, XOF, régulation BCEAO. Stripe indisponible pour une société béninoise → partenaires candidats FedaPay, KkiaPay, CinetPay (à comparer sur séquestre, reversements, cartes internationales, frais). Structure de l'encaissement pour compte de tiers à valider par un avocat spécialisé BCEAO.
- **Équipe d'agents créée** : 20 agents dans `.claude/agents/studio-*.md`, charte commune `docs/saas-createurs/EQUIPE.md`, journal `docs/saas-createurs/suivi/JOURNAL.md`, suivi automatique du temps par hook (`.claude/logs/agents.jsonl`, synthèse : `python3 docs/saas-createurs/suivi/temps.py`).

### R9. Décisions à prendre (remplace la section 14)
1. Nom et domaine. 2. Modèle : A ou B (recommandé). 3. Pays de la société (décide du partenaire de paiement). 4. Taux et paliers définitifs. 5. Langues du lancement. 6. Pile technique. 7. Dépôt dédié. 8. Offre clé en main.

---

## 0. Ce que j'ai compris du projet

**Aujourd'hui** tu as une *coquille* : une vitrine premium (Concept Pub) avec six briques visibles mais sans moteur :

| Brique de la maquette | Ce qu'elle simule | Ce qui manque (le « cœur ») |
|---|---|---|
| Hero + prestations + réalisations | Vitrine / portfolio | Contenu éditable, médias réels, SEO, domaine |
| Méthode (4 étapes) | Process de travail | Pipeline de projet réel, étapes suivies |
| **Devis instantané** (9 prestations, quantité, options, délai, prix animé) | Estimation live | Moteur de prix côté serveur, enregistrement, envoi, validation, paiement |
| **Rendez-vous** (7 jours, créneaux, visio/studio) | Réservation | Disponibilités réelles, agenda, lien visio, rappels |
| **Espace client** (connexion, commandes en cours / livrées / devis) | Suivi client | Authentification, projets, validations, fichiers, factures |
| Footer contact | Contact | Messagerie, WhatsApp, e-mail |

**Ce que tu veux** : transformer cette coquille en **plateforme multi-comptes (SaaS)**. Un graphiste, monteur, motion designer, vidéaste, photographe ou une agence de com :

1. s'inscrit et paie un abonnement mensuel ;
2. obtient **son propre espace créateur** (back-office) ;
3. configure **sa vitrine** (logo, couleurs, textes, ordre des sections, portfolio, prestations et prix) ;
4. publie sa vitrine sur une adresse à lui (`sonstudio.plateforme.com` ou `sonstudio.com`) — trouvable sur Google ;
5. ses clients y **estiment un devis en direct**, **prennent rendez-vous**, **valident et paient**, puis **suivent leurs projets** dans un **espace client** où ils récupèrent livrables et factures.

L'analogie Chariow est juste : Chariow = « boutique clé en main pour vendre des **produits** digitaux ». Toi = « studio clé en main pour vendre des **prestations** créatives ». La différence clé : un produit se livre instantanément, une prestation se **fabrique** (brief → direction → production → livraison), d'où l'importance du suivi de projet et des validations.

Et deux façons de te rémunérer :
- **Self-service** : le créateur paie l'abonnement et fait tout lui-même ;
- **Clé en main** : il te paie pour que tu (ou ton équipe) configures sa vitrine, ses prix, son portfolio.

---

## 1. Les 5 espaces de la plateforme

```
                     ┌──────────────────────────────────────────┐
                     │  1. SITE MARKETING DU SaaS               │
                     │  plateforme.com — offres, tarifs, inscr. │
                     └──────────────┬───────────────────────────┘
                                    │ inscription + paiement
                                    ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│ 5. SUPER-ADMIN (toi) │◄──│ 2. ESPACE CRÉATEUR (back-office) │
│ admin.plateforme.com │   │ app.plateforme.com               │
└──────────────────────┘   │ vitrine, devis, projets, factures│
                           └──────────────┬───────────────────┘
                                          │ publie
                                          ▼
                           ┌──────────────────────────────────┐
                           │ 3. VITRINE PUBLIQUE DU CRÉATEUR  │
                           │ studio.plateforme.com / domaine  │
                           │ portfolio · devis · RDV · contact│
                           └──────────────┬───────────────────┘
                                          │ le visiteur devient client
                                          ▼
                           ┌──────────────────────────────────┐
                           │ 4. ESPACE CLIENT (du créateur)   │
                           │ studio.plateforme.com/espace     │
                           │ projets · validations · fichiers │
                           └──────────────────────────────────┘
```

Un seul code, une seule base de données : chaque créateur est un **« tenant »** (locataire) isolé des autres.

---

## 2. Parcours détaillés

### 2.1 Parcours créateur (de l'inscription à la première vente)

1. **Découverte** → site marketing, page tarifs, exemples de vitrines (dont Concept Pub en vitrine de démonstration).
2. **Inscription** → e-mail + mot de passe ou Google, ou numéro WhatsApp + code OTP.
3. **Choix du métier** (graphiste, monteur, motion designer, vidéaste, photographe, agence, podcast…) → pré-remplit prestations, options, étapes de projet et textes adaptés.
4. **Onboarding guidé (≈10 min)**, checklist visible :
   - nom du studio, slogan, logo, couleur d'accent, police (paires validées) ;
   - choix d'un template (Concept Pub = template n°1 « Maison ») ;
   - 3 prestations minimum avec prix ;
   - 3 réalisations minimum (images/vidéos) ;
   - horaires de rendez-vous ;
   - moyen d'encaissement (Mobile Money / carte / virement) ;
   - informations légales pour factures (raison sociale, IFU/RCCM, adresse, TVA oui/non).
5. **Essai gratuit 14 jours** (vitrine publiée sur sous-domaine) → **paiement abonnement** avant fin d'essai.
6. **Publication** → sous-domaine immédiat ; domaine perso en option (plan Pro+).
7. **Premier devis reçu** → notification e-mail + WhatsApp + push.

### 2.2 Parcours client final (sur la vitrine du créateur)

1. Arrive via Google, Instagram, TikTok, WhatsApp, annuaire de la plateforme.
2. Parcourt portfolio et prestations.
3. **Configure un devis** : prestation → quantité/durée → options → délai → brief (+ pièces jointes) → prix affiché en direct.
4. Clique « Valider et envoyer » → saisit nom + e-mail/WhatsApp → **compte client créé automatiquement** (lien magique, pas de mot de passe à retenir).
5. Le créateur confirme (ou ajuste) le devis sous 24 h → le client reçoit le **devis officiel PDF** + bouton « Accepter et payer l'acompte ».
6. Acceptation = signature électronique simple (case + nom + horodatage + IP) → paiement de l'acompte (ex. 50 %) en Mobile Money ou carte.
7. Le projet démarre → le client suit les étapes dans son **espace client**.
8. Étape « Direction » → le client **valide une piste** ou commente (annotations sur image, commentaires minutés sur vidéo).
9. Livraison → aperçus filigranés visibles → paiement du solde → **fichiers HD débloqués** + facture finale.
10. Après livraison → demande d'avis, proposition de « racheter avec le même brief ».

Alternative : le client peut **prendre rendez-vous** (visio ou studio) à tout moment, notamment juste après avoir vu son estimation.

### 2.3 Parcours toi (super-admin)

Voir les créateurs, leur plan, statut de paiement, MRR, résiliations ; suspendre/réactiver ; se connecter « en tant que » un créateur pour le support (journalisé) ; gérer les plans, templates, codes promo, annuaire ; traiter les demandes « clé en main ».

---

## 3. Fonctionnalités détaillées par espace

### 3.1 Espace créateur (back-office)

**Tableau de bord** : devis en attente, projets en cours, validations attendues, RDV du jour, encaissé ce mois, taux de conversion devis → commande, visites de la vitrine.

**Éditeur de vitrine (builder)**
- Approche **par sections** (pas de glisser-déposer pixel libre — trop fragile et casse le rendu premium) : chaque section a un schéma de champs éditables. Ta maquette `VitrineStudio.dc.html` suit déjà cette logique (`data-props` : `studioName`, `currency`…).
- Bibliothèque de sections (reprises de la maquette) : Navigation · Hero (mot qui tourne) · Bandeau défilant · Le studio (chiffres clés) · Prestations · Réalisations (défilement horizontal) · Méthode · Devis instantané · Rendez-vous · Espace client · Témoignages · FAQ · Équipe · Contact · Footer.
- Actions : **réordonner** (glisser les blocs), masquer/afficher, dupliquer, éditer le contenu en place, choisir une variante de section.
- Thème : logo, favicon, couleur d'accent (contraste vérifié automatiquement), fond clair/sombre, paire de polices, arrondis, intensité des animations.
- **Brouillon / Publier**, historique des versions, retour arrière, aperçu mobile/tablette/desktop.
- SEO par page : titre, description, image de partage générée automatiquement.
- Pages additionnelles : mentions légales, CGV (modèles fournis), page projet détaillée par réalisation.

**Portfolio** : upload images/vidéos (glisser-déposer, gros fichiers en reprise), catégories, projet détaillé (contexte, client, livrables, crédits), mise en avant, ordre, vidéos lues en streaming adaptatif.

**Catalogue & moteur de devis** (généralisation du `vitrine.js`)
- Prestation : nom, description, délai indicatif, visuel, **règle de prix** :
  - forfait fixe ;
  - prix par unité (visuels, photos, publications) avec **paliers dégressifs** ;
  - prix selon durée (secondes de film, jours de tournage) ;
  - courbe « base × facteur » comme la maquette (`base × (0,72 + u × 0,95)`) ;
  - prix minimum, prix « à partir de », ou « sur devis » (pas de prix affiché).
- Options : montant fixe ou % (sous-titres, voix off, étalonnage, musique, déclinaisons, sources ouvertes…).
- Délais : multiplicateurs (standard ×1, accéléré ×1,25, express ×1,6).
- Remises : codes promo, remise volume, remise client fidèle.
- Taxes : TVA configurable (ex. 18 % UEMOA), HT/TTC.
- Paramètres : devise (FCFA XOF/XAF, €, $), marge de fourchette (« à 10 % près »), durée de validité (30 j), acompte (%), nombre de retouches incluses.
- **Le prix est toujours recalculé côté serveur** et figé (« snapshot ») dans le devis : un client ne peut pas trafiquer le montant.

**Devis & commandes (pipeline)** : colonnes Kanban — Nouveau · À confirmer · Envoyé · Accepté · En production · Validation · Livré · Payé · Archivé. Le créateur peut ajuster lignes et prix avant envoi, ajouter des lignes libres.

**Projets** : modèle d'étapes par prestation (Brief → Direction → Production → Livraison, personnalisable), tâches internes, échéances, compteur de retouches, livrables versionnés (v1, v2…), fil de discussion avec le client, notes privées.

**Clients (mini-CRM)** : fiche client, historique commandes, montant total, étiquettes, source d'acquisition, export CSV.

**Agenda & rendez-vous** : disponibilités hebdo, pauses, durée et tampon entre RDV, délai minimum de réservation, jours bloqués, types de RDV (découverte 20 min gratuit, consultation payante), lieu (visio auto / studio / chez le client), synchronisation Google Calendar (et Outlook plus tard).

**Facturation** : devis PDF, factures d'acompte / de solde / finale, avoirs, numérotation chronologique sans trou par créateur, mentions légales, relances d'impayés, export comptable (CSV).

**Paiements** : état des encaissements, liens de paiement, historique.

**Automatisations** : liste d'automatisations prêtes à activer (§6) + (plus tard) constructeur « déclencheur → conditions → actions ».

**Équipe (plan Studio)** : membres, rôles (propriétaire, admin, créatif, comptable), attribution des projets.

**Statistiques** : visites, sources, prestations les plus demandées, conversion par étape, chiffre d'affaires.

**Paramètres** : profil, domaine, intégrations (Google, WhatsApp, Zapier/Make/n8n, webhooks), abonnement et factures de la plateforme.

### 3.2 Vitrine publique

Rendu serveur (rapide et lisible par Google), fidèle au design system (ivoire / noir / or, Cormorant + Manrope + Plex Mono, animations « expo-out », `prefers-reduced-motion` respecté). Sections actives dans l'ordre défini par le créateur. Formulaires devis/RDV connectés au back-office. Bouton WhatsApp flottant optionnel. Badge « Propulsé par Studio OS » sur le plan gratuit (acquisition virale).

### 3.3 Espace client

- Connexion par **lien magique** e-mail ou **code WhatsApp** (pas de mot de passe) ; un compte par créateur (le client d'un studio n'est pas visible par un autre).
- Onglets de la maquette : **En cours · Livrées · Devis**, + Factures, Rendez-vous, Messages.
- Carte projet : référence, statut, barre d'avancement, étape, prix, action principale (« Valider une piste », « Payer l'acompte », « Télécharger »…).
- **Validation** : approuver en un clic ou demander une retouche avec annotations (point sur l'image, commentaire à 00:12 sur la vidéo). Le compteur « 2 retouches incluses » est visible.
- **Fichiers** : aperçus filigranés avant paiement du solde, HD après ; téléchargement par format ; disponibilité 90 jours (configurable) avec rappel avant expiration.
- **Racheter** une prestation passée avec le même brief.
- Payer en ligne, télécharger ses factures, laisser un avis.

### 3.4 Super-admin

Créateurs (recherche, plan, statut, dernière activité) · revenus (MRR, ARR, churn, LTV) · paiements et relances de la plateforme · plans et fonctionnalités par plan · templates et sections · annuaire (modération) · support (« se connecter en tant que », journal d'audit) · demandes « clé en main » · annonces et changelog · drapeaux de fonctionnalités.

---

## 4. Paiements — les deux flux d'argent

Il y a **deux circuits bien distincts** à ne jamais mélanger.

### 4.1 Flux A — Le créateur te paie son abonnement (revenu de la plateforme)

**Offres (hypothèses de départ, en FCFA)**

| | Découverte | Pro | Studio | Clé en main |
|---|---|---|---|---|
| Prix | 0 | 9 900 / mois | 24 900 / mois | Frais d'installation unique (ex. 75 000 – 250 000) + un abonnement |
| Vitrine | sous-domaine, badge plateforme | domaine perso, sans badge | multi-pages, templates premium | faite par toi |
| Portfolio | 10 éléments | illimité | illimité | importé par toi |
| Devis / mois | 5 | illimité | illimité | — |
| Espace client, RDV, factures | limité | ✔ | ✔ | ✔ |
| Stockage | 2 Go | 50 Go | 300 Go | selon plan |
| Automatisations | essentielles | toutes les standard | + constructeur, WhatsApp | ✔ |
| Équipe | 1 | 1 | 5 membres | ✔ |
| Commission sur paiements clients (si encaissés par la plateforme, V2) | 5 % | 2 % | 0 % | — |

Annuel = 2 mois offerts (réduit fortement le risque de non-renouvellement Mobile Money).

**Moyens de paiement (Afrique de l'Ouest + international)**
- **Mobile Money** (MTN MoMo, Moov Money, Orange Money, Wave, Celtiis…) et **cartes** via un agrégateur local : **FedaPay** ou **KkiaPay** (Bénin, UEMOA), **CinetPay** (UEMOA + CEMAC), **Paystack** (Côte d'Ivoire, Ghana, Nigeria, Kenya).
- **Stripe** pour les cartes internationales si tu disposes d'une entité dans un pays supporté (Stripe n'ouvre pas de compte marchand au Bénin).
- Le code passe par une **couche d'abstraction `PaymentProvider`** (créer un paiement, vérifier, rembourser, recevoir un webhook) : on commence avec un agrégateur, on en ajoute sans réécrire.

**Point important — le prélèvement automatique** : le Mobile Money ne permet généralement pas de débiter automatiquement chaque mois. Le renouvellement fonctionne donc ainsi :

```
J-7  e-mail + WhatsApp : « Votre abonnement se renouvelle le … » + lien de paiement
J-3  rappel
J0   facture émise + lien de paiement (carte enregistrée débitée si Stripe/Paystack)
J+1..J+7  période de grâce : bandeau d'alerte dans l'espace créateur, relances J+1, J+3, J+6
J+8  vitrine en lecture seule (reste en ligne, formulaires devis/RDV désactivés)
J+30 vitrine masquée (données conservées 90 j), e-mail de réactivation
Paiement à tout moment → réactivation instantanée
```

### 4.2 Flux B — Le client final paie le créateur

**Échéancier par défaut** (paramétrable) : acompte 50 % à l'acceptation du devis → solde à la livraison (ou 30/40/30 pour les gros projets). Les fichiers HD ne se débloquent qu'après paiement complet.

**Deux modèles, à mettre en place dans cet ordre :**

**V1 — « Compte du créateur » (recommandé pour démarrer)**
Le créateur connecte **son propre compte** FedaPay / KkiaPay / CinetPay / Paystack (il colle ses clés API, stockées chiffrées). L'argent va **directement** chez lui. La plateforme ne touche jamais les fonds → pas de licence d'établissement de paiement, pas de gestion de reversements, pas de risque de fraude sur ta trésorerie. Pour ceux qui n'ont pas de compte : **paiement manuel** (numéro Mobile Money / RIB affiché + le client téléverse la preuve, le créateur confirme).

**V2 — « Encaissement par la plateforme » (comme Chariow)**
La plateforme encaisse pour le compte du créateur, prélève une commission, et **reverse** (hebdomadaire ou à la demande) via l'API de transfert de l'agrégateur. Nécessite : KYC des créateurs (pièce d'identité, IFU/RCCM), conformité (agrément ou contrat de marketplace avec l'agrégateur), gestion des litiges/remboursements, tableau « reversements ». À lancer quand le volume le justifie.

**Chaîne technique d'un paiement (identique pour A et B)**

```
Client clique « Payer l'acompte »
  → serveur crée un Payment (statut: pending, montant recalculé, clé d'idempotence)
  → redirection vers la page de paiement de l'agrégateur (ou widget)
  → client paie en Mobile Money (confirmation sur son téléphone)
  → l'agrégateur appelle notre WEBHOOK  ← source de vérité, jamais la redirection
      • vérification de la signature
      • dédoublonnage (même événement reçu deux fois = traité une fois)
      • re-vérification du statut via l'API de l'agrégateur
  → Payment = succeeded → Facture = payée → reçu PDF → événement « payment.succeeded »
  → les automatisations prennent le relais (projet démarre, notifications…)
Tâche de réconciliation toutes les 15 min : paiements « pending » > 30 min → vérifiés via l'API.
```

### 4.3 Facturation et conformité

- Montants stockés en **entiers** (plus petite unité de la devise) — jamais de nombres à virgule flottante.
- Numérotation **séquentielle sans trou** par créateur et par type (`F-2026-0001`, `D-2026-0001`, `AV-…`).
- Une facture émise n'est **jamais modifiée** : on corrige par un avoir.
- Mentions : identité et identifiants légaux du créateur (IFU, RCCM), client, date, lignes, HT/TVA/TTC, conditions de paiement, pénalités.
- **Bénin** : les entreprises assujetties à la TVA doivent émettre des factures normalisées (système e-MECeF de la DGI) — prévoir une intégration optionnelle en V2 (**à vérifier avec un comptable**). Même logique à étudier pour d'autres pays (Côte d'Ivoire FNE, etc.).
- Les factures de **ton** abonnement (flux A) sont émises par ta structure, séparément.

---

## 5. Architecture technique

### 5.1 Choix de la pile (recommandation)

| Besoin | Choix recommandé | Pourquoi |
|---|---|---|
| Application web (marketing, back-office, vitrines, espace client) | **Next.js (App Router) + TypeScript** | Rendu serveur = SEO des vitrines ; une seule base de code ; écosystème React (ta maquette a déjà des composants React) |
| Style | **Tailwind CSS** alimenté par les **tokens du design system Concept Pub** + composants React portés (Button, Card, Badge, Input, Tabs, Dialog, Toast…) | Rendu identique à la maquette, thème variable par créateur via variables CSS |
| Base de données + authentification + temps réel | **Supabase** (PostgreSQL, Auth, Row Level Security, Realtime) | Isolation des tenants au niveau base, magic link/OTP intégrés, tu as déjà le connecteur |
| Fichiers lourds (rushes, exports vidéo, sources) | **Cloudflare R2** (compatible S3) | Pas de frais de sortie de données — crucial pour la vidéo |
| Vidéos du portfolio et aperçus | **Cloudflare Stream** ou **Mux** | Streaming adaptatif, miniatures, filigrane |
| Images | Optimisation Next/Image ou Cloudflare Images | Portfolio rapide |
| Tâches de fond & automatisations | **Inngest** ou **Trigger.dev** | Files d'attente, relances planifiées, reprises automatiques |
| E-mails transactionnels | **Resend** + React Email | Modèles aux couleurs du créateur |
| WhatsApp | **WhatsApp Business Cloud API** (Meta) | Canal n°1 en Afrique de l'Ouest |
| PDF (devis, factures) | Génération serveur (React-PDF ou Chromium) | Rendu fidèle, archivé |
| Hébergement | **Vercel** (domaines génériques `*.plateforme.com` + API domaines perso) | SSL automatique pour chaque domaine créateur |
| Paiements | Couche `PaymentProvider` : FedaPay/KkiaPay/CinetPay → Paystack → Stripe | §4 |
| Agenda | Google Calendar API (+ lien Google Meet), Zoom en option | §3.1 |
| Observabilité | Sentry (erreurs), journaux structurés, PostHog (analytique produit) | Détecter les pannes avant les clients |

*Alternative si tu préfères Python (le dépôt actuel contient du FastAPI)* : back-end FastAPI + front Next.js. Plus de pièces à maintenir ; je recommande le « tout Next.js + Supabase » pour aller vite en solo.

### 5.2 Routage multi-tenant

```
plateforme.com            → site marketing
app.plateforme.com        → espace créateur
admin.plateforme.com      → super-admin
{slug}.plateforme.com     → vitrine du créateur
{slug}.plateforme.com/espace → espace client du créateur
sonstudio.com (CNAME)     → même vitrine, domaine perso
```

Un *middleware* lit le nom de domaine de chaque requête, retrouve le tenant (cache), et sert la bonne vitrine. Chaque ligne de données porte un `tenant_id` et les **règles RLS** de PostgreSQL empêchent physiquement un créateur (ou un client) de lire les données d'un autre.

### 5.3 Organisation du code (monorepo)

```
apps/
  web/                 Next.js : marketing, app créateur, vitrines, espace client, admin
packages/
  ui/                  design system (tokens + composants React portés de la maquette)
  sections/            sections de vitrine (Hero, Prestations, Devis…) + leur schéma de champs
  pricing/             moteur de prix pur TypeScript, 100 % testé
  payments/            adaptateurs FedaPay / KkiaPay / CinetPay / Paystack / Stripe
  db/                  schéma, migrations, politiques RLS, types générés
  emails/              modèles e-mail et WhatsApp
  automations/         définitions des workflows (Inngest/Trigger.dev)
```

### 5.4 Modèle de données (principales tables)

```
── Plateforme ─────────────────────────────────────────────
plans(id, code, price, interval, limits jsonb, features jsonb)
tenants(id, slug, name, status[trial|active|past_due|read_only|suspended], plan_id,
        trial_ends_at, country, currency, legal jsonb, created_at)
tenant_members(tenant_id, user_id, role[owner|admin|creative|accounting])
subscriptions(id, tenant_id, plan_id, status, current_period_end, provider, provider_ref)
platform_invoices(id, tenant_id, number, amount, status, paid_at)
domains(id, tenant_id, hostname, verified, ssl_status)

── Vitrine ────────────────────────────────────────────────
sites(id, tenant_id, template, theme jsonb, published_version_id)
site_versions(id, site_id, sections jsonb, created_by, published_at)   -- brouillons & historique
pages(id, site_id, slug, seo jsonb, sections jsonb)
portfolio_items(id, tenant_id, title, category, cover_media_id, body jsonb, featured, position)
media(id, tenant_id, kind[image|video|file], storage_key, stream_id, size, width, height, duration)
testimonials(id, tenant_id, client_id, rating, text, approved)

── Catalogue & devis ──────────────────────────────────────
services(id, tenant_id, name, description, lead_time, pricing_rule jsonb, active, position)
service_options(id, tenant_id, service_id?, name, kind[fixed|percent], value)
delay_tiers(id, tenant_id, name, note, multiplier)
discount_codes(id, tenant_id, code, kind, value, limits jsonb)
quotes(id, tenant_id, client_id, number, status[draft|submitted|sent|accepted|declined|expired],
       config_snapshot jsonb, lines jsonb, subtotal, tax, total, currency, valid_until,
       accepted_at, accepted_ip, accepted_name)

── Clients, projets, livrables ────────────────────────────
clients(id, tenant_id, name, company, email, phone, whatsapp, tags, source)
client_users(id, client_id, auth_user_id)       -- accès à l'espace client
projects(id, tenant_id, client_id, quote_id, ref, title, status, current_step,
         progress, revisions_included, revisions_used, due_at)
project_steps(id, project_id, name, position, status, started_at, done_at)
deliverables(id, project_id, step_id, version, media_id, watermarked_media_id,
             status[pending_review|approved|changes_requested], expires_at)
review_comments(id, deliverable_id, author, body, x, y, timecode, resolved)
messages(id, project_id, author_type[creator|client], body, attachments)

── Agenda ─────────────────────────────────────────────────
availability_rules(id, tenant_id, weekday, start, end, buffer_min, slot_min)
appointment_types(id, tenant_id, name, duration, mode[visio|studio|onsite], price)
appointments(id, tenant_id, client_id, type_id, starts_at, ends_at, mode,
             meeting_url, status[booked|confirmed|cancelled|no_show|done], gcal_event_id)

── Argent ─────────────────────────────────────────────────
invoices(id, tenant_id, client_id, project_id, number, kind[deposit|balance|final|credit],
         lines jsonb, subtotal, tax, total, status[issued|paid|overdue|void], pdf_key, issued_at)
payments(id, tenant_id, invoice_id, provider, provider_ref, amount, currency,
         status[pending|succeeded|failed|refunded], idempotency_key, raw jsonb)
payment_provider_accounts(id, tenant_id, provider, encrypted_keys, mode[test|live])
payouts(id, tenant_id, amount, status, provider_ref)           -- V2 uniquement
webhook_events(id, provider, event_id UNIQUE, payload, processed_at)

── Transverse ─────────────────────────────────────────────
automations(id, tenant_id, key, enabled, settings jsonb)       -- prêtes à activer
automation_runs(id, automation_id, event, status, log)
notifications(id, recipient, channel[email|whatsapp|push|in_app], template, status)
outgoing_webhooks(id, tenant_id, url, events[], secret)
analytics_events(id, tenant_id, type, props, created_at)
audit_logs(id, actor, tenant_id, action, target, ip, created_at)
```

### 5.5 Événements internes (le « système nerveux »)

Chaque action métier émet un événement ; automatisations, notifications, statistiques et webhooks sortants s'y abonnent :

`quote.submitted · quote.sent · quote.accepted · quote.expired · invoice.issued · payment.succeeded · payment.failed · project.step_changed · deliverable.uploaded · deliverable.approved · deliverable.changes_requested · project.delivered · appointment.booked · appointment.reminder_due · client.created · testimonial.submitted · subscription.renewal_due · subscription.past_due · subscription.reactivated`

---

## 6. Automatisations (prêtes à activer, réglables par le créateur)

| # | Déclencheur | Actions automatiques |
|---|---|---|
| 1 | Devis soumis par un visiteur | Fiche client créée · accusé de réception au client (e-mail/WhatsApp) avec lien vers son espace · alerte au créateur · tâche « confirmer sous 24 h » |
| 2 | Devis non confirmé par le créateur après 20 h | Rappel au créateur |
| 3 | Devis envoyé, non accepté | Relance client J+2 et J+5 · expiration à J+30 · proposition de RDV |
| 4 | Devis accepté | Facture d'acompte + lien de paiement · projet créé avec les étapes du modèle de la prestation |
| 5 | Acompte payé | Reçu PDF · projet → « En production » · notification créateur · date de livraison estimée calculée |
| 6 | Changement d'étape | Notification au client avec résumé |
| 7 | Livrable déposé pour validation | Aperçu filigrané généré · client notifié · relance J+3 · validation tacite après X jours (option) |
| 8 | Retouche demandée | Compteur décrémenté · si quota dépassé → devis complémentaire proposé automatiquement |
| 9 | Livraison finale | Facture de solde + lien de paiement · relances J+3, J+7, J+14 |
| 10 | Solde payé | Fichiers HD débloqués · facture finale · projet « Livré » |
| 11 | Livré + 3 jours | Demande d'avis (publié sur la vitrine après approbation du créateur) |
| 12 | Livré + 60 jours | Suggestion de « racheter avec le même brief » |
| 13 | Fichiers expirent dans 7 jours | Rappel au client |
| 14 | RDV réservé | Confirmation + invitation calendrier + lien visio · rappels J-1 et H-1 · lien annuler/déplacer |
| 15 | RDV terminé | Suivi « voici votre devis » ou « no-show » |
| 16 | Onboarding créateur | E-mails J+1, J+3, J+7 selon la checklist non terminée |
| 17 | Abonnement créateur | Relances J-7/J-3/J0, grâce, lecture seule, réactivation (§4.1) |

**Plus tard (V3)** : constructeur libre « Quand… Si… Alors… » (comme les *workflows* de Chariow), webhooks sortants signés, connecteurs Zapier / Make / n8n.

---

## 7. Connexions et intégrations

| Intégration | Usage | Phase |
|---|---|---|
| Agrégateur Mobile Money (FedaPay ou KkiaPay ou CinetPay) | Abonnements + paiements clients | MVP |
| Resend (e-mail) | Toutes les notifications | MVP |
| Google (connexion + Calendar + Meet) | Connexion rapide, agenda, lien visio | MVP / V2 |
| WhatsApp Business Cloud API | OTP, notifications, relances | V2 |
| Cloudflare R2 + Stream | Fichiers et vidéos | MVP |
| Domaines perso (API Vercel) | `sonstudio.com` | V2 |
| Paystack / Stripe | Cartes, autres pays | V2 |
| Google Business Profile, Meta Pixel, Google Analytics / Search Console | Visibilité et mesure du créateur | V2 |
| Zapier / Make / n8n, webhooks | Connexion aux outils du créateur | V3 |
| e-MECeF (factures normalisées Bénin) | Conformité fiscale | V2–V3 |
| IA (Claude) | Aide à la rédaction des textes de vitrine, reformulation du brief client, description des réalisations, suggestion de prix | V3 |

---

## 8. Visibilité : être trouvé sur Internet

1. **Vitrine rendue côté serveur**, rapide (objectif Lighthouse > 90), `sitemap.xml` et `robots.txt` par créateur.
2. **Données structurées** schema.org : `ProfessionalService`/`LocalBusiness` (nom, ville, zone, avis), `CreativeWork`/`VideoObject` pour les réalisations.
3. **Page par réalisation** et **page par prestation** (« Motion design à Cotonou ») → plus de pages indexées.
4. **Images de partage** générées automatiquement (WhatsApp, Facebook, LinkedIn).
5. **Annuaire public de la plateforme** (`plateforme.com/createurs/motion-design/cotonou`) : chaque créateur y apparaît, filtrable par métier, ville, budget → trafic mutualisé et canal d'acquisition pour eux (et donc raison de rester abonné).
6. Lien avec Google Business Profile et Search Console guidé dans l'onboarding.

---

## 9. Sécurité, données personnelles, fiabilité

- Isolation des tenants par RLS + **tests automatiques d'isolation** (un créateur A tente de lire B → doit échouer).
- Clés API des agrégateurs **chiffrées** (Supabase Vault), jamais renvoyées au navigateur.
- Webhooks : signature vérifiée, dédoublonnage, re-vérification du statut.
- Fichiers privés servis par **URL signées à durée limitée** ; antivirus sur les uploads ; limites de taille par plan.
- Limitation de débit sur formulaires publics (devis, RDV, connexion) + anti-spam (Turnstile).
- Journal d'audit (qui a fait quoi), connexion « en tant que » tracée.
- Sauvegardes quotidiennes + test de restauration mensuel.
- **Données personnelles** : Code du numérique du Bénin (loi 2017-20, autorité APDP), RGPD pour les clients européens. Registre des traitements, politique de confidentialité, CGU plateforme, **contrat de sous-traitance** avec les créateurs (ils sont responsables des données de leurs clients, toi sous-traitant), export et suppression des données sur demande.
- Documents légaux à rédiger : CGU/CGV plateforme, politique de confidentialité, modèles de CGV et mentions légales pour les créateurs.

---

## 10. Feuille de route

Hypothèse : toi + Claude Code en développement, à temps plein. Chaque phase se termine par une version utilisable.

### Phase 0 — Fondations (1–2 semaines)
- Nom définitif, domaine, identité du SaaS (le design system Concept Pub sert de base).
- Création des comptes : Supabase, Vercel, Cloudflare, Resend, agrégateur de paiement (mode test).
- Monorepo, CI (lint, types, tests), environnements dev / préprod / prod.
- Portage du design system en `packages/ui` (tokens → Tailwind, composants React).
- Schéma de base : tenants, membres, plans, RLS.

### Phase 1 — MVP « Concept Pub tourne dessus » (6–8 semaines)
- Inscription, onboarding, essai 14 jours.
- Vitrine : template « Maison » (la maquette), sections réordonnables/masquables, thème, brouillon/publier, sous-domaine.
- Portfolio (images + vidéos en streaming).
- Catalogue + **moteur de devis** serveur + configurateur live sur la vitrine.
- Pipeline devis → projet, étapes, fil de messages.
- Espace client (lien magique) : devis, projets, fichiers.
- RDV simple (disponibilités, réservation, e-mails de confirmation/rappel).
- Automatisations 1, 3, 4, 6, 14.
- Abonnement créateur via Mobile Money + relances + lecture seule.
- Super-admin minimal.
- **Concept Pub = client n°1** (tu l'utilises pour ton propre studio), puis **5–10 créateurs bêta** gratuits contre retours.

### Phase 2 — L'argent et la validation (5–6 semaines)
- Factures PDF conformes, acompte/solde, paiements clients (modèle V1 « compte du créateur » + paiement manuel avec preuve).
- Validation des livrables : annotations image, commentaires minutés vidéo, compteur de retouches, filigrane, déblocage HD après paiement.
- Automatisations 2, 5, 7–13, 15–17.
- WhatsApp (OTP + notifications), Google Calendar + Meet, domaines perso.
- Statistiques créateur ; SEO complet (schema.org, sitemap, pages réalisation/prestation).
- **Lancement public** + offres payantes.

### Phase 3 — Croissance (6 semaines)
- Équipe et rôles (plan Studio).
- 2–3 templates supplémentaires (sombre cinématique, minimal, éditorial) et variantes de sections.
- Annuaire public des créateurs.
- Avis/témoignages, codes promo, parrainage (un créateur parraine un autre → mois offert).
- Constructeur d'automatisations, webhooks sortants, Zapier/Make.
- Paystack / Stripe pour d'autres pays et devises.

### Phase 4 — Plateforme (en continu)
- Encaissement par la plateforme + commissions + reversements (modèle V2), KYC.
- Factures normalisées (e-MECeF), export comptable.
- Application mobile (PWA installable d'abord) pour créateurs et clients.
- Assistant IA (textes de vitrine, brief, prix conseillé).
- API publique, marketplace de templates créés par des designers.

---

## 11. Correspondance avec Chariow (pour s'inspirer sans copier)

| Chariow (produits digitaux) | Studio OS (prestations créatives) |
|---|---|
| Boutique (store) | Vitrine |
| Produits | Prestations + règles de prix |
| Ventes | Devis → projets → factures |
| Clients | Clients (mini-CRM) + espace client |
| Workflows | Automatisations |
| Pulses (webhooks) | Webhooks sortants |
| Codes promo | Codes promo |
| Affiliés | Parrainage + apporteurs d'affaires |
| Règlements / reversements | Reversements (V2) |
| Avis | Témoignages |
| Popups / bannières | Sections promotionnelles de vitrine |
| — | **Pipeline de production, validations avec annotations, livrables versionnés, rendez-vous** (ce qui te différencie) |

---

## 12. Indicateurs à suivre

- **Activation** : % d'inscrits qui publient leur vitrine en 7 jours (objectif > 40 %).
- **Valeur** : devis reçus par vitrine et par mois ; taux devis → commande payée.
- **Revenu** : MRR, conversion essai → payant (objectif > 15 %), taux de renouvellement Mobile Money, churn mensuel (< 5 %).
- **Qualité** : temps de chargement des vitrines, taux d'échec des paiements, incidents.

---

## 13. Risques et parades

| Risque | Parade |
|---|---|
| Renouvellements Mobile Money oubliés → churn | Relances multi-canal, période de grâce, offre annuelle attractive, lecture seule plutôt que coupure |
| Coût du stockage/streaming vidéo | R2 sans frais de sortie, quotas par plan, expiration des fichiers livrés, compression |
| Builder trop complexe / vitrines laides | Sections contraintes par le design system, contraste vérifié, templates soignés |
| Fraude / litiges paiement | V1 sans détention de fonds ; V2 avec KYC et réserve |
| Fuite de données entre créateurs | RLS + tests d'isolation automatisés dans la CI |
| Portée trop large pour un démarrage solo | MVP strict (Phase 1), dogfooding Concept Pub, bêta fermée |
| Réglementation fiscale / paiement | Validation par un comptable et un juriste avant la Phase 2 |

---

## 14. Décisions à trancher avant de coder

1. **Nom** du SaaS et domaine.
2. **Pays de lancement** (Bénin seul ? UEMOA ?) et devises → choix de l'agrégateur (FedaPay vs KkiaPay vs CinetPay).
3. **Structure juridique** qui encaisse les abonnements (et éventuellement Stripe via une entité étrangère).
4. **Grille tarifaire** définitive (le tableau §4.1 est une proposition).
5. **Pile technique** : « tout Next.js + Supabase » (recommandé) ou FastAPI + Next.js.
6. **Dépôt** : nouveau dépôt dédié (recommandé) ou dossier dans ce dépôt.
7. Offre **clé en main** : prix, ce qui est inclus, délai de mise en ligne.

Une fois ces points validés, on attaque la Phase 0.
