"""
QRMaster Pro — Database Session & Engine.

Provides the SQLAlchemy engine, session factory, and a FastAPI dependency
for obtaining a database session. Also exposes a helper to create the
target database if it does not yet exist (useful for first-run setup).
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


def _create_database_if_not_exists() -> None:
    """Create the MySQL database if it does not exist (first-run helper)."""
    engine: Engine = create_engine(
        settings.database_url_no_db,
        pool_pre_ping=True,
        future=True,
    )
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        # Log but do not crash — the DB may already exist or MySQL may be down.
        print(f"[DB INIT] Could not auto-create database: {exc}")
    finally:
        engine.dispose()


# Ensure the database exists before building the main engine
_create_database_if_not_exists()


# Main engine bound to the application database
engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    future=True,
)

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