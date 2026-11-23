"""
QRMaster Pro — Database Session & Engine.

Provides the SQLAlchemy engine, session factory, and a FastAPI dependency
for obtaining a database session. Configured for Supabase PostgreSQL with
connection pre-ping, configurable pool sizes, and safe error handling.
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.utils.logger import logger


def _create_engine_instance() -> Engine:
    """Create and configure the SQLAlchemy engine."""
    url = settings.resolved_database_url
    connect_args = {}

    if "sqlite" in url:
        connect_args["check_same_thread"] = False
        return create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            future=True,
        )

    return create_engine(
        url,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        future=True,
    )


# Application engine
engine: Engine = _create_engine_instance()

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Verify database connectivity without exposing connection secrets.
    Returns True if database can execute a ping query, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        return False
