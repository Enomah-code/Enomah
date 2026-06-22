"""
Routes des agents : liste (GET /agents) et création manuelle (POST /create-agent).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_core, get_current_user
from app.database import get_session
from app.database.models import AgentRecord, User
from app.models import AgentInfo, CreateAgentRequest
from app.runtime import AngeleckCore

router = APIRouter(tags=["agents"])


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    core: AngeleckCore = Depends(get_core),
):
    """Retourne les agents disponibles avec leurs statistiques."""
    rows = {
        r.key: r
        for r in (await session.execute(select(AgentRecord))).scalars().all()
    }
    result: list[AgentInfo] = []
    for agent in core.registry.all():
        rec = rows.get(agent.key)
        tasks = rec.tasks_count if rec else 0
        success = rec.success_count if rec else 0
        result.append(
            AgentInfo(
                key=agent.key,
                name=agent.name,
                role=agent.definition.role,
                skills=agent.definition.skills,
                is_generated=agent.definition.is_generated,
                is_active=rec.is_active if rec else True,
                tasks_count=tasks,
                success_rate=round(success / tasks, 3) if tasks else 0.0,
            )
        )
    return result


@router.post("/create-agent", response_model=AgentInfo, status_code=201)
async def create_agent(
    payload: CreateAgentRequest,
    user: User = Depends(get_current_user),
    core: AngeleckCore = Depends(get_core),
):
    """Déclenche la création d'un nouvel agent spécialisé via la factory."""
    request_text = payload.description or (
        f"Créer un expert du domaine '{payload.domain}' "
        f"avec les compétences: {', '.join(payload.skills)}"
    )
    definition = await core.recruiter.recruit(request_text, payload.domain)
    if definition is None:
        raise HTTPException(
            status_code=502,
            detail="La factory n'a pas pu générer l'agent (Ollama indisponible ?).",
        )
    return AgentInfo(
        key=definition.key,
        name=definition.name,
        role=definition.role,
        skills=definition.skills,
        is_generated=True,
        is_active=True,
        tasks_count=0,
        success_rate=0.0,
    )
