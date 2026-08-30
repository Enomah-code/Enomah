import httpx
from loguru import logger

from raphael.config import get_settings

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


async def ask_gemini(
    prompt: str,
    system_instruction: str = "",
    model: str = "",
    use_search_grounding: bool = False,
) -> str:
    """Interroge Google AI Studio (Gemini) — utile pour le contexte long et le grounding Google Search."""
    settings = get_settings()

    if not settings.google_ai_studio_api_key:
        return (
            f"[GEMINI SIMULÉ]\n"
            f"Prompt: {prompt}\n"
            f"Note: Configurez GOOGLE_AI_STUDIO_API_KEY dans .env pour interroger Google AI Studio "
            f"(clé disponible sur https://aistudio.google.com/apikey)."
        )

    model_name = model or settings.google_ai_studio_model
    payload: dict = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if use_search_grounding:
        payload["tools"] = [{"google_search": {}}]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{_BASE_URL}/{model_name}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": settings.google_ai_studio_api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                return f"Gemini n'a retourné aucune réponse (feedback: {data.get('promptFeedback')})"

            parts = candidates[0].get("content", {}).get("parts", [])
            text = "\n".join(p.get("text", "") for p in parts if "text" in p).strip()

            sources = []
            grounding = candidates[0].get("groundingMetadata", {})
            for chunk in grounding.get("groundingChunks", []):
                web = chunk.get("web", {})
                if web.get("uri"):
                    sources.append(f"- {web.get('title', web['uri'])}: {web['uri']}")

            if sources:
                text += "\n\nSources (Google Search grounding):\n" + "\n".join(sources)

            return text or "Gemini a retourné une réponse vide."
    except httpx.HTTPStatusError as e:
        logger.error(f"Google AI Studio HTTP error: {e.response.status_code} {e.response.text}")
        return f"Erreur Google AI Studio ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        logger.error(f"Google AI Studio error: {e}")
        return f"Erreur Google AI Studio: {e}"
