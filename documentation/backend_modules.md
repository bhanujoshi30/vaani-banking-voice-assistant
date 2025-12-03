# Backend Module Documentation

## Overview

The Vaani backend is built with **FastAPI** and provides RESTful APIs for banking operations, authentication, device binding, and database management. It runs on port **8000** and uses SQLite for data storage.

---

## Architecture

```
backend/
├── app.py                    # FastAPI application factory
├── __pycache__/
├── api/                      # API layer
│   ├── __init__.py
│   ├── dependencies.py       # Dependency injection
│   ├── routes.py            # API route handlers
│   ├── schemas.py           # Pydantic request/response models
│   └── security.py          # Authentication & authorization
│
└── db/                       # Database layer
    ├── __init__.py
    ├── base.py              # SQLAlchemy base models
    ├── config.py            # Database configuration
    ├── engine.py            # Database engine setup
    ├── seed.py              # Database seeding script
    ├── vaani.db             # SQLite database file
    │
    ├── models/              # SQLAlchemy ORM models
    │   ├── account.py       # Account model
    │   ├── beneficiary.py   # Beneficiary model
    │   ├── branch.py        # Branch model
    │   ├── card.py          # Card model
    │   ├── device_binding.py # Device binding model
    │   ├── reminder.py      # Reminder model
    │   ├── session.py       # Session model
    │   ├── transaction.py   # Transaction model
    │   └── user.py          # User model
    │
    ├── repositories/        # Data access layer
    │   ├── accounts.py      # Account operations
    │   ├── auth.py          # Authentication operations
    │   ├── beneficiaries.py # Beneficiary operations
    │   ├── device_bindings.py # Device binding operations
    │   ├── reminders.py     # Reminder operations
    │   └── transactions.py  # Transaction operations
    │
    ├── services/            # Business logic layer
    │   ├── ai_voice_verification.py  # AI-enhanced voice verification
    │   ├── auth.py          # Authentication service
    │   ├── banking.py       # Banking operations service
    │   ├── device_binding.py # Device binding service
    │   └── voice_verification.py # Voice verification service
    │
    └── utils/               # Utilities
        ├── enums.py         # Enum definitions
        └── types.py         # Custom types
```

---

## Database Models

### 1. User Model (`db/models/user.py`)

Represents a banking customer with authentication and profile information.

**Fields:**
- `id` (GUID): Primary key, UUID
- `customer_number` (String): Unique customer number (e.g., "CUST001")
- `first_name` (String): Customer first name
- `last_name` (String): Customer last name
- `preferred_language` (String): Language preference ("en-IN", "hi-IN")
- `date_of_birth` (Date): Date of birth
- `gender` (String): Gender
- `email` (String): Email address (unique)
- `phone_number` (String): Phone number (unique)
- `upi_id` (String): UPI ID (e.g., "9876543210@sunbank") - unique
- `upi_pin_hash` (String): Encrypted UPI PIN
- `aadhaar_last4` (String): Last 4 digits of Aadhaar
- `pan_number` (String): PAN number
- `kyc_status` (String): KYC verification status
- `risk_segment` (String): Risk segment classification
- `password_hash` (String): Hashed password
- `last_login_at` (DateTime): Last login timestamp
- `primary_branch_id` (GUID): Foreign key to primary branch

**Relationships:**
- `accounts`: One-to-many with Account
- `sessions`: One-to-many with Session
- `cards`: One-to-many with Card
- `reminders`: One-to-many with Reminder
- `device_bindings`: One-to-many with DeviceBinding
- `beneficiaries`: One-to-many with Beneficiary

### 2. Account Model (`db/models/account.py`)

Represents a bank account (savings, current, etc.).

**Fields:**
- `id` (GUID): Primary key
- `account_number` (String): Unique account number
- `account_type` (String): Type of account (savings, current, etc.)
- `user_id` (GUID): Foreign key to User
- `branch_id` (GUID): Foreign key to Branch
- `balance` (Decimal): Current balance
- `currency` (String): Currency code (default: "INR")
- `status` (String): Account status (active, frozen, closed)
- `opened_at` (DateTime): Account opening date
- `closed_at` (DateTime): Account closure date (if applicable)

