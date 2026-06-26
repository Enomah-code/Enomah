"""
API ANGELECK (Modules 5, 6, 7) — couche de connexion du frontend.

Endpoints publics / auth :
  POST /api/auth/register   — créer un compte
  POST /api/auth/login      — obtenir un token (OAuth2 password flow)

Endpoints applicatifs (protégés par JWT) :
  POST /api/chat            — envoyer une demande au cerveau central
  GET  /api/agents          — lister les agents disponibles
  POST /api/create-agent    — recruter un agent dynamiquement
  POST /api/upload          — analyser un fichier
  GET  /api/history         — historique des conversations
  GET  /api/system/status   — état système (santé Ollama/DB/mémoire)

Ces routes constituent la "couche propre" demandée au Module 7 : le frontend
existant n'a qu'à appeler ces endpoints, sans aucune modification du design.
"""
from __future__ import annotations

import logging
import os
import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import registry
from app.auth.security import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)
from app.brain.recruiter import recruiter
from app.brain.supervisor import supervisor
from app.config import settings
from app.memory.database import (
    Conversation,
    Message,
    TaskLog,
    User,
    get_session,
)
from app.models.ollama import ollama_client
from app.tools.file_reader import read_upload

logger = logging.getLogger("angeleck.api")

api_router = APIRouter(prefix="/api")


# --------------------------------------------------------------------------- #
#  Schémas Pydantic
# --------------------------------------------------------------------------- #
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    agents_used: List[str]
    recruited: Optional[str] = None
    reasoning: str = ""


class CreateAgentRequest(BaseModel):
    skill: str = Field(min_length=3, description="Compétence/spécialité à créer")
    context: str = ""


# --------------------------------------------------------------------------- #
#  Logging helper
# --------------------------------------------------------------------------- #
async def _log(
    session: AsyncSession,
    event: str,
    user_id: str = "",
    conversation_id: str = "",
    agent_key: str = "",
    detail: Optional[dict] = None,
    status_: str = "ok",
) -> None:
    session.add(
        TaskLog(
            user_id=user_id,
            conversation_id=conversation_id,
            event=event,
            agent_key=agent_key,
            detail=detail or {},
            status=status_,
        )
    )
    await session.commit()


# --------------------------------------------------------------------------- #
#  AUTH (Module 6)
# --------------------------------------------------------------------------- #
@api_router.post("/auth/register", response_model=TokenResponse, tags=["auth"])
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """Crée un compte et renvoie un token."""
    user = await create_user(session, body.email, body.password, body.full_name)
    token = create_access_token(user.id, extra={"email": user.email})
    await _log(session, "register", user_id=user.id)
    return TokenResponse(access_token=token, user_id=user.id, email=user.email)


