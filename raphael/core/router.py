import re
from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from raphael.core.registry import AgentRegistry, AgentSpec


# Mots-clés par domaine pour le routing rapide (complété par Claude pour les cas ambigus)
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "sophie": ["recherche", "cherche", "trouve", "information", "actualité", "news", "veille",
               "concurrence", "concurrent", "tendance", "source", "article", "web", "internet"],
    "victor": ["rédige", "écris", "copywriting", "article", "blog", "email", "newsletter",
               "script", "texte", "contenu", "landing page", "publicité texte", "copy"],
    "elena": ["campagne", "publicité", "facebook ads", "google ads", "tiktok ads", "marketing",
              "promotion", "audience", "ciblage", "funnel", "acquisition", "growth"],
    "marcus": ["stratégie", "business", "plan", "modèle", "pivot", "scaling", "financement",
               "investissement", "partenariat", "croissance", "entreprise", "startup"],
    "aurora": ["image", "photo", "vidéo", "visuel", "créer", "génère", "illustration",
               "design", "graphique", "banner", "thumbnail", "cinématique", "hollywood"],
    "felix": ["trading", "crypto", "bitcoin", "ethereum", "action", "bourse", "forex",
              "marché", "analyse technique", "indicateur", "RSI", "MACD", "trade"],
    "diana": ["e-commerce", "boutique", "shopify", "woocommerce", "produit", "vente en ligne",
              "conversion", "panier", "stock", "amazon", "marketplace", "dropshipping"],
    "noah": ["sécurité", "risque", "conformité", "RGPD", "protection", "audit", "légal",
             "contrat", "fraude", "incident", "vulnérabilité", "menace"],
    "luna": ["réseaux sociaux", "instagram", "tiktok", "twitter", "youtube", "linkedin",
             "community", "engagement", "followers", "viral", "influencer", "social media"],
    "axel": ["données", "analyse", "statistique", "dashboard", "KPI", "rapport", "graphique",
             "metric", "A/B test", "cohort", "forecast", "prédiction", "BI"],
}


class TaskRouter:
    """Route les tâches vers les agents les plus compétents."""

    def __init__(self, registry: "AgentRegistry"):
        self._registry = registry

    async def route(self, task: str, required_skills: list[str] | None = None) -> list["AgentSpec"]:
        """
        Détermine quel(s) agent(s) traiter la tâche.
        Combine routing par mots-clés + scoring de compétences depuis le registre.
        """
        # Priorité: compétences requises explicites
        if required_skills:
            agents = await self._registry.find_by_expertise(required_skills)
            if agents:
                return agents[:3]

        # Routing par mots-clés rapide
        keyword_matches = self._keyword_match(task)

        # Combine avec le registre
        all_candidates = []
        for agent_name, score in keyword_matches:
            spec = await self._registry.get(agent_name)
            if spec:
                all_candidates.append((score * spec.performance_score, spec))

        # Si pas de match keyword, cherche par expertise générale
        if not all_candidates:
            all_specs = await self._registry.get_all()
            all_candidates = [(spec.performance_score, spec) for spec in all_specs]

        all_candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [spec for _, spec in all_candidates[:3]]

        if selected:
            logger.debug(f"Route '{task[:60]}' → {[a.name for a in selected]}")
        return selected

    def _keyword_match(self, task: str) -> list[tuple[str, float]]:
        task_lower = task.lower()
        scores: dict[str, float] = {}
        for agent_name, keywords in DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in task_lower)
            if matches > 0:
                scores[agent_name] = matches / len(keywords)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    async def identify_required_skills(self, task: str) -> list[str]:
        """Identifie les compétences requises pour une tâche complexe."""
        task_lower = task.lower()
        skills = []
        skill_map = {
            "recherche": ["recherche web", "veille"],
            "campagne": ["marketing digital", "publicité"],
            "image": ["création d'images"],
            "vidéo": ["création vidéo"],
            "trading": ["trading", "analyse technique"],
            "boutique": ["e-commerce"],
            "données": ["analyse de données"],
            "sécurité": ["gestion des risques"],
            "stratégie": ["stratégie business"],
            "contenu": ["copywriting", "rédaction"],
            "social": ["réseaux sociaux"],
        }
        for keyword, associated_skills in skill_map.items():
            if keyword in task_lower:
                skills.extend(associated_skills)
        return list(set(skills))
