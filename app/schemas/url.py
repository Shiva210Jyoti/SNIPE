from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class UrlCreateRequest(BaseModel):
    """API input contract — what clients send when creating a short URL."""

    url: HttpUrl = Field(..., description="The original long URL to shorten")


class UrlCreateResponse(BaseModel):
    """API output contract — what clients receive after creation."""

    short_code: str
    short_url: str
    original_url: str
    created_at: datetime

    model_config = {"from_attributes": True}