@api_router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """OAuth2 password flow : `username` = email."""
    user = await authenticate_user(session, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide.")
    token = create_access_token(user.id, extra={"email": user.email})
    await _log(session, "login", user_id=user.id)
    return TokenResponse(access_token=token, user_id=user.id, email=user.email)


# --------------------------------------------------------------------------- #
#  CHAT (Module 5) — cœur de l'interaction frontend
# --------------------------------------------------------------------------- #
@api_router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Le frontend envoie une demande → le cerveau central l'analyse, choisit/
    recrute le(s) agent(s), exécute et renvoie la réponse.
    """
    # Résoudre / créer la conversation.
    conversation = await _get_or_create_conversation(
        session, user.id, body.conversation_id, title_hint=body.message
    )

    # Reconstituer la mémoire courte (historique de session).
    history = await _conversation_history(session, conversation.id, limit=10)

    # Enregistrer le message utilisateur.
    session.add(
        Message(conversation_id=conversation.id, role="user", content=body.message)
    )
    await session.commit()

    # Appel du cerveau central.
    try:
        result = await supervisor.handle(
            request=body.message,
            user_id=user.id,
            conversation_id=conversation.id,
            history=history,
        )
    except Exception as exc:  # noqa: BLE001
        await _log(session, "chat", user.id, conversation.id, status_="error",
                   detail={"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"Erreur cerveau central : {exc}")

    # Enregistrer la réponse assistant.
    session.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            meta={
                "agents_used": result["agents_used"],
                "recruited": result["recruited"],
            },
        )
    )
    await session.commit()

    # Compteurs d'usage des agents.
    await _bump_usage(session, result["agents_used"])

    await _log(
        session, "chat", user.id, conversation.id,
        agent_key=",".join(result["agents_used"]),
        detail={"recruited": result["recruited"]},
    )

    return ChatResponse(
        answer=result["answer"],
        conversation_id=conversation.id,
        agents_used=result["agents_used"],
        recruited=result["recruited"],
        reasoning=result["reasoning"],
    )


# --------------------------------------------------------------------------- #
#  AGENTS (Module 5)
# --------------------------------------------------------------------------- #
@api_router.get("/agents", tags=["agents"])
async def list_agents(user: User = Depends(get_current_user)):
    """Liste les agents disponibles (natifs + générés)."""
    return {"agents": registry.catalogue(), "count": len(registry.all())}


@api_router.post("/create-agent", tags=["agents"])
async def create_agent(
    body: CreateAgentRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Création dynamique d'un agent (recruteur explicite)."""
    spec = await recruiter.recruit(body.skill, body.context)
    if spec is None:
        raise HTTPException(status_code=500, detail="Échec de la création de l'agent.")
    await _log(session, "recruit", user.id, agent_key=spec.key,
               detail={"skill": body.skill})
    return {"created": True, "agent": spec.to_dict()}


# --------------------------------------------------------------------------- #
#  UPLOAD (Module 5)
# --------------------------------------------------------------------------- #
@api_router.post("/upload", tags=["files"])
async def upload_file(
    file: UploadFile = File(...),
    message: str = Form("Analyse ce fichier."),
    conversation_id: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Reçoit un fichier, l'analyse (file_reader / data tools) puis fait traiter la
    demande par le cerveau central avec le contenu en contexte.
    """
    os.makedirs(settings.uploads_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    dest = os.path.join(settings.uploads_dir, safe_name)
    with open(dest, "wb") as fh:
        fh.write(await file.read())

    parsed = read_upload(dest)
    conversation = await _get_or_create_conversation(
        session, user.id, conversation_id, title_hint=file.filename
    )

    result = await supervisor.handle(
        request=message,
        user_id=user.id,
        conversation_id=conversation.id,
        extra_context=parsed.get("content", ""),
    )
    await _log(session, "upload", user.id, conversation.id,
               detail={"file": file.filename, "type": parsed.get("type")})

    return {
        "conversation_id": conversation.id,
        "file_type": parsed.get("type"),
        "file_meta": parsed.get("meta"),
        "answer": result["answer"],
        "agents_used": result["agents_used"],
    }


# --------------------------------------------------------------------------- #
#  HISTORY (Module 5)
# --------------------------------------------------------------------------- #
@api_router.get("/history", tags=["history"])
async def history(
    conversation_id: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Historique : liste des conversations ou messages d'une conversation."""
    if conversation_id:
        msgs = await session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "meta": m.meta,
                    "created_at": m.created_at.isoformat(),
                }
                for m in msgs
            ],
        }

    convs = await session.scalars(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    return {
        "conversations": [
            {"id": c.id, "title": c.title, "updated_at": c.updated_at.isoformat()}
            for c in convs
        ]
    }


# --------------------------------------------------------------------------- #
#  SYSTEM STATUS (alimente l'interface admin / le frontend)
# --------------------------------------------------------------------------- #
@api_router.get("/system/status", tags=["system"])
async def system_status():
    """État de santé des composants (public, pour monitoring)."""
    from app.memory.vector_memory import vector_memory

    ollama_ok = await ollama_client.ping()
    models = await ollama_client.list_models() if ollama_ok else []
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "ollama": {"online": ollama_ok, "models": models},
        "vector_memory": {"enabled": vector_memory.enabled},
        "agents": {"count": len(registry.all()), "keys": list(registry.skills_overview())},
    }


# --------------------------------------------------------------------------- #
#  Helpers internes
# --------------------------------------------------------------------------- #
async def _get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[str],
    title_hint: str = "",
) -> Conversation:
    if conversation_id:
        conv = await session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        if conv:
            return conv
    conv = Conversation(
        user_id=user_id,
        title=(title_hint[:60] or "Nouvelle conversation"),
    )
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


async def _conversation_history(
    session: AsyncSession, conversation_id: str, limit: int = 10
) -> List[dict]:
    msgs = await session.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    items = list(msgs)[::-1]  # ordre chronologique
    return [{"role": m.role, "content": m.content} for m in items]


async def _bump_usage(session: AsyncSession, agent_keys: List[str]) -> None:
    from app.memory.database import AgentRecord

    for key in agent_keys:
        record = await session.scalar(
            select(AgentRecord).where(AgentRecord.key == key)
        )
        if record:
            record.usage_count += 1
    await session.commit()
