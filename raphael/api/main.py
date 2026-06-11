import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from raphael.config import get_settings
from raphael.core.orchestrator import Raphael

# Instance globale de Raphaël
_raphael_instance: Raphael | None = None


def get_raphael_instance() -> Raphael:
    if _raphael_instance is None:
        raise RuntimeError("Raphaël n'est pas initialisé. Utilisez create_app() d'abord.")
    return _raphael_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _raphael_instance
    settings = get_settings()

    logger.info("Démarrage du réseau Raphaël...")
    _raphael_instance = Raphael()
    await _raphael_instance.initialize()

    # Démarre l'évolution en arrière-plan
    from raphael.evolution import EvolutionEngine
    evolution_engine = EvolutionEngine(
        registry=_raphael_instance._registry,
        factory=_raphael_instance._factory,
        long_memory=_raphael_instance._long_memory,
    )
    evolution_task = asyncio.create_task(evolution_engine.start_background_loop())

    logger.info(f"Raphaël opérationnel sur http://{settings.api_host}:{settings.api_port}")
    yield

    evolution_engine.stop()
    evolution_task.cancel()
    logger.info("Réseau Raphaël arrêté.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Raphaël AI Network",
        description="Réseau d'agents IA interconnectés et auto-évolutifs",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from raphael.api.routes import chat_router, agents_router, evolution_router
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(evolution_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {
            "name": "Raphaël AI Network",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        if _raphael_instance:
            stats = await _raphael_instance.get_network_status()
            return {"status": "healthy", "network": stats}
        return {"status": "initializing"}

    return app
