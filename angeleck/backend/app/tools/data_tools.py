"""
Outils d'analyse de données (CSV / Excel) pour l'agent Data Analyst.
"""
from langchain_core.tools import tool

# Répertoire où l'endpoint /upload dépose les fichiers analysables.
UPLOAD_DIR = "./data/uploads"


@tool
def describe_dataframe(file_path: str) -> str:
    """Charge un fichier CSV/Excel et renvoie un résumé statistique (describe + dtypes).

    Args:
        file_path: chemin du fichier précédemment uploadé.
    """
    try:
        import pandas as pd

        df = _load(file_path)
        summary = [
            f"Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes",
            f"Colonnes: {', '.join(map(str, df.columns))}",
            "\nTypes:\n" + df.dtypes.to_string(),
            "\nStatistiques:\n" + df.describe(include='all').to_string(),
        ]
        return "\n".join(summary)
    except Exception as e:
        return f"Erreur d'analyse: {e}"


@tool
def analyze_csv(file_path: str, question: str) -> str:
    """Analyse un CSV/Excel en fonction d'une question (agrégations courantes).

    Args:
        file_path: chemin du fichier uploadé.
        question: ce que l'on cherche (ex: 'top 5 produits par ventes').
    """
    try:
        import pandas as pd

        df = _load(file_path)
        # Aperçu structurel exploitable par l'agent pour raisonner.
        head = df.head(10).to_string()
        numeric = df.select_dtypes("number")
        corr = numeric.corr().to_string() if numeric.shape[1] > 1 else "n/a"
        return (
            f"Question: {question}\n\n"
            f"Aperçu (10 lignes):\n{head}\n\n"
            f"Sommes numériques:\n{numeric.sum().to_string()}\n\n"
            f"Corrélations:\n{corr}"
        )
    except Exception as e:
        return f"Erreur d'analyse: {e}"


def _load(file_path: str):
    import pandas as pd

    if file_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)
    return pd.read_csv(file_path)
