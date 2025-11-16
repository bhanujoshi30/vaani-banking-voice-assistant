"""Customer master data."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base
from ..utils.types import GUID


class User(Base):
    """Represents a retail banking customer."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("customer_number", name="uq_users_customer_number"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("phone_number", name="uq_users_phone"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    customer_number = Column(String(16), nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    preferred_language = Column(String(20), nullable=False, default="en-IN")
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    email = Column(String(120), nullable=False)
    phone_number = Column(String(20), nullable=False)
    aadhaar_last4 = Column(String(4), nullable=True)
    pan_number = Column(String(10), nullable=True)
    kyc_status = Column(String(20), nullable=False, default="verified")
    risk_segment = Column(String(20), nullable=False, default="retail")
    password_hash = Column(String(256), nullable=False)
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
    )
    primary_branch_id = Column(
        GUID(), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True
    )

    primary_branch = relationship("Branch", backref="customers")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    device_bindings = relationship(
        "DeviceBinding", back_populates="user", cascade="all, delete-orphan"
    )
    beneficiaries = relationship(
        "Beneficiary", back_populates="user", cascade="all, delete-orphan"
    )


__all__ = ["User"]


