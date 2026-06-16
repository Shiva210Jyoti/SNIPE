from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from redis import Redis
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_redis_client, get_settings
from app.config import Settings
from app.messaging.kafka_producer import publish_click_event
from app.services.url_service import resolve_original_url

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to original URL",
    response_class=RedirectResponse,
)
def redirect_to_original_url(
    short_code: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    redis: Redis | None = Depends(get_redis_client),
) -> RedirectResponse:
    """
    Read path (hot path) — browser hits short URL, we redirect.

    Why 302 (Temporary Redirect)?
    - Original URL might change later
    - Browsers/CDNs cache 301 aggressively — hard to update destination
    - Production often uses 302 until URL is confirmed permanent

    Interview: this endpoint gets 100x+ more traffic than create.
    That's why Phase 3 adds Redis cache here.
    """
    original_url = resolve_original_url(db, short_code, settings, redis)
    if original_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # Async analytics — publish to Kafka without blocking the redirect response
    publish_click_event(short_code, original_url, settings)

    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)
