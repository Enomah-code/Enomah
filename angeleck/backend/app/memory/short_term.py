"""
Mémoire court terme : contexte conversationnel récent.

Stockée dans Redis (rapide, TTL automatique). Si Redis est indisponible,
un fallback en mémoire process est utilisé pour ne jamais bloquer le système.
"""
import json
from collections import defaultdict, deque

from loguru import logger

from app.config import get_settings

try:
    import redis.asyncio as aioredis

    _REDIS = True
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore
    _REDIS = False


class ShortTermMemory:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        # Fallback local : {session_id: deque[ {role, content} ]}
        self._local: dict[str, deque] = defaultdict(lambda: deque(maxlen=40))

    async def connect(self) -> None:
        if not _REDIS:
            logger.warning("redis non installé — mémoire court terme locale.")
            return
        try:
            self._client = aioredis.from_url(
                self.settings.redis_url, decode_responses=True
            )
            await self._client.ping()
            logger.info("Mémoire court terme connectée à Redis.")
        except Exception as e:  # pragma: no cover
            logger.warning(f"Redis injoignable ({e}) — fallback local activé.")
            self._client = None

    def _key(self, session_id: str) -> str:
        return f"angeleck:stm:{session_id}"

    async def add(self, session_id: str, role: str, content: str) -> None:
        entry = json.dumps({"role": role, "content": content})
        if self._client:
            key = self._key(session_id)
            await self._client.rpush(key, entry)
            await self._client.ltrim(key, -40, -1)
            await self._client.expire(key, self.settings.short_term_ttl_seconds)
        else:
            self._local[session_id].append({"role": role, "content": content})

    async def get_context(
        self, session_id: str, max_messages: int = 10
    ) -> list[dict]:
        """Retourne les derniers messages au format LangChain (role/content)."""
        if self._client:
            raw = await self._client.lrange(self._key(session_id), -max_messages, -1)
            return [json.loads(r) for r in raw]
        return list(self._local[session_id])[-max_messages:]

    async def clear(self, session_id: str) -> None:
        if self._client:
            await self._client.delete(self._key(session_id))
        else:
            self._local.pop(session_id, None)
