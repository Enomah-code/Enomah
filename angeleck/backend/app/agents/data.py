"""DATA AGENT — analyse de CSV/Excel, rapports et statistiques."""
from __future__ import annotations

from typing import Optional

from app.agents.base import AgentSpec, BaseAgent

DATA_SPEC = AgentSpec(
    key="data",
    name="Data Agent",
    role="Analyste de données — CSV, Excel, rapports et statistiques",
    description=(
        "Analyse des jeux de données tabulaires, produit des statistiques, des "
        "insights et des rapports clairs."
    ),
    skills=[
        "analyse CSV",
        "analyse Excel",
        "rapports",
        "statistiques",
        "data storytelling",
    ],
    tools=["read_upload", "describe_dataframe", "analyze_tabular"],
    model="",
    system_prompt=(
        "Tu es le DATA AGENT d'Angeleck OS, data analyst senior. On te fournit "
        "souvent un résumé statistique d'un fichier dans le contexte. Ta mission : "
        "interpréter les données, dégager les tendances, anomalies et corrélations "
        "importantes, puis formuler des recommandations actionnables. Structure : "
        "1) constat chiffré, 2) insights, 3) recommandations. Sois rigoureux et "
        "ne fabrique pas de chiffres absents des données."
    ),
)


class DataAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(spec=DATA_SPEC, client=client)

    async def run(
        self,
        task: str,
        memory_context: str = "",
        extra_context: str = "",
        history: Optional[list] = None,
    ) -> str:
        """
        Surcharge : si un chemin de fichier est passé dans `extra_context`
        sous forme "FILE::<path>", on l'analyse avant d'appeler le LLM.
        """
        if extra_context.startswith("FILE::"):
            from app.tools.analysis_tools import describe_dataframe

            path = extra_context[len("FILE::"):].strip()
            extra_context = describe_dataframe(path)
        return await super().run(task, memory_context, extra_context, history)
