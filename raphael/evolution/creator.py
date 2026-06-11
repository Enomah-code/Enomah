import asyncio
from typing import TYPE_CHECKING
from loguru import logger

from raphael.config import get_settings
from raphael.evolution.evaluator import PerformanceEvaluator
from raphael.evolution.optimizer import PromptOptimizer

if TYPE_CHECKING:
    from raphael.core.registry import AgentRegistry
    from raphael.core.factory import AgentFactory
    from raphael.memory import LongTermMemory


class EvolutionEngine:
    """
    Moteur d'évolution autonome du réseau Raphaël.
    S'exécute périodiquement pour améliorer le réseau de façon autonome.
    """

    def __init__(
        self,
        registry: "AgentRegistry",
        factory: "AgentFactory",
        long_memory: "LongTermMemory",
    ):
        self._registry = registry
        self._factory = factory
        self._memory = long_memory
        self._settings = get_settings()
        self._evaluator = PerformanceEvaluator(registry, self._settings.min_task_success_rate)
        self._optimizer = PromptOptimizer(registry, long_memory)
        self._running = False

    async def run_cycle(self) -> dict:
        """Exécute un cycle d'évolution complet."""
        logger.info("=== Cycle d'évolution Raphaël démarré ===")
        report = {"evaluations": {}, "optimizations": [], "new_agents": [], "errors": []}

        try:
            # Étape 1: Évaluation des performances
            perf = await self._evaluator.evaluate()
            report["evaluations"] = {
                "network_health": perf.network_health,
                "agent_scores": perf.agent_scores,
                "underperforming": perf.underperforming,
            }

            # Étape 2: Optimisation des agents sous-performants
            for agent_name in perf.underperforming:
                logger.info(f"Optimisation de l'agent {agent_name}...")
                success = await self._optimizer.optimize_agent(agent_name)
                if success:
                    report["optimizations"].append(agent_name)

            # Étape 3: Détection de lacunes et création d'agents
            if self._settings.auto_spawn_agents:
                await self._detect_and_fill_gaps(report)

            # Étape 4: Nettoyage mémoire ancienne
            await self._memory.store_world_knowledge(
                topic="evolution_report",
                content=str(report),
                source="evolution_engine",
            )

            logger.info(
                f"=== Cycle d'évolution terminé === "
                f"Santé: {perf.network_health:.2f} | "
                f"Optimisations: {len(report['optimizations'])} | "
                f"Nouveaux agents: {len(report['new_agents'])}"
            )

        except Exception as e:
            logger.error(f"Evolution cycle error: {e}")
            report["errors"].append(str(e))

        return report

    async def _detect_and_fill_gaps(self, report: dict) -> None:
        """Détecte les lacunes du réseau et crée de nouveaux agents si nécessaire."""
        recent_tasks = await self._memory.search(
            namespace="agent_raphael",
            query="délégation agent non trouvé compétence manquante",
            n_results=20,
        )

        if not recent_tasks:
            return

        # Analyse les tâches non satisfaites
        unmet_domains: dict[str, int] = {}
        for task in recent_tasks:
            content = task.get("content", "")
            if "non trouvé" in content.lower() or "manquant" in content.lower():
                words = content.lower().split()
                for i, word in enumerate(words):
                    if word in ("compétence", "domaine", "expertise") and i + 1 < len(words):
                        domain = words[i + 1].strip(".,!?")
                        unmet_domains[domain] = unmet_domains.get(domain, 0) + 1

        for domain, count in sorted(unmet_domains.items(), key=lambda x: x[1], reverse=True)[:2]:
            if count >= 2:
                logger.info(f"Lacune détectée: {domain} ({count} occurrences)")
                new_spec = await self._factory.spawn_agent(
                    domain=domain,
                    missing_skills=[domain],
                    context=f"Domaine demandé {count} fois sans agent disponible",
                )
                if new_spec:
                    report["new_agents"].append(new_spec.name)

    async def start_background_loop(self) -> None:
        """Démarre la boucle d'évolution en arrière-plan."""
        self._running = True
        logger.info(
            f"Moteur d'évolution démarré "
            f"(cycle toutes les {self._settings.evolution_interval_hours}h)"
        )
        while self._running:
            interval = self._settings.evolution_interval_hours * 3600
            await asyncio.sleep(interval)
            if self._running:
                await self.run_cycle()

    def stop(self) -> None:
        self._running = False
        logger.info("Moteur d'évolution arrêté")
