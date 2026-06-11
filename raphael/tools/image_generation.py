import base64
import asyncio
from pathlib import Path
from typing import Optional
import httpx
from loguru import logger

from raphael.config import get_settings


async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    style: str = "photorealistic",
    provider: str = "stability",
) -> str:
    """Génère une image professionnelle via IA."""
    settings = get_settings()
    enhanced_prompt = _enhance_prompt(prompt, style)

    if provider == "stability" and settings.stability_ai_api_key:
        return await _generate_stability(enhanced_prompt, negative_prompt, width, height, settings.stability_ai_api_key)

    if provider == "dalle3" and settings.openai_api_key:
        return await _generate_dalle3(enhanced_prompt, width, height, settings.openai_api_key)

    if provider == "replicate" and settings.replicate_api_key:
        return await _generate_replicate(enhanced_prompt, negative_prompt, width, height, settings.replicate_api_key)

    # Fallback: essaie le premier disponible
    if settings.stability_ai_api_key:
        return await _generate_stability(enhanced_prompt, negative_prompt, width, height, settings.stability_ai_api_key)
    if settings.openai_api_key:
        return await _generate_dalle3(enhanced_prompt, width, height, settings.openai_api_key)
    if settings.replicate_api_key:
        return await _generate_replicate(enhanced_prompt, negative_prompt, width, height, settings.replicate_api_key)

    return (
        f"[IMAGE SIMULÉE]\n"
        f"Prompt: {enhanced_prompt}\n"
        f"Dimensions: {width}x{height}\n"
        f"Style: {style}\n"
        f"Note: Configurez une clé API (Stability AI, OpenAI ou Replicate) dans .env pour générer de vraies images."
    )


def _enhance_prompt(prompt: str, style: str) -> str:
    style_enhancers = {
        "photorealistic": "photorealistic, 8K ultra HD, professional photography, sharp focus, cinematic lighting",
        "cinematic": "cinematic, Hollywood production quality, dramatic lighting, 8K, wide angle, epic",
        "advertising": "professional advertising photography, product shot, clean background, commercial quality",
        "artistic": "digital art, concept art, artstation trending, highly detailed, masterpiece",
        "portrait": "professional portrait photography, studio lighting, bokeh background, high resolution",
    }
    enhancer = style_enhancers.get(style, style_enhancers["photorealistic"])
    return f"{prompt}, {enhancer}"


async def _generate_stability(prompt: str, negative_prompt: str, width: int, height: int, api_key: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.stability.ai/v2beta/stable-image/generate/core",
                headers={"authorization": f"Bearer {api_key}", "accept": "application/json"},
                data={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "output_format": "jpeg",
                    "width": str(width),
                    "height": str(height),
                },
            )
            response.raise_for_status()
            data = response.json()
            image_b64 = data.get("image", "")
            if image_b64:
                output_path = Path("outputs/images")
                output_path.mkdir(parents=True, exist_ok=True)
                import time
                filename = f"stability_{int(time.time())}.jpg"
                filepath = output_path / filename
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(image_b64))
                return f"Image générée avec succès via Stability AI\nFichier: {filepath}\nPrompt: {prompt}"
    except Exception as e:
        logger.error(f"Stability AI error: {e}")
        return f"Erreur Stability AI: {e}"


async def _generate_dalle3(prompt: str, width: int, height: int, api_key: str) -> str:
    try:
        size_map = {(1024, 1024): "1024x1024", (1792, 1024): "1792x1024", (1024, 1792): "1024x1792"}
        size = size_map.get((width, height), "1024x1024")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": prompt, "size": size, "quality": "hd", "n": 1},
            )
            response.raise_for_status()
            data = response.json()
            url = data["data"][0]["url"]
            revised = data["data"][0].get("revised_prompt", prompt)
            return f"Image générée via DALL-E 3\nURL: {url}\nPrompt révisé: {revised}"
    except Exception as e:
        logger.error(f"DALL-E 3 error: {e}")
        return f"Erreur DALL-E 3: {e}"


async def _generate_replicate(prompt: str, negative_prompt: str, width: int, height: int, api_key: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "input": {
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "output_format": "jpeg",
                        "output_quality": 95,
                    }
                },
            )
            response.raise_for_status()
            prediction = response.json()
            pred_id = prediction["id"]

            # Poll for result
            for _ in range(30):
                await asyncio.sleep(3)
                poll_resp = await client.get(
                    f"https://api.replicate.com/v1/predictions/{pred_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                poll_data = poll_resp.json()
                if poll_data["status"] == "succeeded":
                    urls = poll_data.get("output", [])
                    url = urls[0] if urls else ""
                    return f"Image générée via Replicate (FLUX)\nURL: {url}\nPrompt: {prompt}"
                elif poll_data["status"] == "failed":
                    return f"Replicate génération échouée: {poll_data.get('error', 'unknown')}"
            return "Timeout: génération d'image trop longue"
    except Exception as e:
        logger.error(f"Replicate error: {e}")
        return f"Erreur Replicate: {e}"
