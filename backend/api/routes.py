"""REST API route definitions for Sun National Bank."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db.services.auth import AuthService
from ..db.services.banking import BankingService
from ..db.utils.enums import ReminderStatus, ReminderType, TransactionChannel
from .dependencies import AuthServiceDep, BankingServiceDep
from .schemas import (
    AccountBalanceData,
    AccountBalanceResponse,
    AccountItem,
    AccountListResponse,
    ErrorDetail,
    ErrorResponse,
    LoginData,
    LoginRequest,
    LoginResponse,
    ReminderCreateRequest,
    ReminderListResponse,
    ReminderResource,
    ReminderResponse,
    ReminderStatusUpdateRequest,
    ResponseMeta,
    TransactionHistoryResponse,
    TransferReceipt,
    TransferRequest,
    TransferResponse,
    UserProfile,
)
from .security import CurrentSessionDep, RequestContext, RequestContextDep

router = APIRouter(prefix="/api/v1", tags=["Sun National Bank"])


def build_meta(ctx: RequestContext) -> ResponseMeta:
    return ResponseMeta(
        requestId=ctx.request_id,
        timestamp=ctx.timestamp,
        locale=ctx.locale,
        channel=ctx.channel,
        customerIp=ctx.customer_ip,
        deviceId=ctx.device_id,
    )


def raise_http_error(
    ctx: RequestContext,
    message: str,
    *,
    code: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> None:
    meta = build_meta(ctx)
    detail = ErrorDetail(code=code, message=message)
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(meta=meta, error=detail).model_dump(),
    )


def serialize_reminder(reminder) -> ReminderResource:
    if isinstance(reminder, ReminderResource):
        return reminder
    if isinstance(reminder, dict):
        return ReminderResource(**reminder)
    return ReminderResource(
        id=str(reminder.id),
        reminderType=reminder.reminder_type.value,
        status=reminder.status.value,
        message=reminder.message,
        remindAt=reminder.remind_at,
        channel=reminder.channel,
        accountId=str(reminder.account_id) if reminder.account_id else None,
        recurrenceRule=reminder.recurrence_rule,
    )


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Authenticate user credentials",
    tags=["Authentication"],
)
def login_v1(
    payload: LoginRequest,
    ctx: RequestContext = RequestContextDep,
    auth_service: AuthService = AuthServiceDep,
):
    result = auth_service.authenticate(
        customer_number=payload.userId,
        password=payload.password,
    )

    if not result.success or result.user_profile is None or result.access_token is None:
        raise_http_error(
            ctx,
            message="Invalid user ID or password.",
            code="invalid_credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    profile = UserProfile(**result.user_profile)
    meta = build_meta(ctx)
    data = LoginData(
        accessToken=result.access_token,
        expiresIn=result.expires_in or 0,
        profile=profile,
    )
    return LoginResponse(meta=meta, data=data)


@router.get(
    "/accounts",
    response_model=AccountListResponse,
    tags=["Accounts"],
    summary="List customer accounts",
)
def list_accounts(
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    accounts = banking_service.list_accounts(user_id=session.user_id)
    meta = build_meta(ctx)
    items = [AccountItem(**account) for account in accounts]
    return AccountListResponse(meta=meta, data=items)


@router.get(
    "/accounts/{account_id}/balance",
    response_model=AccountBalanceResponse,
    tags=["Accounts"],
    summary="Retrieve account balance",
)
def get_account_balance(
    account_id: str,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    account = banking_service.get_account_for_user(
        user_id=session.user_id, account_id=account_id
    )
    if account is None:
        raise_http_error(
            ctx,
            message="Account not found.",
            code="account_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    balance = AccountBalanceData(
        accountNumber=account["accountNumber"],
        currency=account["currency"],
        ledgerBalance=account["balance"],
        availableBalance=account["availableBalance"],
        status=account["status"],
    )
    meta = build_meta(ctx)
    return AccountBalanceResponse(meta=meta, data=balance)


@router.get(
    "/accounts/{account_id}/transactions",
    response_model=TransactionHistoryResponse,
    tags=["Transactions"],
    summary="Retrieve transaction history",
)
def list_transactions(
    account_id: str,
    from_date: Optional[datetime] = Query(
        default=None, alias="from", description="ISO8601 start timestamp."
    ),
    to_date: Optional[datetime] = Query(
        default=None, alias="to", description="ISO8601 end timestamp."
    ),
    limit: int = Query(default=50, ge=1, le=500),
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    try:
        transactions = banking_service.fetch_transaction_history(
            user_id=session.user_id,
            account_id=account_id,
            start_date=from_date,
            end_date=to_date,
            limit=limit,
        )
    except ValueError as exc:
        if str(exc) == "account_not_found":
            raise_http_error(
                ctx,
                message="Account not found.",
                code="account_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        raise

    meta = build_meta(ctx)
    return TransactionHistoryResponse(meta=meta, data=transactions)


@router.post(
    "/transfers/internal",
    response_model=TransferResponse,
    tags=["Payments"],
    summary="Initiate an internal transfer",
    status_code=status.HTTP_201_CREATED,
)
def create_internal_transfer(
    payload: TransferRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    source_account = banking_service.get_account_for_user(
        user_id=session.user_id, account_id=payload.sourceAccountId
    )
    if source_account is None:
        raise_http_error(
            ctx,
            message="Source account not found.",
            code="account_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        transfer_result = banking_service.transfer_between_accounts(
            source_account_number=source_account["accountNumber"],
            destination_account_number=payload.destinationAccountNumber,
            amount=Decimal(payload.amount),
            currency_code=payload.currency,
            description=payload.remarks,
            channel=TransactionChannel.VOICE,
            session_id=session.access_token,
            reference_id=payload.referenceId,
        )
    except ValueError as exc:
        raise_http_error(
            ctx,
            message=str(exc),
            code="transfer_failed",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    receipt = TransferReceipt(
        debitTransactionId=str(transfer_result.debit_transaction.id),
        creditTransactionId=str(transfer_result.credit_transaction.id),
        amount=transfer_result.debit_transaction.amount,
        currency=transfer_result.debit_transaction.currency_code,
        description=transfer_result.debit_transaction.description,
    )
    meta = build_meta(ctx)
    return TransferResponse(meta=meta, data=receipt)


@router.get(
    "/reminders",
    response_model=ReminderListResponse,
    tags=["Reminders"],
    summary="List reminders configured for customer",
)
def list_reminders(
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    reminders = banking_service.list_reminders(user_id=session.user_id)
    resources = [ReminderResource(**reminder) for reminder in reminders]
    meta = build_meta(ctx)
    return ReminderListResponse(meta=meta, data=resources)


@router.post(
    "/reminders",
    response_model=ReminderResponse,
    tags=["Reminders"],
    summary="Create a reminder",
    status_code=status.HTTP_201_CREATED,
)
def create_reminder(
    payload: ReminderCreateRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    try:
        reminder = banking_service.schedule_reminder(
            user_id=session.user_id,
            remind_at=payload.remindAt,
            message=payload.message,
            reminder_type=ReminderType(payload.reminderType),
            account_id=payload.accountId,
            channel=payload.channel or "voice",
            recurrence_rule=payload.recurrenceRule,
        )
    except ValueError as exc:
        code = "account_not_found" if str(exc) == "account_not_found" else "invalid_data"
        status_code = status.HTTP_404_NOT_FOUND if code == "account_not_found" else status.HTTP_400_BAD_REQUEST
        raise_http_error(
            ctx,
            message=str(exc),
            code=code,
            status_code=status_code,
        )

    resource = serialize_reminder(reminder)
    meta = build_meta(ctx)
    return ReminderResponse(meta=meta, data=resource)


@router.patch(
    "/reminders/{reminder_id}",
    response_model=ReminderResponse,
    tags=["Reminders"],
    summary="Update reminder status",
)
def update_reminder(
    reminder_id: str,
    payload: ReminderStatusUpdateRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    try:
        reminder = banking_service.update_reminder_status(
            user_id=session.user_id,
            reminder_id=reminder_id,
            status=ReminderStatus(payload.status),
        )
    except ValueError as exc:
        raise_http_error(
            ctx,
            message="Reminder not found.",
            code=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    resource = serialize_reminder(reminder)
    meta = build_meta(ctx)
    return ReminderResponse(meta=meta, data=resource)


__all__ = ["router"]
