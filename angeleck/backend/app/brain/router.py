"""
ROUTEUR DE COMPÉTENCES.

À partir d'une requête utilisateur, identifie le ou les agents les plus
adaptés. Stratégie hybride :

  1. Scoring par mots-clés (rapide, déterministe, sans LLM) ;
  2. Affinage par le LLM (cerveau) qui choisit parmi le catalogue et signale
     si AUCUN agent existant ne convient (-> déclenche le recruteur).

Le routeur ne fait qu'émettre une décision (`RouteDecision`) ; l'exécution est
gérée par le superviseur.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.agents.registry import registry
from app.config import settings
from app.models.ollama import OllamaClient

logger = logging.getLogger("angeleck.router")


@dataclass
class RouteDecision:
    """Résultat du routage."""

    agent_keys: List[str] = field(default_factory=list)
    needs_new_agent: bool = False
    missing_skill: str = ""
    reasoning: str = ""
    confidence: float = 0.0


# Mots-clés indicatifs par agent (français + anglais) pour le pré-scoring.
KEYWORD_MAP = {
    "writer": [
        "publicité", "pub", "ad", "copy", "copywriting", "email", "vente",
        "script", "storytelling", "accroche", "slogan", "newsletter", "page de vente",
    ],
    "marketing": [
        "stratégie", "marketing", "tunnel", "funnel", "acquisition", "client",
        "positionnement", "business", "campagne", "go-to-market", "lancement",
    ],
    "code": [
        "code", "script python", "automatiser", "automatisation", "bug", "api",
        "fonction", "programme", "développe", "scrap", "intégration",
    ],
    "visual": [
        "image", "vidéo", "video", "prompt", "branding", "logo", "design",
        "visuel", "charte", "midjourney", "illustration",
    ],
    "data": [
        "csv", "excel", "données", "data", "analyse", "statistique", "rapport",
        "tableau", "dataset", "graphique", "kpi",
    ],
}


class SkillRouter:
    """Aiguilleur de compétences."""

    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self._client = client or OllamaClient()

    # ------------------------------------------------------------------ #
    def _keyword_scores(self, text: str) -> dict[str, int]:
        text_low = text.lower()
        scores: dict[str, int] = {}
        for key, words in KEYWORD_MAP.items():
            # On ne score que les agents réellement présents dans le registre.
            if not registry.exists(key):
                continue
            score = sum(1 for w in words if w in text_low)
            if score:
                scores[key] = score
        return scores

    def _catalogue_block(self) -> str:
        lines = []
        for spec in registry.specs():
            lines.append(
                f"- {spec.key}: {spec.role}. Compétences: {', '.join(spec.skills)}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    async def route(self, request: str) -> RouteDecision:
        """Décide quel(s) agent(s) traiteront la requête."""
        keyword_scores = self._keyword_scores(request)

        # Tentative de routage par LLM (plus fin, gère le multi-agent et le manque).
        llm_decision = await self._route_with_llm(request, keyword_scores)
        if llm_decision is not None:
            return llm_decision

        # Fallback purement heuristique si le LLM est indisponible.
        if keyword_scores:
            ordered = sorted(keyword_scores, key=keyword_scores.get, reverse=True)
            return RouteDecision(
                agent_keys=ordered[:2],
                reasoning="Routage heuristique par mots-clés.",
                confidence=0.5,
            )

        # Aucun signal : on tente le marketing par défaut, sinon recrutement.
        if registry.exists("marketing"):
            return RouteDecision(
                agent_keys=["marketing"],
                reasoning="Aucun signal clair — agent généraliste par défaut.",
                confidence=0.2,
            )
        return RouteDecision(needs_new_agent=True, missing_skill=request[:120])

    async def _route_with_llm(
        self, request: str, hints: dict[str, int]
    ) -> Optional[RouteDecision]:
        """Demande au cerveau de choisir dans le catalogue (JSON strict)."""
        prompt = (
            "Tu es le ROUTEUR du cerveau central Angeleck OS. Analyse la demande "
            "utilisateur et choisis le ou les agents les plus adaptés PARMI ce "
            "catalogue :\n\n"
            f"{self._catalogue_block()}\n\n"
            f"Indice (scores mots-clés) : {hints or 'aucun'}\n\n"
            f"Demande : \"{request}\"\n\n"
            "Réponds UNIQUEMENT en JSON valide avec ce schéma :\n"
            '{"agent_keys": ["..."], "needs_new_agent": false, '
            '"missing_skill": "", "reasoning": "...", "confidence": 0.0}\n'
            "Si AUCUN agent du catalogue ne possède la compétence requise, mets "
            'needs_new_agent=true et décris la compétence manquante dans '
            '"missing_skill". Sinon laisse agent_keys non vide. confidence ∈ [0,1].'
        )
        try:
            raw = await self._client.chat(
                [{"role": "user", "content": prompt}],
                model=settings.ollama_brain_model,
                temperature=0.1,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Routage LLM indisponible : %s", exc)
            return None

        data = _extract_json(raw)
        if not data:
            return None

        agent_keys = [k for k in data.get("agent_keys", []) if registry.exists(k)]
        needs_new = bool(data.get("needs_new_agent", False))
        # Cohérence : si le LLM dit "nouvel agent" mais a quand même donné des clés valides,
        # on privilégie l'exécution avec les agents existants.
        if agent_keys:
            needs_new = False
        return RouteDecision(
            agent_keys=agent_keys,
            needs_new_agent=needs_new and not agent_keys,
            missing_skill=data.get("missing_skill", "") or request[:120],
            reasoning=data.get("reasoning", ""),
            confidence=float(data.get("confidence", 0.0) or 0.0),
        )


def _extract_json(text: str) -> Optional[dict]:
    """Extrait le premier objet JSON d'une réponse LLM."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


# Singleton
router = SkillRouter()