**Relationships:**
- `user`: Many-to-one with User
- `branch`: Many-to-one with Branch
- `transactions`: One-to-many with Transaction

### 3. Transaction Model (`db/models/transaction.py`)

Represents a financial transaction.

**Fields:**
- `id` (GUID): Primary key
- `account_id` (GUID): Foreign key to Account
- `transaction_type` (String): Type (debit, credit)
- `amount` (Decimal): Transaction amount
- `balance_after` (Decimal): Balance after transaction
- `channel` (TransactionChannel): Channel (ATM, UPI, NEFT, etc.)
- `description` (String): Transaction description
- `reference_id` (String): External reference ID
- `transaction_date` (DateTime): Transaction timestamp
- `status` (String): Transaction status

**Relationships:**
- `account`: Many-to-one with Account

### 4. DeviceBinding Model (`db/models/device_binding.py`)

Represents a trusted device binding for a user.

**Fields:**
- `id` (GUID): Primary key
- `user_id` (GUID): Foreign key to User
- `device_identifier` (String): Unique device identifier
- `device_fingerprint` (String): Device fingerprint hash
- `device_label` (String): User-friendly device name
- `platform` (String): Platform (iOS, Android, Web)
- `trust_level` (DeviceTrustLevel): Trust level (TRUSTED, SUSPICIOUS, REVOKED)
- `voice_signature_vector` (Binary): Voice biometric embedding
- `voice_signature_hash` (String): SHA-256 hash of voice sample
- `registration_method` (String): How device was registered
- `last_verified_at` (DateTime): Last verification timestamp
- `revoked_at` (DateTime): Revocation timestamp
- `created_at` (DateTime): Creation timestamp

**Relationships:**
- `user`: Many-to-one with User

### 5. Reminder Model (`db/models/reminder.py`)

Represents a payment or transaction reminder.

**Fields:**
- `id` (GUID): Primary key
- `user_id` (GUID): Foreign key to User
- `account_id` (GUID): Foreign key to Account (optional)
- `reminder_type` (ReminderType): Type (BILL_PAYMENT, EMI, etc.)
- `status` (ReminderStatus): Status (PENDING, COMPLETED, CANCELLED)
- `message` (String): Reminder message
- `remind_at` (DateTime): Reminder time
- `channel` (String): Notification channel
- `recurrence_rule` (String): Recurrence pattern
- `created_at` (DateTime): Creation timestamp

**Relationships:**
- `user`: Many-to-one with User
- `account`: Many-to-one with Account

### 6. Beneficiary Model (`db/models/beneficiary.py`)

Represents a saved beneficiary for transfers.

**Fields:**
- `id` (GUID): Primary key
- `user_id` (GUID): Foreign key to User
- `name` (String): Beneficiary name
- `account_number` (String): Beneficiary account number
- `upi_id` (String): Beneficiary UPI ID
- `phone_number` (String): Beneficiary phone
- `bank_name` (String): Bank name
- `ifsc_code` (String): IFSC code
- `nickname` (String): User-defined nickname
- `is_favorite` (Boolean): Favorite status
- `created_at` (DateTime): Creation timestamp

**Relationships:**
- `user`: Many-to-one with User

### 7. Session Model (`db/models/session.py`)

Represents an active user session.

**Fields:**
- `id` (GUID): Primary key
- `user_id` (GUID): Foreign key to User
- `access_token` (String): JWT access token
- `device_id` (String): Device identifier
- `ip_address` (String): Client IP address
- `user_agent` (String): Browser/app user agent
- `created_at` (DateTime): Session creation time
- `expires_at` (DateTime): Session expiration time
- `last_activity_at` (DateTime): Last activity timestamp

**Relationships:**
- `user`: Many-to-one with User

### 8. Branch Model (`db/models/branch.py`)

Represents a bank branch.

**Fields:**
- `id` (GUID): Primary key
- `branch_code` (String): Unique branch code
- `branch_name` (String): Branch name
- `ifsc_code` (String): IFSC code
- `city` (String): City
- `state` (String): State
- `address` (String): Full address
- `phone_number` (String): Branch phone
- `email` (String): Branch email

