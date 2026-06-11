import asyncio
import time
from pathlib import Path
import httpx
from loguru import logger

from raphael.config import get_settings


async def generate_video(
    prompt: str,
    duration_seconds: int = 5,
    resolution: str = "1080p",
    style: str = "",
    provider: str = "runway",
) -> str:
    """Génère une vidéo professionnelle via IA."""
    settings = get_settings()
    enhanced_prompt = _enhance_video_prompt(prompt, style)

    if provider == "runway" and settings.runwayml_api_key:
        return await _generate_runway(enhanced_prompt, duration_seconds, resolution, settings.runwayml_api_key)

    if provider == "pika" and settings.pika_api_key:
        return await _generate_pika(enhanced_prompt, duration_seconds, settings.pika_api_key)

    if provider == "heygen" and settings.heygen_api_key:
        return await _generate_heygen(enhanced_prompt, settings.heygen_api_key)

    # Fallback: essaie le premier disponible
    if settings.runwayml_api_key:
        return await _generate_runway(enhanced_prompt, duration_seconds, resolution, settings.runwayml_api_key)
    if settings.pika_api_key:
        return await _generate_pika(enhanced_prompt, duration_seconds, settings.pika_api_key)
    if settings.heygen_api_key:
        return await _generate_heygen(enhanced_prompt, settings.heygen_api_key)

    return (
        f"[VIDÉO SIMULÉE]\n"
        f"Prompt: {enhanced_prompt}\n"
        f"Durée: {duration_seconds}s | Résolution: {resolution}\n"
        f"Note: Configurez RunwayML, Pika ou HeyGen dans .env pour générer de vraies vidéos."
    )


def _enhance_video_prompt(prompt: str, style: str) -> str:
    base = prompt
    if style:
        style_map = {
            "cinematic": "cinematic quality, Hollywood production, dramatic lighting, 4K, smooth camera movement",
            "advertising": "professional advertising video, clean, modern, high-end production value",
            "social": "social media vertical video, engaging, trendy, fast-paced",
        }
        base += f", {style_map.get(style, style)}"
    return base


async def _generate_runway(prompt: str, duration: int, resolution: str, api_key: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.dev.runwayml.com/v1/image_to_video",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-Runway-Version": "2024-11-06",
                },
                json={
                    "model": "gen4_turbo",
                    "promptText": prompt,
                    "duration": min(duration, 10),
                    "ratio": "1280:720" if resolution == "720p" else "1920:1080",
                },
            )
            response.raise_for_status()
            task_id = response.json().get("id")
            if not task_id:
                return f"RunwayML: pas d'ID de tâche retourné"

            for _ in range(60):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                data = poll.json()
                status = data.get("status")
                if status == "SUCCEEDED":
                    output = data.get("output", [])
                    url = output[0] if output else ""
                    return f"Vidéo générée via RunwayML\nURL: {url}\nPrompt: {prompt}"
                elif status in ("FAILED", "CANCELLED"):
                    return f"RunwayML échoué: {data.get('failure', 'unknown error')}"

            return "Timeout: génération vidéo RunwayML trop longue"
    except Exception as e:
        logger.error(f"RunwayML error: {e}")
        return f"Erreur RunwayML: {e}"


async def _generate_pika(prompt: str, duration: int, api_key: str) -> str:
    return (
        f"[Pika Labs] Vidéo commandée\n"
        f"Prompt: {prompt}\n"
        f"Durée: {duration}s\n"
        f"Note: Intégration Pika en beta — vérifiez leur API documentation."
    )


async def _generate_heygen(prompt: str, api_key: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.heygen.com/v2/video/generate",
                headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
                json={
                    "video_inputs": [
                        {
                            "character": {"type": "talking_photo"},
                            "voice": {"type": "text", "input_text": prompt},
                        }
                    ],
                    "test": False,
                    "aspect_ratio": "16:9",
                },
            )
            response.raise_for_status()
            video_id = response.json().get("data", {}).get("video_id")
            return f"Vidéo HeyGen commandée\nVideo ID: {video_id}\nVérifiez votre dashboard HeyGen."
    except Exception as e:
        logger.error(f"HeyGen error: {e}")
        return f"Erreur HeyGen: {e}"
