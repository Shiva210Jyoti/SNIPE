from redis import Redis

from app.config import Settings, get_settings

_redis_client: Redis | None = None


def cache_key(short_code: str) -> str:
    """Namespace cache keys to avoid collisions with other apps on shared Redis."""
    return f"snipurl:url:{short_code}"


def init_redis(settings: Settings | None = None) -> Redis | None:
    """
    Create a shared Redis client at app startup.

  Returns None if Redis is disabled or unreachable (app still works via PostgreSQL).
    """
    global _redis_client

    settings = settings or get_settings()
    if not settings.redis_enabled:
        return None

    client = Redis.from_url(settings.redis_url, decode_responses=True)
    client.ping()
    _redis_client = client
    return _redis_client


def get_redis() -> Redis | None:
    """Return the shared Redis client (or None if caching is unavailable)."""
    return _redis_client


def close_redis() -> None:
    """Close Redis connection on app shutdown."""
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
