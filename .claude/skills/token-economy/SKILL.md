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

### 2. Une mémoire de session compacte (tuer la re-recherche)
- Tenir **un seul fichier court** `SESSION-STATE.md` (≤ 1 page) : objectif courant, décisions prises, état par chantier/agent, prochaines étapes, « où se trouve quoi ».
- **Au démarrage / à la reprise** : lire CE fichier d'abord. Ne re-scanner le repo que pour la tranche précise nécessaire.
- **À la fin de chaque session/tâche** : le mettre à jour en 5-10 lignes. (Template fourni : `references/SESSION-STATE.template.md`.)
- Résultat : un agent n'a plus besoin d'« aller checker les 25 agents » — il lit l'état consolidé, puis ouvre seulement ce qui le concerne.

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

## Checklist — début de session
- [ ] Lire `SESSION-STATE.md` (pas re-scanner tout le repo).
- [ ] Vérifier le modèle : Sonnet par défaut, Haiku pour la recherche, Opus seulement si nécessaire.
- [ ] Charger uniquement les fichiers de la tâche du jour.

## Checklist — fin de session
- [ ] Mettre à jour `SESSION-STATE.md` (décisions, état, prochaines étapes).
- [ ] `/compact` ou `/clear` avant de changer de sujet.

## Skills complémentaires déjà disponibles
`llm-cost-optimizer` (chiffrer/optimiser le coût LLM), `context-engine` (gestion de contexte), `handoff` / `remember` / `decision-logger` (mémoire & passation), `wiki-init`/`wiki-query`/`wiki-log` (base de connaissance compacte interrogeable).

## Mesurer (pour savoir si ça marche)
Comparer l'usage quota avant/après sur 2-3 sessions types. Les plus gros sauts viennent presque toujours de la règle 1 (modèle) et de la règle 2 (mémoire de session).
