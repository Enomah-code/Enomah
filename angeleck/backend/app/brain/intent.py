"""
Analyse d'intention du cerveau central.

À partir d'une requête utilisateur et du catalogue d'agents, détermine :
  - l'intention résumée ;
  - les compétences nécessaires ;
  - les agents à mobiliser (clés existantes) ;
  - si une compétence manque (besoin de recruter un nouvel agent).
"""
import json
import re
from dataclasses import dataclass, field

from loguru import logger

from app.config import get_settings
from app.llm import get_chat_model

_ROUTING_PROMPT = """Tu es le cerveau central d'Angeleck OS. Tu analyses la \
demande d'un utilisateur et tu décides quels experts mobiliser.

AGENTS DISPONIBLES :
{catalog}

DEMANDE UTILISATEUR :
"{request}"

Analyse la demande et réponds UNIQUEMENT avec un JSON valide :
{{
  "intent": "résumé en une phrase de ce que veut l'utilisateur",
  "skills": ["compétence requise 1", "compétence requise 2"],
  "agents": ["clé_agent_existant"],
  "missing_skill": false,
  "missing_domain": ""
}}

Règles :
- "agents" ne doit contenir QUE des clés d'agents existants listés ci-dessus.
- Si AUCUN agent existant ne couvre la demande, mets "missing_skill": true et \
décris le domaine manquant dans "missing_domain", et laisse "agents" au mieux.
- Tu peux choisir plusieurs agents si la demande est multi-compétences."""


@dataclass
class RoutingDecision:
    intent: str
    skills: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    missing_skill: bool = False
    missing_domain: str = ""


class IntentAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def analyze(self, request: str, catalog: str, valid_keys: list[str]) -> RoutingDecision:
        llm = get_chat_model(self.settings.supervisor_model, temperature=0.2)
        prompt = _ROUTING_PROMPT.format(catalog=catalog, request=request)
        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            data = _extract_json(raw) or {}
        except Exception as e:  # pragma: no cover - dépend d'Ollama
            logger.warning(f"Analyse d'intention en échec ({e}) — fallback.")
            data = {}

        # Filtre les agents pour ne garder que des clés valides
        agents = [a for a in data.get("agents", []) if a in valid_keys]
        missing = bool(data.get("missing_skill", False))

        # Fallback : si rien ne ressort, mobiliser le marketing par défaut
        if not agents and not missing:
            agents = ["marketing"] if "marketing" in valid_keys else valid_keys[:1]

        return RoutingDecision(
            intent=str(data.get("intent", request[:200])),
            skills=[str(s) for s in data.get("skills", [])],
            agents=agents,
            missing_skill=missing and not agents,
            missing_domain=str(data.get("missing_domain", "")),
        )


def _extract_json(text: str) -> dict | None:
    text = re.sub(r"^```(json)?", "", text.strip()).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
