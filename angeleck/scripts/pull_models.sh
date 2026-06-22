#!/usr/bin/env bash
# Télécharge les modèles Ollama nécessaires à Angeleck OS.
# Usage : ./scripts/pull_models.sh   (Ollama doit être démarré)
set -euo pipefail

OLLAMA_HOST="${OLLAMA_BASE_URL:-http://localhost:11434}"
MODELS=("llama3" "mistral" "phi3" "qwen2.5-coder" "nomic-embed-text")

echo "Téléchargement des modèles via ${OLLAMA_HOST}..."
for model in "${MODELS[@]}"; do
  echo ">> pull ${model}"
  if command -v ollama >/dev/null 2>&1; then
    ollama pull "${model}"
  else
    curl -s "${OLLAMA_HOST}/api/pull" -d "{\"name\":\"${model}\"}" >/dev/null
  fi
done
echo "Modèles prêts."
