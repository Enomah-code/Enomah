"""
Configuration centrale d'Angeleck OS.

Toutes les variables sont chargées depuis l'environnement (.env) via
pydantic-settings. Aucune clé d'API payante n'est requise : le système
fonctionne par défaut avec Ollama (modèles auto-hébergés).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Identité applicative ---
    app_name: str = "Angeleck OS"
    app_version: str = "1.0.0"
    environment: str = "development"  # development | production

    # --- Ollama (moteur IA local, aucune API payante) ---
    ollama_base_url: str = "http://localhost:11434"
    # Modèle du cerveau central (raisonnement / orchestration)
    supervisor_model: str = "llama3"
    # Modèle des agents spécialisés
    agent_model: str = "mistral"
    # Modèle rapide (classification d'intention, tâches courtes)
    fast_model: str = "phi3"
    # Modèle de génération d'agents (le recruteur)
    factory_model: str = "qwen2.5-coder"
    # Température par défaut
    llm_temperature: float = 0.7
    llm_request_timeout: int = 180

    # --- Base de données relationnelle (PostgreSQL) ---
    database_url: str = (
        "postgresql+asyncpg://angeleck:angeleck@localhost:5432/angeleck"
    )
    db_echo: bool = False

    # --- Mémoire vectorielle (ChromaDB) ---
    vector_db_path: str = "./data/chroma"
    embedding_model: str = "nomic-embed-text"  # via Ollama

    # --- Cache / mémoire court terme (Redis) ---
    redis_url: str = "redis://localhost:6379/0"
    short_term_ttl_seconds: int = 60 * 60 * 6  # 6h

    # --- Sécurité / JWT ---
    secret_key: str = "change-me-with-a-strong-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # --- Limitation de ressources ---
    rate_limit_per_minute: int = 60
    max_upload_mb: int = 25
    max_agent_iterations: int = 8

    # --- Factory (recruteur automatique) ---
    auto_spawn_agents: bool = True
    generated_agents_path: str = "./app/agents/generated"

    # --- Logs ---
    log_level: str = "INFO"
    log_file: str = "logs/angeleck.log"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique (mise en cache) des paramètres."""
    return Settings()
