"""
Outils web pour les agents : recherche et récupération de page.

`web_search` utilise DuckDuckGo (sans clé API) si la lib est présente.
`fetch_url` récupère et nettoie le texte d'une page HTML.
Tout est défensif : en cas d'indisponibilité réseau, on renvoie un message
exploitable plutôt qu'une exception.
"""
from __future__ import annotations

import logging
from typing import Dict, List

import httpx

logger = logging.getLogger("angeleck.tools.web")


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Recherche web (DuckDuckGo). Renvoie [{title, href, body}]."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return [{"title": "indisponible", "href": "", "body": "duckduckgo_search non installé."}]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {
                "title": r.get("title", ""),
                "href": r.get("href", ""),
                "body": r.get("body", ""),
            }
            for r in results
        ]
    except Exception as exc:  # noqa: BLE001
        logger.error("Échec recherche web : %s", exc)
        return [{"title": "erreur", "href": "", "body": str(exc)}]


def fetch_url(url: str, max_chars: int = 6000) -> str:
    """Récupère une page et renvoie son texte nettoyé."""
    try:
        resp = httpx.get(url, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        return f"Erreur de récupération ({url}) : {exc}"

    html = resp.text
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except ImportError:
        return html[:max_chars]
