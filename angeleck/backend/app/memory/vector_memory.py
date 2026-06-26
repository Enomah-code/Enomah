"""
Mémoire longue d'Angeleck OS — base vectorielle ChromaDB.

Rôle : mémoriser de façon sémantique les conversations, projets, préférences,
résultats et connaissances acquises, puis les retrouver par similarité afin
d'enrichir le contexte du cerveau central et des agents (RAG).

Conception défensive : si ChromaDB n'est pas installé ou pas joignable, la
mémoire bascule en mode "no-op" (les écritures sont ignorées et les recherches
renvoient une liste vide) pour ne jamais bloquer le système.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger("angeleck.vector")


class VectorMemory:
    """Wrapper autour de ChromaDB (mode HTTP client de préférence)."""

    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._enabled = False
        self._connect()

    # ------------------------------------------------------------------ #
    def _connect(self) -> None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
        except ImportError:  # pragma: no cover
            logger.warning("chromadb non installé — mémoire longue désactivée.")
            return

        try:
            # Connexion au serveur ChromaDB (conteneur Docker dédié).
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            # Fonction d'embedding locale (sentence-transformers) — pas de cloud.
            embedding_fn = self._build_embedding_fn()
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection,
                embedding_function=embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )
            self._enabled = True
            logger.info("Mémoire vectorielle ChromaDB connectée.")
        except Exception as exc:  # noqa: BLE001 - on tolère toute panne de connexion
            logger.warning("ChromaDB injoignable (%s) — mémoire longue désactivée.", exc)
            self._enabled = False

    @staticmethod
    def _build_embedding_fn():
        """Crée la fonction d'embedding sentence-transformers (locale)."""
        try:
            from chromadb.utils import embedding_functions

            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.embedding_model
            )
        except Exception:  # noqa: BLE001 - retombe sur l'embedding par défaut
            return None

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ------------------------------------------------------------------ #
    def remember(
        self,
        text: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Stocke un souvenir (upsert)."""
        if not self._enabled or not text.strip():
            return False
        try:
            self._collection.upsert(
                documents=[text],
                ids=[doc_id],
                metadatas=[metadata or {}],
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Échec écriture mémoire: %s", exc)
            return False

    def recall(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Recherche sémantique : renvoie les k souvenirs les plus proches."""
        if not self._enabled or not query.strip():
            return []
        try:
            res = self._collection.query(
                query_texts=[query],
                n_results=k,
                where=where,
            )
            documents = res.get("documents", [[]])[0]
            metadatas = res.get("metadatas", [[]])[0]
            distances = res.get("distances", [[]])[0]
            return [
                {"text": doc, "metadata": meta, "distance": dist}
                for doc, meta, dist in zip(documents, metadatas, distances)
            ]
        except Exception as exc:  # noqa: BLE001
            logger.error("Échec lecture mémoire: %s", exc)
            return []

    def build_context(self, query: str, k: int = 5) -> str:
        """Construit un bloc de contexte texte à injecter dans un prompt."""
        memories = self.recall(query, k=k)
        if not memories:
            return ""
        lines = [f"- {m['text']}" for m in memories]
        return "Contexte mémorisé pertinent :\n" + "\n".join(lines)


# Singleton applicatif
vector_memory = VectorMemory()
