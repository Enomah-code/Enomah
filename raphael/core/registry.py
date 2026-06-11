import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
from loguru import logger


class AgentSpec(BaseModel):
    name: str
    role: str
    expertise: list[str]
    system_prompt: str
    model: str = "claude-sonnet-4-6"
    tools: list[str] = []
    active: bool = True
    performance_score: float = 1.0
    task_count: int = 0
    success_count: int = 0
    created_at: datetime = datetime.now()
    last_used: Optional[datetime] = None
    metadata: dict[str, Any] = {}

    @property
    def success_rate(self) -> float:
        if self.task_count == 0:
            return 1.0
        return self.success_count / self.task_count

    def record_task(self, success: bool) -> None:
        self.task_count += 1
        if success:
            self.success_count += 1
        self.last_used = datetime.now()
        # Exponential moving average for performance score
        alpha = 0.1
        self.performance_score = (1 - alpha) * self.performance_score + alpha * (1.0 if success else 0.0)


class AgentRegistry:
    """Registre persistant de tous les agents du réseau Raphaël."""

    def __init__(self, db_path: str = "./raphael_registry.json"):
        self._path = Path(db_path)
        self._agents: dict[str, AgentSpec] = {}
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        await self._load()
        logger.info(f"Registre initialisé: {len(self._agents)} agents")

    async def register(self, spec: AgentSpec) -> None:
        async with self._lock:
            self._agents[spec.name.lower()] = spec
            await self._save()
            logger.info(f"Agent enregistré: {spec.name} ({spec.role})")

    async def get(self, name: str) -> Optional[AgentSpec]:
        async with self._lock:
            return self._agents.get(name.lower())

    async def get_all(self) -> list[AgentSpec]:
        async with self._lock:
            return [a for a in self._agents.values() if a.active]

    async def find_by_expertise(self, required: list[str]) -> list[AgentSpec]:
        async with self._lock:
            scored: list[tuple[float, AgentSpec]] = []
            for agent in self._agents.values():
                if not agent.active:
                    continue
                req_lower = [r.lower() for r in required]
                exp_lower = [e.lower() for e in agent.expertise]
                matches = sum(
                    1 for r in req_lower
                    if any(r in e or e in r for e in exp_lower)
                )
                if matches > 0:
                    score = (matches / len(required)) * agent.performance_score
                    scored.append((score, agent))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [a for _, a in scored]

    async def update_performance(self, name: str, success: bool) -> None:
        async with self._lock:
            agent = self._agents.get(name.lower())
            if agent:
                agent.record_task(success)
                await self._save()

    async def deactivate(self, name: str) -> None:
        async with self._lock:
            agent = self._agents.get(name.lower())
            if agent:
                agent.active = False
                await self._save()

    async def exists(self, name: str) -> bool:
        async with self._lock:
            return name.lower() in self._agents

    async def list_names(self) -> list[str]:
        async with self._lock:
            return [a.name for a in self._agents.values() if a.active]

    async def get_stats(self) -> dict:
        async with self._lock:
            total = len(self._agents)
            active = sum(1 for a in self._agents.values() if a.active)
            total_tasks = sum(a.task_count for a in self._agents.values())
            return {
                "total_agents": total,
                "active_agents": active,
                "total_tasks_processed": total_tasks,
                "agents": [
                    {
                        "name": a.name,
                        "role": a.role,
                        "tasks": a.task_count,
                        "success_rate": round(a.success_rate, 3),
                        "performance_score": round(a.performance_score, 3),
                    }
                    for a in self._agents.values()
                ],
            }

    async def _save(self) -> None:
        try:
            data = {name: spec.model_dump(mode="json") for name, spec in self._agents.items()}
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Registry save error: {e}")

    async def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            for name, spec_data in data.items():
                try:
                    self._agents[name] = AgentSpec(**spec_data)
                except Exception as e:
                    logger.warning(f"Could not load agent {name}: {e}")
        except Exception as e:
            logger.error(f"Registry load error: {e}")