### 9. Card Model (`db/models/card.py`)

Represents a debit/credit card.

**Fields:**
- `id` (GUID): Primary key
- `user_id` (GUID): Foreign key to User
- `card_number` (String): Masked card number
- `card_type` (String): Type (debit, credit)
- `expiry_date` (Date): Expiration date
- `status` (String): Card status (active, blocked)
- `issued_at` (DateTime): Issue date

**Relationships:**
- `user`: Many-to-one with User

---

## Repositories (Data Access Layer)

Repositories handle direct database operations using SQLAlchemy.

### AuthRepository (`db/repositories/auth.py`)

**Methods:**
- `get_user_by_customer_number(customer_number)`: Fetch user by customer number
- `get_user_by_id(user_id)`: Fetch user by UUID
- `create_session(user_id, access_token, device_id, ip, user_agent, expires_at)`: Create session
- `get_session(access_token)`: Retrieve session by token
- `delete_session(access_token)`: Delete session
- `update_last_login(user_id)`: Update last login timestamp

### AccountsRepository (`db/repositories/accounts.py`)

**Methods:**
- `get_accounts_by_user_id(user_id)`: Get all accounts for a user
- `get_account_by_number(account_number)`: Get account by number
- `update_account_balance(account_id, new_balance)`: Update balance

### TransactionsRepository (`db/repositories/transactions.py`)

**Methods:**
- `create_transaction(account_id, type, amount, balance_after, channel, description, reference_id)`: Create transaction
- `get_transactions_by_account(account_id, limit, offset)`: Get transaction history
- `get_transactions_by_date_range(account_id, start_date, end_date)`: Get transactions in date range

### DeviceBindingsRepository (`db/repositories/device_bindings.py`)

**Methods:**
- `get_binding_by_device(user_id, device_identifier)`: Get binding by device
- `create_binding(user_id, device_identifier, device_fingerprint, device_label, platform, registration_method)`: Create new binding
- `update_binding(binding_id, **kwargs)`: Update binding fields
- `revoke_binding(binding_id)`: Revoke device binding
- `get_bindings_by_user(user_id)`: Get all bindings for user

### RemindersRepository (`db/repositories/reminders.py`)

**Methods:**
- `create_reminder(user_id, reminder_type, message, remind_at, **kwargs)`: Create reminder
- `get_reminders_by_user(user_id, status)`: Get user reminders
- `update_reminder_status(reminder_id, status)`: Update reminder status
- `delete_reminder(reminder_id)`: Delete reminder

### BeneficiariesRepository (`db/repositories/beneficiaries.py`)

**Methods:**
- `create_beneficiary(user_id, name, account_number, **kwargs)`: Add beneficiary
- `get_beneficiaries_by_user(user_id)`: Get all beneficiaries
- `get_beneficiary_by_id(beneficiary_id)`: Get beneficiary by ID
- `update_beneficiary(beneficiary_id, **kwargs)`: Update beneficiary
- `delete_beneficiary(beneficiary_id)`: Delete beneficiary

---

## Services (Business Logic Layer)

Services implement business logic and orchestrate repository operations.

### AuthService (`db/services/auth.py`)

Handles authentication, session management, and voice-based login.

**Key Methods:**

#### `authenticate_user_with_password(customer_number, password, device_info, validate_only=False)`
- Validates password
- Creates or retrieves device binding
- Creates session and returns access token

#### `authenticate_user_with_voice(customer_number, device_info, voice_sample, validate_only=False)`
- Validates voice biometric
- Checks device binding and voice signature
- Supports device re-binding after revocation
- Uses AI-enhanced verification if available
- Creates session on successful verification

#### `logout_user(access_token)`
- Invalidates session
- Removes access token

**Authentication Flow:**
1. User provides credentials (password or voice sample)
2. Service validates credentials
3. Device binding is verified or created
4. Session is created with JWT token
5. User receives access token for API requests

### BankingService (`db/services/banking.py`)

Handles banking operations like transfers, balance checks, and transactions.

