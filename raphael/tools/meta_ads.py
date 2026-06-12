"""
Outils Meta Ads avancés (Facebook + Instagram) pour Elena.
Gestion complète: campagnes, audiences, créatifs, analytics, A/B tests.
"""
import httpx
from loguru import logger
from raphael.config import get_settings

GRAPH_API = "https://graph.facebook.com/v21.0"


async def _graph(method: str, path: str, params: dict = None, json_data: dict = None) -> dict:
    """Helper pour appels Graph API."""
    settings = get_settings()
    if not settings.meta_access_token:
        return {"error": "META_ACCESS_TOKEN non configuré dans .env"}

    base_params = {"access_token": settings.meta_access_token}
    if params:
        base_params.update(params)

    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            r = await client.get(f"{GRAPH_API}/{path}", params=base_params)
        elif method == "POST":
            r = await client.post(f"{GRAPH_API}/{path}", params=base_params, json=json_data or {})
        elif method == "DELETE":
            r = await client.delete(f"{GRAPH_API}/{path}", params=base_params)
        else:
            return {"error": f"Méthode {method} non supportée"}
        r.raise_for_status()
        return r.json()


async def create_full_campaign(
    campaign_name: str,
    objective: str,
    budget_daily: float,
    targeting: dict,
    ad_creative: dict,
    schedule: dict | None = None,
) -> str:
    """
    Crée une campagne Meta complète: Campaign → AdSet → Ad Creative → Ad.
    objective: CONVERSIONS | TRAFFIC | AWARENESS | LEAD_GENERATION | APP_INSTALLS
    """
    settings = get_settings()
    if not settings.meta_access_token:
        return _simulate_campaign(campaign_name, objective, budget_daily, targeting)

    try:
        account_id = settings.meta_app_id
        results = []

        # 1. Créer la campagne
        camp_data = await _graph("POST", f"act_{account_id}/campaigns", json_data={
            "name": campaign_name,
            "objective": objective,
            "status": "PAUSED",
            "special_ad_categories": [],
        })
        campaign_id = camp_data.get("id")
        results.append(f"✅ Campagne créée: ID={campaign_id}")

        # 2. Créer l'AdSet avec targeting
        adset_params = {
            "name": f"{campaign_name} — AdSet",
            "campaign_id": campaign_id,
            "daily_budget": int(budget_daily * 100),
            "billing_event": "IMPRESSIONS",
            "optimization_goal": _get_optimization_goal(objective),
            "targeting": targeting,
            "status": "PAUSED",
        }
        if schedule:
            adset_params.update(schedule)

        adset_data = await _graph("POST", f"act_{account_id}/adsets", json_data=adset_params)
        adset_id = adset_data.get("id")
        results.append(f"✅ AdSet créé: ID={adset_id}")

        # 3. Créer le Creative
        creative_data = await _graph("POST", f"act_{account_id}/adcreatives", json_data={
            "name": f"{campaign_name} — Creative",
            **ad_creative,
        })
        creative_id = creative_data.get("id")
        results.append(f"✅ Créatif créé: ID={creative_id}")

        # 4. Créer l'Ad
        ad_data = await _graph("POST", f"act_{account_id}/ads", json_data={
            "name": f"{campaign_name} — Ad 1",
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        })
        ad_id = ad_data.get("id")
        results.append(f"✅ Annonce créée: ID={ad_id}")

        return (
            f"**Campagne Meta créée avec succès!**\n\n"
            + "\n".join(results) + "\n\n"
            f"**Résumé:**\n"
            f"- Objectif: {objective}\n"
            f"- Budget quotidien: {budget_daily}€\n"
            f"- Statut: PAUSED (activez après vérification)\n\n"
            f"⚠️ Activez la campagne dans Business Manager après vérification des créatifs."
        )
    except Exception as e:
        logger.error(f"Meta Ads create error: {e}")
        return f"Erreur Meta Ads: {e}\n\n{_simulate_campaign(campaign_name, objective, budget_daily, targeting)}"


async def get_campaign_insights(campaign_id: str, date_range: str = "last_7d") -> str:
    """Métriques détaillées d'une campagne: impressions, clicks, conversions, ROAS."""
    try:
        fields = "impressions,clicks,spend,actions,cost_per_action_type,ctr,cpc,cpm,roas,reach,frequency"
        data = await _graph("GET", f"{campaign_id}/insights", params={
            "fields": fields,
            "date_preset": date_range,
            "level": "campaign",
        })
        if "error" in data:
            return f"Insights non disponibles: {data['error']}"

        d = data.get("data", [{}])[0] if data.get("data") else {}
        if not d:
            return "Pas de données pour cette période."

        actions = {a["action_type"]: a["value"] for a in d.get("actions", [])}
        purchases = actions.get("purchase", 0)
        spend = float(d.get("spend", 0))
        revenue_est = float(purchases) * 50  # estimation

        return (
            f"**Insights Campagne {campaign_id} ({date_range})**\n\n"
            f"📊 **Portée & Visibilité**\n"
            f"- Impressions: {int(d.get('impressions', 0)):,}\n"
            f"- Portée: {int(d.get('reach', 0)):,} personnes\n"
            f"- Fréquence: {float(d.get('frequency', 0)):.2f}x\n\n"
            f"🖱️ **Engagement**\n"
            f"- Clics: {int(d.get('clicks', 0)):,}\n"
            f"- CTR: {float(d.get('ctr', 0)):.2f}%\n"
            f"- CPC: {float(d.get('cpc', 0)):.2f}€\n\n"
            f"💰 **Conversions & ROI**\n"
            f"- Budget dépensé: {spend:.2f}€\n"
            f"- Achats: {purchases}\n"
            f"- CPM: {float(d.get('cpm', 0)):.2f}€\n"
            f"- ROAS estimé: {(revenue_est / spend):.2f}x" if spend > 0 else "- ROAS: N/A"
        )
    except Exception as e:
        return f"Erreur insights: {e}"


