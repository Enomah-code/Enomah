"""
Cerveau central d'Angeleck OS — le Superviseur.

Orchestration via LangGraph (StateGraph) :

    analyze ──> route ──> [recruit?] ──> execute ──> synthesize

  - analyze   : comprend l'intention, détecte les compétences requises.
  - route     : sélectionne les agents existants ; signale une compétence manquante.
  - recruit   : (conditionnel) crée un nouvel agent via la factory.
  - execute   : lance les agents sélectionnés sur leurs missions.
  - synthesize: fusionne les résultats en une réponse finale cohérente.

Si LangGraph n'est pas disponible, un orchestrateur séquentiel équivalent
prend le relais (même logique, mêmes étapes).
"""
import time
from typing import Any, TypedDict

from loguru import logger

from app.agents import AgentRegistry, AgentResult
from app.brain.intent import IntentAnalyzer, RoutingDecision
from app.config import get_settings
from app.database import session_scope
from app.database.models import Mission
from app.factory import AgentRecruiter
from app.llm import get_chat_model
from app.memory import ShortTermMemory

try:
    from langgraph.graph import END, START, StateGraph

    _LANGGRAPH = True
except Exception:  # pragma: no cover
    _LANGGRAPH = False


class BrainState(TypedDict, total=False):
    request: str
    user_id: str
    session_id: str
    conversation_id: str
    decision: RoutingDecision
    results: list[AgentResult]
    created_agents: list[str]
    response: str


class Supervisor:
    def __init__(
        self,
        registry: AgentRegistry,
        recruiter: AgentRecruiter,
        short_memory: ShortTermMemory,
    ) -> None:
        self.registry = registry
        self.recruiter = recruiter
        self.short_memory = short_memory
        self.settings = get_settings()
        self.analyzer = IntentAnalyzer()
        self._graph = self._build_graph() if _LANGGRAPH else None

    # ------------------------------------------------------------------ #
    # Construction du graphe LangGraph
    # ------------------------------------------------------------------ #
    def _build_graph(self):
        graph = StateGraph(BrainState)
        graph.add_node("analyze", self._node_analyze)
        graph.add_node("recruit", self._node_recruit)
        graph.add_node("execute", self._node_execute)
        graph.add_node("synthesize", self._node_synthesize)

        graph.add_edge(START, "analyze")
        graph.add_conditional_edges(
            "analyze",
            self._should_recruit,
            {"recruit": "recruit", "execute": "execute"},
        )
        graph.add_edge("recruit", "execute")
        graph.add_edge("execute", "synthesize")
        graph.add_edge("synthesize", END)
        return graph.compile()

    @staticmethod
    def _should_recruit(state: BrainState) -> str:
        decision = state["decision"]
        return "recruit" if (decision.missing_skill or not decision.agents) else "execute"

    # ------------------------------------------------------------------ #
    # Nœuds
    # ------------------------------------------------------------------ #
    async def _node_analyze(self, state: BrainState) -> BrainState:
        decision = await self.analyzer.analyze(
            state["request"], self.registry.catalog(), self.registry.keys()
        )
        logger.info(
            f"Intention: {decision.intent} | agents={decision.agents} "
            f"| manquant={decision.missing_skill}"
        )
        state["decision"] = decision
        state["created_agents"] = []
        return state

    async def _node_recruit(self, state: BrainState) -> BrainState:
        decision = state["decision"]
        new_def = await self.recruiter.recruit(
            state["request"], decision.missing_domain
        )
        if new_def:
            decision.agents.append(new_def.key)
            state["created_agents"] = [new_def.key]
        elif not decision.agents:
            # Aucun agent dispo + recrutement KO → on retombe sur un agent générique
            decision.agents = self.registry.keys()[:1]
        return state

    async def _node_execute(self, state: BrainState) -> BrainState:
        decision = state["decision"]
        results: list[AgentResult] = []
        for key in decision.agents:
            agent = self.registry.get(key)
            if agent is None:
                continue
            result = await agent.execute(
                task=state["request"],
                context=f"Intention détectée: {decision.intent}",
                session_id=state["session_id"],
            )
            results.append(result)
            await self.registry.record_mission(key, result.success)
            await self._persist_mission(state, decision, result)
        state["results"] = results
        return state

    async def _node_synthesize(self, state: BrainState) -> BrainState:
        results = state.get("results", [])
        if not results:
            state["response"] = (
                "Je n'ai pas pu mobiliser d'agent pour cette demande. "
                "Vérifiez qu'Ollama est démarré et qu'un modèle est installé."
            )
            return state

        if len(results) == 1:
            state["response"] = results[0].result
            return state

        # Plusieurs agents → synthèse par le superviseur
        llm = get_chat_model(self.settings.supervisor_model, temperature=0.5)
        combined = "\n\n".join(
            f"### Contribution de {r.agent_name} ({r.agent_key})\n{r.result}"
            for r in results
        )
        prompt = (
            "Tu es le cerveau central d'Angeleck OS. Voici les contributions de "
            "plusieurs experts pour répondre à la demande de l'utilisateur. "
            "Fusionne-les en UNE réponse finale cohérente, structurée et "
            f"actionnable, sans répétitions.\n\nDEMANDE: {state['request']}\n\n"
            f"{combined}"
        )
        try:
            response = await llm.ainvoke(prompt)
            state["response"] = (
                response.content if hasattr(response, "content") else str(response)
            )
        except Exception as e:  # pragma: no cover
            logger.warning(f"Synthèse en échec ({e}) — concaténation brute.")
            state["response"] = combined
        return state

    async def _persist_mission(
        self, state: BrainState, decision: RoutingDecision, result: AgentResult
    ) -> None:
        async with session_scope() as session:
            session.add(
                Mission(
                    user_id=state["user_id"],
                    conversation_id=state.get("conversation_id"),
                    request=state["request"],
                    agent_key=result.agent_key,
                    skill=", ".join(decision.skills),
                    result=result.result[:8000],
                    success=result.success,
                    elapsed_seconds=result.elapsed_seconds,
                )
            )

    # ------------------------------------------------------------------ #
    # Point d'entrée public
    # ------------------------------------------------------------------ #
    async def handle(
        self, request: str, user_id: str, session_id: str, conversation_id: str
    ) -> dict[str, Any]:
        """Traite une requête utilisateur de bout en bout."""
        start = time.monotonic()
        await self.short_memory.add(session_id, "user", request)

        state: BrainState = {
            "request": request,
            "user_id": user_id,
            "session_id": session_id,
            "conversation_id": conversation_id,
        }

        if self._graph is not None:
            final = await self._graph.ainvoke(state)
        else:
            final = await self._run_sequential(state)

        decision: RoutingDecision = final["decision"]
        results: list[AgentResult] = final.get("results", [])
        logger.info(f"Requête traitée en {time.monotonic() - start:.1f}s")

        return {
            "response": final.get("response", ""),
            "intent": decision.intent,
            "skills_detected": decision.skills,
            "created_agents": final.get("created_agents", []),
            "missions": [
                {
                    "agent_key": r.agent_key,
                    "agent_name": r.agent_name,
                    "skill": ", ".join(decision.skills),
                    "result": r.result,
                    "success": r.success,
                    "elapsed_seconds": r.elapsed_seconds,
                }
                for r in results
            ],
        }

    async def _run_sequential(self, state: BrainState) -> BrainState:
        """Fallback sans LangGraph : exécute les étapes en séquence."""
        state = await self._node_analyze(state)
        if self._should_recruit(state) == "recruit":
            state = await self._node_recruit(state)
        state = await self._node_execute(state)
        state = await self._node_synthesize(state)
        return state
