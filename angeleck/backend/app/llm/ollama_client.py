"""
Couche d'accès aux modèles IA locaux via Ollama.

Angeleck OS n'a AUCUNE dépendance obligatoire à une API payante.
Tous les modèles (Llama 3, Mistral, Qwen, Phi, ...) sont servis par
Ollama et orchestrés au travers de LangChain (`langchain_ollama`).
"""
from functools import lru_cache

import httpx
from loguru import logger

from app.config import get_settings

try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings

    _LANGCHAIN_OLLAMA = True
except Exception:  # pragma: no cover - dépendance optionnelle à l'import
    ChatOllama = None  # type: ignore
    OllamaEmbeddings = None  # type: ignore
    _LANGCHAIN_OLLAMA = False


@lru_cache(maxsize=16)
def get_chat_model(model: str | None = None, temperature: float | None = None):
    """
    Retourne un client de chat LangChain branché sur Ollama.

    Le résultat est mis en cache par (modèle, température) pour éviter de
    recréer des clients à chaque requête.
    """
    settings = get_settings()
    if not _LANGCHAIN_OLLAMA:
        raise RuntimeError(
            "langchain_ollama n'est pas installé. Lancez "
            "`pip install langchain-ollama` ou utilisez l'image Docker fournie."
        )

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model or settings.agent_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
        timeout=settings.llm_request_timeout,
    )


@lru_cache(maxsize=1)
def get_embeddings():
    """Retourne le modèle d'embeddings local (pour la mémoire vectorielle)."""
    settings = get_settings()
    if not _LANGCHAIN_OLLAMA:
        raise RuntimeError("langchain_ollama n'est pas installé.")
    return OllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.embedding_model,
    )


async def health_check() -> dict:
    """
    Vérifie qu'Ollama est joignable et liste les modèles disponibles.
    Utilisé par l'endpoint /health et l'interface admin.
    """
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"available": True, "models": models}
    except Exception as e:  # pragma: no cover - dépend de l'environnement
        logger.warning(f"Ollama injoignable: {e}")
        return {"available": False, "models": [], "error": str(e)}


async def ensure_model(model: str) -> bool:
    """
    S'assure qu'un modèle est présent localement ; déclenche un `pull`
    si nécessaire. Renvoie True si le modèle est disponible.
    """
    settings = get_settings()
    status = await health_check()
    if not status["available"]:
        return False
    if any(model in m for m in status["models"]):
        return True
    try:
        logger.info(f"Téléchargement du modèle Ollama '{model}'...")
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{settings.ollama_base_url}/api/pull",
                json={"name": model},
            ) as resp:
                async for _ in resp.aiter_lines():
                    pass
        return True
    except Exception as e:  # pragma: no cover
        logger.error(f"Échec du pull de '{model}': {e}")
        return False
