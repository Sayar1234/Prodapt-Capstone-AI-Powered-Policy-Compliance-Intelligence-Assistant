import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError


class LocalCache:
    def __init__(self) -> None:
        self._items: dict[str, object] = {}

    async def get(self, key: str) -> object | None:
        return self._items.get(key)

    async def set(self, key: str, value: object, ttl: int | None = None) -> None:
        self._items[key] = value

    async def ping(self) -> bool:
        return True


class UpstashRedisCache:
    def __init__(self, rest_url: str, rest_token: str) -> None:
        self.rest_url = rest_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {rest_token}"}

    async def _command(self, *parts: Any) -> Any:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self.rest_url, headers=self.headers, json=list(parts))
            response.raise_for_status()
            payload = response.json()
            if "error" in payload and payload["error"]:
                raise RuntimeError(payload["error"])
            return payload.get("result")

    async def get(self, key: str) -> object | None:
        value = await self._command("GET", key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    async def set(self, key: str, value: object, ttl: int | None = None) -> None:
        serialized = json.dumps(value)
        if ttl:
            await self._command("SET", key, serialized, "EX", ttl)
        else:
            await self._command("SET", key, serialized)

    async def ping(self) -> bool:
        return await self._command("PING") == "PONG"


def build_cache() -> LocalCache | UpstashRedisCache:
    settings = get_settings()
    if settings.cache_provider == "local":
        return LocalCache()
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        raise ValidationAppError(
            "Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN when CACHE_PROVIDER=upstash"
        )
    return UpstashRedisCache(settings.upstash_redis_rest_url, settings.upstash_redis_rest_token)


cache = build_cache()
