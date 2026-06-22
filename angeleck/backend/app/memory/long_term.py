"""
Mémoire long terme : connaissances vectorielles (ChromaDB).

Stocke les résultats de missions, connaissances métier et apprentissages.
Recherche sémantique par similarité pour enrichir le contexte des agents.
Les embeddings sont calculés localement via Ollama (nomic-embed-text).
"""
from loguru import logger

from app.config import get_settings

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    _CHROMA = True
except Exception:  # pragma: no cover
    chromadb = None  # type: ignore
    _CHROMA = False


class LongTermMemory:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        self._collection = None
        self._embeddings = None
        # Fallback : liste en mémoire si Chroma absent
        self._local: list[dict] = []

    def connect(self) -> None:
        if not _CHROMA:
            logger.warning("chromadb non installé — mémoire long terme locale.")
            return
        try:
            self._client = chromadb.PersistentClient(
                path=self.settings.vector_db_path,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name="angeleck_knowledge",
                metadata={"hnsw:space": "cosine"},
            )
            # Embeddings via Ollama (peut échouer si Ollama down → fallback Chroma défaut)
            try:
                from app.llm import get_embeddings

                self._embeddings = get_embeddings()
            except Exception as e:  # pragma: no cover
                logger.warning(f"Embeddings Ollama indisponibles: {e}")
            logger.info("Mémoire long terme (ChromaDB) initialisée.")
        except Exception as e:  # pragma: no cover
            logger.warning(f"ChromaDB indisponible ({e}) — fallback local.")
            self._client = None

    def _embed(self, text: str) -> list[float] | None:
        if not self._embeddings:
            return None
        try:
            return self._embeddings.embed_query(text)
        except Exception as e:  # pragma: no cover
            logger.warning(f"Échec embedding: {e}")
            return None

    async def store(self, content: str, metadata: dict) -> None:
        import uuid

        doc_id = str(uuid.uuid4())
        if self._collection is not None:
            embedding = self._embed(content)
            kwargs = {
                "documents": [content],
                "metadatas": [metadata],
                "ids": [doc_id],
            }
            if embedding:
                kwargs["embeddings"] = [embedding]
            self._collection.add(**kwargs)
        else:
            self._local.append({"content": content, "metadata": metadata})

    async def store_mission_result(
        self, agent_key: str, task: str, result: str, success: bool
    ) -> None:
        content = f"Tâche: {task}\nRésultat: {result[:1500]}"
        await self.store(
            content,
            {"agent": agent_key, "success": success, "type": "mission"},
        )

    async def search(self, query: str, n_results: int = 4) -> list[dict]:
        """Recherche sémantique. Retourne [{content, metadata}]."""
        if self._collection is not None:
            try:
                embedding = self._embed(query)
                if embedding:
                    res = self._collection.query(
                        query_embeddings=[embedding], n_results=n_results
                    )
                else:
                    res = self._collection.query(
                        query_texts=[query], n_results=n_results
                    )
                docs = res.get("documents", [[]])[0]
                metas = res.get("metadatas", [[]])[0]
                return [
                    {"content": d, "metadata": m} for d, m in zip(docs, metas)
                ]
            except Exception as e:  # pragma: no cover
                logger.warning(f"Recherche vectorielle échouée: {e}")
                return []
        # Fallback naïf par mots-clés
        q = query.lower()
        scored = [
            item for item in self._local if any(w in item["content"].lower() for w in q.split())
        ]
        return scored[:n_results]

    async def get_agent_learnings(self, agent_key: str, task: str) -> list[dict]:
        results = await self.search(task, n_results=6)
        return [r for r in results if r["metadata"].get("agent") == agent_key][:3]
