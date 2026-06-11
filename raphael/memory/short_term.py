import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Any
from pydantic import BaseModel


class MemoryEntry(BaseModel):
    id: str
    session_id: str
    role: str  # user | assistant | agent
    content: str
    metadata: dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    ttl_minutes: int = 60


class ShortTermMemory:
    """Mémoire à court terme par session — contexte conversationnel fenêtré."""

    def __init__(self, max_entries: int = 100, ttl_minutes: int = 60):
        self._store: dict[str, deque[MemoryEntry]] = {}
        self._lock = asyncio.Lock()
        self.max_entries = max_entries
        self.ttl_minutes = ttl_minutes

    async def add(self, session_id: str, role: str, content: str, metadata: dict | None = None) -> None:
        async with self._lock:
            if session_id not in self._store:
                self._store[session_id] = deque(maxlen=self.max_entries)
            entry = MemoryEntry(
                id=f"{session_id}_{datetime.now().timestamp()}",
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata or {},
            )
            self._store[session_id].append(entry)

    async def get_context(self, session_id: str, max_messages: int = 20) -> list[dict]:
        async with self._lock:
            if session_id not in self._store:
                return []
            cutoff = datetime.now() - timedelta(minutes=self.ttl_minutes)
            valid = [
                e for e in self._store[session_id]
                if e.timestamp > cutoff
            ]
            recent = valid[-max_messages:]
            return [{"role": e.role if e.role in ("user", "assistant") else "user",
                     "content": f"[{e.role}]: {e.content}" if e.role not in ("user", "assistant") else e.content}
                    for e in recent]

    async def get_summary(self, session_id: str) -> str:
        async with self._lock:
            entries = self._store.get(session_id, deque())
            if not entries:
                return "Aucun historique de conversation."
            lines = [f"[{e.role}] {e.content[:200]}" for e in list(entries)[-10:]]
            return "\n".join(lines)

    async def clear_session(self, session_id: str) -> None:
        async with self._lock:
            self._store.pop(session_id, None)

    async def cleanup_expired(self) -> int:
        async with self._lock:
            cutoff = datetime.now() - timedelta(minutes=self.ttl_minutes)
            removed = 0
            for sid in list(self._store.keys()):
                before = len(self._store[sid])
                self._store[sid] = deque(
                    (e for e in self._store[sid] if e.timestamp > cutoff),
                    maxlen=self.max_entries
                )
                removed += before - len(self._store[sid])
                if not self._store[sid]:
                    del self._store[sid]
            return removed
