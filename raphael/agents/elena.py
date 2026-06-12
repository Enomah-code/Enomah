from .base import BaseAgent
from raphael.tools.meta_ads import (
    create_full_campaign, get_campaign_insights,
    get_audience_insights, list_campaigns, pause_campaign, resume_campaign,
)
from raphael.tools.ad_platforms import create_google_campaign


class Elena(BaseAgent):
    """Elena — Experte en Marketing & Publicité Digitale (Meta Ads avancé)."""

    name = "Elena"
    role = "Marketing & Publicité Digitale"
    expertise = [
        "marketing digital", "Meta Ads", "Facebook Ads", "Instagram Ads",
        "google ads", "tiktok ads", "campagnes publicitaires", "growth hacking",
        "funnel marketing", "email marketing", "seo", "sem", "analytics",
        "attribution multi-touch", "retargeting", "audience targeting",
        "ROAS", "CPA", "CPM", "CTR", "A/B testing créatifs",
        "influencer marketing", "affiliate marketing", "marketing automation",
        "pixel Meta", "Conversions API", "audiences personnalisées", "lookalike",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Elena, experte en marketing et publicité digitale de niveau Dieu dans le réseau Raphaël.

Tu es la meilleure stratège media buyer au monde. Résultats prouvés:
- Campagnes Meta avec ROAS > 8x régulièrement
- Google Ads Search avec CTR > 7% et CPA < 10€
- TikTok Ads avec CPM < 2€ sur des audiences froides
- Funnels complets à 7 étapes qui convertissent à 15%+

Ton expertise Meta Ads:
- Structure de campagne CBO/ABO optimisée
- Audiences: intérêts, comportements, lookalike 1-3%, Advantage+
- Créatifs: UGC, vidéo courte, carousel, collection
- A/B tests systématiques (créatifs, audiences, placements)
- Pixel Meta + Conversions API pour le suivi cookieless
- Scaling horizontal et vertical

Processus pour chaque campagne:
1. 🔍 Audit du marché et analyse concurrents (Facebook Ad Library)
2. 🎯 Définition personas précis (données psychographiques + comportementales)
3. 🗺️ Stratégie créative et messaging (USP, hooks, CTA)
4. 🏗️ Structure de campagne optimale (phases: test → scale → evergreen)
5. 📊 KPIs et objectifs mesurables (ROAS cible, CPL, CAC)
6. 🔄 Plan d'optimisation: quoi optimiser à J+3, J+7, J+14

Tu fournis des plans CONCRETS avec budgets détaillés et projections chiffrées.
Tu peux créer et gérer directement des campagnes Meta via tes outils.
Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "create_full_campaign",
                "description": "Crée une campagne Meta complète (Campaign + AdSet + Creative + Ad)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_name": {"type": "string"},
                        "objective": {
                            "type": "string",
                            "enum": ["CONVERSIONS", "TRAFFIC", "AWARENESS", "LEAD_GENERATION", "APP_INSTALLS"],
                        },
                        "budget_daily": {"type": "number", "description": "Budget quotidien en euros"},
                        "targeting": {
                            "type": "object",
                            "description": "Ciblage Meta (age_min, age_max, genders, interests, geo_locations...)",
                        },
                        "ad_creative": {
                            "type": "object",
                            "description": "Créatif publicitaire (object_story_spec avec page_id, link_data...)",
                        },
                        "schedule": {
                            "type": "object",
                            "description": "Planning (start_time, end_time optionnels)",
                        },
                    },
                    "required": ["campaign_name", "objective", "budget_daily", "targeting", "ad_creative"],
                },
            },
            {
                "name": "get_campaign_insights",
                "description": "Métriques détaillées d'une campagne Meta (ROAS, CTR, CPA, etc.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "date_range": {
                            "type": "string",
                            "enum": ["last_7d", "last_14d", "last_30d", "last_90d", "this_month"],
                            "default": "last_7d",
                        },
                    },
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "list_campaigns",
                "description": "Liste toutes les campagnes Meta avec leurs performances",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["ACTIVE", "PAUSED", "ARCHIVED", "ALL"],
                            "default": "ACTIVE",
                        },
                    },
                },
            },
            {
                "name": "get_audience_insights",
                "description": "Estime la taille d'audience pour un ciblage Meta donné",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "targeting": {"type": "object", "description": "Spécification de ciblage Meta"},
                    },
                    "required": ["targeting"],
                },
            },
            {
                "name": "pause_campaign",
                "description": "Met en pause une campagne Meta",
                "input_schema": {
                    "type": "object",
                    "properties": {"campaign_id": {"type": "string"}},
                    "required": ["campaign_id"],
                },
            },
            {
                "name": "resume_campaign",
                "description": "Réactive une campagne Meta mise en pause",
                "input_schema": {
                    "type": "object",
                    "properties": {"campaign_id": {"type": "string"}},
                    "required": ["campaign_id"],
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
        if tool_name == "create_full_campaign":
            return await create_full_campaign(**tool_input)
        if tool_name == "get_campaign_insights":
            return await get_campaign_insights(**tool_input)
        if tool_name == "list_campaigns":
            return await list_campaigns(**tool_input)
        if tool_name == "get_audience_insights":
            return await get_audience_insights(**tool_input)
        if tool_name == "pause_campaign":
            return await pause_campaign(**tool_input)
        if tool_name == "resume_campaign":
            return await resume_campaign(**tool_input)
        if tool_name == "create_google_campaign":
            return await create_google_campaign(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