**Key Methods:**

#### `get_account_balance(account_number)`
- Returns current balance and account details

#### `get_transaction_history(account_number, limit=10, offset=0)`
- Returns paginated transaction history

#### `transfer_between_accounts(from_account, to_account, amount, description, channel, user_id, session_id)`
- Validates accounts
- Checks sufficient balance
- Creates debit and credit transactions
- Updates account balances
- Atomic transaction with rollback on error

#### `get_account_statement(account_number, start_date, end_date)`
- Returns transactions in date range
- Formatted for statement download

### DeviceBindingService (`db/services/device_binding.py`)

Manages trusted device bindings for users.

**Key Methods:**

#### `create_or_update_binding(user_id, device_identifier, device_fingerprint, device_label, platform, registration_method, voice_sample=None)`
- Creates new binding or updates existing
- Stores voice signature if provided
- Sets trust level to TRUSTED

#### `get_user_bindings(user_id)`
- Returns all device bindings for user

#### `revoke_binding(binding_id, user_id)`
- Marks binding as REVOKED
- Updates revocation timestamp

#### `verify_device(user_id, device_identifier)`
- Checks if device is trusted
- Returns binding details

### VoiceVerificationService (`db/services/voice_verification.py`)

Handles voice biometric verification using Resemblyzer.

**Key Methods:**

#### `extract_embedding(audio_bytes)`
- Extracts 256-dimensional voice embedding
- Uses Resemblyzer ECAPA-TDNN model
- Returns numpy array

#### `compute_similarity(embedding1, embedding2)`
- Calculates cosine similarity
- Returns score between 0 and 1

#### `matches(stored_embedding, test_audio, threshold=0.75)`
- Verifies if voice matches stored signature
- Returns boolean result

**Voice Verification Flow:**
1. User provides voice sample (audio bytes)
2. Service extracts embedding using Resemblyzer
3. Compares with stored voice signature
4. Returns match result based on similarity threshold

### AIVoiceVerificationService (`db/services/ai_voice_verification.py`)

Enhanced voice verification using AI analysis.

**Key Methods:**

#### `verify_with_ai(similarity_score, threshold, user_context)`
- Sends similarity score to AI backend
- Gets confidence, risk level, and recommendation
- Combines AI analysis with baseline similarity

#### `get_adaptive_threshold(device_trust_level, is_new_device)`
- Adjusts threshold based on context
- Higher threshold for suspicious/new devices
- Lower threshold for trusted devices

**AI Enhancement Benefits:**
- Context-aware verification
- Risk assessment
- Adaptive thresholds
- Anomaly detection
- Graceful fallback to baseline verification

---

## API Layer

### Routes (`api/routes.py`)

Main API endpoints for the application.

#### Authentication Endpoints

**POST /api/v1/auth/login**
- Authenticate user with password or voice
- Supports device binding
- Returns access token and user profile

**POST /api/v1/auth/logout**
- Invalidate current session
- Requires authentication

#### Account Endpoints

**GET /api/v1/accounts**
- List all user accounts
- Requires authentication

**GET /api/v1/accounts/{account_number}/balance**
- Get account balance
- Requires authentication

#### Transaction Endpoints

**GET /api/v1/accounts/{account_number}/transactions**
- Get transaction history
- Supports pagination
- Requires authentication

**POST /api/v1/accounts/{account_number}/transfer**
- Transfer funds between accounts
- Validates balance and accounts
- Requires authentication

**POST /api/v1/accounts/{account_number}/statement/download**
- Download account statement
- Supports date range filtering
- Returns structured statement data

#### Device Binding Endpoints

**GET /api/v1/device-bindings**
- List all device bindings
- Requires authentication

**POST /api/v1/device-bindings**
- Create new device binding
- Supports voice enrollment

**DELETE /api/v1/device-bindings/{binding_id}**
- Revoke device binding
- Requires authentication

#### Reminder Endpoints

**GET /api/v1/reminders**
- List user reminders
- Filter by status
- Requires authentication

**POST /api/v1/reminders**
- Create new reminder
- Supports recurrence
- Requires authentication

