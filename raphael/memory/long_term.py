import json
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from loguru import logger


class LongTermMemory:
    """
    Mémoire à long terme basée sur ChromaDB (vecteurs sémantiques).
    Stocke les connaissances accumulées, leçons apprises, résultats de tâches.
    """

    def __init__(self, persist_path: str = "./raphael_vectors"):
        self._path = Path(persist_path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collections: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._fallback_store: dict[str, list[dict]] = {}

    async def _init_chromadb(self) -> bool:
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(self._path))
            return True
        except ImportError:
            logger.warning("ChromaDB non disponible, utilisation du fallback JSON")
            return False
        except Exception as e:
            logger.warning(f"ChromaDB init échouée: {e}, utilisation du fallback JSON")
            return False

    async def _get_collection(self, namespace: str):
        if self._client is None:
            await self._init_chromadb()
        if self._client is not None:
            try:
                if namespace not in self._collections:
                    self._collections[namespace] = self._client.get_or_create_collection(
                        name=namespace,
                        metadata={"hnsw:space": "cosine"}
                    )
                return self._collections[namespace]
            except Exception as e:
                logger.warning(f"Collection ChromaDB {namespace}: {e}")
        return None

    def _embed_fallback(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    async def store(
        self,
        namespace: str,
        content: str,
        metadata: dict | None = None,
        doc_id: str | None = None,
    ) -> str:
        async with self._lock:
            doc_id = doc_id or hashlib.md5(f"{namespace}{content}{datetime.now()}".encode()).hexdigest()
            meta = {
                "namespace": namespace,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {}),
            }
            collection = await self._get_collection(namespace)
            if collection is not None:
                try:
                    collection.upsert(
                        documents=[content],
                        metadatas=[meta],
                        ids=[doc_id],
                    )
                    return doc_id
                except Exception as e:
                    logger.error(f"ChromaDB upsert: {e}")

            # Fallback JSON
            if namespace not in self._fallback_store:
                self._fallback_store[namespace] = []
            self._fallback_store[namespace].append({
                "id": doc_id,
                "content": content,
                "metadata": meta,
            })
            self._save_fallback()
            return doc_id

    async def search(
        self,
        namespace: str,
        query: str,
        n_results: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[dict]:
        async with self._lock:
            collection = await self._get_collection(namespace)
            if collection is not None:
                try:
                    where = filter_metadata if filter_metadata else None
                    results = collection.query(
                        query_texts=[query],
                        n_results=min(n_results, collection.count() or 1),
                        where=where,
                        include=["documents", "metadatas", "distances"],
                    )
                    docs = results.get("documents", [[]])[0]
                    metas = results.get("metadatas", [[]])[0]
                    dists = results.get("distances", [[]])[0]
                    return [
                        {"content": d, "metadata": m, "score": 1 - dist}
                        for d, m, dist in zip(docs, metas, dists)
                    ]
                except Exception as e:
                    logger.error(f"ChromaDB search: {e}")

            # Fallback: keyword search
            entries = self._fallback_store.get(namespace, [])
            query_lower = query.lower()
            matches = [
                {"content": e["content"], "metadata": e["metadata"], "score": 0.5}
                for e in entries
                if query_lower in e["content"].lower()
            ]
            return matches[:n_results]

    async def get_agent_learnings(self, agent_name: str, topic: str) -> list[dict]:
        return await self.search(f"agent_{agent_name}", topic, n_results=10)

    async def store_task_result(self, agent_name: str, task: str, result: str, success: bool) -> str:
        return await self.store(
            namespace=f"agent_{agent_name}",
            content=f"TASK: {task}\nRESULT: {result}",
            metadata={"success": str(success), "type": "task_result"},
        )

    async def store_world_knowledge(self, topic: str, content: str, source: str = "") -> str:
        return await self.store(
            namespace="world_knowledge",
            content=content,
            metadata={"topic": topic, "source": source},
        )

    def _save_fallback(self) -> None:
        fallback_file = self._path / "fallback_store.json"
        try:
            with open(fallback_file, "w", encoding="utf-8") as f:
                json.dump(self._fallback_store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Fallback save: {e}")

    def _load_fallback(self) -> None:
        fallback_file = self._path / "fallback_store.json"
        if fallback_file.exists():
            try:
                with open(fallback_file, encoding="utf-8") as f:
                    self._fallback_store = json.load(f)
            except Exception as e:
                logger.error(f"Fallback load: {e}")

    async def initialize(self) -> None:
        self._load_fallback()
        await self._init_chromadb()
        logger.info("Mémoire à long terme initialisée")
