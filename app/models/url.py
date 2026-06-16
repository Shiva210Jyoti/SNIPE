from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Url(Base):
    """
    Persistent storage for short URL mappings.

    Interview schema questions:
    - short_code is UNIQUE + indexed → O(log n) lookup on redirect (hot path)
    - id is internal BIGINT PK → never exposed in public URLs
    - original_url is TEXT → URLs can be long
    """

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_urls_short_code", "short_code"),)