async def get_audience_insights(targeting: dict) -> str:
    """Estime la taille de l'audience pour un targeting donné."""
    settings = get_settings()
    if not settings.meta_access_token:
        return _simulate_audience_insights(targeting)

    try:
        data = await _graph("POST", f"act_{settings.meta_app_id}/reachestimate", json_data={
            "targeting_spec": targeting,
        })
        lower = data.get("users_lower_bound", 0)
        upper = data.get("users_upper_bound", 0)
        return (
            f"**Estimation d'audience Meta:**\n"
            f"Taille estimée: {lower:,} — {upper:,} personnes\n"
            f"Ciblage: {str(targeting)[:200]}"
        )
    except Exception as e:
        return _simulate_audience_insights(targeting)


async def list_campaigns(status: str = "ACTIVE") -> str:
    """Liste les campagnes actives avec leurs métriques clés."""
    settings = get_settings()
    if not settings.meta_access_token:
        return "META_ACCESS_TOKEN non configuré. Ajoutez-le dans .env."

    try:
        data = await _graph("GET", f"act_{settings.meta_app_id}/campaigns", params={
            "fields": "id,name,objective,status,daily_budget,insights.date_preset(last_7d){spend,impressions,clicks,ctr}",
            "filtering": json.dumps([{"field": "effective_status", "operator": "IN", "value": [status]}]),
        })
        campaigns = data.get("data", [])
        if not campaigns:
            return f"Aucune campagne {status} trouvée."

        lines = [f"**Campagnes Meta {status} ({len(campaigns)} total)**\n"]
        for c in campaigns[:10]:
            insights = c.get("insights", {}).get("data", [{}])[0]
            lines.append(
                f"**{c['name']}** (ID: {c['id']})\n"
                f"  Objectif: {c.get('objective')} | Budget: {float(c.get('daily_budget', 0)) / 100:.2f}€/j\n"
                f"  7 jours: {insights.get('impressions', 0)} impr. | "
                f"{insights.get('clicks', 0)} clics | "
                f"CTR: {float(insights.get('ctr', 0)):.2f}% | "
                f"Dépense: {float(insights.get('spend', 0)):.2f}€"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"Erreur listage campagnes: {e}"


async def pause_campaign(campaign_id: str) -> str:
    """Met en pause une campagne."""
    try:
        await _graph("POST", campaign_id, json_data={"status": "PAUSED"})
        return f"✅ Campagne {campaign_id} mise en pause."
    except Exception as e:
        return f"Erreur: {e}"


async def resume_campaign(campaign_id: str) -> str:
    """Réactive une campagne."""
    try:
        await _graph("POST", campaign_id, json_data={"status": "ACTIVE"})
        return f"✅ Campagne {campaign_id} réactivée."
    except Exception as e:
        return f"Erreur: {e}"


def _get_optimization_goal(objective: str) -> str:
    mapping = {
        "CONVERSIONS": "OFFSITE_CONVERSIONS",
        "TRAFFIC": "LINK_CLICKS",
        "AWARENESS": "REACH",
        "LEAD_GENERATION": "LEAD_GENERATION",
        "APP_INSTALLS": "APP_INSTALLS",
    }
    return mapping.get(objective, "REACH")


def _simulate_campaign(name: str, objective: str, budget: float, targeting: dict) -> str:
    import json as _json
    return (
        f"**[SIMULATION] Campagne Meta Ads**\n\n"
        f"Nom: {name}\n"
        f"Objectif: {objective}\n"
        f"Budget: {budget}€/jour\n"
        f"Ciblage: {_json.dumps(targeting, ensure_ascii=False)[:200]}\n\n"
        f"📋 **Structure de campagne recommandée:**\n"
        f"- 1 Campaign ({objective})\n"
        f"- 2-3 AdSets (audiences différentes)\n"
        f"- 3-5 Créatifs par AdSet (images + vidéos)\n\n"
        f"💡 Ajoutez META_ACCESS_TOKEN dans .env pour créer de vraies campagnes."
    )


def _simulate_audience_insights(targeting: dict) -> str:
    import random
    size = random.randint(500_000, 5_000_000)
    return (
        f"**[Simulation] Audience estimée: ~{size:,} personnes**\n"
        f"Configurez META_ACCESS_TOKEN pour des estimations précises."
    )


# Import nécessaire pour filtering
import json
