"""
Outil de lecture de fichiers uploadés.

Supporte : texte brut, Markdown, JSON, CSV et Excel. Renvoie un extrait
textuel exploitable par un agent. Pour les fichiers tabulaires, délègue à
analysis_tools pour produire un résumé statistique.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger("angeleck.tools.file")

MAX_PREVIEW_CHARS = 8000


def read_upload(path: str) -> Dict[str, Any]:
    """
    Lit un fichier et renvoie {type, content, meta}.

    `content` est une représentation texte tronquée, prête à être injectée
    dans le prompt d'un agent.
    """
    if not os.path.exists(path):
        return {"type": "error", "content": f"Fichier introuvable : {path}", "meta": {}}

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in {".csv", ".xlsx", ".xls"}:
            return _read_tabular(path, ext)
        if ext == ".json":
            return _read_json(path)
        # Par défaut : texte (txt, md, py, log, etc.)
        return _read_text(path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur lecture %s : %s", path, exc)
        return {"type": "error", "content": str(exc), "meta": {}}


def _read_text(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        data = fh.read()
    return {
        "type": "text",
        "content": data[:MAX_PREVIEW_CHARS],
        "meta": {"chars": len(data), "truncated": len(data) > MAX_PREVIEW_CHARS},
    }


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    pretty = json.dumps(data, ensure_ascii=False, indent=2)
    return {
        "type": "json",
        "content": pretty[:MAX_PREVIEW_CHARS],
        "meta": {"keys": list(data.keys()) if isinstance(data, dict) else None},
    }


def _read_tabular(path: str, ext: str) -> Dict[str, Any]:
    try:
        import pandas as pd
    except ImportError:
        return {
            "type": "error",
            "content": "pandas requis pour lire les fichiers CSV/Excel.",
            "meta": {},
        }
    df = pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
    summary = (
        f"Fichier tabulaire : {df.shape[0]} lignes x {df.shape[1]} colonnes.\n"
        f"Colonnes : {', '.join(map(str, df.columns))}\n\n"
        f"Aperçu :\n{df.head(10).to_string()}\n\n"
        f"Statistiques :\n{df.describe(include='all').to_string()}"
    )
    return {
        "type": "tabular",
        "content": summary[:MAX_PREVIEW_CHARS],
        "meta": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
    }
