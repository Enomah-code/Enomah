"""
Boîte à outils partagée des agents.

Les outils sont déclarés comme des fonctions LangChain (`@tool`) et
référencés par nom dans la configuration de chaque agent.
"""
from app.tools.code_tools import run_python
from app.tools.data_tools import analyze_csv, describe_dataframe
from app.tools.web_search import web_search

# Registre nom -> outil LangChain, utilisé par BaseAgent pour résoudre
# la liste `tools` déclarative en objets exécutables.
TOOL_REGISTRY = {
    "web_search": web_search,
    "run_python": run_python,
    "analyze_csv": analyze_csv,
    "describe_dataframe": describe_dataframe,
}


def resolve_tools(names: list[str]) -> list:
    """Convertit une liste de noms d'outils en objets LangChain Tool."""
    return [TOOL_REGISTRY[n] for n in names if n in TOOL_REGISTRY]


__all__ = ["TOOL_REGISTRY", "resolve_tools"]
