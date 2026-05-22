# File: app/database.py
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base metadata chung cho toàn bộ SQLAlchemy ORM models."""

    pass


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Cung cấp SQLAlchemy Session cho dependency injection của FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
