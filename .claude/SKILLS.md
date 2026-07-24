# Skills Claude Code — comment ça marche dans ce repo

Ce dépôt embarque un pack de skills Claude Code (`.claude/skills/`) et un
mécanisme qui les rend **disponibles dans n'importe quelle discussion** ouverte
sur ce repo — nouvelle comme ancienne.

## Le problème résolu

Dans Claude Code sur le web, chaque discussion tourne dans un **conteneur
éphémère** : il est recréé à partir du repo, puis recyclé après inactivité.
Résultat : `~/.claude/skills/` (le dossier global des skills) est **vidé**
d'une session à l'autre. Seul le **dépôt git** survit.

La solution : versionner tous les skills dans le repo, et les réinstaller
automatiquement au démarrage de chaque session.

## Les pièces

| Fichier | Rôle |
|---|---|
| `.claude/skills/` | **Source de vérité.** 438 skills versionnés dans git → persistants. |
| `.claude/install-skills.sh` | Hook `SessionStart` : recopie les skills du repo vers `~/.claude/skills/` (global). Idempotent et non destructif (`cp -rn`). |
| `.claude/suggest-skills.py` | Hook `SessionStart` : analyse le projet et suggère les skills pertinents. |
| `.claude/settings.json` | Déclare les deux hooks ci-dessus sur l'événement `SessionStart`. |

## Deux familles de skills

1. **Le pack du repo (438 skills)** — persistant uniquement grâce à ce repo +
   le hook. Disponible dans toute session ouverte **sur ce repo**.
2. **Les skills installés via l'interface Claude Code** (`pdf`, `docx`, `pptx`,
   `xlsx`, `morning`, `skill-creator`, `frontend-design`, `ui-ux-pro-max`…) —
   gérés au niveau du **compte** et ré-provisionnés côté serveur à chaque
   session, donc déjà disponibles partout automatiquement. Le hook ne les
   écrase jamais (`cp -n`) : les versions du compte restent prioritaires.

## Ajouter un nouveau skill (il sera disponible partout)

```bash
# 1. Déposer le dossier du skill dans le repo
cp -r mon-skill .claude/skills/mon-skill

# 2. Commit + push
git add .claude/skills/mon-skill
git commit -m "Ajouter le skill mon-skill"
git push
```

Au démarrage de la prochaine session, le hook l'installera automatiquement
dans `~/.claude/skills/` et il sera invocable via `/mon-skill`.

## Vérifier que tout est en place

```bash
bash .claude/install-skills.sh
# → ✅ Skills disponibles globalement : 438 (dont 438 versionnés dans le repo)
```
