"""Reminder scheduling for proactive engagements."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, Index
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from ..base import Base
from ..utils.enums import ReminderStatus, ReminderType
from ..utils.types import GUID


class Reminder(Base):
    """Represents a reminder or alert configured by or for a customer."""

    __tablename__ = "reminders"
    __table_args__ = (
        Index("ix_reminders_user_remind_at", "user_id", "remind_at"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(
        GUID(), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    reminder_type = Column(
        Enum(ReminderType, name="reminder_type", native_enum=False), nullable=False
    )
    status = Column(
        Enum(ReminderStatus, name="reminder_status", native_enum=False),
        nullable=False,
        default=ReminderStatus.PENDING,
    )
    message = Column(Text, nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False, default=func.now)
    recurrence_rule = Column(String(80), nullable=True)
    channel = Column(String(20), nullable=False, default="voice")

    user = relationship("User", back_populates="reminders")
    account = relationship("Account", back_populates="reminders")


__all__ = ["Reminder"]


