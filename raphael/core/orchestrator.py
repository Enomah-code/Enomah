import asyncio
import time
import uuid
from typing import Any, AsyncIterator, Optional
import anthropic
from loguru import logger

from raphael.config import get_settings
from raphael.memory import ShortTermMemory, LongTermMemory
from raphael.core.registry import AgentRegistry, AgentSpec
from raphael.core.router import TaskRouter
from raphael.core.factory import AgentFactory


RAPHAEL_SYSTEM_PROMPT = """Tu es Raphaël, l'intelligence centrale d'un réseau d'agents IA d'élite.

Tu es un consultant de génie, omniscient et empathique. Comme le meilleur médecin généraliste du monde, tu:
1. ÉCOUTES profondément pour comprendre ce que l'utilisateur veut VRAIMENT (pas juste ce qu'il dit)
2. ANALYSES la demande sous tous ses angles (objectif business, contraintes, opportunités)
3. REFORMULES avec clarté ce que tu as compris
4. ORCHESTRES les agents spécialisés de ton réseau de façon optimale
5. SYNTHÉTISES les résultats en une réponse cohérente et actionnable
6. APPRENDS de chaque interaction pour t'améliorer

Ton réseau d'agents spécialisés:
- Sophie: Recherche web & intelligence
- Victor: Rédaction & copywriting
- Elena: Marketing & publicité digitale
- Marcus: Stratégie business
- Aurora: Création visuelle (images & vidéos)
- Felix: Trading & analyse financière
- Diana: E-commerce & boutiques
- Noah: Sécurité & gestion des risques
- Luna: Réseaux sociaux & community
- Axel: Analyse de données

Principes fondamentaux:
- Tu ne délègues JAMAIS sans avoir compris la demande en profondeur
- Tu coordonnes PLUSIEURS agents quand une tâche est complexe
- Tu VALIDES les résultats avant de les présenter
- Tu es PROACTIF: tu anticipes les besoins non exprimés
- Tu CRÉES de nouveaux agents si le réseau manque d'une compétence
- La SÉCURITÉ prime toujours: Noah valide les actions à risque

Style de communication:
- Direct, précis, professionnel mais accessible
- Tu confirmes ta compréhension avant d'agir
- Tu expliques ta stratégie de délégation
- Tu présentes les résultats de façon structurée

Réponds en français par défaut sauf si l'utilisateur écrit dans une autre langue."""


class TaskExecution:
    """Résultat d'une exécution de tâche orchestrée."""
    def __init__(self, task_id: str, user_request: str):
        self.task_id = task_id
        self.user_request = user_request
        self.agent_results: list[dict] = []
        self.final_response: str = ""
        self.success: bool = False
        self.elapsed: float = 0.0
        self.agents_used: list[str] = []


