"""
Point d'entrée de l'API Angeleck OS (FastAPI).

Assemble :
  - le cycle de vie (initialisation du noyau au démarrage) ;
  - la sécurité (CORS, limitation de débit, validation) ;
  - les routes (auth, chat, agents, memory, upload, admin).
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.routes import admin, agents, auth, chat, memory, upload
from app.config import get_settings
from app.llm import health_check
from app.runtime import core

settings = get_settings()

# --- Logging ---
logger.remove()
logger.add(sys.stderr, level=settings.log_level)
Path("logs").mkdir(exist_ok=True)
logger.add(settings.log_file, rotation="10 MB", retention="30 days", level="DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise le noyau au démarrage, libère les ressources à l'arrêt."""
    try:
        await core.startup()
    except Exception as e:  # pragma: no cover - dépend de l'infra
        logger.error(f"Échec d'initialisation du noyau: {e}")
    yield
    logger.info("Arrêt d'Angeleck OS.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Écosystème IA multi-agents autonome — auto-hébergeable (Ollama).",
        lifespan=lifespan,
    )

    # --- CORS pour le frontend existant ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Limitation de débit (best-effort, sans dépendance lourde) ---
    _setup_rate_limit(app)

    # --- Routes ---
    prefix = settings.api_prefix
    app.include_router(auth.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(agents.router, prefix=prefix)
    app.include_router(memory.router, prefix=prefix)
    app.include_router(upload.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)

    @app.get("/health", tags=["system"])
    async def health():
        ollama = await health_check()
        return {
            "status": "ok" if core.ready else "starting",
            "app": settings.app_name,
            "version": settings.app_version,
            "ollama": ollama,
        }

    @app.get("/", tags=["system"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "api": settings.api_prefix,
        }

    return app


def _setup_rate_limit(app: FastAPI) -> None:
    """Limitation de débit en mémoire par IP (fenêtre glissante d'une minute)."""
    import time
    from collections import defaultdict, deque

    buckets: dict[str, deque] = defaultdict(deque)
    limit = settings.rate_limit_per_minute

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        # On ne limite pas les endpoints système / docs.
        if request.url.path.startswith(("/health", "/docs", "/openapi", "/redoc")):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = buckets[ip]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Trop de requêtes. Réessayez dans un instant."},
            )
        bucket.append(now)
        return await call_next(request)


app = create_app()
