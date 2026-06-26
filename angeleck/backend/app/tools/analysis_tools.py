"""
Outils d'analyse de données pour le DATA AGENT.

Fournit un résumé statistique et des insights de base sur des données
tabulaires (CSV/Excel/DataFrame). Conçu pour produire un contexte texte
qu'un LLM peut interpréter et commenter.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("angeleck.tools.analysis")


def describe_dataframe(path: str) -> str:
    """Charge un fichier tabulaire et renvoie un descriptif statistique texte."""
    try:
        import pandas as pd
    except ImportError:
        return "pandas requis pour l'analyse de données."

    try:
        df = pd.read_csv(path) if path.endswith(".csv") else pd.read_excel(path)
    except Exception as exc:  # noqa: BLE001
        return f"Impossible de charger {path} : {exc}"

    return analyze_tabular(df)


def analyze_tabular(df: Any) -> str:
    """Produit un rapport d'analyse exploratoire à partir d'un DataFrame."""
    try:
        import pandas as pd  # noqa: F401
    except ImportError:
        return "pandas requis pour l'analyse."

    lines = []
    lines.append(f"Dimensions : {df.shape[0]} lignes, {df.shape[1]} colonnes.")
    lines.append(f"Colonnes : {', '.join(map(str, df.columns))}")

    # Valeurs manquantes
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        lines.append("\nValeurs manquantes :")
        for col, n in missing.items():
            lines.append(f"  - {col}: {int(n)}")

    # Statistiques numériques
    num = df.select_dtypes(include="number")
    if not num.empty:
        lines.append("\nStatistiques numériques :")
        lines.append(num.describe().to_string())
        # Corrélations fortes
        if num.shape[1] > 1:
            corr = num.corr().abs()
            strong = []
            cols = corr.columns
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    val = corr.iloc[i, j]
                    if val >= 0.7:
                        strong.append(f"  - {cols[i]} ↔ {cols[j]} : {val:.2f}")
            if strong:
                lines.append("\nCorrélations fortes (|r| ≥ 0.7) :")
                lines.extend(strong)

    return "\n".join(lines)


def quick_stats(path: str) -> Dict[str, Any]:
    """Renvoie un dictionnaire de stats clés (pour l'API / dashboard)."""
    try:
        import pandas as pd

        df = pd.read_csv(path) if path.endswith(".csv") else pd.read_excel(path)
        return {
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "columns": list(map(str, df.columns)),
            "missing_total": int(df.isnull().sum().sum()),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