**PATCH /api/v1/reminders/{reminder_id}/status**
- Update reminder status
- Requires authentication

**DELETE /api/v1/reminders/{reminder_id}**
- Delete reminder
- Requires authentication

#### Beneficiary Endpoints

**GET /api/v1/beneficiaries**
- List all beneficiaries
- Requires authentication

**POST /api/v1/beneficiaries**
- Add new beneficiary
- Requires authentication

**DELETE /api/v1/beneficiaries/{beneficiary_id}**
- Remove beneficiary
- Requires authentication

#### UPI Endpoints

**POST /api/v1/upi/verify-pin**
- Verify UPI PIN (mock implementation)
- Used in UPI payment flow

### Schemas (`api/schemas.py`)

Pydantic models for request/response validation.

**Request Models:**
- `LoginData`: Login request
- `TransferRequest`: Fund transfer request
- `ReminderCreateRequest`: Create reminder
- `BeneficiaryCreateRequest`: Add beneficiary
- `UPIPinVerifyRequest`: UPI PIN verification
- `StatementDownloadRequest`: Statement download

**Response Models:**
- `LoginResponse`: Login response with token and profile
- `AccountBalanceResponse`: Balance response
- `TransactionHistoryResponse`: Transaction list
- `TransferResponse`: Transfer confirmation
- `ReminderResponse`: Reminder details
- `BeneficiaryResponse`: Beneficiary details
- `DeviceBindingResponse`: Device binding details
- `ErrorResponse`: Error details

### Security (`api/security.py`)

Authentication and authorization helpers.

**Key Components:**

#### `RequestContext`
- Captures request metadata
- Request ID, timestamp, locale, channel
- Customer IP, device ID

#### `CurrentSessionDep`
- Dependency for authenticated routes
- Validates access token
- Retrieves session and user

#### `create_access_token(user_id)`
- Generates JWT token
- Sets expiration time
- Returns token string

### Dependencies (`api/dependencies.py`)

Dependency injection for services.

**Service Dependencies:**
- `AuthServiceDep`: Injects AuthService
- `BankingServiceDep`: Injects BankingService
- `DeviceBindingServiceDep`: Injects DeviceBindingService
- `VoiceVerificationServiceDep`: Injects VoiceVerificationService

---

## Database Configuration

### Engine Setup (`db/engine.py`)

**Database**: SQLite (default)
- **File Location**: `backend/db/vaani.db`
- **Type**: SQLite3 (file-based, no server required)
- **Connection pooling**: Managed by SQLAlchemy
- **Auto-commit**: Disabled for transactions
- **Migrations**: Supports future PostgreSQL migration

**Why SQLite?**
- Zero configuration required
- Perfect for development and prototyping
- File-based (no separate database server)
- Easy to backup (just copy vaani.db file)
- Full SQL feature support
- Production-ready for small to medium workloads

**Configuration** (`db/config.py`):
```python
# Default SQLite database
DEFAULT_SQLITE_PATH = "backend/db/vaani.db"
DATABASE_URL = "sqlite:///backend/db/vaani.db"

# Can be overridden with environment variables
DB_BACKEND=sqlite  # or postgresql for production
DATABASE_URL=sqlite:///path/to/db.db
```

**Future PostgreSQL Support**:
The system is designed to easily switch to PostgreSQL for production:
```bash
export DB_BACKEND=postgresql
export DATABASE_URL=postgresql://user:pass@localhost/vaani
```

### Database Seeding (`db/seed.py`)

Populates database with sample data:
- Test users with various profiles
- Accounts with balances
- Transaction history
- Reminders
- Beneficiaries
- Device bindings

**Usage:**
```bash
python -m backend.db.seed
```

---

## Enumerations

Defined in `db/utils/enums.py`:

### TransactionChannel
- `ATM`: ATM withdrawal/deposit
- `BRANCH`: Branch transaction
- `ONLINE`: Online banking
- `MOBILE`: Mobile app
- `UPI`: UPI payment
- `NEFT`: NEFT transfer
- `RTGS`: RTGS transfer
- `IMPS`: IMPS transfer

