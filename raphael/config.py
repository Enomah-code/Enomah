from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Anthropic
    anthropic_api_key: str = ""
    orchestrator_model: str = "claude-opus-4-8"
    specialist_model: str = "claude-sonnet-4-6"
    fast_model: str = "claude-haiku-4-5"

    # Database
    database_url: str = "sqlite+aiosqlite:///./raphael.db"
    vector_db_path: str = "./raphael_vectors"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Search
    serper_api_key: str = ""
    brave_search_api_key: str = ""

    # Image generation
    stability_ai_api_key: str = ""
    openai_api_key: str = ""
    replicate_api_key: str = ""

    # Video generation
    runwayml_api_key: str = ""
    heygen_api_key: str = ""
    pika_api_key: str = ""

    # Advertising
    meta_access_token: str = ""
    meta_app_id: str = ""
    meta_app_secret: str = ""
    google_ads_developer_token: str = ""
    google_ads_client_id: str = ""
    google_ads_client_secret: str = ""
    google_ads_refresh_token: str = ""
    google_ads_customer_id: str = ""
    tiktok_access_token: str = ""

    # Social media
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    instagram_access_token: str = ""
    linkedin_access_token: str = ""

    # Trading
    binance_api_key: str = ""
    binance_secret_key: str = ""
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    alpha_vantage_api_key: str = ""
    coinmarketcap_api_key: str = ""

    # E-commerce
    shopify_access_token: str = ""
    shopify_store_url: str = ""
    stripe_secret_key: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "changeme"
    api_debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # Memory & Evolution
    memory_max_entries: int = 10000
    evolution_interval_hours: int = 24
    performance_eval_interval_hours: int = 6
    auto_spawn_agents: bool = True
    min_task_success_rate: float = 0.75

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/raphael.log"


@lru_cache
def get_settings() -> Settings:
    return Settings()
