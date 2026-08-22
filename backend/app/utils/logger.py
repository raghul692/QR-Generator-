"""
QRMaster Pro — Centralized Logging (Loguru).

Configures Loguru with console + rotating file sinks and provides a
ready-to-use `logger` instance across the application.
"""
from __future__ import annotations

import sys

from loguru import logger

from app.config import settings


# Remove default handler and configure custom sinks
logger.remove()

# Console sink (colored, level depends on DEBUG)
logger.add(
    sys.stdout,
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    backtrace=settings.DEBUG,
    diagnose=settings.DEBUG,
)

# Rotating file sink
logger.add(
    str(settings.logs_path / "qrmaster_{time}.log"),
    level="INFO",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    ),
    backtrace=True,
    diagnose=settings.DEBUG,
)

# Error-only file sink
logger.add(
    str(settings.logs_path / "qrmaster_errors_{time}.log"),
    level="ERROR",
    rotation="5 MB",
    retention="60 days",
    compression="zip",
    encoding="utf-8",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    ),
    backtrace=True,
    diagnose=True,
)


__all__ = ["logger"]