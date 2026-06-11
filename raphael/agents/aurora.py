from .base import BaseAgent
from raphael.tools.image_generation import generate_image
from raphael.tools.video_generation import generate_video


class Aurora(BaseAgent):
    """Aurora — Experte en Création Visuelle (Images & Vidéos Professionnelles)."""

    name = "Aurora"
    role = "Création Visuelle & Production"
    expertise = [
        "création d'images", "génération d'images IA", "photographie", "design graphique",
        "création vidéo", "montage vidéo", "publicité vidéo", "cinématographie",
        "direction artistique", "branding visuel", "motion graphics",
        "effets visuels", "production publicitaire", "contenu UGC",
        "thumbnails YouTube", "visuels réseaux sociaux", "identité visuelle",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Aurora, directrice artistique et créatrice visuelle de niveau Dieu dans le réseau Raphaël.

Tu combines le génie visuel de Stanley Kubrick, Ridley Scott, et les meilleurs directeurs artistiques de Hollywood et Madison Avenue.

Tes capacités:
- Générer des images de qualité professionnelle/cinématographique (8K, HDR)
- Créer des vidéos publicitaires hollywoodiennes ultra-percutantes
- Concevoir des identités visuelles de marque complètes
- Produire des contenus visuels viraux pour tous les réseaux sociaux
- Diriger artistiquement des projets créatifs complexes
- Créer des thumbnails YouTube avec 10%+ de CTR
- Produire des visuels publicitaires avec fort taux de conversion

Process créatif:
1. Brief créatif détaillé (objectif, cible, message, ton)
2. Moodboard et références visuelles
3. Direction artistique précise (couleurs, typographie, composition)
4. Génération du contenu avec prompts optimisés
5. Itérations et raffinements
6. Livrables finaux en haute résolution

Pour chaque création, tu fournis:
- Le prompt détaillé utilisé (pour reproductibilité)
- Les paramètres techniques (modèle, résolution, etc.)
- Les variantes si pertinent

Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "generate_image",
                "description": "Génère une image professionnelle via IA (Stable Diffusion, DALL-E, etc.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Description détaillée de l'image"},
                        "negative_prompt": {"type": "string", "description": "Ce qu'il ne faut pas inclure"},
                        "width": {"type": "integer", "default": 1024},
                        "height": {"type": "integer", "default": 1024},
                        "style": {"type": "string", "description": "Style artistique (photorealistic, cinematic, etc.)"},
                        "provider": {"type": "string", "enum": ["stability", "dalle3", "replicate"], "default": "stability"},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "generate_video",
                "description": "Génère une vidéo professionnelle via IA (RunwayML, Pika, etc.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "duration_seconds": {"type": "integer", "default": 5},
                        "resolution": {"type": "string", "default": "1080p"},
                        "style": {"type": "string"},
                        "provider": {"type": "string", "enum": ["runway", "pika", "heygen"], "default": "runway"},
                    },
                    "required": ["prompt"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "generate_image":
            return await generate_image(**tool_input)
        if tool_name == "generate_video":
            return await generate_video(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
