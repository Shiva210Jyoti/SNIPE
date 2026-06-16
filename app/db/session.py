from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Engine = connection pool to PostgreSQL.
# pool_pre_ping=True verifies connections before use (handles stale connections).
engine = create_engine(settings.database_url, pool_pre_ping=True)

# SessionLocal = factory for database sessions (one per request).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a DB session and always closes it.

    Interview flow:
    Request arrives → get_db opens session → endpoint runs query → session closes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
