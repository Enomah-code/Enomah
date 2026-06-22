"""
Routes d'administration : statistiques globales pour l'interface admin.
Réservées aux utilisateurs administrateurs.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_user, get_core
from app.database import get_session
from app.database.models import AgentRecord, Mission, User
from app.llm import health_check
from app.runtime import AngeleckCore

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def stats(
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    core: AngeleckCore = Depends(get_core),
):
    """Vue d'ensemble : agents, missions, utilisateurs, état d'Ollama."""
    total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
    total_missions = (
        await session.execute(select(func.count(Mission.id)))
    ).scalar() or 0
    success_missions = (
        await session.execute(
            select(func.count(Mission.id)).where(Mission.success.is_(True))
        )
    ).scalar() or 0

    agents = (await session.execute(select(AgentRecord))).scalars().all()
    ollama = await health_check()

    return {
        "users": total_users,
        "missions_total": total_missions,
        "missions_success": success_missions,
        "success_rate": round(success_missions / total_missions, 3)
        if total_missions
        else 0.0,
        "agents_total": len(agents),
        "agents_generated": sum(1 for a in agents if a.is_generated),
        "ollama": ollama,
        "agents": [
            {
                "key": a.key,
                "name": a.name,
                "role": a.role,
                "is_generated": a.is_generated,
                "tasks": a.tasks_count,
                "success_rate": round(a.success_count / a.tasks_count, 3)
                if a.tasks_count
                else 0.0,
            }
            for a in agents
        ],
    }


@router.get("/missions")
async def recent_missions(
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    limit: int = 100,
):
    """Historique récent des missions (toutes confondues)."""
    rows = (
        await session.execute(
            select(Mission).order_by(Mission.created_at.desc()).limit(limit)
        )
    ).scalars().all()
    return [
        {
            "agent_key": m.agent_key,
            "request": m.request,
            "skill": m.skill,
            "success": m.success,
            "elapsed_seconds": m.elapsed_seconds,
            "created_at": m.created_at,
        }
        for m in rows
    ]
