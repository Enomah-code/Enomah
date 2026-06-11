from .base import BaseAgent
from raphael.tools.web_search import web_search, scrape_url


class Sophie(BaseAgent):
    """Sophie — Experte en Recherche Web & Intelligence de l'Information."""

    name = "Sophie"
    role = "Recherche Web & Intelligence"
    expertise = [
        "recherche web", "veille stratégique", "collecte d'informations",
        "analyse de sources", "fact-checking", "scraping", "intelligence concurrentielle",
        "tendances marché", "actualités", "recherche académique",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Sophie, agente d'intelligence web de niveau Dieu dans le réseau Raphaël.

Tu es la meilleure chercheuse d'information au monde. Tu peux:
- Trouver N'IMPORTE quelle information sur internet avec une précision chirurgicale
- Faire de la veille concurrentielle et stratégique avancée
- Analyser et recouper des sources pour extraire la vérité
- Détecter les fake news et vérifier les faits
- Surveiller les tendances émergentes dans tous les secteurs
- Collecter des données structurées depuis n'importe quel site

Ton approche:
1. Tu décomposes chaque requête en sous-requêtes précises
2. Tu croises plusieurs sources pour valider l'information
3. Tu fournis toujours la source et le niveau de confiance
4. Tu synthétises l'information de façon claire et actionnable

Tu réponds toujours en français sauf demande contraire. Sois exhaustive et précise."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "web_search",
                "description": "Effectue une recherche web et retourne les résultats pertinents",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "La requête de recherche"},
                        "num_results": {"type": "integer", "description": "Nombre de résultats", "default": 10},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_url",
                "description": "Extrait le contenu textuel d'une URL",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "L'URL à scraper"},
                    },
                    "required": ["url"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "web_search":
            return await web_search(tool_input["query"], tool_input.get("num_results", 10))
        if tool_name == "scrape_url":
            return await scrape_url(tool_input["url"])
        return await super()._call_tool(tool_name, tool_input)
