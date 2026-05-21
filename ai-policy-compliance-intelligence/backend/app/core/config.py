import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        enable_decoding=False,
    )

    app_name: str = "AI-Powered Policy Compliance Intelligence Assistant"
    app_version: str = "1.0.0"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    data_dir: Path = BASE_DIR / "data"
    raw_dir: Path = BASE_DIR / "data" / "raw"
    processed_dir: Path = BASE_DIR / "data" / "processed"
    embeddings_dir: Path = BASE_DIR / "data" / "embeddings"

    llm_provider: Literal["local", "openrouter"] = "local"
    embedding_provider: Literal["local", "openrouter"] = "local"
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_site_url: str | None = None
    openrouter_app_name: str = "AI Policy Compliance Intelligence"

    document_store_provider: Literal["local", "mongodb"] = "local"
    mongodb_uri: str | None = None
    mongodb_database: str = "policy_compliance"

    cache_provider: Literal["local", "upstash"] = "local"
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None

    graph_provider: Literal["local", "neo4j"] = "local"
    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None

    vector_store_provider: Literal["local", "weaviate"] = "local"
    weaviate_url: str | None = None
    weaviate_api_key: str | None = None
    weaviate_collection: str = "PolicyChunk"

    max_upload_mb: int = 25
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_top_k: int = 6
    risk_threshold_high: float = 0.72
    risk_threshold_medium: float = 0.42
    enable_link_scraping: bool = True
    scrape_timeout_seconds: float = 8.0
    max_scraped_links: int = 5
    max_scraped_chars_per_link: int = 5000

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("weaviate_url", mode="before")
    @classmethod
    def normalize_weaviate_url(cls, value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return value
        stripped = value.strip()
        if stripped.startswith(("http://", "https://")):
            return stripped
        return f"https://{stripped}"

    def ensure_directories(self) -> None:
        for path in (self.data_dir, self.raw_dir, self.processed_dir, self.embeddings_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
