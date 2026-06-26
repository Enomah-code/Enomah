"""
Classe de base de tous les agents Angeleck.

Un agent = une identité (nom, rôle), un ensemble de compétences, une liste
d'outils autorisés, un prompt système, et un modèle Ollama. La méthode `run`
construit le prompt final (système + mémoire + contexte + mission) et interroge
le LLM local.

Tous les agents — natifs ou générés dynamiquement par le recruteur — héritent
de `BaseAgent` ou produisent une `AgentSpec` interprétée par `GenericAgent`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.models.ollama import OllamaClient
from app.tools import TOOL_REGISTRY


@dataclass
class AgentSpec:
    """Spécification déclarative d'un agent (sérialisable, persistable)."""

    key: str
    name: str
    role: str
    description: str = ""
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    system_prompt: str = ""
    model: str = ""
    origin: str = "native"  # native | generated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "skills": self.skills,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "origin": self.origin,
        }


class BaseAgent:
    """Agent exécutable basé sur une `AgentSpec`."""

    spec: AgentSpec

    def __init__(self, spec: Optional[AgentSpec] = None, client: Optional[OllamaClient] = None):
        if spec is not None:
            self.spec = spec
        elif not hasattr(self, "spec"):
            raise ValueError("Un AgentSpec doit être fourni.")
        self._client = client or OllamaClient()

    # ------------------------------------------------------------------ #
    @property
    def key(self) -> str:
        return self.spec.key

    @property
    def name(self) -> str:
        return self.spec.name

    def available_tools(self) -> Dict[str, Any]:
        """Outils réellement disponibles pour cet agent."""
        return {t: TOOL_REGISTRY[t] for t in self.spec.tools if t in TOOL_REGISTRY}

    # ------------------------------------------------------------------ #
    def _build_messages(
        self,
        task: str,
        memory_context: str = "",
        extra_context: str = "",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """Assemble la liste de messages envoyée au LLM."""
        system = self.spec.system_prompt.strip()
        if self.spec.tools:
            system += (
                "\n\nOutils disponibles : " + ", ".join(self.spec.tools) +
                ". Demande explicitement leur usage si nécessaire."
            )
        messages: List[Dict[str, str]] = [{"role": "system", "content": system}]

        if memory_context:
            messages.append(
                {"role": "system", "content": f"[MÉMOIRE]\n{memory_context}"}
            )
        if history:
            messages.extend(history)

        user_block = task
        if extra_context:
            user_block = f"{task}\n\n[CONTEXTE FOURNI]\n{extra_context}"
        messages.append({"role": "user", "content": user_block})
        return messages

    async def run(
        self,
        task: str,
        memory_context: str = "",
        extra_context: str = "",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Exécute la mission et renvoie la réponse texte de l'agent."""
        messages = self._build_messages(task, memory_context, extra_context, history)
        model = self.spec.model or None
        return await self._client.chat(messages, model=model)


class GenericAgent(BaseAgent):
    """Agent instancié uniquement à partir d'une `AgentSpec` (cas générés)."""

    def __init__(self, spec: AgentSpec, client: Optional[OllamaClient] = None):
        super().__init__(spec=spec, client=client)
