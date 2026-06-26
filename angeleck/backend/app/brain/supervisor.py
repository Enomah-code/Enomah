"""
CERVEAU CENTRAL — Superviseur Angeleck OS (Module 1).

Orchestration via LangGraph. Le graphe d'état suit ce flux :

    analyze ──► recruit (si compétence manquante) ──► execute ──► synthesize ──► remember

Étapes :
  * analyze    : routeur → quel(s) agent(s) / faut-il recruter ?
  * recruit    : si besoin, crée un nouvel agent puis ré-aiguille vers lui.
  * execute    : exécute le(s) agent(s) sélectionné(s) avec le contexte mémoire.
  * synthesize : si plusieurs agents, fusionne les réponses en une seule.
  * remember   : écrit le résultat dans la mémoire longue (ChromaDB).

Si LangGraph n'est pas installé, un orchestrateur linéaire équivalent prend le
relais (`_run_linear`) — le système reste 100 % fonctionnel.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict

from app.agents.registry import registry
from app.brain.recruiter import recruiter
from app.brain.router import RouteDecision, router
from app.config import settings
from app.memory.vector_memory import vector_memory
from app.models.ollama import OllamaClient

logger = logging.getLogger("angeleck.supervisor")


class BrainState(TypedDict, total=False):
    """État circulant dans le graphe LangGraph."""

    request: str
    user_id: str
    conversation_id: str
    extra_context: str
    history: List[Dict[str, str]]
    memory_context: str
    decision: RouteDecision
    agent_outputs: List[Dict[str, str]]
    final_answer: str
    agents_used: List[str]
    recruited: Optional[str]


class Supervisor:
    """Cerveau central orchestrant routage, recrutement, exécution et mémoire."""

    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self._client = client or OllamaClient()
        self._graph = self._build_graph()

    # ------------------------------------------------------------------ #
    #  Construction du graphe LangGraph (avec fallback)
    # ------------------------------------------------------------------ #
    def _build_graph(self):
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError:  # pragma: no cover
            logger.warning("langgraph indisponible — orchestrateur linéaire utilisé.")
            return None

        graph = StateGraph(BrainState)
        graph.add_node("analyze", self._node_analyze)
        graph.add_node("recruit", self._node_recruit)
        graph.add_node("execute", self._node_execute)
        graph.add_node("synthesize", self._node_synthesize)
        graph.add_node("remember", self._node_remember)

        graph.add_edge(START, "analyze")
        # Branchement conditionnel : recruter ou exécuter directement.
        graph.add_conditional_edges(
            "analyze",
            self._needs_recruit,
            {"recruit": "recruit", "execute": "execute"},
        )
        graph.add_edge("recruit", "execute")
        graph.add_edge("execute", "synthesize")
        graph.add_edge("synthesize", "remember")
        graph.add_edge("remember", END)
        return graph.compile()

    @staticmethod
    def _needs_recruit(state: BrainState) -> str:
        decision = state.get("decision")
        if decision and decision.needs_new_agent:
            return "recruit"
        return "execute"

    # ------------------------------------------------------------------ #
    #  Nœuds
    # ------------------------------------------------------------------ #
    async def _node_analyze(self, state: BrainState) -> BrainState:
        request = state["request"]
        # Récupère le contexte mémoire long terme pertinent.
        state["memory_context"] = vector_memory.build_context(request, k=4)
        state["decision"] = await router.route(request)
        logger.info(
            "Analyse → agents=%s recrutement=%s",
            state["decision"].agent_keys,
            state["decision"].needs_new_agent,
        )
        return state

    async def _node_recruit(self, state: BrainState) -> BrainState:
        decision = state["decision"]
        spec = await recruiter.recruit(decision.missing_skill, state["request"])
        if spec is not None:
            state["recruited"] = spec.key
            state["decision"].agent_keys = [spec.key]
        else:
            # Échec du recrutement : on tombe sur un agent généraliste.
            fallback = "marketing" if registry.exists("marketing") else None
            state["decision"].agent_keys = [fallback] if fallback else []
        return state

    async def _node_execute(self, state: BrainState) -> BrainState:
        decision = state["decision"]
        outputs: List[Dict[str, str]] = []
        for key in decision.agent_keys:
            agent = registry.get(key)
            if not agent:
                continue
            try:
                reply = await agent.run(
                    task=state["request"],
                    memory_context=state.get("memory_context", ""),
                    extra_context=state.get("extra_context", ""),
                    history=state.get("history"),
                )
                outputs.append({"agent": key, "name": agent.name, "content": reply})
            except Exception as exc:  # noqa: BLE001
                logger.error("Agent %s a échoué : %s", key, exc)
                outputs.append(
                    {"agent": key, "name": key, "content": f"[Erreur agent: {exc}]"}
                )
        state["agent_outputs"] = outputs
        state["agents_used"] = [o["agent"] for o in outputs]
        return state

    async def _node_synthesize(self, state: BrainState) -> BrainState:
        outputs = state.get("agent_outputs", [])
        if not outputs:
            state["final_answer"] = (
                "Aucun agent n'a pu traiter la demande. Vérifiez qu'Ollama est "
                "lancé et qu'un modèle est installé."
            )
            return state
        if len(outputs) == 1:
            state["final_answer"] = outputs[0]["content"]
            return state

        # Fusion multi-agents par le cerveau.
        combined = "\n\n".join(
            f"### Contribution de {o['name']}\n{o['content']}" for o in outputs
        )
        prompt = (
            "Tu es le cerveau central Angeleck OS. Plusieurs agents experts ont "
            "répondu à la demande de l'utilisateur. Synthétise leurs contributions "
            "en UNE réponse cohérente, sans répétition, fidèle au contenu.\n\n"
            f"Demande : {state['request']}\n\n{combined}\n\nRéponse finale :"
        )
        try:
            state["final_answer"] = await self._client.chat(
                [{"role": "user", "content": prompt}],
                model=settings.ollama_brain_model,
                temperature=0.5,
            )
        except Exception:  # noqa: BLE001
            # En cas d'échec de synthèse, on concatène simplement.
            state["final_answer"] = combined
        return state

    async def _node_remember(self, state: BrainState) -> BrainState:
        answer = state.get("final_answer", "")
        if answer:
            import uuid

            vector_memory.remember(
                text=f"Demande: {state['request']}\nRéponse: {answer}",
                doc_id=str(uuid.uuid4()),
                metadata={
                    "user_id": state.get("user_id", ""),
                    "conversation_id": state.get("conversation_id", ""),
                    "agents": ",".join(state.get("agents_used", [])),
                },
            )
        return state

    # ------------------------------------------------------------------ #
    #  Point d'entrée public
    # ------------------------------------------------------------------ #
    async def handle(
        self,
        request: str,
        user_id: str = "",
        conversation_id: str = "",
        extra_context: str = "",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Traite une requête utilisateur de bout en bout.

        Retourne : {answer, agents_used, recruited, reasoning}.
        """
        state: BrainState = {
            "request": request,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "extra_context": extra_context,
            "history": history or [],
        }

        if self._graph is not None:
            result: BrainState = await self._graph.ainvoke(state)
        else:
            result = await self._run_linear(state)

        decision = result.get("decision")
        return {
            "answer": result.get("final_answer", ""),
            "agents_used": result.get("agents_used", []),
            "recruited": result.get("recruited"),
            "reasoning": decision.reasoning if decision else "",
        }

    async def _run_linear(self, state: BrainState) -> BrainState:
        """Orchestrateur de secours (sans LangGraph)."""
        state = await self._node_analyze(state)
        if self._needs_recruit(state) == "recruit":
            state = await self._node_recruit(state)
        state = await self._node_execute(state)
        state = await self._node_synthesize(state)
        state = await self._node_remember(state)
        return state


# Singleton
supervisor = Supervisor()
