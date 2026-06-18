"""Route d'anonymisation de frames vidéo / images.

Détecte les informations personnelles identifiables (IPI) dans une image via
Claude, puis renvoie les zones à flouter (en pourcentages). Le flouage lui-même
est appliqué côté client (canvas) afin de ne jamais transférer l'image floutée.

La clé API Anthropic reste côté serveur — l'image est envoyée en base64 au
backend, qui interroge Claude. Le navigateur n'a jamais accès à la clé.
"""
import json
import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from raphael.config import get_settings

router = APIRouter(prefix="/anonymize", tags=["Anonymiseur"])


# ─── PROMPT SYSTÈME POUR LA DÉTECTION IPI ───────────────────────────────────
DETECTION_PROMPT = """Tu es un expert en protection des données personnelles (RGPD, vie privée).
Analyse cette image et identifie TOUS les éléments d'information personnelle identifiable (IPI) visibles.

Éléments à détecter OBLIGATOIREMENT :
- Visages humains (même partiels, même flous, même de profil)
- Photos de profil / avatars
- Noms et prénoms
- Numéros de téléphone / WhatsApp
- Adresses email
- Adresses postales
- Âge
- Lieu d'habitation / ville
- Éléments de contact (réseaux sociaux, pseudo, identifiant)
- Toute autre information permettant d'identifier une personne

IMPORTANT : Sois exhaustif. Mieux vaut détecter trop que pas assez.

Pour chaque élément, retourne des coordonnées en POURCENTAGES (0 à 100) de la largeur/hauteur de l'image.
Ajoute une marge de 8-10% autour de chaque zone détectée pour garantir un flouage complet.

Retourne UNIQUEMENT un tableau JSON valide. Aucun texte avant ou après. Aucun markdown.

Format EXACT :
[
  {
    "type": "visage",
    "description": "Visage masculin côté gauche",
    "x": 12,
    "y": 8,
    "width": 20,
    "height": 28
  }
]

Si aucun IPI n'est détecté, retourne exactement : []"""

# Types MIME acceptés par l'API Anthropic pour les images.
SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


class DetectRequest(BaseModel):
    """Image encodée en base64 (sans le préfixe data:...;base64,)."""

    image_base64: str
    media_type: str = "image/jpeg"


class PiiRegion(BaseModel):
    type: str
    description: str = ""
    x: float
    y: float
    width: float
    height: float


class DetectResponse(BaseModel):
    regions: list[PiiRegion] = []
    count: int = 0


def _parse_regions(raw_text: str) -> list[dict]:
    """Extrait le tableau JSON renvoyé par Claude, en tolérant un wrapping markdown."""
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Tente de récupérer le premier tableau JSON présent dans le texte.
        start, end = cleaned.find("["), cleaned.rfind("]")
        if start == -1 or end == -1 or end <= start:
            logger.warning("Réponse Claude non parsable: {}", raw_text[:200])
            return []
        try:
            data = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            logger.warning("Tableau JSON non parsable: {}", raw_text[:200])
            return []
    return data if isinstance(data, list) else []


@router.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest) -> DetectResponse:
    """Détecte les IPI d'une image et renvoie les zones à flouter (en %)."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY non configurée côté serveur.",
        )

    media_type = request.media_type if request.media_type in SUPPORTED_MEDIA_TYPES else "image/jpeg"

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model=settings.specialist_model,
            max_tokens=1000,
            system=DETECTION_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": request.image_base64,
                            },
                        },
                        {"type": "text", "text": "Analyse et retourne le JSON des IPI détectés."},
                    ],
                }
            ],
        )
    except anthropic.APIError as exc:
        logger.error("Erreur API Anthropic lors de la détection IPI: {}", exc)
        raise HTTPException(status_code=502, detail=f"Erreur API Anthropic: {exc}") from exc

    raw_text = "".join(block.text for block in response.content if block.type == "text") or "[]"
    raw_regions = _parse_regions(raw_text)

    regions: list[PiiRegion] = []
    for item in raw_regions:
        if not isinstance(item, dict):
            continue
        try:
            regions.append(
                PiiRegion(
                    type=str(item.get("type", "inconnu")),
                    description=str(item.get("description", "")),
                    x=float(item["x"]),
                    y=float(item["y"]),
                    width=float(item["width"]),
                    height=float(item["height"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            logger.warning("Zone IPI ignorée (format invalide): {}", item)
            continue

    return DetectResponse(regions=regions, count=len(regions))
