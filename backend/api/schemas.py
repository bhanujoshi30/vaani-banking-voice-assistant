"""Pydantic models for API contracts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, condecimal, constr


# --- Generic metadata envelopes -------------------------------------------------


class ResponseMeta(BaseModel):
    requestId: str
    timestamp: datetime
    locale: Optional[str] = "en-IN"
    channel: Optional[str] = "voice-web"
    customerIp: Optional[str] = None
    deviceId: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    info: Optional[dict] = None


class ErrorResponse(BaseModel):
    meta: ResponseMeta
    error: ErrorDetail


# --- Auth -----------------------------------------------------------------------


class LoginRequest(BaseModel):
    userId: constr(min_length=4, max_length=32) = Field(
        description="Customer identifier issued by Sun National Bank."
    )
    password: constr(min_length=4, max_length=128) = Field(
        description="Secret shared during onboarding or updated by customer."
    )


class AccountSummary(BaseModel):
    accountNumber: str
    type: str
    balance: str
    currency: str


class BranchInfo(BaseModel):
    name: str
    city: str


class ReminderInfo(BaseModel):
    label: str
    date: datetime


class UserProfile(BaseModel):
    id: str  # User UUID for AI backend
    customerId: str
    fullName: str
    segment: str
    branch: BranchInfo
    accountSummary: List[AccountSummary]
    preferredLanguage: Optional[str] = None
    lastLogin: Optional[datetime] = None
    nextReminder: Optional[ReminderInfo] = None


class LoginData(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    profile: UserProfile


class LoginResponse(BaseModel):
    meta: ResponseMeta
    data: LoginData


# --- Accounts -------------------------------------------------------------------


class CardInfo(BaseModel):
    id: str
    cardType: str
    status: str
    maskedNumber: str
    network: str
    expiryMonth: str
    expiryYear: str


class AccountItem(BaseModel):
    id: str
    accountNumber: str
    type: str
    status: str
    currency: str
    balance: float
    availableBalance: float
    openedOn: str
    branchId: Optional[str] = None
    debitCards: List[CardInfo] = []
    creditCards: List[CardInfo] = []


class AccountListResponse(BaseModel):
    meta: ResponseMeta
    data: List[AccountItem]


class AccountBalanceData(BaseModel):
    accountNumber: str
    currency: str
    ledgerBalance: float
    availableBalance: float
    status: str


class AccountBalanceResponse(BaseModel):
    meta: ResponseMeta
    data: AccountBalanceData


# --- Transactions ---------------------------------------------------------------


class TransactionItem(BaseModel):
    id: str
    type: str
    status: str
    amount: float
    currency: str
    description: Optional[str] = None
    referenceId: Optional[str] = None
    counterpartyAccount: Optional[str] = None
    counterpartyName: Optional[str] = None
    occurredAt: datetime


class TransactionHistoryResponse(BaseModel):
    meta: ResponseMeta
    data: List[TransactionItem]


class TransferRequest(BaseModel):
    sourceAccountId: str = Field(..., description="UUID of the debited account.")
    destinationAccountNumber: constr(min_length=10, max_length=32)
    amount: condecimal(gt=0)
    currency: constr(min_length=3, max_length=3) = "INR"
    remarks: Optional[str] = Field(
        default=None, description="Narration presented to both parties."
    )
    referenceId: Optional[str] = Field(
        default=None,
        description="Idempotency key supplied by client for duplicate detection.",
    )


class TransferReceipt(BaseModel):
    debitTransactionId: str
    creditTransactionId: str
    amount: Decimal
    currency: str
    description: Optional[str] = None


class TransferResponse(BaseModel):
    meta: ResponseMeta
    data: TransferReceipt


# --- Reminders ------------------------------------------------------------------


class ReminderCreateRequest(BaseModel):
    reminderType: str = Field(default="bill_payment")
    remindAt: datetime
    message: constr(min_length=4, max_length=200)
    accountId: Optional[str] = None
    channel: Optional[str] = "voice"
    recurrenceRule: Optional[str] = Field(
        default=None,
        description="RFC 5545 RRULE expression for recurring reminders.",
    )


class ReminderStatusUpdateRequest(BaseModel):
    status: str


class ReminderResource(BaseModel):
    id: str
    reminderType: str
    status: str
    message: str
    remindAt: datetime
    channel: str
    accountId: Optional[str] = None
    recurrenceRule: Optional[str] = None


class ReminderResponse(BaseModel):
    meta: ResponseMeta
    data: ReminderResource


class ReminderListResponse(BaseModel):
    meta: ResponseMeta
    data: List[ReminderResource]


__all__ = [
    "ResponseMeta",
    "ErrorDetail",
    "ErrorResponse",
    "LoginRequest",
    "LoginData",
    "LoginResponse",
    "UserProfile",
    "CardInfo",
    "AccountItem",
    "AccountListResponse",
    "AccountBalanceData",
    "AccountBalanceResponse",
    "TransactionItem",
    "TransactionHistoryResponse",
    "TransferRequest",
    "TransferResponse",
    "ReminderCreateRequest",
    "ReminderStatusUpdateRequest",
    "ReminderResponse",
    "ReminderListResponse",
]
