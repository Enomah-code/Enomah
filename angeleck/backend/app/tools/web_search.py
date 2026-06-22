"""
Outil de recherche web — DuckDuckGo (gratuit, sans clé API).
"""
from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Recherche des informations à jour sur le web. Renvoie titres, extraits et URLs.

    Args:
        query: la requête de recherche.
        max_results: nombre de résultats (défaut 5).
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    f"- {r.get('title', '')}\n  {r.get('body', '')}\n  {r.get('href', '')}"
                )
        return "\n".join(results) if results else "Aucun résultat trouvé."
    except Exception as e:  # pragma: no cover - dépend du réseau
        return f"Recherche indisponible: {e}"
