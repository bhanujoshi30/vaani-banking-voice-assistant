# Backend Architecture (FastAPI)

This document describes the backend architecture for the Sun National Bank voice-first experience. The backend is a FastAPI app with clear boundaries between the API layer, domain services, repositories, and persistence.

- Entry point: `backend/app.py`
- API Layer: `backend/api/*`
- Domain Services: `backend/db/services/*`
- Repositories: `backend/db/repositories/*`
- Models & Base: `backend/db/models/*`, `backend/db/base.py`
- Engine & Config: `backend/db/engine.py`, `backend/db/config.py`
- Utilities: `backend/db/utils/*`

See the diagram in `documents/backend_architecture.mmd`.

## Modules and Responsibilities

### Application (`backend/app.py`)
- Factory `create_app()` configures logging, CORS, and includes the API router.
- Middleware: CORS for local dev (5173) and wildcard `*` for permissive cross-origin during development.
- Startup hook logs readiness.

### API Layer (`backend/api/*`)
- `routes.py`: Defines REST endpoints under `/api/v1`.
  - Authentication: `/auth/login`, device binding CRUD.
  - Accounts: list accounts, get balance, transactions.
  - Payments: internal transfers.
  - Beneficiaries: list/create/delete.
  - Reminders: list/create/update.
  - UPI: `/upi/verify-pin` (PIN format validation, balance check or payment workflow).
- `dependencies.py`: Wires domain services and DB session factory via FastAPI `Depends` using `lru_cache` for singleton-style providers.
- `security.py`:
  - `RequestContext`: standard metadata (request id, timestamp IST, locale, channel, device, IPs).
  - `get_current_session`: Bearer auth that verifies access tokens via `AuthService.validate_token`.
- `schemas.py`: Pydantic models used for request/response validation and OpenAPI.

### Domain Services (`backend/db/services/*`)
- `AuthService`:
  - Validates credentials and device state (binding, trust level).
  - Handles voice enrollment/verification (via `VoiceVerificationService` and AI-enhanced path `ai_voice_verification.py` when available).
  - On success, issues an access token and creates a `Session` record; on validate-only, returns structured status without issuing tokens.
  - Enforces single trusted device at a time by revoking others on successful voice login (and clears old voice vectors).
- `BankingService`:
  - Orchestrates account queries, transfers, statement generation, beneficiaries, reminders.
  - Uses repositories for data access.
- `DeviceBindingService`:
  - Manage device bindings (register/refresh, list, revoke).
- `VoiceVerificationService` and `ai_voice_verification.py`:
  - Compute/serialize embeddings; compare vectors; optionally augment with AI scoring.

All services work within a `session_scope(session_factory)` transactional boundary and compose repositories.

### Repositories (`backend/db/repositories/*`)
- Thin data-access modules for specific aggregates:
  - `auth.py` (sessions, users)
  - `accounts.py`
  - `transactions.py`
  - `reminders.py`
  - `beneficiaries.py`
  - `device_bindings.py`
- Operate on SQLAlchemy models and return entities or dicts for service consumption.

### Persistence
- `db/config.py`:
  - `DatabaseConfig` holds backend, URL, echo, pooling options.
  - `load_database_config()` loads from env; defaults to SQLite at `backend/db/vaani.db` if no `DATABASE_URL` for sqlite backend.
- `db/engine.py`:
  - `create_db_engine()` builds engine with backend-specific connect args (`check_same_thread=False` for sqlite).
  - `get_session_factory()` returns a configured `sessionmaker`.
  - `session_scope()` context manager for transactional operations (commit/rollback).
- `db/base.py`: SQLAlchemy Base for model metadata.
- `db/models/*`: ORM models (User, Account, Transaction, Reminder, DeviceBinding, Session, etc.).
- `db/seed.py`: Seed helper for local dev datasets.
- Physical database file for dev: `backend/db/vaani.db`.

### Utilities (`backend/db/utils/*`)
- `enums.py`: Enumerations (ReminderStatus, ReminderType, TransactionChannel, etc.).
- `security.py`: Password hashing/verification, UPI PIN helpers.
- `types.py`: Common typing/aliases if needed.

## Request Flows

### 1) Login with Voice (validate-only)
1. `POST /api/v1/auth/login` with `validateOnly=true`, `loginMode=voice`, and `voiceSample`.
2. `routes.py` builds `RequestContext`, injects `AuthService`.
3. `AuthService.authenticate()` loads user, computes voice embedding, compares with stored signature (or enrolls), and returns `AuthResult` without issuing a token.
4. Response: `LoginResponse` with `detail` explaining next actions (e.g., binding required, similarityScore, enrollment flags).

### 2) Login (issue token)
1. `POST /api/v1/auth/login` with proper OTP and either password or voice + device binding.
2. On success, `AuthService` issues token (stored in `Session`), returns `LoginResponse` with `accessToken` and `UserProfile`.
3. Subsequent calls include `Authorization: Bearer <token>`; `security.get_current_session` validates with `AuthService.validate_token`.

### 3) Get Account Balance
1. `GET /api/v1/accounts/{account_id}/balance` with Bearer token.
2. Router injects `BankingService` and the `AuthenticatedSession`.
3. `BankingService.get_account_for_user()` ensures ownership and returns account data.
4. Response: `AccountBalanceResponse`.

### 4) Internal Transfer
1. `POST /api/v1/transfers/internal` with `TransferRequest`.
2. Router normalizes the source account id/number; uses `BankingService.transfer_between_accounts()`.
3. Service coordinates account retrieval, balance checks, and transaction creation via `accounts.py` and `transactions.py`.
4. Response: `TransferResponse` with `TransferReceipt` (referenceId, debit/credit IDs, amounts).

### 5) UPI PIN Verify (Balance or Payment)
1. `POST /api/v1/upi/verify-pin` with PIN and optional `paymentDetails`.
2. Validates PIN format and verifies against stored hash; uses SQLAlchemy session to read `User`/`Account`.
3. If `operation=balance_check`, returns current balance for the given account.
4. Else resolves recipient (UPI ID / phone / beneficiary), generates a UPI reference id, and calls `transfer_between_accounts()` with `TransactionChannel.UPI`.

### 6) Reminders & Beneficiaries
- Standard CRUD orchestrated by `BankingService` and repos; responses serialized via Pydantic schemas.

## Cross-Cutting Concerns
- Logging: Configured globally in `app.py` and service modules (notably voice verification INFO logs).
- Caching: `lru_cache` used for providers (config, session factory, service instances).
- Timezone: IST (`Asia/Kolkata`) for request timestamps and session expiry checks.
- Security: Bearer token validation + structured error payloads; password/PIN verification via utils.

## Notes
- For production hardening, tighten CORS, consider structured logging, and replace SQLite with Postgres by setting `DB_BACKEND=postgresql` and `DATABASE_URL`.
- AI voice verification is optional: service falls back to basic vector similarity if AI augmentation is unavailable.
