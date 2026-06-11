from datetime import datetime
from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from raphael.core.registry import AgentRegistry


class PerformanceReport:
    def __init__(self):
        self.timestamp = datetime.now()
        self.agent_scores: dict[str, float] = {}
        self.underperforming: list[str] = []
        self.recommendations: list[str] = []
        self.network_health: float = 1.0


class PerformanceEvaluator:
    """Évalue les performances du réseau et de chaque agent."""

    def __init__(self, registry: "AgentRegistry", min_success_rate: float = 0.75):
        self._registry = registry
        self._min_rate = min_success_rate

    async def evaluate(self) -> PerformanceReport:
        report = PerformanceReport()
        agents = await self._registry.get_all()

        total_score = 0.0
        for agent in agents:
            score = agent.performance_score
            report.agent_scores[agent.name] = round(score, 3)
            total_score += score

            if agent.task_count >= 5 and agent.success_rate < self._min_rate:
                report.underperforming.append(agent.name)
                report.recommendations.append(
                    f"{agent.name}: taux de succès {agent.success_rate:.1%} < {self._min_rate:.1%} "
                    f"— optimisation du prompt recommandée"
                )

        if agents:
            report.network_health = round(total_score / len(agents), 3)

        logger.info(
            f"Évaluation réseau: santé={report.network_health:.2f} | "
            f"Sous-performants: {report.underperforming}"
        )
        return report
