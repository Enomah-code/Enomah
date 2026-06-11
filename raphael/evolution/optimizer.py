import anthropic
from loguru import logger

from raphael.config import get_settings
from raphael.core.registry import AgentRegistry
from raphael.memory import LongTermMemory


OPTIMIZATION_PROMPT = """Tu es un expert en prompt engineering et optimisation d'agents IA.

Agent à optimiser: {agent_name} ({agent_role})
Prompt système actuel:
{current_prompt}

Historique des échecs récents:
{failures}

Analyse les patterns d'échec et génère un prompt système AMÉLIORÉ qui:
1. Corrige les faiblesses identifiées
2. Améliore la précision et la qualité des réponses
3. Ajoute des instructions spécifiques pour éviter les erreurs récurrentes
4. Renforce l'expertise et la confiance de l'agent

Réponds UNIQUEMENT avec le nouveau prompt système, sans explication."""


class PromptOptimizer:
    """Optimise automatiquement les prompts des agents sous-performants."""

    def __init__(self, registry: AgentRegistry, long_memory: LongTermMemory):
        self._registry = registry
        self._memory = long_memory
        self._settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=self._settings.anthropic_api_key)

    async def optimize_agent(self, agent_name: str) -> bool:
        """Optimise le prompt d'un agent sous-performant."""
        spec = await self._registry.get(agent_name)
        if not spec:
            return False

        # Récupère les échecs récents depuis la mémoire
        failures = await self._memory.search(
            namespace=f"agent_{agent_name}",
            query="erreur échec failed",
            n_results=10,
            filter_metadata={"success": "False"},
        )

        if not failures:
            logger.info(f"Pas d'échecs trouvés pour {agent_name}, optimisation non nécessaire")
            return False

        failures_text = "\n".join([f"- {f['content'][:200]}" for f in failures[:5]])

        try:
            response = await self._client.messages.create(
                model=self._settings.orchestrator_model,
                max_tokens=4096,
                thinking={"type": "adaptive"},
                messages=[{
                    "role": "user",
                    "content": OPTIMIZATION_PROMPT.format(
                        agent_name=spec.name,
                        agent_role=spec.role,
                        current_prompt=spec.system_prompt[:2000],
                        failures=failures_text,
                    ),
                }],
            )

            new_prompt = ""
            for block in response.content:
                if hasattr(block, "text"):
                    new_prompt += block.text

            if new_prompt.strip():
                spec.system_prompt = new_prompt.strip()
                # Réinitialise le compteur de performances après optimisation
                spec.performance_score = 0.8
                await self._registry.register(spec)
                logger.info(f"Prompt de {agent_name} optimisé avec succès")
                return True

        except Exception as e:
            logger.error(f"Optimization error for {agent_name}: {e}")

        return False
