"""
Couche d'accès aux modèles IA via Ollama local.

Angeleck OS est 100 % local : aucun appel à une API cloud. Tous les modèles
(Llama, Mistral, Qwen, Phi...) tournent via un serveur Ollama.

Ce module fournit :
  * `OllamaClient` — client async minimaliste (httpx) pour /api/chat et /api/tags.
  * `get_llm()`    — fabrique un `ChatOllama` LangChain (si langchain installé).
  * `list_available_models()` — découverte des modèles installés.

La conception est défensive : si LangChain n'est pas disponible, on retombe
sur le client httpx brut. Si Ollama n'est pas joignable, on lève une erreur
explicite plutôt que de planter silencieusement.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger("angeleck.ollama")


class OllamaUnavailableError(RuntimeError):
    """Levée quand le serveur Ollama est injoignable."""


class OllamaClient:
    """Client asynchrone léger pour l'API Ollama."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout or settings.ollama_timeout

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **options: Any,
    ) -> str:
        """
        Envoie une conversation à Ollama et renvoie le texte de réponse.

        `messages` suit le format OpenAI/Ollama :
            [{"role": "system", "content": "..."},
             {"role": "user", "content": "..."}]
        """
        model = model or settings.ollama_agent_model
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": (
                    temperature
                    if temperature is not None
                    else settings.ollama_temperature
                ),
                **options,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "").strip()
        except httpx.ConnectError as exc:
            raise OllamaUnavailableError(
                f"Ollama injoignable sur {self.base_url}. "
                "Lancez `ollama serve` ou le conteneur Docker `ollama`."
            ) from exc
        except httpx.HTTPStatusError as exc:
            # Souvent : modèle non installé -> message clair.
            raise OllamaUnavailableError(
                f"Ollama a répondu {exc.response.status_code} pour le modèle "
                f"'{model}'. Avez-vous fait `ollama pull {model}` ?"
            ) from exc

    async def generate(self, prompt: str, model: Optional[str] = None, **opts: Any) -> str:
        """Raccourci pour une simple complétion sans historique."""
        return await self.chat([{"role": "user", "content": prompt}], model=model, **opts)

    async def list_models(self) -> List[str]:
        """Renvoie la liste des modèles installés localement."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError:
            return []

    async def ping(self) -> bool:
        """Vérifie que le serveur Ollama répond."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False


# Singleton réutilisable
ollama_client = OllamaClient()


async def list_available_models() -> List[str]:
    """Liste des modèles disponibles (helper async)."""
    return await ollama_client.list_models()


def get_llm(model: Optional[str] = None, temperature: Optional[float] = None):
    """
    Fabrique un LLM LangChain (`ChatOllama`) pour usage dans LangGraph/LangChain.

    Retombe sur `None` si langchain_ollama n'est pas installé : le code appelant
    utilisera alors `OllamaClient` directement.
    """
    try:
        from langchain_ollama import ChatOllama
    except ImportError:  # pragma: no cover - dépendance optionnelle
        logger.warning("langchain_ollama indisponible — fallback OllamaClient brut.")
        return None

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model or settings.ollama_agent_model,
        temperature=(
            temperature if temperature is not None else settings.ollama_temperature
        ),
    )
