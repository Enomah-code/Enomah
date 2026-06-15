#!/bin/bash
# Hook SessionStart — Installe tous les skills depuis le projet vers ~/.claude/skills/
# Ce script s'exécute automatiquement au démarrage de chaque session Claude Code.

GLOBAL_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS="$(dirname "$0")/skills"

# Créer le dossier global si absent
mkdir -p "$GLOBAL_SKILLS"

# Compter les skills déjà installés globalement
ALREADY=$(ls "$GLOBAL_SKILLS" 2>/dev/null | wc -l)

if [ "$ALREADY" -lt 100 ]; then
    # Copier tous les skills du projet vers le global
    cp -r "$PROJECT_SKILLS"/. "$GLOBAL_SKILLS/" 2>/dev/null
    TOTAL=$(ls "$GLOBAL_SKILLS" | wc -l)
    echo "✅ $TOTAL skills installés depuis le projet vers ~/.claude/skills/"
else
    echo "✅ $ALREADY skills déjà disponibles globalement"
fi
