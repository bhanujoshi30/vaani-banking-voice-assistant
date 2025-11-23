# Vaani Backend Module Architecture

This document maps the `backend/` service for Sun National Bank. Use it together with `documentation/backend-architecture.mmd` for a visual reference.

---

## 1. Purpose and scope

The backend module is a FastAPI application that powers every non-AI capability of the platform:

- **Authentication** (password + OTP + voice verification).
- **Device binding** (registering trusted devices plus voice signatures).
- **Account operations** (balances, transactions, reminders, beneficiaries, statements, transfers).
- **Regulatory context** (request metadata, structured responses, localized timestamps).

It exposes REST endpoints under `/api/v1/*` and persists data in `backend/db/vaani.db` (SQLite via SQLAlchemy).

---

## 2. Request lifecycle

1. A **web or voice client** calls the FastAPI app (`backend/app.py`).
2. Requests route through `backend/api/routes.py` using a single `APIRouter` mounted at `/api/v1`.
3. `backend/api/security.py` constructs a `RequestContext` (request ID, locale, IP, device ID) and enforces bearer tokens via `CurrentSessionDep`.
4. The route handlers declare dependencies on services (e.g., `AuthServiceDep`, `BankingServiceDep`). The dependency module (`backend/api/dependencies.py`) lazily builds singletons for the SQLAlchemy engine and each service.
5. Services in `backend/db/services/` execute business logic. They open SQLAlchemy sessions via `session_scope`, talk to repositories, and optionally invoke helpers such as `VoiceVerificationService`.
6. Repositories in `backend/db/repositories/` run actual ORM queries against models defined in `backend/db/models/`.
7. The handler serializes the response into Pydantic schemas from `backend/api/schemas.py`, attaches context metadata (`ResponseMeta`), and returns JSON back to the client.

The Mermaid diagram shows this flow end-to-end: client → FastAPI → API layer → services → repositories → models → SQLite database.

---

## 3. API layer (backend/api)

### 3.1 `routes.py`
Key endpoint groups:
- `POST /auth/login`: OTP-gated login supporting password or voice modes, with optional `validateOnly` pre-checks.
- `GET/POST/DELETE /auth/device-bindings`: manage trusted devices, voice enrollment, and session replacement flags.
- `GET /accounts`, `GET /accounts/{id}`, `GET /accounts/{id}/transactions`: account summaries and history.
- `POST /transfers`: internal transfers with confirmation receipts.
- `GET/POST /reminders`: create, list, and update payment reminders.
- `GET/POST /beneficiaries`: manage external payees.
- `POST /statements`: generate downloadable statements using the templates in `backend/documents/`.
- `POST /upi/pin/verify`: verify UPI PIN payloads for voice-driven flows.

The module also houses utility helpers such as `build_meta()`, `raise_http_error()`, and serializer functions for reminders and beneficiaries.

### 3.2 `schemas.py`
Defines all response/request models (e.g., `LoginResponse`, `AccountListResponse`, `ReminderResource`). These ensure clients always receive consistent payloads, complete with `meta` blocks.

### 3.3 `security.py`
- `RequestContext`: captures RBI-required metadata (request ID, locale, channel, device ID, IP) per request.
- `get_current_session`: validates bearer tokens by delegating to `AuthService.validate_token` and raises structured HTTP errors on failure.

### 3.4 `dependencies.py`
- Loads `DatabaseConfig` (connection string, echo flags) and builds the SQLAlchemy engine (via `create_db_engine`).
- Initializes services (`AuthService`, `BankingService`, `DeviceBindingService`, `VoiceVerificationService`) and exposes them as FastAPI dependencies.
- Ensures metadata tables exist by calling `Base.metadata.create_all(engine)` the first time the module loads.

---

## 4. Domain services (backend/db/services)

