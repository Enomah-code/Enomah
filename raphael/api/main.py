import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    logger.info(f"Dashboard: http://{settings.api_host}:{settings.api_port}/dashboard")
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes API
    from raphael.api.routes import chat_router, agents_router, evolution_router, market_router
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(evolution_router, prefix="/api/v1")
    app.include_router(market_router, prefix="/api/v1")

    # Serve dashboard statique
    dashboard_path = Path(__file__).parent.parent.parent / "dashboard"
    if dashboard_path.exists():
        app.mount("/dashboard", StaticFiles(directory=str(dashboard_path), html=True), name="dashboard")

    @app.get("/")
    async def root():
        # Redirige vers le dashboard si disponible
        dashboard_index = dashboard_path / "index.html"
        if dashboard_index.exists():
            return FileResponse(str(dashboard_index))
        return {
            "name": "Raphaël AI Network",
            "version": "1.0.0",
            "status": "operational",
            "dashboard": "/dashboard",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        if _raphael_instance:
            stats = await _raphael_instance.get_network_status()
            return {"status": "healthy", "network": stats}
        return {"status": "initializing"}

    return app
