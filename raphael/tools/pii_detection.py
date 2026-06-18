"""Détection d'informations personnelles identifiables (IPI) via Claude.

Module partagé par l'endpoint image (`routes/anonymizer.py`) et le moteur
d'anonymisation vidéo (`tools/video_anonymizer.py`). La clé API reste côté
serveur ; ce module ne fait qu'interroger Claude et parser sa réponse.
"""
import json
import anthropic
from loguru import logger

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
Les coordonnées doivent ÉPOUSER AU PLUS PRÈS la zone, sans la surdimensionner (marge de 2-3% maximum).

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

# Prompt orienté texte : utilisé pour la vidéo, où les visages sont déjà gérés
# en local par OpenCV. On demande surtout à Claude le texte/IPI non visuels.
TEXT_DETECTION_PROMPT = """Tu es un expert en protection des données personnelles (RGPD, vie privée).
Analyse cette image extraite d'une vidéo et identifie les informations personnelles
identifiables (IPI) **textuelles ou graphiques** visibles à l'écran.

Éléments à détecter OBLIGATOIREMENT :
- Noms et prénoms affichés
- Numéros de téléphone / WhatsApp
- Adresses email
- Adresses postales
- Pseudos, identifiants, comptes de réseaux sociaux
- Plaques d'immatriculation
- Documents d'identité, badges, écrans affichant des données personnelles
- Toute autre information textuelle permettant d'identifier une personne

(Les visages sont déjà traités séparément : ne les retourne PAS.)

Pour chaque élément, retourne des coordonnées en POURCENTAGES (0 à 100) de la largeur/hauteur.
Les coordonnées doivent COLLER AU PLUS PRÈS du texte, sans le surdimensionner (marge de 2-3% maximum).

Retourne UNIQUEMENT un tableau JSON valide. Aucun texte avant ou après. Aucun markdown.
Format EXACT :
[{"type": "téléphone", "description": "Numéro en bas", "x": 12, "y": 80, "width": 30, "height": 8}]

Si aucun IPI textuel n'est détecté, retourne exactement : []"""

# Types MIME acceptés par l'API Anthropic pour les images.
SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def parse_regions(raw_text: str) -> list[dict]:
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


def normalize_regions(raw_regions: list) -> list[dict]:
    """Filtre et normalise les zones (x, y, width, height en %) renvoyées par Claude."""
    regions: list[dict] = []
    for item in raw_regions:
        if not isinstance(item, dict):
            continue
        try:
            regions.append(
                {
                    "type": str(item.get("type", "inconnu")),
                    "description": str(item.get("description", "")),
                    "x": float(item["x"]),
                    "y": float(item["y"]),
                    "width": float(item["width"]),
                    "height": float(item["height"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            logger.warning("Zone IPI ignorée (format invalide): {}", item)
            continue
    return regions


async def detect_pii(
    client: "anthropic.AsyncAnthropic",
    image_base64: str,
    media_type: str,
    model: str,
    system_prompt: str = DETECTION_PROMPT,
) -> list[dict]:
    """Interroge Claude sur une image (base64) et renvoie les zones IPI normalisées."""
    media_type = media_type if media_type in SUPPORTED_MEDIA_TYPES else "image/jpeg"
    response = await client.messages.create(
        model=model,
        max_tokens=1000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_base64},
                    },
                    {"type": "text", "text": "Analyse et retourne le JSON des IPI détectés."},
                ],
            }
        ],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text") or "[]"
    return normalize_regions(parse_regions(raw_text))