| Service | Responsibilities | Key collaborators |
| --- | --- | --- |
| `AuthService` | Validates credentials, issues tokens, records sessions, orchestrates OTP flows, coordinates device binding requirements, enforces login/voice policies. | `device_binding.py`, `voice_verification.py`, repositories for users/sessions, `utils.security` |
| `BankingService` | Lists accounts/beneficiaries, fetches balances & statements, executes transfers, schedules reminders, tracks transactions, interacts with statement templates. | `repositories.accounts`, `repositories.transactions`, `repositories.reminders`, document templates |
| `DeviceBindingService` | Registers, refreshes, lists, and revokes trusted devices. Tracks voice signature hashes/vectors and trust levels. | `voice_verification.py`, `repositories.device_bindings` |
| `VoiceVerificationService` | Encapsulates speaker embeddings via Resemblyzer. Computes/serializes embeddings, similarity scores, and threshold checks for voice login & device enrollment. | Used by `AuthService` & `DeviceBindingService` |
| `ai_voice_verification.py` (optional) | Gateway for delegating complex voice checks to the AI pipeline (if configured). | AI services (not always enabled) |

Each service receives a `session_factory` so they can run DB work inside `session_scope` and stay stateless between requests.

---

## 5. Persistence stack (backend/db)

1. **Configuration (`db/config.py`)** – reads environment variables (database URL, echo flags, pool size).
2. **Engine & sessions (`db/engine.py`)** – builds SQLAlchemy engine, exposes `get_session_factory`, and provides the `session_scope` context manager used everywhere.
3. **Base models (`db/base.py`)** – declarative base for all ORM models.
4. **Models (`db/models/*.py`)** – domain entities (users, accounts, cards, transactions, reminders, beneficiaries, sessions, device bindings) plus relationships.
5. **Repositories (`db/repositories/*.py`)** – CRUD helpers for each domain: e.g., `list_accounts_for_user`, `execute_internal_transfer`, `create_reminder`, `list_beneficiaries`.
6. **Utilities (`db/utils/`)** – enums (`ReminderType`, `TransactionChannel`, `BeneficiaryStatus`), security helpers, custom SQLAlchemy types.
7. **Database file** – default SQLite database `backend/db/vaani.db` (can be swapped via config).
8. **Seed scripts & documents** – `db/seed.py` populates sample data; `backend/documents/` stores PDF templates and assets for statements or investment guides.

The services call repositories rather than raw models, which keeps transaction management centralized and simplifies testing.

---

## 6. Document and statement generation

`BankingService`’s statement endpoints rely on templates in `backend/documents/` (e.g., PDF skeletons for statements or investment guides). When a user requests a statement, the service pulls transactions from the DB, fills out the template, and returns a downloadable payload via `StatementDownloadResponse`.

---

## 7. Security, logging, and observability

- Logging is configured at startup in `backend/app.py` (`setup_logging()`), setting INFO level globally, promoting voice-verification logs, and suppressing noisy libraries.
- Each route attaches a `ResponseMeta` block (request ID, timestamp, locale, channel, device ID, customer IP) to comply with RBI/IDRBT digital banking guidelines.
- Authentication uses bearer tokens (validated via `AuthService.validate_token`) and enforces OTP + voice rules where applicable.
- Device binding routes ensure every trusted device has a voice signature; session replacement flags tell the frontend whether to refresh sessions.

---

## 8. Extending the backend

1. **Add a new endpoint** – define the handler in `backend/api/routes.py`, add/extend schemas, and declare whichever services you need via dependencies.
2. **Add domain logic** – implement the behavior inside a service (or a new service) in `backend/db/services/`, keeping DB access inside repositories.
3. **Extend persistence** – add models/repositories and include them in `Base.metadata`. Update `seed.py` if sample data is necessary.
4. **Update docs** – note the change in `documentation/backend-architecture.md` and update the Mermaid diagram if the flow changes.

---

## 9. How it interacts with other modules

- The backend is the **authority for authentication and banking data**. The AI module relies on these APIs and the shared SQLite database for facts (balances, reminders, transactions).
- `run_services.py` runs both the backend FastAPI app (port 8000) and the AI FastAPI app (port 8001) side by side so the frontend can call each surface as needed.

Together, the diagram (`backend-architecture.mmd`) and this document give a complete picture of how a request moves from the client, through FastAPI and the service layer, down to the database and back.