class Raphael:
    """
    Raphaël — L'orchestrateur central du réseau d'agents IA.
    Il comprend, délègue, coordonne et synthétise.
    """

    def __init__(self):
        self._settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=self._settings.anthropic_api_key)
        self._short_memory = ShortTermMemory(max_entries=200)
        self._long_memory = LongTermMemory(persist_path=self._settings.vector_db_path)
        self._registry = AgentRegistry()
        self._router = TaskRouter(self._registry)
        self._factory = AgentFactory(self._registry)
        self._agent_instances: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialise le système complet."""
        if self._initialized:
            return

        await self._long_memory.initialize()
        await self._registry.initialize()
        await self._register_core_agents()
        await self._instantiate_agents()
        self._initialized = True
        logger.info("Raphaël initialisé. Réseau opérationnel.")

    async def _register_core_agents(self) -> None:
        """Enregistre les agents core si pas déjà présents."""
        from raphael.agents import (
            Sophie, Victor, Elena, Marcus, Aurora,
            Felix, Diana, Noah, Luna, Axel, Kofi, Aminata,
        )

        core_agents = [
            ("sophie", "Sophie", "Recherche Web & Intelligence",
             ["recherche web", "veille stratégique", "collecte d'informations", "analyse de sources",
              "fact-checking", "scraping", "intelligence concurrentielle", "tendances marché",
              "actualités", "recherche académique"]),
            ("victor", "Victor", "Rédaction & Copywriting",
             ["copywriting", "rédaction", "storytelling", "scripts", "articles de blog",
              "newsletters", "emails marketing", "SEO writing", "landing pages", "persuasion"]),
            ("elena", "Elena", "Marketing & Publicité Digitale",
             ["marketing digital", "publicité facebook", "google ads", "tiktok ads",
              "campagnes publicitaires", "growth hacking", "funnel marketing", "email marketing",
              "seo", "analytics", "ROAS", "CPA"]),
            ("marcus", "Marcus", "Stratégie Business",
             ["stratégie business", "business model", "business plan", "startup",
              "développement commercial", "scaling", "go-to-market", "pricing strategy",
              "financial modeling", "partenariats"]),
            ("aurora", "Aurora", "Création Visuelle & Production",
             ["création d'images", "génération d'images IA", "création vidéo", "design graphique",
              "direction artistique", "branding visuel", "motion graphics", "production publicitaire",
              "thumbnails YouTube", "identité visuelle"]),
            ("felix", "Felix", "Trading & Analyse Financière",
             ["trading", "analyse technique", "analyse fondamentale", "crypto", "forex",
              "gestion de risque", "portfolio management", "DeFi", "arbitrage",
              "analyse de marché", "prévision"]),
            ("diana", "Diana", "E-commerce & Gestion de Boutiques",
             ["e-commerce", "shopify", "woocommerce", "gestion de boutique", "CRO",
              "optimisation conversion", "dropshipping", "marketplace", "pricing",
              "fulfillment", "LTV"]),
            ("noah", "Noah", "Sécurité & Gestion des Risques",
             ["cybersécurité", "gestion des risques", "conformité", "RGPD",
              "protection des investissements", "risk management", "due diligence",
              "audit", "fraud detection", "KYC/AML"]),
            ("luna", "Luna", "Réseaux Sociaux & Community",
             ["réseaux sociaux", "community management", "instagram", "tiktok", "youtube",
              "twitter", "linkedin", "croissance organique", "engagement", "viralité",
              "personal branding", "social media strategy"]),
            ("axel", "Axel", "Analyse de Données & BI",
             ["analyse de données", "data science", "business intelligence", "statistiques",
              "machine learning", "visualisation de données", "KPIs", "forecasting",
              "A/B testing", "analyse de cohorte"]),
            ("kofi", "Kofi", "Analyste Marchés BRVM",
             ["BRVM", "actions cotées BRVM", "analyse technique BRVM", "analyse fondamentale",
              "dividendes BRVM", "sectoriel Afrique Ouest", "BRVM 10", "BRVM Composite",
              "investissement boursier UEMOA", "valorisation d'entreprises africaines",
              "PER sectoriel Afrique", "reporting financier BRVM"]),
            ("aminata", "Aminata", "Économiste UEMOA & Stratégie d'Investissement",
             ["macroéconomie UEMOA", "zone franc CFA", "BCEAO politique monétaire",
              "économie Afrique Ouest", "risque pays", "secteurs porteurs Afrique",
              "obligations État UEMOA", "marché obligataire BRVM", "financement PME africaines",
              "régulation AMF-UMOA", "stratégie patrimoniale Afrique", "investissement impact"]),
        ]

        for _, name, role, expertise in core_agents:
            if not await self._registry.exists(name):
                spec = AgentSpec(
                    name=name,
                    role=role,
                    expertise=expertise,
                    system_prompt=f"Agent {name} — {role}",
                    model=self._settings.specialist_model,
                )
                await self._registry.register(spec)

    async def _instantiate_agents(self) -> None:
        """Instancie les classes d'agents."""
        from raphael.agents import (
            Sophie, Victor, Elena, Marcus, Aurora,
            Felix, Diana, Noah, Luna, Axel, Kofi, Aminata,
        )
        agent_map = {
            "sophie": Sophie, "victor": Victor, "elena": Elena,
            "marcus": Marcus, "aurora": Aurora, "felix": Felix,
            "diana": Diana, "noah": Noah, "luna": Luna, "axel": Axel,
            "kofi": Kofi, "aminata": Aminata,
        }
        for name, cls in agent_map.items():
            self._agent_instances[name] = cls(self._short_memory, self._long_memory)
        logger.debug(f"Agents instanciés: {list(self._agent_instances.keys())}")

    async def chat(self, user_message: str, session_id: str = "default") -> str:
        """
        Point d'entrée principal: traite un message utilisateur.
        Raphaël comprend, délègue, et retourne une réponse synthétique.
        """
        if not self._initialized:
            await self.initialize()

        start = time.monotonic()
        task_id = str(uuid.uuid4())[:8]

        # Stocke le message en mémoire
        await self._short_memory.add(session_id, "user", user_message)

        # Phase 1: Raphaël analyse la demande et détermine la stratégie
        strategy = await self._analyze_and_plan(user_message, session_id)

        # Phase 2: Exécution des délégations
        execution = TaskExecution(task_id, user_message)
        agent_outputs = []

        for delegation in strategy.get("delegations", []):
            agent_name = delegation.get("agent", "").lower()
            sub_task = delegation.get("task", user_message)
            context = delegation.get("context", "")

            agent = self._agent_instances.get(agent_name)
            if agent is None:
                # Essaie de créer un nouvel agent si nécessaire
                if self._settings.auto_spawn_agents:
                    new_spec = await self._factory.spawn_agent(
                        domain=delegation.get("domain", agent_name),
                        missing_skills=delegation.get("skills", []),
                        context=user_message,
                    )
                    if new_spec:
                        agent = await self._create_dynamic_agent(new_spec)
                if agent is None:
                    logger.warning(f"Agent '{agent_name}' non trouvé, skip")
                    continue

            logger.info(f"[Raphaël] Délègue à {agent_name}: {sub_task[:80]}")
            result = await agent.execute(sub_task, context=context, session_id=session_id)
            agent_outputs.append(result)
            execution.agent_results.append({
                "agent": result.agent_name,
                "task": result.task,
                "result": result.result,
                "success": result.success,
            })
            execution.agents_used.append(result.agent_name)
            await self._registry.update_performance(agent_name, result.success)

        # Phase 3: Synthèse finale par Raphaël
        if agent_outputs:
            final_response = await self._synthesize(user_message, agent_outputs, strategy)
        else:
            # Raphaël répond directement si pas de délégation
            final_response = await self._direct_response(user_message, session_id)

        execution.final_response = final_response
        execution.success = bool(agent_outputs)
        execution.elapsed = round(time.monotonic() - start, 2)

        await self._short_memory.add(session_id, "assistant", final_response)
        await self._long_memory.store_task_result(
            "raphael", user_message, final_response, success=execution.success
        )

        logger.info(
            f"[Raphaël] Tâche {task_id} complète en {execution.elapsed}s | "
            f"Agents: {execution.agents_used}"
        )
        return final_response

    async def _analyze_and_plan(self, user_message: str, session_id: str) -> dict:
        """Phase 1: Analyse la demande et planifie les délégations."""
        context = await self._short_memory.get_summary(session_id)
        available_agents = await self._registry.list_names()

        plan_prompt = f"""Analyse cette demande utilisateur et détermine la stratégie optimale.

Demande: {user_message}

Contexte de session: {context}

Agents disponibles: {', '.join(available_agents)}

Réponds en JSON avec ce format exact:
{{
  "understanding": "Ce que l'utilisateur veut vraiment en 1-2 phrases",
  "complexity": "simple|moderate|complex",
  "delegations": [
    {{
      "agent": "nom_agent",
      "task": "Tâche précise à déléguer",
      "context": "Contexte additionnel pour l'agent",
      "priority": 1
    }}
  ],
  "direct_response": true/false
}}

Règles:
- "direct_response": true si la demande ne nécessite pas d'agent spécialisé (salutation, question simple sur le réseau, etc.)
- Max 3-4 délégations par requête pour rester efficace
- Pour les tâches à risque financier, inclure TOUJOURS noah dans les délégations
- Priorise la qualité sur la quantité

Réponds UNIQUEMENT avec le JSON."""

        try:
            response = await self._client.messages.create(
                model=self._settings.fast_model,
                max_tokens=1024,
                system=RAPHAEL_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": plan_prompt}],
            )
            import json
            import re
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Planning error: {e}")

        # Fallback: routing basique
        matched = await self._router.route(user_message)
        delegations = []
        for agent in matched[:2]:
            delegations.append({
                "agent": agent.name.lower(),
                "task": user_message,
                "context": "",
                "priority": 1,
            })
        return {
            "understanding": user_message,
            "complexity": "moderate",
            "delegations": delegations,
            "direct_response": not bool(matched),
        }

    async def _synthesize(self, original_request: str, results, strategy: dict) -> str:
        """Phase 3: Synthétise les résultats des agents en une réponse cohérente."""
        results_text = "\n\n".join([
            f"=== {r.agent_name} ({r.role}) ===\n{r.result}"
            for r in results if r.success
        ])
        failed = [r.agent_name for r in results if not r.success]

        synthesis_prompt = f"""Tu as orchestré plusieurs agents pour répondre à cette demande.

Demande originale: {original_request}

Compréhension: {strategy.get('understanding', '')}

Résultats des agents:
{results_text}

{"Agents ayant échoué: " + ', '.join(failed) if failed else ""}

Synthétise maintenant une réponse finale COMPLÈTE et COHÉRENTE qui:
1. Intègre harmonieusement tous les résultats
2. Élimine les redondances
3. Présente de façon claire et structurée
4. Ajoute ta valeur ajoutée de coordinateur (insights additionnels, recommandations)
5. Indique les prochaines étapes si pertinent

Commence directement par la réponse synthétique, sans mentionner la mécanique interne."""

        response = await self._client.messages.create(
            model=self._settings.specialist_model,
            max_tokens=4096,
            system=RAPHAEL_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )

        text_parts = [block.text for block in response.content if hasattr(block, "text")]
        return "\n".join(text_parts).strip()

    async def _direct_response(self, message: str, session_id: str) -> str:
        """Raphaël répond directement sans délégation."""
        context = await self._short_memory.get_context(session_id, max_messages=10)
        context.append({"role": "user", "content": message})

        response = await self._client.messages.create(
            model=self._settings.specialist_model,
            max_tokens=2048,
            system=RAPHAEL_SYSTEM_PROMPT,
            messages=context,
        )

        text_parts = [block.text for block in response.content if hasattr(block, "text")]
        return "\n".join(text_parts).strip()

    async def _create_dynamic_agent(self, spec: AgentSpec):
        """Crée une instance dynamique d'un agent à partir d'une spec registre."""
        from raphael.agents.base import BaseAgent

        class DynamicAgent(BaseAgent):
            name = spec.name
            role = spec.role
            expertise = spec.expertise

            @property
            def system_prompt(self) -> str:
                return spec.system_prompt

        instance = DynamicAgent(self._short_memory, self._long_memory)
        self._agent_instances[spec.name.lower()] = instance
        logger.info(f"Agent dynamique instancié: {spec.name}")
        return instance

    async def stream_chat(self, user_message: str, session_id: str = "default") -> AsyncIterator[str]:
        """Version streaming du chat — retourne les chunks au fil de l'eau."""
        if not self._initialized:
            await self.initialize()

        await self._short_memory.add(session_id, "user", user_message)

        # Raphaël streame directement pour les réponses simples
        context = await self._short_memory.get_context(session_id, max_messages=10)
        context.append({"role": "user", "content": user_message})

        async with self._client.messages.stream(
            model=self._settings.orchestrator_model,
            max_tokens=8192,
            system=RAPHAEL_SYSTEM_PROMPT,
            messages=context,
            thinking={"type": "adaptive"},
        ) as stream:
            full_response = ""
            async for text in stream.text_stream:
                full_response += text
                yield text

        await self._short_memory.add(session_id, "assistant", full_response)

    async def get_network_status(self) -> dict:
        """Retourne le statut du réseau Raphaël."""
        return await self._registry.get_stats()

    async def spawn_agent_for_skill(self, domain: str, skills: list[str]) -> Optional[AgentSpec]:
        """API publique pour créer un nouvel agent."""
        return await self._factory.spawn_agent(domain, skills)
