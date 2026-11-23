"""
Pytest configuration and transactional fixtures for QRMaster Pro test suite.
"""
import os
import sys
import pytest
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.database.seed import seed_categories, seed_settings
from app.main import create_app

# Use isolated SQLite for unit & integration testing
TEST_DB_FILE = backend_root / "test_suite.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all 12 tables and seed default categories/settings once per test session."""
    # Build schema
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        seed_categories(db)
        seed_settings(db)
    finally:
        db.close()

    yield

    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass


@pytest.fixture
def db_session():
    """Yield a transactional database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
