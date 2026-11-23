"""
QRMaster Pro — Application Configuration.

Centralized settings loaded from environment variables / .env file using
pydantic-settings. All configuration is strongly typed and validated.
Supports Supabase PostgreSQL, Render, and Vercel production deployments.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the backend root directory (where this file's parent lives)
BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "QRMaster Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ---- Server ----
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ---- Database (Supabase PostgreSQL) ----
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "postgres"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 1800

    # ---- Supabase Cloud Services ----
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "qr-assets"
    SUPABASE_JWT_SECRET: Optional[str] = None

    # ---- CORS & URLs ----
    FRONTEND_ORIGIN: Optional[str] = None
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://127.0.0.1:5173"
    PUBLIC_REDIRECT_BASE_URL: str = "http://127.0.0.1:8000"

    # ---- Storage directories (relative to backend/) ----
    GENERATED_QR_DIR: str = "app/generated_qr"
    UPLOADS_DIR: str = "app/uploads"
    EXPORTS_DIR: str = "app/exports"
    LOGS_DIR: str = "app/logs"
    BACKUP_DIR: str = "app/backups"

    # ---- Default QR settings ----
    DEFAULT_QR_SIZE: int = 400
    DEFAULT_ERROR_CORRECTION: str = "H"
    DEFAULT_FOREGROUND_COLOR: str = "#000000"
    DEFAULT_BACKGROUND_COLOR: str = "#FFFFFF"

    # ------------------------------------------------------------------ #
    # Validators / Derived properties
    # ------------------------------------------------------------------ #
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins
        return v  # type: ignore[return-value]

    @property
    def public_redirect_url(self) -> str:
        """
        Public base URL for dynamic QR redirect links.
        Defaults to RENDER_EXTERNAL_URL if deployed on Render and default localhost was kept.
        """
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url and self.PUBLIC_REDIRECT_BASE_URL in ("http://127.0.0.1:8000", "http://localhost:8000"):
            return render_url.rstrip("/")
        return self.PUBLIC_REDIRECT_BASE_URL.rstrip("/")

    @property
    def cors_origins_list(self) -> List[str]:
        """Return combined CORS origins including FRONTEND_ORIGIN if set."""
        origins: List[str] = []
        if isinstance(self.CORS_ORIGINS, list):
            origins.extend(self.CORS_ORIGINS)
        elif isinstance(self.CORS_ORIGINS, str):
            origins.extend([o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()])
        if self.FRONTEND_ORIGIN and self.FRONTEND_ORIGIN not in origins:
            origins.append(self.FRONTEND_ORIGIN.rstrip("/"))
        return origins

    @property
    def resolved_database_url(self) -> str:
        """
        SQLAlchemy PostgreSQL connection URL.
        Normalizes postgres:// -> postgresql+psycopg2:// and ensures
        safe pooler / direct connection format.
        """
        raw_url = self.DATABASE_URL
        if raw_url and raw_url.strip():
            url = raw_url.strip()
            # Normalize driver
            if url.startswith("postgres://"):
                url = "postgresql+psycopg2://" + url[len("postgres://"):]
            elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
                url = "postgresql+psycopg2://" + url[len("postgresql://"):]
            return url

        # Construct from components if no DATABASE_URL given
        password = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+psycopg2://{self.DB_USER}{password}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def _resolve(self, rel: str) -> Path:
        """Resolve a relative storage path to an absolute Path and create it."""
        p = Path(rel)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def generated_qr_path(self) -> Path:
        return self._resolve(self.GENERATED_QR_DIR)

    @property
    def uploads_path(self) -> Path:
        return self._resolve(self.UPLOADS_DIR)

    @property
    def exports_path(self) -> Path:
        return self._resolve(self.EXPORTS_DIR)

    @property
    def logs_path(self) -> Path:
        return self._resolve(self.LOGS_DIR)

    @property
    def backup_path(self) -> Path:
        return self._resolve(self.BACKUP_DIR)


# Singleton settings instance
settings = Settings()

# Ensure all storage directories exist on import
for _dir_attr in (
    "generated_qr_path",
    "uploads_path",
    "exports_path",
    "logs_path",
    "backup_path",
):
    getattr(settings, _dir_attr)
