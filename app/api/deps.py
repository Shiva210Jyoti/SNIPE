from redis import Redis

from app.cache.redis_client import get_redis
from app.config import Settings, get_settings
from app.db.session import get_db


def get_redis_client() -> Redis | None:
    return get_redis()


__all__ = ["get_db", "get_redis_client", "get_settings", "Settings"]
