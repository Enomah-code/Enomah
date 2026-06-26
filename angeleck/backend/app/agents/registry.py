"""
REGISTRE DES AGENTS — source de vérité en mémoire + synchronisation DB.

Le registre :
  * charge les 5 agents natifs au démarrage ;
  * recharge les agents générés (package agents.generated) ;
  * permet d'enregistrer un nouvel agent (recruteur) ;
  * fournit la résolution clé -> instance exécutable.

Il s'appuie sur `AgentSpec` pour rester découplé du LLM et facilement
persistable dans la table `agents` (AgentRecord).
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Dict, List, Optional

from app.agents.base import AgentSpec, BaseAgent, GenericAgent
from app.agents.code import CodeAgent
from app.agents.data import DataAgent
from app.agents.marketing import MarketingAgent
from app.agents.visual import VisualAgent
from app.agents.writer import WriterAgent

logger = logging.getLogger("angeleck.registry")


class AgentRegistry:
    """Conteneur central des agents disponibles."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        self._load_native()
        self._load_generated()

    # ------------------------------------------------------------------ #
    def _load_native(self) -> None:
        for cls in (WriterAgent, MarketingAgent, CodeAgent, VisualAgent, DataAgent):
            agent = cls()
            self._agents[agent.key] = agent
        logger.info("Agents natifs chargés : %s", ", ".join(self._agents))

    def _load_generated(self) -> None:
        """Importe dynamiquement les agents du package generated."""
        try:
            import app.agents.generated as generated_pkg
        except ImportError:
            return

        for mod_info in pkgutil.iter_modules(generated_pkg.__path__):
            if mod_info.name.startswith("_"):
                continue
            try:
                module = importlib.import_module(
                    f"app.agents.generated.{mod_info.name}"
                )
                spec = getattr(module, "SPEC", None)
                if isinstance(spec, AgentSpec):
                    self.register(GenericAgent(spec))
                    logger.info("Agent généré chargé : %s", spec.key)
            except Exception as exc:  # noqa: BLE001
                logger.error("Échec chargement agent généré %s : %s", mod_info.name, exc)

    # ------------------------------------------------------------------ #
    def register(self, agent: BaseAgent) -> None:
        """Ajoute/remplace un agent dans le registre."""
        self._agents[agent.key] = agent

    def register_spec(self, spec: AgentSpec) -> BaseAgent:
        """Enregistre un agent à partir d'une spec (cas recruteur)."""
        agent = GenericAgent(spec)
        self.register(agent)
        return agent

    def get(self, key: str) -> Optional[BaseAgent]:
        return self._agents.get(key)

    def exists(self, key: str) -> bool:
        return key in self._agents

    def all(self) -> List[BaseAgent]:
        return list(self._agents.values())

    def specs(self) -> List[AgentSpec]:
        return [a.spec for a in self._agents.values()]

    def catalogue(self) -> List[dict]:
        """Représentation JSON pour l'API /agents."""
        return [a.spec.to_dict() for a in self._agents.values()]

    def skills_overview(self) -> Dict[str, List[str]]:
        """Map clé d'agent -> compétences (utilisé par le routeur)."""
        return {a.key: a.spec.skills for a in self._agents.values()}


# Singleton applicatif
registry = AgentRegistry()
