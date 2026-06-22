"""
Registre central des agents.

- Charge les agents initiaux + les agents générés (persistés en base).
- Fournit l'accès aux agents par clé.
- Permet l'ajout dynamique d'agents (utilisé par le recruteur / factory).
"""
from loguru import logger
from sqlalchemy import select

from app.agents.base import Agent, AgentDefinition
from app.agents.definitions import INITIAL_AGENTS
from app.database import session_scope
from app.database.models import AgentRecord
from app.memory import LongTermMemory, ShortTermMemory


class AgentRegistry:
    def __init__(
        self, short_memory: ShortTermMemory, long_memory: LongTermMemory
    ) -> None:
        self.short_memory = short_memory
        self.long_memory = long_memory
        self._agents: dict[str, Agent] = {}

    async def load(self) -> None:
        """Initialise le registre : agents initiaux puis agents persistés."""
        # 1) Agents initiaux (upsert en base)
        for definition in INITIAL_AGENTS:
            await self._persist_definition(definition)
            self._register(definition)

        # 2) Agents générés persistés en base
        async with session_scope() as session:
            rows = (await session.execute(select(AgentRecord))).scalars().all()
            for row in rows:
                if row.key in self._agents or not row.is_active:
                    continue
                definition = AgentDefinition(
                    key=row.key,
                    name=row.name,
                    role=row.role,
                    skills=list(row.skills or []),
                    tools=list(row.tools or []),
                    system_prompt=row.system_prompt or "",
                    model=row.model or "",
                    is_generated=row.is_generated,
                )
                self._register(definition)

        logger.info(f"Registre chargé : {len(self._agents)} agents disponibles.")

    def _register(self, definition: AgentDefinition) -> Agent:
        agent = Agent(definition, self.short_memory, self.long_memory)
        self._agents[definition.key] = agent
        return agent

    async def _persist_definition(self, definition: AgentDefinition) -> None:
        """Crée ou met à jour l'enregistrement d'un agent en base."""
        async with session_scope() as session:
            existing = (
                await session.execute(
                    select(AgentRecord).where(AgentRecord.key == definition.key)
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(
                    AgentRecord(
                        key=definition.key,
                        name=definition.name,
                        role=definition.role,
                        skills=definition.skills,
                        tools=definition.tools,
                        system_prompt=definition.system_prompt,
                        model=definition.model,
                        is_generated=definition.is_generated,
                    )
                )
            else:
                existing.name = definition.name
                existing.role = definition.role
                existing.skills = definition.skills
                existing.tools = definition.tools
                existing.system_prompt = definition.system_prompt

    async def add_agent(self, definition: AgentDefinition) -> Agent:
        """Ajoute un agent au runtime + en base (utilisé par la factory)."""
        await self._persist_definition(definition)
        agent = self._register(definition)
        logger.info(f"Nouvel agent enregistré : {definition.key} ({definition.name})")
        return agent

    def get(self, key: str) -> Agent | None:
        return self._agents.get(key)

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def keys(self) -> list[str]:
        return list(self._agents.keys())

    def catalog(self) -> str:
        """Description textuelle du catalogue pour le routage du cerveau."""
        return "\n".join(
            f"- {a.key}: {a.name} — {a.definition.role} "
            f"(compétences: {', '.join(a.definition.skills)})"
            for a in self._agents.values()
        )

    async def record_mission(self, agent_key: str, success: bool) -> None:
        """Met à jour les compteurs de performance d'un agent."""
        async with session_scope() as session:
            row = (
                await session.execute(
                    select(AgentRecord).where(AgentRecord.key == agent_key)
                )
            ).scalar_one_or_none()
            if row:
                row.tasks_count += 1
                if success:
                    row.success_count += 1
