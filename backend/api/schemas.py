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
    password: constr(min_length=0, max_length=128) = Field(
        description="Secret shared during onboarding or updated by customer. Optional when using voice mode."
    )
    deviceIdentifier: Optional[constr(min_length=4, max_length=128)] = Field(
        default=None,
        description="Stable identifier for the customer device (hashed fingerprint).",
    )
    deviceFingerprint: Optional[constr(min_length=8, max_length=256)] = Field(
        default=None,
        description="Additional device fingerprint or browser signature hash.",
    )
    deviceLabel: Optional[constr(max_length=120)] = Field(
        default=None, description="Friendly label shown to the customer."
    )
    platform: Optional[constr(max_length=40)] = Field(
        default=None, description="Platform or operating system (e.g., ios, android, web)."
    )
    registrationMethod: Optional[constr(max_length=40)] = Field(
        default="otp+voice",
        description="Method used to confirm device binding (otp, otp+voice, etc.).",
    )
    loginMode: constr(min_length=4, max_length=16) = Field(
        default="password",
        description="Mode chosen by customer (password or voice).",
    )
    otp: constr(min_length=4, max_length=10) = Field(
        description="One-time password provided during step-up verification."
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
    detail: Optional[dict] = None


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
    referenceId: Optional[str] = None
    timestamp: Optional[str] = None
    sourceAccountNumber: Optional[str] = None
    destinationAccountNumber: Optional[str] = None
    beneficiaryName: Optional[str] = None


class TransferResponse(BaseModel):
    meta: ResponseMeta
    data: TransferReceipt


# --- Statements ----------------------------------------------------------------


class StatementTransaction(BaseModel):
    date: str
    type: str
    amount: Decimal
    currency: str
    description: Optional[str] = None
    status: Optional[str] = None
    counterparty: Optional[str] = None
    reference_id: Optional[str] = None


class StatementData(BaseModel):
    accountNumber: str
    accountType: str
    fromDate: str
    toDate: str
    periodType: str
    transactionCount: int
    transactions: List[StatementTransaction]
    currentBalance: Decimal
    currency: str


class StatementDownloadRequest(BaseModel):
    accountNumber: str = Field(min_length=6, max_length=20)
    fromDate: str = Field(description="Start date in YYYY-MM-DD format")
    toDate: str = Field(description="End date in YYYY-MM-DD format")
    periodType: Optional[str] = Field(default="custom")


class StatementDownloadResponse(BaseModel):
    meta: ResponseMeta
    data: StatementData


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


class BeneficiaryResource(BaseModel):
    id: str
    name: str
    accountNumber: str
    bankName: str
    ifsc: str
    status: str
    addedAt: datetime
    verifiedAt: Optional[datetime] = None
    lastUsedAt: Optional[datetime] = None
    removedAt: Optional[datetime] = None


class BeneficiaryCreateRequest(BaseModel):
    name: constr(min_length=2, max_length=120)
    accountNumber: constr(min_length=10, max_length=32)
    bankName: Optional[constr(max_length=120)] = None
    ifsc: Optional[constr(min_length=4, max_length=16)] = None


class BeneficiaryListResponse(BaseModel):
    meta: ResponseMeta
    data: List[BeneficiaryResource]


class BeneficiaryResponse(BaseModel):
    meta: ResponseMeta
    data: BeneficiaryResource


# --- Device Binding -------------------------------------------------------------


class DeviceBindingResource(BaseModel):
    id: str
    deviceIdentifier: str
    registrationMethod: str
    platform: Optional[str] = None
    deviceLabel: Optional[str] = None
    trustLevel: str
    voiceSignaturePresent: bool
    lastVerifiedAt: Optional[datetime] = None
    revokedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class DeviceBindingCreateRequest(BaseModel):
    deviceIdentifier: constr(min_length=4, max_length=128)
    fingerprintHash: constr(min_length=8, max_length=256)
    registrationMethod: Optional[constr(max_length=40)] = "otp+voice"
    platform: Optional[constr(max_length=40)] = None
    deviceLabel: Optional[constr(max_length=120)] = None
    voiceSignatureHash: Optional[constr(min_length=8, max_length=256)] = None


class DeviceBindingResponse(BaseModel):
    meta: ResponseMeta
    data: DeviceBindingResource


class DeviceBindingListResponse(BaseModel):
    meta: ResponseMeta
    data: List[DeviceBindingResource]


# --- UPI PIN Verification -------------------------------------------------


class UPIPinVerifyRequest(BaseModel):
    pin: constr(min_length=6, max_length=6) = Field(
        description="6-digit UPI PIN"
    )
    paymentDetails: Optional[dict] = Field(
        default=None,
        description="Payment details for verification context"
    )


class UPIPinVerifyResponse(BaseModel):
    meta: ResponseMeta
    data: dict  # Contains success status and transaction details if successful


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
    "DeviceBindingCreateRequest",
    "DeviceBindingResponse",
    "DeviceBindingListResponse",
    "DeviceBindingResource",
    "BeneficiaryCreateRequest",
    "BeneficiaryListResponse",
    "BeneficiaryResource",
    "BeneficiaryResponse",
    "UPIPinVerifyRequest",
    "UPIPinVerifyResponse",
]
