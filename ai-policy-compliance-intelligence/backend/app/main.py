from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import compliance, health, ingestion
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.observability.logging import configure_logging
from app.observability.monitoring import metrics_middleware, metrics_response
from app.observability.telemetry import lifespan

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(metrics_middleware)
register_exception_handlers(app)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(ingestion.router, prefix=settings.api_prefix)
app.include_router(compliance.router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/metrics")
async def metrics():
    return metrics_response()
