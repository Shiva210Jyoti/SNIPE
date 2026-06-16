from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_redis_client, get_settings
from app.config import Settings
from app.core.exceptions import ShortCodeCollisionError
from app.schemas.url import UrlCreateRequest, UrlCreateResponse
from app.services.url_service import create_short_url

router = APIRouter()


@router.post(
    "",
    response_model=UrlCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a short URL",
)
def create_url(
    payload: UrlCreateRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    redis: Redis | None = Depends(get_redis_client),
) -> UrlCreateResponse:
    """
    Write path — called when a client wants to shorten a URL.

    Request flow (explain this in interviews):
    1. FastAPI validates JSON body via Pydantic (UrlCreateRequest)
    2. Dependency injection provides DB session (get_db)
    3. Service layer handles business logic + DB insert
    4. Response serialized via Pydantic (UrlCreateResponse)
    """
    try:
        url_record = create_short_url(db, str(payload.url), settings, redis)
    except ShortCodeCollisionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return UrlCreateResponse(
        short_code=url_record.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{url_record.short_code}",
        original_url=url_record.original_url,
        created_at=url_record.created_at,
    )
