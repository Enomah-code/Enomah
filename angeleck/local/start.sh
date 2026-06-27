#!/usr/bin/env bash
# ============================================================
#   Angeleck OS - Lanceur local (macOS / Linux)
# ============================================================
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "   ANGELECK OS - Demarrage local (EMK Blue Diamond)"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERREUR] Python 3 introuvable. Installez-le : https://www.python.org/downloads/"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "[1/3] Creation de l'environnement Python..."
  python3 -m venv .venv
fi

echo "[2/3] Installation des dependances..."
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet -r requirements-local.txt

echo "[3/3] Demarrage du serveur sur http://localhost:8000"
# Ouvre le navigateur (macOS: open, Linux: xdg-open)
(command -v open >/dev/null && open http://localhost:8000) || \
(command -v xdg-open >/dev/null && xdg-open http://localhost:8000) || true

exec ./.venv/bin/python server.py
