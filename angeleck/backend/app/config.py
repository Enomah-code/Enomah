"""
Configuration centrale d'Angeleck OS.

Toutes les variables sont chargées depuis l'environnement (fichier .env) via
pydantic-settings. Aucune valeur sensible n'est codée en dur : on fournit des
valeurs par défaut raisonnables pour un déploiement local Docker.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres applicatifs (12-factor)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -----------------------------------------------------
    app_name: str = "Angeleck OS"
    app_env: str = Field(default="development")  # development | production
    debug: bool = Field(default=True)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    # CORS — origines autorisées (le frontend EMK Blue Diamond Studio).
    # Liste séparée par des virgules dans la variable CORS_ORIGINS.
    cors_origins: str = Field(default="*")

    # --- Sécurité / Auth -------------------------------------------------
    secret_key: str = Field(default="change-me-in-production-please")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 24)  # 24h

    # --- Base de données PostgreSQL --------------------------------------
    postgres_user: str = Field(default="angeleck")
    postgres_password: str = Field(default="angeleck")
    postgres_db: str = Field(default="angeleck")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)

    # --- Mémoire vectorielle ChromaDB ------------------------------------
    chroma_host: str = Field(default="localhost")
    chroma_port: int = Field(default=8001)
    chroma_collection: str = Field(default="angeleck_memory")
    # Modèle d'embedding (sentence-transformers) pour la mémoire longue.
    embedding_model: str = Field(default="all-MiniLM-L6-v2")

    # --- Modèles IA (Ollama local) --------------------------------------
    ollama_base_url: str = Field(default="http://localhost:11434")
    # Modèle par défaut du cerveau central (raisonnement / routage).
    ollama_brain_model: str = Field(default="llama3.1")
    # Modèle par défaut des agents experts.
    ollama_agent_model: str = Field(default="mistral")
    ollama_timeout: int = Field(default=120)
    ollama_temperature: float = Field(default=0.7)

    # --- Chemins ---------------------------------------------------------
    # Dossier où le recruteur écrit le code des agents générés dynamiquement.
    generated_agents_dir: str = Field(default="app/agents/generated")
    uploads_dir: str = Field(default="uploads")

    # ------------------------------------------------------------------ #
    @property
    def database_url(self) -> str:
        """URL SQLAlchemy async (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """URL SQLAlchemy synchrone (psycopg2) — utile pour Alembic/Streamlit."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        """Liste des origines CORS."""
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuration (mis en cache)."""
    return Settings()


settings = get_settings()
