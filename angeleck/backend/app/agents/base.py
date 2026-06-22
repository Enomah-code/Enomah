"""
Cœur du système d'agents d'Angeleck OS.

Un agent est piloté par une `AgentDefinition` (identité, rôle, compétences,
outils, prompt système, modèle). La classe `Agent` exécute la boucle
"agentic" : appel du modèle Ollama, exécution des outils demandés, puis
synthèse finale — tout en s'enrichissant de la mémoire long terme.

Conforme à la structure demandée :
    Agent { name, role, skills, tools, memory, execute() }
"""
import time
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from app.config import get_settings
from app.llm import get_chat_model
from app.memory import LongTermMemory, ShortTermMemory
from app.tools import resolve_tools


@dataclass
class AgentDefinition:
    """Définition déclarative d'un agent (sérialisable en base)."""

    key: str
    name: str
    role: str
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    system_prompt: str = ""
    model: str = ""  # vide => modèle agent par défaut
    is_generated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "role": self.role,
            "skills": self.skills,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "is_generated": self.is_generated,
        }


@dataclass
class AgentResult:
    agent_key: str
    agent_name: str
    task: str
    result: str
    success: bool
    tools_used: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0


class Agent:
    """Agent exécutable construit à partir d'une `AgentDefinition`."""

    def __init__(
        self,
        definition: AgentDefinition,
        short_memory: ShortTermMemory,
        long_memory: LongTermMemory,
    ) -> None:
        self.definition = definition
        self.short_memory = short_memory
        self.long_memory = long_memory
        self.settings = get_settings()

    # --- Propriétés pratiques ---
    @property
    def key(self) -> str:
        return self.definition.key

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def model(self) -> str:
        return self.definition.model or self.settings.agent_model

    def _build_system_prompt(self, learnings: list[dict]) -> str:
        base = self.definition.system_prompt or (
            f"Tu es {self.name}, expert en {self.definition.role}. "
            f"Compétences: {', '.join(self.definition.skills)}."
        )
        if learnings:
            base += "\n\nConnaissances issues de tes missions passées:\n" + "\n".join(
                f"- {l['content'][:300]}" for l in learnings
            )
        base += (
            "\n\nRéponds de manière structurée, professionnelle et actionnable, "
            "en français."
        )
        return base

    async def execute(
        self, task: str, context: str = "", session_id: str = "default"
    ) -> AgentResult:
        """Exécute une mission et retourne un résultat structuré."""
        start = time.monotonic()
        tools_used: list[str] = []
        try:
            learnings = await self.long_memory.get_agent_learnings(self.key, task)
            system_prompt = self._build_system_prompt(learnings)

            history = await self.short_memory.get_context(session_id, max_messages=8)
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            user_content = f"{context}\n\nMission: {task}".strip()
            messages.append({"role": "user", "content": user_content})

            result_text = await self._run_agentic_loop(messages, tools_used)

            # Persiste l'apprentissage + le tour de conversation
            await self.long_memory.store_mission_result(
                self.key, task, result_text, success=True
            )
            await self.short_memory.add(
                session_id, "assistant", f"[{self.name}] {result_text}"
            )

            return AgentResult(
                agent_key=self.key,
                agent_name=self.name,
                task=task,
                result=result_text,
                success=True,
                tools_used=tools_used,
                elapsed_seconds=round(time.monotonic() - start, 2),
            )
        except Exception as e:
            logger.error(f"[{self.name}] échec sur '{task[:60]}': {e}")
            await self.long_memory.store_mission_result(
                self.key, task, str(e), success=False
            )
            return AgentResult(
                agent_key=self.key,
                agent_name=self.name,
                task=task,
                result=f"Erreur lors de l'exécution: {e}",
                success=False,
                elapsed_seconds=round(time.monotonic() - start, 2),
            )

    async def _run_agentic_loop(
        self, messages: list[dict], tools_used: list[str]
    ) -> str:
        """Boucle d'appels modèle + outils (LangChain / Ollama)."""
        llm = get_chat_model(self.model)
        tools = resolve_tools(self.definition.tools)
        tool_map = {t.name: t for t in tools}

        runnable = llm.bind_tools(tools) if tools else llm

        for _ in range(self.settings.max_agent_iterations):
            response = await runnable.ainvoke(messages)
            tool_calls = getattr(response, "tool_calls", None) or []

            if not tool_calls:
                return _extract_text(response)

            # Ajoute la réponse de l'assistant (avec les appels d'outils)
            messages.append(response)
            for call in tool_calls:
                name = call["name"]
                tools_used.append(name)
                tool = tool_map.get(name)
                if tool is None:
                    observation = f"Outil inconnu: {name}"
                else:
                    try:
                        observation = await _ainvoke_tool(tool, call.get("args", {}))
                    except Exception as e:
                        observation = f"Erreur outil {name}: {e}"
                messages.append(
                    {
                        "role": "tool",
                        "content": str(observation),
                        "tool_call_id": call.get("id", name),
                    }
                )

        # Dernier appel pour forcer une synthèse finale sans outils
        final = await llm.ainvoke(messages)
        return _extract_text(final)


async def _ainvoke_tool(tool, args: dict) -> Any:
    """Invoque un outil LangChain de façon asynchrone si possible."""
    try:
        return await tool.ainvoke(args)
    except NotImplementedError:
        return tool.invoke(args)


def _extract_text(response) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, list):
        parts = [
            c.get("text", "") if isinstance(c, dict) else str(c) for c in content
        ]
        return "\n".join(p for p in parts if p).strip()
    return str(content).strip()
