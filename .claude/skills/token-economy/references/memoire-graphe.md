# La mémoire-graphe — mode d'emploi

But : une mémoire de projet **permanente, légère, retrouvable**, qui vit dans des
**fichiers sur GitHub** (pas dans le fil de chat, pas dans un serveur local). On lit
**une branche** à la fois au lieu de tout l'historique.

## L'idée (une toile de nœuds reliés)
- **Tronc** = `INDEX.md` : la carte. Liste chaque branche avec une ligne de description + un lien.
- **Branches** = un fichier par sujet dans `memoire/` (ex. `memoire/formation.md`).
- **Arêtes** = les liens entre branches (section « Branches liées » en bas de chaque fichier).
- **Règle de lecture** : `INDEX.md` → la branche concernée → (un lien seulement si nécessaire). Jamais « lis tout ».
- **Règle d'écriture** : après un changement, on met à jour **la seule branche touchée** (5-10 lignes) + un lien si une relation nouvelle apparaît.

## Pourquoi ça marche
Dans un chat, tout l'historique est refacturé à chaque message — rien n'y change.
Le graphe sort la connaissance du chat : le fil devient **jetable**, la mémoire est ailleurs.
Du coup : on ne recharge que la branche utile, et on retrouve toujours **où est tel sujet**
(une branche nommée, au lieu de fouiller 5 sessions).

## Où le mettre
- `memoire/` à la racine du repo (visible, versionné).
- Si un `SESSION-STATE.md` existait, le transformer en **pointeur** vers `memoire/INDEX.md`
  (pour que les anciennes références y mènent, sans contenu en double qui dérive).

## Découper en branches (comment choisir les nœuds)
- Un **sujet durable** = une branche (un chantier, un livrable, un domaine).
- Ni trop gros (« tout le projet » → inutile), ni trop fin (« une tâche » → trop de fichiers).
- Bon repère : 4 à 10 branches pour un projet. Au-delà, regrouper.
- Quand un nouveau grand sujet arrive : nouvelle branche + ligne dans `INDEX.md`.

## Gabarit — `INDEX.md` (le tronc)
```markdown
# 🧠 Mémoire-graphe <PROJET> — la carte (tronc)
> Lis CE fichier d'abord, puis UNIQUEMENT la branche qui concerne ta question.

## Comment ça marche
- Chaque sujet = une branche (un fichier). Les branches se citent entre elles (liens = arêtes).
- Pour une question sur X : ouvre la branche X ; suis un lien seulement si nécessaire.
- Après un changement : mets à jour SEULEMENT la branche touchée (+ un lien si besoin).

## Branches
| Branche | De quoi ça parle | Fichier |
|---|---|---|
| <Nom> | <une ligne> | <fichier.md> |
```

## Gabarit — une branche (`memoire/<sujet>.md`)
```markdown
# <Nom de la branche>
> Branche du graphe-mémoire <PROJET>. Tronc : INDEX.md. Dernière mise à jour : <date>.

## État actuel
- ...

## Décisions prises
- ...

## Où trouver quoi
- <fichier/chemin> — <ce que c'est>

## Prochaines étapes
- ...

## Branches liées (arêtes)
- [<Autre branche>](autre.md) — <pourquoi elles sont liées>
```

## Entretien (le réflexe)
1. Tu changes quelque chose → tu mets à jour **la branche** correspondante, tout de suite.
2. Nouveau grand sujet → **nouvelle branche** + ligne dans `INDEX.md`.
3. Une relation apparaît entre deux sujets → ajoute un **lien** dans les deux branches.
4. Tu commits : la mémoire est sur GitHub, disponible partout (cloud ou PC), permanente.
