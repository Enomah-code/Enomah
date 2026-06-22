"""
Routes mémoire : GET /memory (mémoire utilisateur) + écriture de préférences.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_session
from app.database.models import Mission, User, UserMemory
from app.models import MemoryItem

router = APIRouter(tags=["memory"])


@router.get("/memory")
async def get_memory(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Retourne la mémoire utilisateur : préférences + historique des missions."""
    prefs = (
        await session.execute(
            select(UserMemory).where(UserMemory.user_id == user.id)
        )
    ).scalars().all()

    missions = (
        await session.execute(
            select(Mission)
            .where(Mission.user_id == user.id)
            .order_by(Mission.created_at.desc())
            .limit(50)
        )
    ).scalars().all()

    return {
        "preferences": [
            {"key": p.key, "value": p.value, "category": p.category}
            for p in prefs
        ],
        "missions": [
            {
                "agent_key": m.agent_key,
                "request": m.request,
                "skill": m.skill,
                "success": m.success,
                "created_at": m.created_at,
            }
            for m in missions
        ],
    }


@router.post("/memory")
async def add_memory(
    item: MemoryItem,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Enregistre une préférence / un fait à mémoriser pour l'utilisateur."""
    session.add(
        UserMemory(
            user_id=user.id,
            key=item.key,
            value=item.value,
            category=item.category,
        )
    )
    return {"status": "saved"}
