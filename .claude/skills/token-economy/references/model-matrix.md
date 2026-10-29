# Matrice — le modèle le plus rentable par tâche

**Principe directeur :** choisir le modèle **le moins cher qui fait la tâche à 100 %**. Démarrer bas, escalader seulement sur échec réel. « Opus par défaut » est l'erreur n°1.

**Coût relatif** (ordre de grandeur — vérifier les prix courants via le skill `/claude-api`) : **Opus ≫ Sonnet ≫ Haiku**. Typiquement Sonnet ≈ 1/5 d'Opus, Haiku ≈ 1/4 de Sonnet. Donc une tâche faite en Haiku au lieu d'Opus coûte ~20× moins.

## Table tâche → modèle

| Catégorie | Exemples | Modèle visé |
|---|---|---|
| **Mécanique / lecture** | recherche web, résumer un doc, extraire/classer, trier des fichiers, trier des logs, lint, renommage, formatage, traduction simple, boilerplate évident | **Haiku** |
| **Standard (défaut agentic coding)** | écrire/éditer du code applicatif, refactor courant, écrire des tests, revue de code standard, debug habituel, rédaction de contenu, conception d'écran, plan de tâches / orchestration | **Sonnet** |
| **Raisonnement difficile & fort enjeu** | architecture système à contraintes multiples, arbitrage délicat, bug retors non résolu par Sonnet, jugement final de qualité (design/sécurité/juridique/paiements) | **Opus** |

## Protocole de qualification (à appliquer par tâche ET par agent)
1. **Qualifier** la tâche : mécanique / standard / difficile-à-enjeu.
2. **Prendre le moins cher plausible** de la table.
3. **Vérifier le résultat.** S'il est faux/incomplet après 1-2 essais → **escalader d'un cran** (Haiku→Sonnet, Sonnet→Opus), pas directement au sommet.
4. **Par agent** : régler `model:` sur le plus bas qui tient le poste. Garder Opus seulement pour les postes de jugement/risque.
5. **Mesurer & ajuster** : si un agent Sonnet échoue souvent sur un type de tâche, soit on l'escalade pour CE type, soit (souvent mieux et moins cher) on améliore son brief / ses références.

## Signaux « tu paies trop cher »
- Opus réglé « par défaut » sur des agents à fort volume.
- Opus utilisé pour de la recherche, de la lecture ou du tri.
- Un seul gros modèle pour absolument tout.
- Un agent qui relit tout le repo à chaque tâche (voir règle 2 : mémoire de session).

## Repère concret (Studio OS)
Opus gardé pour le jugement/risque : directeur artistique, architecte, juriste, paiements, relecteur-code, sécurité. Sonnet pour le volume : designer, front-end, chef de projet, back-end, QA, etc. Haiku pour les agents de recherche/tri si on en ajoute.
