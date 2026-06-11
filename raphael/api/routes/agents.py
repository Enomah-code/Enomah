from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/agents", tags=["Agents"])


class SpawnRequest(BaseModel):
    domain: str
    skills: list[str]


class AgentTaskRequest(BaseModel):
    task: str
    context: Optional[str] = ""
    session_id: Optional[str] = "default"


def get_raphael():
    from raphael.api.main import get_raphael_instance
    return get_raphael_instance()


@router.get("")
async def list_agents():
    """Liste tous les agents actifs du réseau."""
    raphael = get_raphael()
    return await raphael.get_network_status()


@router.post("/spawn")
async def spawn_agent(request: SpawnRequest):
    """Crée un nouvel agent spécialisé pour un domaine donné."""
    raphael = get_raphael()
    spec = await raphael.spawn_agent_for_skill(request.domain, request.skills)
    if not spec:
        raise HTTPException(status_code=500, detail="Impossible de créer l'agent")
    return {
        "name": spec.name,
        "role": spec.role,
        "expertise": spec.expertise,
        "status": "created",
    }


@router.post("/{agent_name}/task")
async def run_agent_task(agent_name: str, request: AgentTaskRequest):
    """Exécute une tâche directement sur un agent spécifique."""
    raphael = get_raphael()
    agent = raphael._agent_instances.get(agent_name.lower())
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' non trouvé")

    result = await agent.execute(
        request.task,
        context=request.context or "",
        session_id=request.session_id or "default",
    )
    return {
        "agent": result.agent_name,
        "task": result.task,
        "result": result.result,
        "success": result.success,
        "elapsed_seconds": result.elapsed_seconds,
        "tools_used": result.tools_used,
    }
