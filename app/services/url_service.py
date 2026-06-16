import secrets
import string

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from redis import Redis

from app.cache.redis_client import cache_key
from app.config import Settings
from app.core.exceptions import ShortCodeCollisionError
from app.models.url import Url

# Base62-ish alphabet: lowercase + uppercase + digits.
# 62^7 ≈ 3.5 trillion combinations — plenty for Phase 1.
BASE62_ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int) -> str:
    """Cryptographically secure random short code."""
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))


def _cache_url(redis: Redis | None, settings: Settings, short_code: str, original_url: str) -> None:
    if redis is not None:
        redis.setex(cache_key(short_code), settings.cache_ttl_seconds, original_url)


def create_short_url(
    db: Session,
    original_url: str,
    settings: Settings,
    redis: Redis | None = None,
) -> Url:
    """
    Write path: persist a new short URL mapping.

    Collision strategy (common interview topic):
    1. Generate random code
    2. INSERT with UNIQUE constraint on short_code
    3. On IntegrityError (collision), retry up to N times

    Alternative at scale: encode auto-increment ID in base62 (no collisions).
    """
    max_attempts = 5

    for _ in range(max_attempts):
        short_code = generate_short_code(settings.short_code_length)
        url_record = Url(short_code=short_code, original_url=original_url)

        try:
            db.add(url_record)
            db.commit()
            db.refresh(url_record)
            _cache_url(redis, settings, url_record.short_code, url_record.original_url)
            return url_record
        except IntegrityError:
            db.rollback()

    raise ShortCodeCollisionError("Failed to generate a unique short code")


def resolve_original_url(
    db: Session,
    short_code: str,
    settings: Settings,
    redis: Redis | None = None,
) -> str | None:
    """
    Read path (hot path): cache-aside pattern.

    1. Check Redis
    2. On miss, query PostgreSQL
    3. On hit in DB, write back to Redis (populate cache)
    """
    if redis is not None:
        cached_url = redis.get(cache_key(short_code))
        if cached_url is not None:
            return cached_url

    url_record = db.execute(
        select(Url).where(Url.short_code == short_code)
    ).scalar_one_or_none()
    if url_record is None:
        return None

    _cache_url(redis, settings, short_code, url_record.original_url)
    return url_record.original_url
