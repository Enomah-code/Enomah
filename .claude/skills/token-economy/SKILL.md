---
name: token-economy
description: "Réduire la consommation de tokens / quota en agentic coding sans perdre en efficacité. À utiliser quand l'utilisateur dit que ses sessions coûtent trop cher, qu'il épuise son quota Claude (hebdomadaire/Pro) trop vite, que l'agentic coding « aspire » ses tokens, qu'il a trop d'agents qui re-cherchent tout à chaque reprise, ou qu'il veut organiser/optimiser ses sessions pour économiser. Déclencheurs : économiser tokens, réduire conso, quota épuisé, trop cher, token economy, cost optimization, context management, mémoire de session, reprise de session."
---

# Économie de tokens — sessions efficaces

But : même travail, beaucoup moins de tokens. Un token n'est pas gratuit : **tout ce qui entre dans le contexte à chaque tour est refacturé à chaque tour**. On réduit donc ce qui entre, pas la qualité.

## Diagnostic — d'où partent les tokens (par ordre d'impact)
1. **Le modèle.** Opus coûte ~5× Sonnet et ~25× Haiku par token. Un agent Opus qui tourne en boucle vide un quota Pro en heures.
2. **Le fan-out d'agents.** N agents qui démarrent chacun en lisant les mêmes gros docs = N × (gros contexte). 25 agents = 25 fois la facture de lecture.
3. **La re-lecture à chaque reprise.** Reprendre une session en re-scannant tout le repo / tous les agents « pour retrouver où on en est » recharge un énorme contexte à chaque fois.
4. **Les grosses sorties d'outils.** Un `list`/`cat`/log de 80 000 caractères entre dans le contexte et y reste.
5. **Le transcript qui gonfle.** Une session fourre-tout de 2h traîne tout son historique à chaque tour.

## Les 6 règles d'or

