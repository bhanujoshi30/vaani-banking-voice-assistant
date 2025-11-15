"""Voice assistant session metadata."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from ..base import Base
from ..utils.enums import AuthenticationLevel, SessionStatus, TransactionChannel
from ..utils.types import GUID


class Session(Base):
    """Represents a conversational banking session."""

    __tablename__ = "sessions"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_sessions_external_id"),
        Index("ix_sessions_access_token", "access_token"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(64), nullable=True)
    access_token = Column(String(96), nullable=True, unique=True)
    channel = Column(
        Enum(TransactionChannel, name="session_channel", native_enum=False),
        nullable=False,
        default=TransactionChannel.VOICE,
    )
    status = Column(
        Enum(SessionStatus, name="session_status", native_enum=False),
        nullable=False,
        default=SessionStatus.ACTIVE,
    )
    auth_level = Column(
        Enum(AuthenticationLevel, name="auth_level", native_enum=False),
        nullable=False,
        default=AuthenticationLevel.PASSIVE,
    )
    device_fingerprint = Column(String(120), nullable=True)
    mfa_method = Column(String(40), nullable=True)
    started_at = Column(DateTime(timezone=True), default=func.now, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_intent = Column(String(80), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
    transactions = relationship("Transaction", back_populates="session")


__all__ = ["Session"]


