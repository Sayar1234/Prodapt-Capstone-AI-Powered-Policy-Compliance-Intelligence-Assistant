from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.database.redis import cache
from app.models.response_models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        services={"api": "ok", "cache": "ok" if await cache.ping() else "unavailable", "storage": "local"},
        providers={
            "llm": settings.llm_provider,
            "embedding": settings.embedding_provider,
            "document_store": settings.document_store_provider,
            "cache": settings.cache_provider,
            "graph": settings.graph_provider,
            "vector_store": settings.vector_store_provider,
        },
    )
