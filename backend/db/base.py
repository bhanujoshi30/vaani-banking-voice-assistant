"""
Declarative base definition for all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime


class Base(DeclarativeBase):
    """Declarative base that adds automatic table naming and audit columns."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base"]


