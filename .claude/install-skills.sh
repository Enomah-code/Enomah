#!/bin/bash
# Hook SessionStart — Rend tous les skills du repo disponibles globalement.
#
# Pourquoi : dans l'environnement Claude Code (web), le conteneur est éphémère.
# Seul le dépôt git (donc .claude/skills/) survit d'une session à l'autre.
# ~/.claude/skills/ est vidé à chaque nouveau conteneur. Ce hook recopie donc
# le pack de skills versionné dans le repo vers ~/.claude/skills/ au démarrage
# de CHAQUE session, pour qu'ils soient utilisables dans n'importe quelle
# discussion ouverte sur ce repo.
#
# Le repo est la source de vérité unique : ajoute un skill dans
# .claude/skills/, commit, et il sera automatiquement disponible partout.

set -u

GLOBAL_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS="$(cd "$(dirname "$0")" && pwd)/skills"

mkdir -p "$GLOBAL_SKILLS"

# Copie idempotente et non destructive :
#   -r  récursif (chaque skill est un dossier)
#   -n  no-clobber : n'écrase JAMAIS un skill déjà présent globalement.
#       → respecte les versions gérées par le compte Claude (pdf, docx,
#         skill-creator, morning, etc. ré-provisionnées côté serveur)
#       → installe tout skill du repo encore absent (dont les futurs ajouts)
# Contrairement à l'ancien garde-fou "si moins de 100 skills", ceci propage
# bien les nouveaux skills ajoutés au repo, même quand le global est déjà peuplé.
cp -rn "$PROJECT_SKILLS"/. "$GLOBAL_SKILLS"/ 2>/dev/null || true

PROJECT_COUNT=$(find "$PROJECT_SKILLS" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
GLOBAL_COUNT=$(find "$GLOBAL_SKILLS" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')

echo "✅ Skills disponibles globalement : $GLOBAL_COUNT (dont $PROJECT_COUNT versionnés dans le repo)"
