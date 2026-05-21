from time import perf_counter
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response

from app.observability.logging import set_request_id

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
    REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "path"])
except ModuleNotFoundError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    REQUEST_COUNT = None
    REQUEST_LATENCY = None

    def generate_latest() -> bytes:
        return b"# prometheus_client is not installed\n"


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    set_request_id(request_id)
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    path = request.url.path
    if REQUEST_COUNT and REQUEST_LATENCY:
        REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(perf_counter() - start)
    return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
