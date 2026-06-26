"""
Point d'entrée FastAPI d'Angeleck OS.

Assemble :
  * le middleware CORS (connexion du frontend EMK Blue Diamond Studio) ;
  * le routeur API (/api/...) ;
  * le cycle de vie (création des tables, chargement de la base agents) ;
  * un endpoint racine de santé.

Lancement local :
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("angeleck")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Démarrage / arrêt applicatif."""
    logger.info("Démarrage d'Angeleck OS…")
    # 1. Initialiser la base relationnelle (tables).
    try:
        from app.memory.database import init_db

        await init_db()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Init DB différée (DB indisponible ?) : %s", exc)

    # 2. Recharger les agents générés persistés en base dans le registre.
    await _restore_generated_agents()

    # 3. Sonder Ollama (information seulement).
    from app.models.ollama import ollama_client

    if await ollama_client.ping():
        models = await ollama_client.list_models()
        logger.info("Ollama en ligne. Modèles : %s", ", ".join(models) or "(aucun)")
    else:
        logger.warning("Ollama hors ligne — les agents ne pourront pas répondre.")

    yield
    logger.info("Arrêt d'Angeleck OS.")


async def _restore_generated_agents() -> None:
    """Recharge en mémoire les agents générés enregistrés en base."""
    try:
        from sqlalchemy import select

        from app.agents.base import AgentSpec
        from app.agents.registry import registry
        from app.memory.database import AgentRecord, SessionLocal

        async with SessionLocal() as session:
            records = await session.scalars(
                select(AgentRecord).where(AgentRecord.origin == "generated")
            )
            for r in records:
                if registry.exists(r.key):
                    continue
                registry.register_spec(
                    AgentSpec(
                        key=r.key,
                        name=r.name,
                        role=r.role,
                        description=r.description,
                        skills=r.skills,
                        tools=r.tools,
                        system_prompt=r.system_prompt,
                        model=r.model,
                        origin="generated",
                    )
                )
        logger.info("Agents générés restaurés depuis la base.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Restauration des agents générés ignorée : %s", exc)


# --------------------------------------------------------------------------- #
app = FastAPI(
    title="Angeleck OS API",
    description=(
        "Cerveau central IA, agents experts auto-évolutifs et mémoire persistante. "
        "Powered by EMK Blue Diamond."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS (Module 7 : connexion du frontend existant sans le modifier) ----- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes API ------------------------------------------------------------ #
app.include_router(api_router)


@app.get("/", tags=["system"])
async def root():
    """Endpoint racine — santé rapide."""
    return {
        "name": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "api": "/api",
        "powered_by": "EMK Blue Diamond",
    }


@app.get("/health", tags=["system"])
async def health():
    return {"status": "healthy"}
