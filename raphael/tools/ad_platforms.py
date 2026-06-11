import httpx
from loguru import logger
from raphael.config import get_settings


async def create_meta_campaign(
    campaign_name: str,
    objective: str,
    budget_daily: float,
    audience: dict | None = None,
    creative: dict | None = None,
) -> str:
    """Crée une campagne publicitaire Meta (Facebook/Instagram)."""
    settings = get_settings()
    if not settings.meta_access_token:
        return (
            f"[META ADS SIMULÉ]\n"
            f"Campagne: {campaign_name}\n"
            f"Objectif: {objective} | Budget/jour: {budget_daily}€\n"
            f"Audience: {audience or 'Non définie'}\n"
            f"Créatif: {creative or 'Non défini'}\n"
            f"Note: Configurez META_ACCESS_TOKEN dans .env pour créer de vraies campagnes."
        )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Crée la campagne
            camp_resp = await client.post(
                f"https://graph.facebook.com/v21.0/act_{settings.meta_app_id}/campaigns",
                params={
                    "access_token": settings.meta_access_token,
                    "name": campaign_name,
                    "objective": objective,
                    "status": "PAUSED",
                    "special_ad_categories": "[]",
                },
            )
            camp_resp.raise_for_status()
            campaign_id = camp_resp.json().get("id")

            # Crée l'ad set
            adset_resp = await client.post(
                f"https://graph.facebook.com/v21.0/act_{settings.meta_app_id}/adsets",
                params={
                    "access_token": settings.meta_access_token,
                    "campaign_id": campaign_id,
                    "name": f"{campaign_name} - AdSet 1",
                    "daily_budget": int(budget_daily * 100),
                    "billing_event": "IMPRESSIONS",
                    "optimization_goal": "CONVERSIONS" if objective == "CONVERSIONS" else "REACH",
                    "status": "PAUSED",
                },
            )
            adset_resp.raise_for_status()
            adset_id = adset_resp.json().get("id")

            return (
                f"Campagne Meta créée avec succès!\n"
                f"Campaign ID: {campaign_id}\n"
                f"Ad Set ID: {adset_id}\n"
                f"Statut: PAUSED (activez manuellement après vérification)\n"
                f"Budget quotidien: {budget_daily}€"
            )
    except Exception as e:
        logger.error(f"Meta Ads error: {e}")
        return f"Erreur Meta Ads: {e}"


async def create_google_campaign(
    campaign_name: str,
    campaign_type: str,
    budget_daily: float,
    keywords: list[str] | None = None,
    ad_copy: dict | None = None,
) -> str:
    """Crée une campagne Google Ads."""
    settings = get_settings()
    if not settings.google_ads_developer_token:
        return (
            f"[GOOGLE ADS SIMULÉ]\n"
            f"Campagne: {campaign_name}\n"
            f"Type: {campaign_type} | Budget/jour: {budget_daily}€\n"
            f"Mots-clés: {keywords or []}\n"
            f"Copy: {ad_copy or 'Non défini'}\n"
            f"Note: Configurez Google Ads dans .env pour créer de vraies campagnes."
        )
    return (
        f"Google Ads: Intégration OAuth requise.\n"
        f"Campagne '{campaign_name}' ({campaign_type}) préparée.\n"
        f"Budget: {budget_daily}€/jour | Mots-clés: {len(keywords or [])} définis\n"
        f"Veuillez compléter l'authentification OAuth Google Ads."
    )


async def get_campaign_metrics(platform: str, campaign_id: str) -> dict:
    """Récupère les métriques d'une campagne publicitaire."""
    settings = get_settings()
    if platform == "meta" and settings.meta_access_token:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"https://graph.facebook.com/v21.0/{campaign_id}/insights",
                    params={
                        "access_token": settings.meta_access_token,
                        "fields": "impressions,clicks,spend,actions,cost_per_action_type,ctr,cpc",
                    },
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Meta metrics error: {e}")
    return {"error": f"Métriques non disponibles pour {platform}/{campaign_id}"}
