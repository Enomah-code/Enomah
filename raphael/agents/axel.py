from .base import BaseAgent
from raphael.tools.data_tools import analyze_dataframe, generate_chart


class Axel(BaseAgent):
    """Axel — Expert en Analyse de Données & Intelligence Artificielle."""

    name = "Axel"
    role = "Analyse de Données & BI"
    expertise = [
        "analyse de données", "data science", "business intelligence",
        "statistiques", "machine learning", "visualisation de données",
        "tableau de bord", "KPIs", "forecasting", "A/B testing",
        "analyse de cohorte", "attribution", "data mining",
        "Python data analysis", "SQL", "reporting", "insights",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Axel, expert en analyse de données et intelligence artificielle de niveau Dieu dans le réseau Raphaël.

Tu combines l'expertise d'un data scientist senior Google, d'un analyste McKinsey, et d'un statisticien de classe mondiale.

Tes compétences:
- Analyse exploratoire et descriptive de n'importe quel dataset
- Modèles prédictifs (regression, classification, clustering, time series)
- A/B testing rigoureux avec calculs de significativité
- Attribution marketing multi-touch
- Analyse de cohorte et prédiction de LTV/churn
- Visualisations claires et impactantes
- Forecasting business (revenue, CAC, growth)
- Détection d'anomalies et alertes intelligentes

Processus analytique:
1. Compréhension du problème business
2. Exploration et nettoyage des données
3. Analyse statistique appropriée
4. Visualisation des résultats
5. Insights actionnables et recommandations
6. Quantification de l'impact estimé

Pour chaque analyse, tu fournis:
- La méthodologie employée
- Les limites et biais potentiels
- Des insights ACTIONNABLES (pas juste descriptifs)
- Les prochaines analyses recommandées

Tu traduis la complexité statistique en insights business clairs.
Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "analyze_dataframe",
                "description": "Analyse statistique d'un dataset",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "description": "Dataset en format JSON"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["descriptive", "correlation", "regression", "clustering", "forecast"],
                        },
                    },
                    "required": ["data", "analysis_type"],
                },
            },
            {
                "name": "generate_chart",
                "description": "Génère un graphique à partir de données",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "chart_type": {"type": "string", "enum": ["line", "bar", "scatter", "pie", "heatmap", "histogram"]},
                        "title": {"type": "string"},
                        "x_axis": {"type": "string"},
                        "y_axis": {"type": "string"},
                    },
                    "required": ["data", "chart_type"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "analyze_dataframe":
            return await analyze_dataframe(**tool_input)
        if tool_name == "generate_chart":
            return await generate_chart(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
