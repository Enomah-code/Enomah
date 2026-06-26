"""
Mémoire courte / persistance relationnelle — PostgreSQL via SQLAlchemy 2.0 async.

Tables :
  * users           — comptes utilisateurs (auth).
  * conversations   — fils de discussion (sessions).
  * messages        — messages échangés (historique).
  * agents          — REGISTRE DES AGENTS persistant (natifs + générés).
  * task_logs       — journal des tâches / logs système.

Cette couche constitue la "mémoire de travail" structurée d'Angeleck OS.
La mémoire sémantique long terme vit dans ChromaDB (voir vector_memory.py).
"""
from __future__ import annotations

import datetime as dt
import logging
import uuid
from typing import AsyncGenerator

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.config import settings

logger = logging.getLogger("angeleck.db")


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    """Base déclarative SQLAlchemy."""


# --------------------------------------------------------------------------- #
#  Modèles
# --------------------------------------------------------------------------- #
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="Nouvelle conversation")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    # Quel(s) agent(s) a/ont produit la réponse, métadonnées de routage, etc.
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class AgentRecord(Base):
    """REGISTRE DES AGENTS — source de vérité persistante."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True)  # ex: "writer"
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    skills: Mapped[list] = mapped_column(JSON, default=list)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    system_prompt: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(80), default="")
    # native = agent livré d'origine ; generated = recruté automatiquement.
    origin: Mapped[str] = mapped_column(String(20), default="native")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Si généré : chemin du fichier python produit par le recruteur.
    module_path: Mapped[str] = mapped_column(String(255), default="")
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TaskLog(Base):
    """Journal des tâches et événements système (Module 6 — logs)."""

    __tablename__ = "task_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), default="", index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), default="")
    event: Mapped[str] = mapped_column(String(80))  # chat | route | recruit | error...
    agent_key: Mapped[str] = mapped_column(String(80), default="")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="ok")  # ok | error
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


# --------------------------------------------------------------------------- #
#  Moteur / session
# --------------------------------------------------------------------------- #
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI : fournit une session DB par requête."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Crée les tables si elles n'existent pas (démarrage applicatif)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de données initialisée (tables créées).")
