"""
Route principale : POST /chat — point d'entrée du frontend vers le cerveau.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_core, get_current_user
from app.database import get_session
from app.database.models import Conversation, Message, User
from app.models import ChatRequest, ChatResponse
from app.runtime import AngeleckCore

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    core: AngeleckCore = Depends(get_core),
):
    """Envoie une demande à l'IA. Le cerveau choisit les experts et répond."""
    # Récupère/crée la conversation
    conversation = None
    if payload.conversation_id:
        conversation = (
            await session.execute(
                select(Conversation).where(
                    Conversation.id == payload.conversation_id,
                    Conversation.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
    if conversation is None:
        conversation = Conversation(
            user_id=user.id, title=payload.message[:60]
        )
        session.add(conversation)
        await session.flush()

    # Enregistre le message utilisateur
    session.add(
        Message(
            conversation_id=conversation.id, role="user", content=payload.message
        )
    )

    # Traitement par le cerveau central
    session_id = f"{user.id}:{conversation.id}"
    outcome = await core.supervisor.handle(
        request=payload.message,
        user_id=user.id,
        session_id=session_id,
        conversation_id=conversation.id,
    )

    # Enregistre la réponse de l'assistant
    session.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=outcome["response"],
            extra={
                "intent": outcome["intent"],
                "agents": [m["agent_key"] for m in outcome["missions"]],
            },
        )
    )

    return ChatResponse(
        conversation_id=conversation.id,
        response=outcome["response"],
        intent=outcome["intent"],
        skills_detected=outcome["skills_detected"],
        missions=outcome["missions"],
        created_agents=outcome["created_agents"],
    )
