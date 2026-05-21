from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings().ensure_directories()
    yield
