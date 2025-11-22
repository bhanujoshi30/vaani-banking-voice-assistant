"""REST API route definitions for Sun National Bank."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form
from fastapi.responses import FileResponse

from ..db.services.auth import AuthService
from ..db.services.banking import BankingService
from ..db.services.device_binding import DeviceBindingService
from ..db.services.voice_verification import VoiceVerificationService
from ..db.utils.enums import ReminderStatus, ReminderType, TransactionChannel
from .dependencies import (
    AuthServiceDep,
    BankingServiceDep,
    DeviceBindingServiceDep,
    VoiceVerificationServiceDep,
)
from .schemas import (
    AccountBalanceData,
    AccountBalanceResponse,
    AccountItem,
    AccountListResponse,
    BranchInfo,
    ErrorDetail,
    ErrorResponse,
    LoginData,
    LoginResponse,
    DeviceBindingListResponse,
    DeviceBindingResponse,
    DeviceBindingResource,
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
    StatementDownloadRequest,
    StatementDownloadResponse,
    StatementTransaction,
    StatementData,
    UserProfile,
    BeneficiaryCreateRequest,
    BeneficiaryListResponse,
    BeneficiaryResource,
    BeneficiaryResponse,
    UPIPinVerifyRequest,
    UPIPinVerifyResponse,
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
    info: Optional[dict] = None,
) -> None:
    meta = build_meta(ctx)
    detail = ErrorDetail(code=code, message=message, info=info)
    payload = ErrorResponse(meta=meta, error=detail).model_dump(mode="json")
    raise HTTPException(
        status_code=status_code,
        detail=payload,
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
async def login_v1(
    userId: str = Form(...),
    password: Optional[str] = Form(None),
    deviceIdentifier: Optional[str] = Form(None),
    deviceFingerprint: Optional[str] = Form(None),
    deviceLabel: Optional[str] = Form(None),
    platform: Optional[str] = Form(None),
    registrationMethod: Optional[str] = Form("otp+voice"),
    voiceSample: UploadFile | None = File(None),
    loginMode: str = Form("password"),
    otp: Optional[str] = Form(None),
    validateOnly: str = Form("false"),
    ctx: RequestContext = RequestContextDep,
    auth_service: AuthService = AuthServiceDep,
):
    voice_bytes = await voiceSample.read() if voiceSample else None
    validate_only_flag = str(validateOnly).lower() in {"true", "1", "yes", "on"}

    if not validate_only_flag:
        if not otp:
            raise_http_error(
                ctx,
                message="One-time password required.",
                code="otp_required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # Trim OTP to handle any whitespace issues
        otp_clean = otp.strip() if otp else otp
        if otp_clean != "12345":
            raise_http_error(
                ctx,
                message="Invalid one-time password.",
                code="otp_invalid",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    # Ensure password is trimmed and not empty for password login
    password_clean = password.strip() if password and loginMode == "password" else password
    
    result = auth_service.authenticate(
        customer_number=userId.strip() if userId else userId,
        password=password_clean,
        device_identifier=deviceIdentifier,
        fingerprint_hash=deviceFingerprint,
        platform=platform,
        device_label=deviceLabel,
        voice_sample=voice_bytes,
        registration_method=registrationMethod or "otp+voice",
        login_mode=loginMode,
        validate_only=validate_only_flag,
    )

    message_map = {
        "invalid_credentials": "Invalid user ID or password.",
        "device_binding_required": "Device binding required before continuing.",
        "device_verification_required": "Verify this device to continue.",
        "voice_verification_required": "Please complete voice verification to continue.",
        "voice_enrollment_required": "Please enroll your voice signature to continue.",
        "voice_mismatch": "Voice sample did not match our records.",
        "voice_sample_invalid": "Voice sample was too short or unclear. Please record again.",
        "validated": "Credentials validated successfully.",
    }

    if validate_only_flag:
        if not result.success:
            reason = result.reason or "invalid_credentials"
            # For password login, don't return voice-related errors
            if loginMode != "voice" and reason in ("voice_sample_invalid", "voice_mismatch", "voice_verification_required", "voice_enrollment_required"):
                reason = "invalid_credentials"
            message = message_map.get(reason, "Authentication failed.")
            raise_http_error(
                ctx,
                message=message,
                code=reason,
                status_code=status.HTTP_401_UNAUTHORIZED,
                info=result.detail,
            )
        return LoginResponse(
            meta=build_meta(ctx),
            data=LoginData(
                accessToken="",
                expiresIn=0,
                profile=UserProfile(
                    id=result.user_id or "",  # Use user_id from auth result
                    customerId=userId,
                    fullName="",
                    segment="",
                    branch=BranchInfo(name="", city=""),
                    accountSummary=[],
                ),
                detail=result.detail,
            ),
        )

    if not result.success or result.user_profile is None or result.access_token is None:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"[Login Route] Authentication failed: success={result.success}, "
            f"has_profile={result.user_profile is not None}, "
            f"has_token={result.access_token is not None}, "
            f"reason={result.reason}"
        )
        reason = result.reason or "invalid_credentials"
        # For password login, don't return voice-related errors
        if loginMode != "voice" and reason in ("voice_sample_invalid", "voice_mismatch", "voice_verification_required", "voice_enrollment_required"):
            reason = "invalid_credentials"
        message = message_map.get(reason, "Authentication failed.")
        raise_http_error(
            ctx,
            message=message,
            code=reason,
            status_code=status.HTTP_401_UNAUTHORIZED,
            info=result.detail,
        )

    # Validate and create profile - ensure all required fields are present
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        profile = UserProfile(**result.user_profile)
        logger.info(
            f"[Login Route] Profile created successfully: loginMode={loginMode}, "
            f"profile_id={profile.id}, customer_id={profile.customerId}, "
            f"has_accounts={len(profile.accountSummary) > 0}"
        )
    except Exception as e:
        logger.error(
            f"[Login Route] Failed to create UserProfile: error={type(e).__name__}: {str(e)}, "
            f"profile_data_keys={list(result.user_profile.keys()) if result.user_profile else 'None'}, "
            f"profile_data={result.user_profile}"
        )
        raise_http_error(
            ctx,
            message="Failed to create user profile.",
            code="profile_creation_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
    meta = build_meta(ctx)
    data = LoginData(
        accessToken=result.access_token,
        expiresIn=result.expires_in or 0,
        profile=profile,
        detail=result.detail,
    )
    
    logger.info(
        f"[Login Route] Login successful: loginMode={loginMode}, "
        f"has_profile={profile is not None}, has_token={bool(result.access_token)}, "
        f"profile_id={profile.id if profile else 'N/A'}, "
        f"access_token_length={len(result.access_token) if result.access_token else 0}"
    )
    
    # Ensure the response structure is correct
    response_data = LoginResponse(meta=meta, data=data)
    logger.debug(
        f"[Login Route] Response structure: has_data={response_data.data is not None}, "
        f"has_profile={response_data.data.profile is not None if response_data.data else False}"
    )
    
    return response_data


@router.get(
    "/auth/device-bindings",
    response_model=DeviceBindingListResponse,
    summary="List trusted devices for the authenticated user",
    tags=["Authentication"],
)
def list_device_bindings_v1(
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    device_binding_service: DeviceBindingService = DeviceBindingServiceDep,
):
    bindings = device_binding_service.list_bindings(user_id=session.user_id)
    meta = build_meta(ctx)
    resources = [DeviceBindingResource(**binding) for binding in bindings]
    return DeviceBindingListResponse(meta=meta, data=resources)


@router.post(
    "/auth/device-bindings",
    response_model=DeviceBindingResponse,
    summary="Register or refresh a trusted device binding",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def create_device_binding_v1(
    deviceIdentifier: str = Form(...),
    fingerprintHash: str = Form(...),
    registrationMethod: Optional[str] = Form("otp+voice"),
    platform: Optional[str] = Form(None),
    deviceLabel: Optional[str] = Form(None),
    voiceSample: UploadFile | None = File(None),
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    device_binding_service: DeviceBindingService = DeviceBindingServiceDep,
    voice_verifier: VoiceVerificationService = VoiceVerificationServiceDep,
    auth_service: AuthService = AuthServiceDep,
):
    voice_bytes = await voiceSample.read() if voiceSample else None
    if voice_bytes is None:
        raise_http_error(
            ctx,
            message="Voice sample required to register this device.",
            code="voice_sample_missing",
        )
    voice_hash = hashlib.sha256(voice_bytes).hexdigest() if voice_bytes else None
    voice_vector = None
    if voice_bytes:
        embedding = voice_verifier.compute_embedding(voice_bytes)
        if embedding is None:
            raise_http_error(
                ctx,
                message="Voice sample too short or unclear. Please record again.",
                code="voice_sample_invalid",
            )
        voice_vector = voice_verifier.serialize_embedding(embedding)
    
    # Check if user had any voice bindings BEFORE this registration
    existing_bindings = device_binding_service.list_bindings(user_id=session.user_id)
    had_voice_binding = any(b.get("voiceSignaturePresent", False) for b in existing_bindings)
    had_trusted_voice_binding = any(
        b.get("voiceSignaturePresent", False) and b.get("trustLevel") == "trusted" 
        for b in existing_bindings
    )
    
    binding = device_binding_service.register_or_refresh_binding(
        user_id=session.user_id,
        device_identifier=deviceIdentifier,
        fingerprint_hash=fingerprintHash,
        platform=platform,
        device_label=deviceLabel,
        registration_method=registrationMethod or "otp+voice",
        voice_signature_hash=voice_hash,
        voice_signature_vector=voice_vector,
    )
    
    # Determine if session replacement is required and what type of replacement
    session_replacement_required = False
    is_voice_replacement = False
    if binding.get("voiceSignaturePresent", False):
        if not had_voice_binding:
            # Password binding has been converted to voice binding (password-to-voice upgrade)
            # Mark for replacement but don't force logout - user can continue with current session
            session_replacement_required = True
        elif had_trusted_voice_binding:
            # User already has a trusted voice binding and is replacing/updating it
            # This is a voice-to-voice replacement - should warn user
            session_replacement_required = True
            is_voice_replacement = True
    
    meta = build_meta(ctx)
    # Create resource with session replacement flag
    # Note: isVoiceReplacement will be passed as extra data in the binding dict
    # Frontend can access it via binding.isVoiceReplacement if needed
    resource_data = {**binding}
    if is_voice_replacement:
        resource_data["isVoiceReplacement"] = True
    resource = DeviceBindingResource(**resource_data, sessionReplacementRequired=session_replacement_required)
    return DeviceBindingResponse(meta=meta, data=resource)


@router.delete(
    "/auth/device-bindings/{binding_id}",
    response_model=DeviceBindingResponse,
    summary="Revoke a trusted device binding",
    tags=["Authentication"],
)
def revoke_device_binding_v1(
    binding_id: str,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    device_binding_service: DeviceBindingService = DeviceBindingServiceDep,
):
    binding = device_binding_service.revoke_binding(binding_id=binding_id)
    if binding is None:
        raise_http_error(
            ctx,
            message="Device binding not found.",
            code="device_binding_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    meta = build_meta(ctx)
    # Extract logoutRequired flag if present
    logout_required = binding.pop("logoutRequired", False)
    resource = DeviceBindingResource(**binding, logoutRequired=logout_required)
    return DeviceBindingResponse(meta=meta, data=resource)


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
    # Check if sourceAccountId is a UUID or account number
    import uuid as uuid_lib
    import logging
    logger = logging.getLogger(__name__)
    
    # First, try to get all user accounts for debugging
    all_user_accounts = banking_service.list_accounts(user_id=session.user_id)
    logger.info(f"User {session.user_id} has {len(all_user_accounts)} accounts")
    logger.info(f"Requested account: {payload.sourceAccountId}")
    if all_user_accounts:
        logger.info(f"Available accounts: {[acc.get('accountNumber') for acc in all_user_accounts]}")
    
    try:
        # Try to parse as UUID first
        uuid_lib.UUID(payload.sourceAccountId)
        # It's a UUID, use get_account_for_user
        source_account = banking_service.get_account_for_user(
            user_id=session.user_id, account_id=payload.sourceAccountId
        )
    except ValueError:
        # It's not a UUID, treat it as account number
        # Try exact match first
        source_account = banking_service.get_account_by_number_for_user(
            user_id=session.user_id, account_number=payload.sourceAccountId
        )
        
        # If not found, try to find in user's accounts list
        if source_account is None and all_user_accounts:
            matching_account = next(
                (acc for acc in all_user_accounts 
                 if acc.get('accountNumber') == payload.sourceAccountId or 
                    acc.get('accountNumber', '').endswith(payload.sourceAccountId) or
                    payload.sourceAccountId in acc.get('accountNumber', '')),
                None
            )
            if matching_account:
                # Use the account ID if available, otherwise use account number
                account_id_to_use = matching_account.get('id') or matching_account.get('accountNumber')
                if account_id_to_use:
                    try:
                        uuid_lib.UUID(account_id_to_use)
                        source_account = banking_service.get_account_for_user(
                            user_id=session.user_id, account_id=account_id_to_use
                        )
                    except ValueError:
                        source_account = banking_service.get_account_by_number_for_user(
                            user_id=session.user_id, account_number=matching_account.get('accountNumber')
                        )
    
    if source_account is None:
        logger.error(f"Account not found: account_number={payload.sourceAccountId}, user_id={session.user_id}")
        logger.error(f"User's available accounts: {[acc.get('accountNumber') for acc in all_user_accounts]}")
        
        raise_http_error(
            ctx,
            message=f"Source account not found. Please select a valid account from your account list.",
            code="account_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        destination_account_number = payload.destinationAccountNumber.strip()
        if not destination_account_number:
            raise_http_error(
                ctx,
                message="Provide a valid destination account number.",
                code="invalid_destination_account",
            )
        if destination_account_number == source_account["accountNumber"]:
            raise_http_error(
                ctx,
                message="Destination account must be different from the source account.",
                code="invalid_destination_account",
            )

        reference_id = payload.referenceId or uuid.uuid4().hex[:12].upper()
        
        # Log reference_id for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Transfer reference_id: {reference_id}")

        result = banking_service.transfer_between_accounts(
            source_account_number=source_account["accountNumber"],
            destination_account_number=destination_account_number,
            amount=Decimal(payload.amount),
            currency_code=payload.currency,
            description=payload.remarks,
            channel=TransactionChannel.VOICE,
            user_id=session.user_id,
            session_id=session.session_id,
            reference_id=reference_id,
        )
        
        # Ensure reference_id is in result - always set it from the one we generated/passed
        # This ensures consistency even if the banking service doesn't return it
        result["reference_id"] = reference_id
        logger.info(f"Setting reference_id in result: {reference_id}")
        
        # Also log what the banking service returned
        service_ref = result.get("reference_id") or result.get("referenceId")
        logger.info(f"Reference ID from banking service: {service_ref}, using: {reference_id}")
    except ValueError as exc:
        message = str(exc)
        error_code = "transfer_failed"
        status_code_value = status.HTTP_400_BAD_REQUEST
        if "Insufficient funds" in message:
            error_code = "insufficient_funds"
            message = "Insufficient funds in source account."
        raise_http_error(
            ctx,
            message=message,
            code=error_code,
            status_code=status_code_value,
        )

    # Convert snake_case keys to camelCase for Pydantic model
    # Get reference_id from result - we set it above, so it should be there
    reference_id_value = result.get("reference_id") or result.get("referenceId")
    
    # Log for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating receipt - result keys: {list(result.keys())}")
    logger.info(f"Reference ID from result: {reference_id_value}")
    logger.info(f"Result reference_id value: {result.get('reference_id')}")
    logger.info(f"Result referenceId value: {result.get('referenceId')}")
    
    # If reference_id is still None or empty, this is a critical error
    if not reference_id_value:
        logger.error(f"CRITICAL: reference_id is None/empty when creating receipt! Result: {result}")
        # Don't create receipt with None reference_id - this should not happen
    
    receipt = TransferReceipt(
        debitTransactionId=result["debit"]["id"],
        creditTransactionId=result["credit"]["id"],
        amount=result["debit"]["amount"],
        currency=result["debit"]["currency"],
        description=result["debit"]["description"],
        referenceId=reference_id_value if reference_id_value else "UNKNOWN",  # Use the extracted value, fallback to UNKNOWN if missing
        timestamp=result.get("timestamp"),
        sourceAccountNumber=result.get("source_account_number") or result.get("sourceAccountNumber"),
        destinationAccountNumber=result.get("destination_account_number") or result.get("destinationAccountNumber"),
        beneficiaryName=result.get("beneficiary_name") or result.get("beneficiaryName"),
    )
    
    logger.info(f"Transfer receipt created: amount={receipt.amount}, source={receipt.sourceAccountNumber}, dest={receipt.destinationAccountNumber}, beneficiary={receipt.beneficiaryName}, ref={receipt.referenceId}")
    meta = build_meta(ctx)
    return TransferResponse(meta=meta, data=receipt)


@router.post(
    "/statements/download",
    response_model=StatementDownloadResponse,
    tags=["Statements"],
    summary="Prepare account statement for download",
)
def download_statement_v1(
    payload: StatementDownloadRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    from datetime import datetime

    try:
        from_date = datetime.strptime(payload.fromDate, "%Y-%m-%d")
        to_date = datetime.strptime(payload.toDate, "%Y-%m-%d")
    except ValueError:
        raise_http_error(
            ctx,
            message="Invalid date format. Use YYYY-MM-DD.",
            code="invalid_date_format",
        )

    if from_date > to_date:
        raise_http_error(
            ctx,
            message="Start date must be before end date.",
            code="invalid_date_range",
        )

    try:
        statement = banking_service.generate_account_statement(
            user_id=session.user_id,
            account_number=payload.accountNumber,
            from_date=from_date,
            to_date=to_date,
            period_type=payload.periodType or "custom",
        )
    except ValueError as exc:
        raise_http_error(
            ctx,
            message=str(exc),
            code="statement_error",
        )

    transactions = [
        StatementTransaction(
            date=txn["date"],
            type=txn["type"],
            amount=Decimal(str(txn["amount"])),
            currency=txn["currency"],
            description=txn.get("description"),
            status=txn.get("status"),
            counterparty=txn.get("counterparty"),
            reference_id=txn.get("reference_id"),
        )
        for txn in statement["transactions"]
    ]

    data = StatementData(
        accountNumber=statement["account_number"],
        accountType=statement["account_type"],
        fromDate=statement["from_date"],
        toDate=statement["to_date"],
        periodType=statement["period_type"],
        transactionCount=statement["transaction_count"],
        transactions=transactions,
        currentBalance=Decimal(str(statement["current_balance"])),
        currency=statement["currency"],
    )
    meta = build_meta(ctx)
    return StatementDownloadResponse(meta=meta, data=data)


@router.get(
    "/beneficiaries",
    response_model=BeneficiaryListResponse,
    tags=["Beneficiaries"],
    summary="List registered beneficiaries",
)
def list_beneficiaries_v1(
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    beneficiaries = banking_service.list_beneficiaries(user_id=session.user_id)
    resources = [BeneficiaryResource(**item) for item in beneficiaries]
    meta = build_meta(ctx)
    return BeneficiaryListResponse(meta=meta, data=resources)


@router.post(
    "/beneficiaries",
    response_model=BeneficiaryResponse,
    tags=["Beneficiaries"],
    summary="Register a new beneficiary",
    status_code=status.HTTP_201_CREATED,
)
def create_beneficiary_v1(
    payload: BeneficiaryCreateRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    try:
        beneficiary = banking_service.add_beneficiary(
            user_id=session.user_id,
            display_name=payload.name,
            account_number=payload.accountNumber,
            bank_name=payload.bankName,
            ifsc=payload.ifsc,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "account_not_found":
            raise_http_error(
                ctx,
                message="The destination account could not be found.",
                code="account_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if message == "beneficiary_exists":
            raise_http_error(
                ctx,
                message="This account is already present in your beneficiary list.",
                code="beneficiary_exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        raise_http_error(
            ctx,
            message="Unable to add beneficiary at the moment.",
            code="beneficiary_creation_failed",
        )

    meta = build_meta(ctx)
    resource = BeneficiaryResource(**beneficiary)
    return BeneficiaryResponse(meta=meta, data=resource)


@router.delete(
    "/beneficiaries/{beneficiary_id}",
    response_model=BeneficiaryResponse,
    tags=["Beneficiaries"],
    summary="Remove a beneficiary",
)
def delete_beneficiary_v1(
    beneficiary_id: str,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    beneficiary = banking_service.remove_beneficiary(
        user_id=session.user_id, beneficiary_id=beneficiary_id
    )
    if beneficiary is None:
        raise_http_error(
            ctx,
            message="Beneficiary not found.",
            code="beneficiary_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    meta = build_meta(ctx)
    resource = BeneficiaryResource(**beneficiary)
    return BeneficiaryResponse(meta=meta, data=resource)


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


@router.post(
    "/upi/verify-pin",
    response_model=UPIPinVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify UPI PIN",
    description="Mock UPI PIN verification endpoint. Validates 6-digit PIN format.",
)
def verify_upi_pin(
    payload: UPIPinVerifyRequest,
    ctx: RequestContext = RequestContextDep,
    session=CurrentSessionDep,
    banking_service: BankingService = BankingServiceDep,
):
    """
    Verify UPI PIN against stored hash.
    """
    from ..db.utils.security import verify_password
    from ..db.models import User
    
    # Validate PIN format
    if not payload.pin or len(payload.pin) != 6 or not payload.pin.isdigit():
        raise_http_error(
            ctx,
            message="Invalid UPI PIN format. PIN must be 6 digits.",
            code="invalid_pin_format",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Get user from session
    user_id = session.user_id
    
    # Get user from database using banking service
    from sqlalchemy import select
    from ..db.models import User
    from ..db.engine import get_session_factory
    from ..db.config import load_database_config
    from ..db.engine import create_db_engine
    
    config = load_database_config()
    engine = create_db_engine(config)
    session_factory = get_session_factory(engine)
    
    with session_factory() as db:
        stmt = select(User).where(User.id == user_id)
        user = db.execute(stmt).scalars().first()
        
        if not user:
            raise_http_error(
                ctx,
                message="User not found.",
                code="user_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        # Check if user has UPI PIN set
        if not user.upi_pin_hash:
            raise_http_error(
                ctx,
                message="UPI PIN not set. Please set your UPI PIN first.",
                code="upi_pin_not_set",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Verify PIN
        if not verify_password(payload.pin, user.upi_pin_hash):
            raise_http_error(
                ctx,
                message="Invalid UPI PIN. Please try again.",
                code="invalid_upi_pin",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    
    # PIN verified - now process the UPI operation (payment or balance check)
    payment_details = payload.paymentDetails or {}
    operation = payment_details.get("operation")
    source_account_number = payment_details.get("sourceAccount")
    
    # Handle balance check operation
    if operation == "balance_check":
        if not source_account_number:
            raise_http_error(
                ctx,
                message="Missing account details for balance check.",
                code="missing_account_details",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Get account balance
        try:
            from ..db.repositories import accounts as account_repo
            from sqlalchemy import select
            from ..db.models import Account
            
            with session_factory() as db:
                account = account_repo.get_account_by_number(db, source_account_number)
                if not account:
                    raise_http_error(
                        ctx,
                        message="Account not found.",
                        code="account_not_found",
                        status_code=status.HTTP_404_NOT_FOUND,
                    )
                
                balance_data = {
                    "success": True,
                    "balance": {
                        "account_number": account.account_number,
                        "account_type": account.account_type.value if hasattr(account.account_type, 'value') else str(account.account_type),
                        "balance": float(account.balance),
                        "currency": "INR"
                    }
                }
                
                from .schemas import ResponseMeta
                # Use build_meta helper function for consistent meta creation
                meta = build_meta(ctx)
                
                return UPIPinVerifyResponse(meta=meta, data=balance_data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching balance: {str(e)}")
            raise_http_error(
                ctx,
                message=f"Error fetching balance: {str(e)}",
                code="balance_check_error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    # Handle payment operation (existing logic)
    recipient_identifier = payment_details.get("recipient")
    amount = payment_details.get("amount")
    remarks = payment_details.get("remarks")
    
    if not all([source_account_number, recipient_identifier, amount]):
        raise_http_error(
            ctx,
            message="Missing payment details. Please provide amount, recipient, and source account.",
            code="missing_payment_details",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Process UPI payment using banking service
    try:
        # Resolve recipient UPI ID to account number
        import logging
        logger = logging.getLogger(__name__)
        from ..db.repositories import beneficiaries as beneficiary_repo
        from ..db.repositories import accounts as account_repo
        from ..db.models import User, Account
        from sqlalchemy import select
        
        destination_account_number = None
        beneficiary_name = None
        
        # Try to resolve recipient
        with session_factory() as db:
            # Check if recipient is a UPI ID (contains @)
            if "@" in recipient_identifier:
                # If it's a UPI ID format, ONLY match by UPI ID - don't fall back to phone/beneficiary
                # Trim whitespace and use case-insensitive comparison
                trimmed_upi_id = recipient_identifier.strip()
                # Use func.lower() for case-insensitive comparison
                # SQLite string comparison is case-insensitive by default, but be explicit
                from sqlalchemy import func, or_
                
                # First, try to find by User.upi_id
                stmt = select(User).where(
                    func.lower(User.upi_id) == func.lower(trimmed_upi_id)
                ).where(User.upi_id.isnot(None))  # Exclude NULL values
                recipient_user = db.execute(stmt).scalars().first()
                
                # If not found in User table, try Account table
                if not recipient_user:
                    account_stmt = select(Account).where(
                        func.lower(Account.upi_id) == func.lower(trimmed_upi_id)
                    ).where(Account.upi_id.isnot(None))  # Exclude NULL values
                    recipient_account = db.execute(account_stmt).scalars().first()
                    
                    if recipient_account:
                        # Found account with UPI ID - get the user
                        recipient_user = recipient_account.user
                        destination_account_number = recipient_account.account_number
                        beneficiary_name = f"{recipient_user.first_name} {recipient_user.last_name}"
                
                # If found via User table, get the account
                if recipient_user and not destination_account_number:
                    accounts = account_repo.list_accounts_for_user(db, recipient_user.id)
                    primary_account = next(iter(accounts), None)
                    if primary_account:
                        destination_account_number = primary_account.account_number
                        beneficiary_name = f"{recipient_user.first_name} {recipient_user.last_name}"
                
                # If still not found, raise error
                if not recipient_user or not destination_account_number:
                    # UPI ID not found - raise error immediately (don't try phone/beneficiary lookup)
                    raise_http_error(
                        ctx,
                        message=f"UPI ID not found: {recipient_identifier}. Please verify the UPI ID and try again.",
                        code="upi_id_not_found",
                        status_code=status.HTTP_404_NOT_FOUND,
                    )
            else:
                # Not a UPI ID format - try phone number
                if not destination_account_number:
                    clean_phone = ''.join(filter(str.isdigit, recipient_identifier))
                    if len(clean_phone) >= 10:
                        clean_phone = clean_phone[-10:]
                        stmt = select(User).where(User.phone_number.like(f"%{clean_phone}%"))
                        recipient_user = db.execute(stmt).scalars().first()
                        if recipient_user:
                            accounts = account_repo.list_accounts_for_user(db, recipient_user.id)
                            primary_account = next(iter(accounts), None)
                            if primary_account:
                                destination_account_number = primary_account.account_number
                                beneficiary_name = f"{recipient_user.first_name} {recipient_user.last_name}"
                
                # If still not found, try beneficiary lookup
                if not destination_account_number:
                    beneficiaries = beneficiary_repo.list_beneficiaries(db, user_id=user_id, include_blocked=False)
                    beneficiaries_list = list(beneficiaries)
                    if beneficiaries_list:
                        # Try to match by name
                        for beneficiary in beneficiaries_list:
                            if recipient_identifier.lower() in beneficiary.name.lower() or beneficiary.name.lower() in recipient_identifier.lower():
                                destination_account_number = beneficiary.account_number
                                beneficiary_name = beneficiary.name
                                break
        
        if not destination_account_number:
            raise_http_error(
                ctx,
                message=f"Recipient not found: {recipient_identifier}",
                code="recipient_not_found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        # Generate UPI reference ID
        from datetime import datetime
        upi_ref_id = f"UPI-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        
        # Process the transfer with UPI channel
        from ..db.utils.enums import TransactionChannel
        result = banking_service.transfer_between_accounts(
            source_account_number=source_account_number,
            destination_account_number=destination_account_number,
            amount=float(amount),
            currency_code="INR",
            description=remarks or f"UPI Payment to {beneficiary_name or recipient_identifier}",
            channel=TransactionChannel.UPI,
            user_id=user_id,
            session_id=session.session_id,
            reference_id=upi_ref_id
        )
        
        # Create receipt data
        from .schemas import TransferReceipt
        receipt = TransferReceipt(
            debitTransactionId=result.get("debit", {}).get("id", ""),
            creditTransactionId=result.get("credit", {}).get("id", ""),
            amount=float(amount),
            currency="INR",
            description=remarks or f"UPI Payment to {beneficiary_name or recipient_identifier}",
            referenceId=upi_ref_id,
            timestamp=result.get("timestamp"),
            sourceAccountNumber=source_account_number,
            destinationAccountNumber=destination_account_number,
            beneficiaryName=beneficiary_name or recipient_identifier,
        )
        
        meta = build_meta(ctx)
        return UPIPinVerifyResponse(
            meta=meta,
            data={
                "success": True,
                "message": "UPI payment processed successfully",
                "receipt": receipt.model_dump(mode="json"),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPI payment processing error: {str(e)}")
        raise_http_error(
            ctx,
            message=f"Failed to process UPI payment: {str(e)}",
            code="payment_processing_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get(
    "/documents/{document_type}/{document_name}",
    tags=["Documents"],
    summary="Download loan or investment PDF document",
    response_class=FileResponse,
)
def download_document(
    document_type: str,
    document_name: str,
    language: str = Query(default="en-IN", description="Language code (en-IN or hi-IN)"),
    ctx: RequestContext = RequestContextDep,
):
    """
    Download PDF documents for loan products or investment schemes.
    
    - document_type: "loan" or "investment"
    - document_name: Product/scheme identifier (e.g., "home_loan", "ppf")
    - language: "en-IN" for English, "hi-IN" for Hindi
    """
    import os
    from pathlib import Path
    
    # Map document names to PDF filenames
    loan_name_mapping = {
        "home_loan": "home_loan_product_guide.pdf",
        "personal_loan": "personal_loan_product_guide.pdf",
        "auto_loan": "auto_loan_product_guide.pdf",
        "education_loan": "education_loan_product_guide.pdf",
        "business_loan": "business_loan_product_guide.pdf",
        "gold_loan": "gold_loan_product_guide.pdf",
        "loan_against_property": "loan_against_property_guide.pdf",
        # Handle display names (English)
        "home loan": "home_loan_product_guide.pdf",
        "personal loan": "personal_loan_product_guide.pdf",
        "auto loan": "auto_loan_product_guide.pdf",
        "education loan": "education_loan_product_guide.pdf",
        "business loan": "business_loan_product_guide.pdf",
        "gold loan": "gold_loan_product_guide.pdf",
        "loan against property": "loan_against_property_guide.pdf",
        # Hindi names
        "होम लोन": "home_loan_product_guide.pdf",
        "होमलोन": "home_loan_product_guide.pdf",
        "पर्सनल लोन": "personal_loan_product_guide.pdf",
        "पर्सनललोन": "personal_loan_product_guide.pdf",
        "ऑटो लोन": "auto_loan_product_guide.pdf",
        "अटो लोन": "auto_loan_product_guide.pdf",  # Variant spelling
        "ऑटोलोन": "auto_loan_product_guide.pdf",
        "अटोलोन": "auto_loan_product_guide.pdf",  # Variant spelling
        "एजुकेशन लोन": "education_loan_product_guide.pdf",
        "एजुकेशनलोन": "education_loan_product_guide.pdf",
        "बिजनेस लोन": "business_loan_product_guide.pdf",
        "बिजनेसलोन": "business_loan_product_guide.pdf",
        "गोल्ड लोन": "gold_loan_product_guide.pdf",
        "गोल्डलोन": "gold_loan_product_guide.pdf",
        "प्रॉपर्टी के खिलाफ लोन": "loan_against_property_guide.pdf",
        "प्रॉपर्टी लोन": "loan_against_property_guide.pdf",
        # Hindi sub-loan types -> parent documents
        "मुद्रा लोन": "business_loan_product_guide.pdf",
        "मुद्रा": "business_loan_product_guide.pdf",
        "टर्म लोन": "business_loan_product_guide.pdf",
        "वर्किंग कैपिटल": "business_loan_product_guide.pdf",
        "वर्किंग कैपिटल लोन": "business_loan_product_guide.pdf",
        "इनवॉइस फाइनेंसिंग": "business_loan_product_guide.pdf",
        "इक्विपमेंट फाइनेंसिंग": "business_loan_product_guide.pdf",
        "बिजनेस ओवरड्राफ्ट": "business_loan_product_guide.pdf",
    }
    
    investment_name_mapping = {
        "ppf": "ppf_scheme_guide.pdf",
        "nps": "nps_scheme_guide.pdf",
        "ssy": "ssy_scheme_guide.pdf",
        "sukanya samriddhi yojana": "ssy_scheme_guide.pdf",
        "sukanya": "ssy_scheme_guide.pdf",
        "sukanya samriddhi": "ssy_scheme_guide.pdf",
        "public provident fund": "ppf_scheme_guide.pdf",
        "national pension system": "nps_scheme_guide.pdf",
        "national pension": "nps_scheme_guide.pdf",
        # Handle display names (English)
        "PPF": "ppf_scheme_guide.pdf",
        "NPS": "nps_scheme_guide.pdf",
        "SSY": "ssy_scheme_guide.pdf",
        "elss": "elss_scheme_guide.pdf",
        "ELSS": "elss_scheme_guide.pdf",
        "fd": "fd_scheme_guide.pdf",
        "FD": "fd_scheme_guide.pdf",
        "fixed deposit": "fd_scheme_guide.pdf",
        "rd": "rd_scheme_guide.pdf",
        "RD": "rd_scheme_guide.pdf",
        "recurring deposit": "rd_scheme_guide.pdf",
        "nsc": "nsc_scheme_guide.pdf",
        "NSC": "nsc_scheme_guide.pdf",
        "national savings certificate": "nsc_scheme_guide.pdf",
        # Hindi names
        "पीपीएफ": "ppf_scheme_guide.pdf",
        "एनपीएस": "nps_scheme_guide.pdf",
        "सुकन्या समृद्धि योजना": "ssy_scheme_guide.pdf",
        "सुकन्या": "ssy_scheme_guide.pdf",
        "सुकन्या समृद्धि": "ssy_scheme_guide.pdf",
        "ईएलएसएस": "elss_scheme_guide.pdf",
        "फिक्स्ड डिपॉजिट": "fd_scheme_guide.pdf",
        "रिकरिंग डिपॉजिट": "rd_scheme_guide.pdf",
        "नेशनल सेविंग्स सर्टिफिकेट": "nsc_scheme_guide.pdf",
    }
    
    # Normalize document name (lowercase for English, strip whitespace)
    # For Hindi text, .lower() won't change anything, which is fine
    normalized_name = document_name.lower().strip()
    
    # Determine PDF filename based on document type
    if document_type.lower() == "loan":
        # First try direct lookup
        pdf_filename = loan_name_mapping.get(normalized_name)
        if not pdf_filename:
            # Try to find a match by checking if any key is contained in the name
            # Normalize keys for comparison (replace underscores with spaces)
            for key, value in loan_name_mapping.items():
                normalized_key = key.replace("_", " ")
                # Check if key contains the normalized name or vice versa
                if normalized_key in normalized_name or normalized_name in normalized_key:
                    pdf_filename = value
                    break
            # If still not found, try case-insensitive substring matching for Hindi
            if not pdf_filename:
                for key, value in loan_name_mapping.items():
                    if normalized_name in key or key in normalized_name:
                        pdf_filename = value
                        break
    elif document_type.lower() == "investment":
        # First try direct lookup
        pdf_filename = investment_name_mapping.get(normalized_name)
        if not pdf_filename:
            # Try to find a match
            for key, value in investment_name_mapping.items():
                # Check substring matching
                if key in normalized_name or normalized_name in key:
                    pdf_filename = value
                    break
    else:
        raise_http_error(
            ctx,
            message=f"Invalid document type: {document_type}. Must be 'loan' or 'investment'.",
            code="invalid_document_type",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    if not pdf_filename:
        raise_http_error(
            ctx,
            message=f"Document not found: {document_name}",
            code="document_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Determine directory based on language
    if language == "hi-IN":
        if document_type.lower() == "loan":
            doc_dir = "loan_products_hindi"
        else:
            doc_dir = "investment_schemes_hindi"
    else:
        if document_type.lower() == "loan":
            doc_dir = "loan_products"
        else:
            doc_dir = "investment_schemes"
    
    # Get the base directory (backend/documents)
    base_dir = Path(__file__).parent.parent / "documents"
    pdf_path = base_dir / doc_dir / pdf_filename
    
    if not pdf_path.exists():
        raise_http_error(
            ctx,
            message=f"PDF file not found: {pdf_filename}",
            code="pdf_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return FileResponse(
        path=str(pdf_path),
        filename=pdf_filename,
        media_type="application/pdf",
    )


__all__ = ["router"]
