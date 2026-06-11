import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from pydantic import BaseModel
import anthropic
from loguru import logger

from raphael.config import get_settings
from raphael.memory import ShortTermMemory, LongTermMemory


class AgentResponse(BaseModel):
    agent_name: str
    task: str
    result: str
    success: bool
    tools_used: list[str] = []
    elapsed_seconds: float = 0.0
    metadata: dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Classe de base pour tous les agents spécialisés du réseau Raphaël.
    Chaque agent est un expert de niveau Dieu dans son domaine.
    """

    name: str = "BaseAgent"
    role: str = "Generic"
    expertise: list[str] = []
    model_override: Optional[str] = None

    def __init__(
        self,
        short_term_memory: ShortTermMemory,
        long_term_memory: LongTermMemory,
    ):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        self.async_client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        self.short_memory = short_term_memory
        self.long_memory = long_term_memory
        self._model = self.model_override or self.settings.specialist_model

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Prompt système définissant l'identité et l'expertise de l'agent."""

    def get_tools(self) -> list[dict]:
        """Retourne les définitions d'outils disponibles pour cet agent."""
        return []

    async def execute(self, task: str, context: str = "", session_id: str = "default") -> AgentResponse:
        """Exécute une tâche et retourne une réponse structurée."""
        start = time.monotonic()
        tools_used: list[str] = []

        try:
            # Enrichit avec la mémoire à long terme
            learnings = await self.long_memory.get_agent_learnings(self.name, task)
            learning_context = ""
            if learnings:
                learning_context = "\n\nConnaissances pertinentes de mes expériences passées:\n" + \
                    "\n".join(f"- {l['content'][:300]}" for l in learnings[:3])

            messages = await self.short_memory.get_context(session_id, max_messages=10)
            messages.append({"role": "user", "content": f"{context}\n\nTâche: {task}{learning_context}".strip()})

            tools = self.get_tools()
            result = await self._run_with_tools(messages, tools, tools_used)

            # Stocke le résultat dans la mémoire à long terme
            await self.long_memory.store_task_result(self.name, task, result, success=True)
            await self.short_memory.add(session_id, "assistant", f"[{self.name}]: {result}")

            elapsed = time.monotonic() - start
            return AgentResponse(
                agent_name=self.name,
                task=task,
                result=result,
                success=True,
                tools_used=tools_used,
                elapsed_seconds=round(elapsed, 2),
            )

        except Exception as e:
            logger.error(f"[{self.name}] Erreur sur tâche '{task[:80]}': {e}")
            await self.long_memory.store_task_result(self.name, task, str(e), success=False)
            elapsed = time.monotonic() - start
            return AgentResponse(
                agent_name=self.name,
                task=task,
                result=f"Erreur: {e}",
                success=False,
                elapsed_seconds=round(elapsed, 2),
            )

    async def _run_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        tools_used: list[str],
    ) -> str:
        """Boucle agentic: appelle Claude et gère les tool calls jusqu'à la réponse finale."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": 8192,
            "system": self.system_prompt,
            "messages": messages,
            "thinking": {"type": "adaptive"},
        }
        if tools:
            kwargs["tools"] = tools

        for _iteration in range(20):  # Max 20 tours d'outils
            response = await self.async_client.messages.create(**kwargs)

            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tools_used.append(block.name)
                        tool_result = await self._call_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(tool_result),
                        })

                # Ajoute réponse + résultats d'outils pour le prochain tour
                kwargs["messages"] = list(kwargs["messages"]) + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results},
                ]
                continue

            # Autre stop reason (max_tokens, etc.)
            return self._extract_text(response)

        return self._extract_text(response)  # Sécurité: retourne après la limite

    async def _call_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Dispatch vers l'implémentation du tool. Sous-classes peuvent surcharger."""
        logger.warning(f"[{self.name}] Outil non implémenté: {tool_name}")
        return f"Outil {tool_name} non disponible dans cet environnement."

    def _extract_text(self, response) -> str:
        """Extrait le texte final de la réponse Claude."""
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()

    async def stream(self, task: str, context: str = "") -> AsyncIterator[str]:
        """Streaming de la réponse."""
        messages = [{"role": "user", "content": f"{context}\n\nTâche: {task}".strip()}]
        async with self.async_client.messages.stream(
            model=self._model,
            max_tokens=8192,
            system=self.system_prompt,
            messages=messages,
            thinking={"type": "adaptive"},
        ) as stream:
            async for text in stream.text_stream:
                yield text
