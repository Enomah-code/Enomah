import anthropic
from loguru import logger

from raphael.config import get_settings
from raphael.core.registry import AgentRegistry, AgentSpec


AGENT_CREATION_PROMPT = """Tu es l'architecte du réseau Raphaël. Tu dois créer un nouvel agent spécialisé.

Domaine requis: {domain}
Compétences manquantes: {missing_skills}
Contexte de la demande: {context}

Génère une spécification complète pour ce nouvel agent au format JSON:
{{
  "name": "PrénomHumain",
  "role": "Titre du rôle",
  "expertise": ["compétence1", "compétence2", ...],
  "system_prompt": "Prompt système complet définissant l'identité et l'expertise de l'agent...",
  "model": "claude-sonnet-4-6",
  "tools": ["outil1", "outil2"]
}}

Règles:
- Le nom doit être un prénom humain unique (pas déjà utilisé: {existing_names})
- L'agent doit être un expert de niveau Dieu dans son domaine
- Le system_prompt doit être détaillé, inspirant, et très spécifique
- L'expertise doit être exhaustive avec 10+ compétences spécifiques

Réponds UNIQUEMENT avec le JSON valide, sans explication."""


class AgentFactory:
    """Fabrique d'agents: crée automatiquement de nouveaux agents spécialisés."""

    def __init__(self, registry: AgentRegistry):
        self._registry = registry
        self._settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=self._settings.anthropic_api_key)

    async def spawn_agent(self, domain: str, missing_skills: list[str], context: str = "") -> AgentSpec | None:
        """Crée et enregistre un nouvel agent pour le domaine spécifié."""
        existing = await self._registry.list_names()
        logger.info(f"Création d'un nouvel agent pour: {domain} | Compétences: {missing_skills}")

        prompt = AGENT_CREATION_PROMPT.format(
            domain=domain,
            missing_skills=", ".join(missing_skills),
            context=context or "Aucun contexte supplémentaire",
            existing_names=", ".join(existing),
        )

        try:
            response = await self._client.messages.create(
                model=self._settings.orchestrator_model,
                max_tokens=4096,
                thinking={"type": "adaptive"},
                messages=[{"role": "user", "content": prompt}],
            )
            raw = self._extract_json(response)
            if not raw:
                logger.error("AgentFactory: Impossible d'extraire le JSON de la réponse")
                return None

            spec = AgentSpec(**raw)

            # Vérifie que le nom n'est pas déjà pris
            if await self._registry.exists(spec.name):
                spec.name = f"{spec.name}_{domain[:4].capitalize()}"

            await self._registry.register(spec)
            logger.info(f"Nouvel agent créé et enregistré: {spec.name} ({spec.role})")
            return spec

        except Exception as e:
            logger.error(f"AgentFactory spawn error: {e}")
            return None

    async def detect_capability_gaps(self, task: str, failed_agents: list[str]) -> list[str]:
        """Détecte les compétences manquantes dans le réseau pour une tâche donnée."""
        try:
            existing = await self._registry.get_all()
            existing_expertise = []
            for agent in existing:
                existing_expertise.extend(agent.expertise)

            response = await self._client.messages.create(
                model=self._settings.fast_model,
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Tâche: {task}\n"
                        f"Agents ayant échoué: {', '.join(failed_agents)}\n"
                        f"Expertises existantes: {', '.join(set(existing_expertise[:30]))}\n\n"
                        "Identifie en 3-5 mots les compétences MANQUANTES pour cette tâche. "
                        "Réponds avec une liste de compétences séparées par des virgules, rien d'autre."
                    ),
                }],
            )
            gaps_str = response.content[0].text.strip()
            return [g.strip() for g in gaps_str.split(",") if g.strip()]
        except Exception as e:
            logger.error(f"Gap detection error: {e}")
            return []

    def _extract_json(self, response) -> dict | None:
        import json
        import re
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text

        # Cherche le JSON dans la réponse
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
        return None
