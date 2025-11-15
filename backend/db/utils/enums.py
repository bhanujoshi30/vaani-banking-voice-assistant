"""Domain enumerations for banking operations."""

from enum import Enum


class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    FIXED_DEPOSIT = "fixed_deposit"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    DORMANT = "dormant"
    CLOSED = "closed"
    SUSPENDED = "suspended"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    PAYMENT = "payment"
    REFUND = "refund"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"
    REVERSED = "reversed"


class TransactionChannel(str, Enum):
    VOICE = "voice"
    UPI = "upi"
    CARD = "card"
    BRANCH = "branch"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class AuthenticationLevel(str, Enum):
    PASSIVE = "passive"
    STEP_UP = "step_up"
    FULL = "full"


class CardType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"


class CardStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    REISSUED = "reissued"


class ReminderType(str, Enum):
    BILL_PAYMENT = "bill_payment"
    DUE_DATE = "due_date"
    SAVINGS = "savings"
    CUSTOM = "custom"


class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


__all__ = [
    "AccountType",
    "AccountStatus",
    "TransactionType",
    "TransactionStatus",
    "TransactionChannel",
    "SessionStatus",
    "AuthenticationLevel",
    "CardType",
    "CardStatus",
    "ReminderType",
    "ReminderStatus",
]


