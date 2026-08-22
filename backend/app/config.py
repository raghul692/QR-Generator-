"""
QRMaster Pro — Application Configuration.

Centralized settings loaded from environment variables / .env file using
pydantic-settings. All configuration is strongly typed and validated.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Union

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
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ---- Database ----
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "qrmaster_pro"

    # ---- CORS ----
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173"

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
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    @property
    def database_url(self) -> str:
        """SQLAlchemy MySQL connection URL (PyMySQL driver)."""
        password = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"mysql+pymysql://{self.DB_USER}{password}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def database_url_no_db(self) -> str:
        """Connection URL without the database name (used to create the DB)."""
        password = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"mysql+pymysql://{self.DB_USER}{password}@"
            f"{self.DB_HOST}:{self.DB_PORT}/?charset=utf8mb4"
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