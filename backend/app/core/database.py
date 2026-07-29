"""Sessao e engine do SQLAlchemy. Unico ponto que conhece o banco fisico."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa de todos os models (camada Model do MVC)."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia do FastAPI - injeta a sessao nos routers (DIP do SOLID)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
