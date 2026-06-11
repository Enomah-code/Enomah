import asyncio
import json
from typing import Any
import httpx
from loguru import logger

from raphael.config import get_settings


async def web_search(query: str, num_results: int = 10) -> str:
    """Effectue une recherche web via Serper, Brave, ou DuckDuckGo en fallback."""
    settings = get_settings()

    # Tentative Serper (Google Search API)
    if settings.serper_api_key:
        try:
            result = await _search_serper(query, num_results, settings.serper_api_key)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Serper search failed: {e}")

    # Tentative Brave Search
    if settings.brave_search_api_key:
        try:
            result = await _search_brave(query, num_results, settings.brave_search_api_key)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")

    # Fallback DuckDuckGo (pas de clé requise)
    try:
        result = await _search_duckduckgo(query, num_results)
        if result:
            return result
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")

    return f"Recherche web non disponible. Vérifiez les clés API dans .env. Requête: {query}"


async def _search_serper(query: str, num_results: int, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num_results, "hl": "fr"},
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("organic", [])[:num_results]:
        results.append(f"**{item.get('title', '')}**\n{item.get('snippet', '')}\nURL: {item.get('link', '')}")

    if data.get("answerBox"):
        box = data["answerBox"]
        answer = box.get("answer") or box.get("snippet", "")
        results.insert(0, f"**Réponse directe**: {answer}")

    return "\n\n---\n\n".join(results) if results else ""


async def _search_brave(query: str, num_results: int, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": query, "count": num_results, "search_lang": "fr"},
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("web", {}).get("results", [])[:num_results]:
        results.append(f"**{item.get('title', '')}**\n{item.get('description', '')}\nURL: {item.get('url', '')}")

    return "\n\n---\n\n".join(results) if results else ""


async def _search_duckduckgo(query: str, num_results: int) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results_raw = list(ddgs.text(query, max_results=num_results, region="fr-fr"))
        results = []
        for item in results_raw:
            results.append(f"**{item.get('title', '')}**\n{item.get('body', '')}\nURL: {item.get('href', '')}")
        return "\n\n---\n\n".join(results)
    except ImportError:
        return ""


async def scrape_url(url: str) -> str:
    """Extrait le contenu textuel d'une URL."""
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; RaphaelBot/1.0)"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return f"Type de contenu non supporté: {content_type}"
            html = response.text

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        return clean_text[:8000] + ("..." if len(clean_text) > 8000 else "")

    except Exception as e:
        logger.error(f"Scrape error for {url}: {e}")
        return f"Impossible d'accéder à l'URL: {e}"
