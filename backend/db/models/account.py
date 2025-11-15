"""Deposit account model."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from ..base import Base
from ..utils.enums import AccountStatus, AccountType
from ..utils.types import GUID


class Account(Base):
    """Represents a customer's bank account."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("account_number", name="uq_accounts_number"),
        Index("ix_accounts_user_id_status", "user_id", "status"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(GUID(), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    account_number = Column(String(20), nullable=False)
    account_type = Column(Enum(AccountType, name="account_type", native_enum=False), nullable=False)
    status = Column(Enum(AccountStatus, name="account_status", native_enum=False), nullable=False, default=AccountStatus.ACTIVE)
    currency_code = Column(String(3), nullable=False, default="INR")
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    available_balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    interest_rate = Column(Numeric(precision=5, scale=2), nullable=True)
    opened_on = Column(Date, nullable=False, default=date.today)
    last_activity_on = Column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
    )
    nominee_name = Column(String(120), nullable=True)

    user = relationship("User", back_populates="accounts")
    branch = relationship("Branch", backref="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )
    cards = relationship("Card", back_populates="account")
    reminders = relationship("Reminder", back_populates="account")


__all__ = ["Account"]


