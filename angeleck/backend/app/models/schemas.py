"""
Schémas Pydantic : contrats d'entrée/sortie de l'API.
Servent aussi à la validation des entrées utilisateur (sécurité).
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Authentification ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Chat ---
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: str | None = None


class MissionInfo(BaseModel):
    agent_key: str
    agent_name: str
    skill: str
    result: str
    success: bool
    elapsed_seconds: float


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    intent: str
    skills_detected: list[str]
    missions: list[MissionInfo]
    created_agents: list[str] = []


# --- Agents ---
class AgentInfo(BaseModel):
    key: str
    name: str
    role: str
    skills: list[str]
    is_generated: bool
    is_active: bool
    tasks_count: int
    success_rate: float


class CreateAgentRequest(BaseModel):
    domain: str = Field(min_length=2, max_length=120)
    skills: list[str] = Field(default_factory=list, max_length=20)
    description: str = Field(default="", max_length=2000)


# --- Mémoire ---
class MemoryItem(BaseModel):
    key: str
    value: str
    category: str
    created_at: datetime | None = None
