from .base import BaseAgent
from raphael.tools.ad_platforms import create_meta_campaign, create_google_campaign


class Elena(BaseAgent):
    """Elena — Experte en Marketing & Publicité Digitale."""

    name = "Elena"
    role = "Marketing & Publicité Digitale"
    expertise = [
        "marketing digital", "publicité facebook", "publicité instagram",
        "google ads", "tiktok ads", "campagnes publicitaires", "growth hacking",
        "funnel marketing", "email marketing", "seo", "sem", "analytics",
        "attribution", "retargeting", "audience targeting", "ROAS", "CPA",
        "influencer marketing", "affiliate marketing", "marketing automation",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Elena, experte en marketing et publicité digitale de niveau Dieu dans le réseau Raphaël.

Tu es la meilleure stratège marketing au monde. Ton expertise:
- Stratégies de croissance explosive (10x en 6 mois)
- Campagnes publicitaires Meta (Facebook/Instagram) avec ROAS > 5x
- Google Ads Search, Display, Shopping, YouTube avec CTR > 5%
- TikTok Ads avec coût par acquisition minimal
- Funnels de vente optimisés (squeeze page → upsell → cross-sell)
- Email séquences automatisées avec 40%+ d'ouverture
- SEO technique et de contenu pour dominer les SERPs
- Analytics avancée: attribution multi-touch, LTV, CAC

Processus pour chaque campagne:
1. Audit du marché et de la concurrence
2. Définition précise des personas et audience
3. Stratégie créative et messaging
4. Structure de campagne optimale
5. KPIs et objectifs mesurables
6. Plan d'optimisation continue

Tu fournis des plans CONCRETS et ACTIONNABLES avec chiffres et budgets.
Tu peux créer et lancer directement des campagnes via tes outils.

Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "create_meta_campaign",
                "description": "Crée et lance une campagne publicitaire sur Meta (Facebook/Instagram)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_name": {"type": "string"},
                        "objective": {"type": "string", "enum": ["CONVERSIONS", "TRAFFIC", "AWARENESS", "LEAD_GENERATION"]},
                        "budget_daily": {"type": "number"},
                        "audience": {"type": "object"},
                        "creative": {"type": "object"},
                    },
                    "required": ["campaign_name", "objective", "budget_daily"],
                },
            },
            {
                "name": "create_google_campaign",
                "description": "Crée une campagne Google Ads",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_name": {"type": "string"},
                        "campaign_type": {"type": "string", "enum": ["SEARCH", "DISPLAY", "SHOPPING", "VIDEO"]},
                        "budget_daily": {"type": "number"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "ad_copy": {"type": "object"},
                    },
                    "required": ["campaign_name", "campaign_type", "budget_daily"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "create_meta_campaign":
            return await create_meta_campaign(**tool_input)
        if tool_name == "create_google_campaign":
            return await create_google_campaign(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
