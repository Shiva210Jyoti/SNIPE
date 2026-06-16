from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.cache.redis_client import close_redis, get_redis, init_redis
from app.config import get_settings
from app.messaging.kafka_producer import close_kafka_producer, get_kafka_producer, init_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Connect shared clients on startup; close them on shutdown."""
    settings = get_settings()
    try:
        init_redis(settings)
    except Exception:
        # App still works without Redis — falls back to PostgreSQL only.
        pass
    try:
        init_kafka_producer(settings)
    except Exception:
        # App still works without Kafka — redirects are not blocked.
        pass
    yield
    close_kafka_producer()
    close_redis()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Production-grade URL shortener for backend learning",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # API routes under /api/v1 — versioned, REST-style
    app.include_router(api_router, prefix="/api/v1")

    # Register fixed paths BEFORE /{short_code} catch-all redirect
    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        redis_status = "ok" if get_redis() is not None else "unavailable"
        kafka_status = "ok" if get_kafka_producer() is not None else "unavailable"
        return {"status": "ok", "redis": redis_status, "kafka": kafka_status}

    # Redirect route mounted at root for clean short URLs: snip.url/abc123
    from app.api.v1.endpoints import redirect

    app.include_router(redirect.router, tags=["redirect"])

    return app


app = create_app()