### 1. Le bon modèle pour la bonne tâche (gain n°1)
- **Haiku** : recherche, tri, lecture/résumé, lint, extraction, tâches mécaniques.
- **Sonnet** : défaut pour presque tout l'agentic coding (écriture de code, refactor, revue).
- **Opus** : réservé au raisonnement vraiment difficile (architecture, arbitrage délicat). Pas « par défaut ».
- Dans Claude Code : régler le modèle **par sous-agent** (frontmatter `model:` d'un agent, ou choix du modèle du sous-agent). Repasser en revue les agents « tout Opus » : c'est souvent 70 % d'économie immédiate.
- **Règle de qualification (le moins cher qui fait la tâche à 100 %)** : pour CHAQUE tâche, se demander — est-ce *mécanique* (→ Haiku), *standard* (→ Sonnet), ou *raisonnement difficile à fort enjeu* (→ Opus) ? Prendre le moins cher plausible, puis **escalader d'un seul cran** seulement si le résultat est faux/incomplet après 1-2 essais — jamais sauter directement à Opus « par sécurité ». La matrice détaillée tâche → modèle est dans `references/model-matrix.md` (prix courants à vérifier via `/claude-api`).

### 2. Une mémoire-graphe compacte (tuer la re-recherche) — gain n°2
La mémoire du projet ne doit **jamais** vivre dans le fil de chat (qui est jetable et refacturé en entier à chaque tour) : elle vit dans des **fichiers sur GitHub**, organisés en **graphe**.
- **Le tronc** : un `INDEX.md` (≤ 1 page) qui liste les **branches** (un sujet = un fichier) avec une ligne de description et un lien vers chacune. C'est la carte.
- **Une branche = un fichier par sujet** (`memoire/<sujet>.md`) : état courant, décisions, « où trouver quoi », prochaines étapes, et **liens vers les branches liées** (les arêtes du graphe).
- **Au démarrage / à la reprise** : lire l'`INDEX`, puis **UNIQUEMENT la branche** qui concerne la question (et un lien seulement si nécessaire). Jamais tout le repo, jamais tout l'historique.
- **Après un changement** : mettre à jour **seulement la branche touchée** (5-10 lignes), + un lien si une nouvelle relation apparaît.
- Détails et gabarits : `references/memoire-graphe.md`. (Un `SESSION-STATE.md` à plat reste acceptable pour un tout petit projet ; dès que ça couvre plusieurs sujets, passer au graphe.)
- Résultat : on retrouve toujours **où est tel sujet** (une branche nommée, pas 5 sessions éparpillées), et on ne recharge que la branche utile.

### 3. Lectures ciblées, jamais « lis tout »
- `Grep`/`Glob` pour localiser, puis lire **une tranche** (offset/limit), pas le fichier entier.
- Bannir les consignes d'agent du type « avant toute tâche, lis docA + docB + docC » en entier : les remplacer par « lis `SESSION-STATE.md`, puis la section précise dont tu as besoin ».
- Un **index** (où trouver quoi) coûte 20 lignes ; re-scanner pour le reconstruire coûte des milliers de tokens.

### 4. Moins d'agents, mieux briefés
- N'ouvrir un sous-agent que si la tâche le justifie vraiment. 2 bons agents > 10 agents qui se marchent dessus.
- Donner à chaque agent un **brief compact** (le strict nécessaire), pas tout le contexte du projet.
- Le superviseur passe un **plan de délégation** avec le contexte minimal par agent.

### 5. Maîtriser les sorties d'outils
- Paginer / `head` / filtrer au lieu de tout déverser. Résumer une grosse sortie au lieu de la recoller.
- Ne jamais recopier un gros bloc déjà affiché.

### 6. Hygiène de session
- **Une session = un sujet.** Ne pas enchaîner 5 chantiers différents dans le même fil.
- `/compact` dès que le contexte gonfle ; `/clear` entre deux sujets sans lien.
- Clore les tâches (pas de boucles ouvertes qui obligent à tout relire).

### 7. La mémoire-graphe remplace la « forêt de sessions » — gain majeur sur la durée
Le plus gros gouffre à long terme : une conversation qui **dure des jours et couvre beaucoup de sujets**. Chaque nouveau message **re-traîne tout l'historique accumulé** → le coût par message ne fait que grimper.

**Le vrai problème n'est pas « une session vs plusieurs » — c'est : où vit la mémoire.** Si elle vit dans le fil de chat, tout est refacturé et on s'éparpille (« où ai-je commencé tel sujet ? »). Si elle vit dans la **mémoire-graphe** (règle 2, sur GitHub), le fil de chat devient **jetable** : la connaissance est ailleurs, permanente et navigable.

**Règle.** On s'appuie sur la **mémoire-graphe**, pas sur la longueur du fil. Pour un sujet X : lire `INDEX.md` → la branche X. Ouvrir une nouvelle session devient **optionnel** (uniquement quand le fil en cours est devenu vraiment lourd), **plus une obligation** à chaque sujet.

**Quand (optionnellement) ouvrir un fil neuf :** quand le fil courant est long/lent/cher. Alors : mettre à jour la branche concernée dans `memoire/`, ouvrir un fil neuf, qui lit `INDEX.md` + la branche — **pas** l'historique. Pas besoin de « mini-brief » séparé : la branche EST le brief.

**Rôle de l'assistant.** Quand un **nouveau grand sujet** apparaît, Claude **crée/met à jour sa branche** dans `memoire/` (pour que ce soit retrouvable), puis continue — sans forcer l'utilisateur à ouvrir une session à chaque fois. Il ne propose un fil neuf que si le fil courant est devenu trop lourd. (Claude ne peut pas forker une session seul ; mais désormais il n'en a plus besoin pour garder la mémoire.)

## Checklist — début de session
- [ ] Lire `memoire/INDEX.md`, puis **seulement la branche** concernée (pas re-scanner tout le repo).
- [ ] Vérifier le modèle : Sonnet par défaut, Haiku pour la recherche, Opus seulement si nécessaire.
- [ ] Charger uniquement les fichiers de la tâche du jour.

## Checklist — fin de session
- [ ] Mettre à jour **la branche touchée** dans `memoire/` (décisions, état, prochaines étapes) — pas tout le repo.
- [ ] Un **nouveau grand sujet** ? Créer/mettre à jour sa **branche** dans `memoire/` (+ l'ajouter à `INDEX.md`) pour qu'il reste retrouvable (règle 7).
- [ ] `/compact` ou `/clear` si le fil est devenu lourd (optionnel — la mémoire est dans le graphe, pas dans le fil).

## Skills complémentaires déjà disponibles
`llm-cost-optimizer` (chiffrer/optimiser le coût LLM), `context-engine` (gestion de contexte), `handoff` / `remember` / `decision-logger` (mémoire & passation), `wiki-init`/`wiki-query`/`wiki-log` (base de connaissance compacte interrogeable).

## Mesurer (pour savoir si ça marche)
Comparer l'usage quota avant/après sur 2-3 sessions types. Les plus gros sauts viennent presque toujours de la règle 1 (modèle) et de la règle 2 (mémoire-graphe).
