"""
QRMaster Pro — SQLAlchemy Declarative Base.

All ORM models inherit from `Base` defined here.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass