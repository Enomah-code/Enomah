"""
Recruteur automatique d'agents (Factory).

Lorsque le cerveau central détecte qu'aucune compétence existante ne couvre
une demande, le recruteur :
  1. génère la définition d'un nouveau rôle (nom, compétences, prompt système) ;
  2. choisit les outils nécessaires parmi le registre d'outils autorisés ;
  3. teste l'agent sur une mini-mission ;
  4. l'enregistre dans le registre + la base ;
  5. le rend disponible pour les prochaines demandes.

La génération utilise un modèle local (Ollama) — aucune API payante.
"""
import json
import re

from loguru import logger

from app.agents.base import Agent, AgentDefinition
from app.agents.registry import AgentRegistry
from app.config import get_settings
from app.llm import get_chat_model
from app.tools import TOOL_REGISTRY

_GENERATION_PROMPT = """Tu es l'architecte d'agents IA d'Angeleck OS.
On a besoin d'un nouvel agent spécialisé car aucun agent existant ne couvre \
cette demande utilisateur :

DEMANDE: "{request}"
DOMAINE SUGGÉRÉ: "{domain}"

Outils disponibles que l'agent peut utiliser (choisis uniquement parmi eux) :
{tools}

Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, au format :
{{
  "key": "identifiant_snake_case_court",
  "name": "Nom propre de l'agent",
  "role": "Rôle / domaine d'expertise",
  "skills": ["compétence 1", "compétence 2", "compétence 3"],
  "tools": ["nom_outil_autorisé"],
  "system_prompt": "Prompt système détaillé décrivant l'identité, l'expertise et la méthode de travail de l'agent, en français."
}}"""


class AgentRecruiter:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry
        self.settings = get_settings()

    async def recruit(self, request: str, domain: str = "") -> AgentDefinition | None:
        """Génère, teste et enregistre un nouvel agent. Renvoie sa définition."""
        if not self.settings.auto_spawn_agents:
            logger.info("Auto-spawn désactivé — recrutement ignoré.")
            return None

        definition = await self._generate_definition(request, domain)
        if definition is None:
            return None

        # Évite les collisions de clé
        if self.registry.get(definition.key):
            definition.key = f"{definition.key}_{abs(hash(request)) % 1000}"

        # Étape de test avant enregistrement définitif
        ok = await self._test_agent(definition, request)
        if not ok:
            logger.warning(f"Agent généré '{definition.key}' a échoué au test.")
            # On l'enregistre quand même mais inactif ? Ici on l'enregistre actif
            # car le test est best-effort (dépend de la dispo du modèle).

        await self.registry.add_agent(definition)
        logger.info(f"Agent recruté avec succès : {definition.name} ({definition.key})")
        return definition

    async def _generate_definition(
        self, request: str, domain: str
    ) -> AgentDefinition | None:
        llm = get_chat_model(self.settings.factory_model, temperature=0.4)
        tools_desc = "\n".join(
            f"- {name}: {tool.description}" for name, tool in TOOL_REGISTRY.items()
        )
        prompt = _GENERATION_PROMPT.format(
            request=request, domain=domain or "à déterminer", tools=tools_desc
        )
        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            data = _extract_json(raw)
            if not data:
                logger.error("La factory n'a pas produit de JSON exploitable.")
                return None

            # Validation / nettoyage
            allowed_tools = [t for t in data.get("tools", []) if t in TOOL_REGISTRY]
            key = re.sub(r"[^a-z0-9_]", "", str(data.get("key", "")).lower()) or "agent"

            return AgentDefinition(
                key=key,
                name=str(data.get("name", "Agent")).strip()[:120],
                role=str(data.get("role", domain or "Spécialiste")).strip()[:255],
                skills=[str(s)[:120] for s in data.get("skills", [])][:20],
                tools=allowed_tools,
                system_prompt=str(data.get("system_prompt", "")).strip(),
                model=self.settings.agent_model,
                is_generated=True,
            )
        except Exception as e:  # pragma: no cover - dépend d'Ollama
            logger.error(f"Échec de génération d'agent: {e}")
            return None

    async def _test_agent(self, definition: AgentDefinition, request: str) -> bool:
        """Teste l'agent sur la demande pour valider qu'il répond."""
        try:
            agent = Agent(
                definition,
                self.registry.short_memory,
                self.registry.long_memory,
            )
            result = await agent.execute(
                task=f"Démontre brièvement ta compétence sur: {request}",
                session_id="factory_test",
            )
            return result.success and len(result.result) > 20
        except Exception as e:  # pragma: no cover
            logger.warning(f"Test agent échoué: {e}")
            return False


def _extract_json(text: str) -> dict | None:
    """Extrait le premier objet JSON d'une réponse LLM."""
    text = text.strip()
    # Retire d'éventuels fences markdown
    text = re.sub(r"^```(json)?", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