### ReminderType
- `BILL_PAYMENT`: Utility bill payment
- `EMI`: Loan EMI
- `SUBSCRIPTION`: Subscription renewal
- `CUSTOM`: User-defined reminder

### ReminderStatus
- `PENDING`: Not yet triggered
- `COMPLETED`: Reminder completed
- `CANCELLED`: User cancelled

### DeviceTrustLevel
- `TRUSTED`: Verified trusted device
- `SUSPICIOUS`: Flagged for review
- `REVOKED`: Binding revoked

---

## Key Features

### 1. Voice-Based Authentication
- Biometric voice verification using Resemblyzer
- AI-enhanced verification with context analysis
- Device binding with voice signature
- Supports re-binding after revocation

### 2. Secure Device Binding
- Unique device fingerprinting
- Voice biometric enrollment
- Trust level management
- Revocation and re-binding support

### 3. Transaction Management
- Atomic fund transfers
- Transaction history tracking
- Multiple transaction channels
- Balance validation

### 4. Reminder System
- Multiple reminder types
- Recurrence support
- Status tracking
- User-specific reminders

### 5. Beneficiary Management
- Save frequent transfer recipients
- UPI ID and account number support
- Nickname and favorites
- Quick transfer to beneficiaries

---

## Security Features

### Authentication
- Password hashing with bcrypt
- JWT-based session tokens
- Session expiration
- Voice biometric verification

### Device Security
- Device fingerprinting
- Trust level management
- Voice signature verification
- Revocation support

### Transaction Security
- Balance validation
- Atomic transactions
- Rollback on error
- Transaction limits

### Data Protection
- No raw audio storage
- Voice embeddings only
- Password hashing
- Encrypted UPI PINs

---

## Error Handling

### Standard Error Response
```json
{
  "meta": {
    "requestId": "uuid",
    "timestamp": "ISO datetime",
    "locale": "en-IN"
  },
  "error": {
    "code": "error_code",
    "message": "Error description",
    "info": {}
  }
}
```

### Common Error Codes
- `invalid_credentials`: Authentication failed
- `insufficient_funds`: Not enough balance
- `account_not_found`: Account doesn't exist
- `device_not_trusted`: Device not verified
- `voice_verification_failed`: Voice doesn't match
- `otp_required`: OTP needed for operation
- `otp_invalid`: Wrong OTP provided

---

## Best Practices

### Repository Layer
- Keep database operations isolated
- Use SQLAlchemy ORM
- Handle database exceptions
- Return domain models

### Service Layer
- Implement business logic
- Orchestrate repository calls
- Validate business rules
- Handle service-level errors

### API Layer
- Validate input with Pydantic
- Use dependency injection
- Return appropriate HTTP status codes
- Provide detailed error messages

---

## Testing

### Unit Tests
- Test individual methods
- Mock dependencies
- Cover edge cases

### Integration Tests
- Test full workflows
- Use test database
- Verify transactions

### API Tests
- Test endpoints with curl
- Verify response schemas
- Check error handling

---

## Performance Considerations

### Database
- Use indexes on frequently queried fields
- Limit result sets with pagination
- Use connection pooling

### API
- Enable CORS for frontend
- Use async handlers where possible
- Implement rate limiting (future)

### Voice Processing
- Process audio in background (future)
- Cache voice embeddings
- Optimize model loading

---

## Future Enhancements

1. **PostgreSQL Migration**: Move from SQLite to PostgreSQL
2. **Redis Caching**: Cache frequently accessed data
3. **Background Jobs**: Celery for async tasks
4. **Rate Limiting**: Protect against abuse
5. **Audit Logging**: Track all operations
6. **Multi-factor Authentication**: Additional security layers
7. **Webhooks**: Real-time notifications
8. **GraphQL API**: Alternative to REST

---

## Related Documentation

- [Setup Guide](./other/setup_guide.md) - Installation instructions
- [AI Architecture](./ai_architecture.md) - AI backend details
- [Frontend Architecture](./frontend-architecture.md) - Frontend structure
- [API Reference](./api_reference.md) - Complete API documentation
- [Database Schema](./database_schema.md) - Detailed schema documentation
