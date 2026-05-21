import hashlib
import logging
import math

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def deterministic_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    if settings.embedding_provider != "openrouter":
        return deterministic_embedding(text)
    if not settings.openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY is missing; falling back to local embeddings")
        return deterministic_embedding(text)

    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    if settings.openrouter_site_url:
        headers["HTTP-Referer"] = settings.openrouter_site_url
    if settings.openrouter_app_name:
        headers["X-Title"] = settings.openrouter_app_name

    payload = {"model": settings.openrouter_embedding_model, "input": text}
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{settings.openrouter_base_url.rstrip('/')}/embeddings", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["data"][0]["embedding"]
    except Exception as exc:
        logger.warning("OpenRouter embedding call failed; falling back to local embeddings: %s", exc)
        return deterministic_embedding(text)
