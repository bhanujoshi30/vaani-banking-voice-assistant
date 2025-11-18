# Test Credentials for Vaani Banking Voice Assistant

## Issue Fixed
The "No accounts found" error was caused by a mismatch between user ID types:
- **Frontend was sending**: `user_id=1` (integer)
- **Database uses**: UUID strings like `3370530d-376d-400d-870a-41b36be9abab`

## Changes Made

### 1. Backend (`/backend/db/services/auth.py`)
- Added `id` field to user profile containing the UUID
- This is now returned on login

### 2. Backend Schema (`/backend/api/schemas.py`)
- Added `id: str` field to `UserProfile` class
- Frontend now receives user UUID in login response

### 3. AI Backend (`/ai/tools/banking_tools.py`)
- Changed `user_id` from `int` to `str` in `GetUserAccountsInput`
- Now accepts UUID strings correctly

### 4. AI Backend (`/ai/main.py`)
- Changed `user_id` from `Optional[int]` to `Optional[str]`
- No longer defaults to integer 1

### 5. Frontend (`/frontend/src/pages/Chat.jsx`)
- Removed fallback to `user_id=1`
- Now uses `session.user?.id` (UUID from login)

## Test Users

You can login with any of these users. Password format: `Sun@{last 4 digits of customer number}`

| Customer ID | Name | Password | User ID (UUID) | Accounts |
|-------------|------|----------|----------------|----------|
| SNB001000 | Isaac Bakshi | `Sun@1000` | 3370530d-376d-400d-870a-41b36be9abab | 2 SAVINGS |
| SNB001001 | Mohammed Khalsa | `Sun@1001` | 8dbbd434-168e-4cdd-9450-ca6b77b2d061 | 1 SAVINGS, 1 CURRENT |
| SNB001002 | Veda Shroff | `Sun@1002` | 1284dc05-8f47-4531-b030-320abde8f35f | 1 SAVINGS, 1 CURRENT |
| SNB001003 | Max Tandon | `Sun@1003` | d097b6eb-8a3d-490e-80aa-e24007197416 | 1 SAVINGS, 1 CURRENT |
| SNB001004 | Jason Roy | `Sun@1004` | 9fa9f050-a060-4f21-a75e-83fde40a9e5a | 2 SAVINGS |

## How to Test

1. **Stop all servers** (if running):
   ```bash
   # Press Ctrl+C in each terminal running servers
   ```

2. **Restart Backend** (port 8000):
   ```bash
   cd backend
   uvicorn app:app --reload --port 8000
   ```

3. **Restart AI Backend** (port 8001):
   ```bash
   cd ai
   python main.py
   ```

4. **Restart Frontend** (port 5173):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Login**:
   - Go to `http://localhost:5173`
   - User ID: `SNB001000`
   - Password: `Sun@1000`

6. **Test Multi-Account Detection**:
   - Navigate to Chat page
   - Try these queries:
     - **"Check balance"** → Shows ALL account balances in a list
     - **"Check my savings account balance"** → Shows SAVINGS balance only
     - **"Check my current account balance"** → Shows CURRENT balance only
     - **"Show all my accounts"** → Lists all accounts
   
   **For best multi-account testing, login as Mohammed Khalsa (SNB001001)**:
   - Has both SAVINGS (₹0.00) and CURRENT (₹131,288.00) accounts
   - Try:
     - **"Check balance"** → Should show both:
       ```
       Your account balances:
       
       • SAVINGS: ₹0.00
       • CURRENT: ₹131,288.00
       ```
     - **"Check my savings account balance"** → "Your SAVINGS account balance is ₹0.00."
     - **"Check my current account balance"** → "Your CURRENT account balance is ₹131,288.00."
     - **"बैलेंस चेक करो"** → Shows both accounts in Hindi
     - **"मेरा बचत खाता बैलेंस दिखाओ"** → Shows SAVINGS in Hindi
     - **"मेरा चालू खाता बैलेंस दिखाओ"** → Shows CURRENT in Hindi

## Account Types

Each user has multiple accounts (randomly generated):
- **SAVINGS** accounts: Most users have 1-2
- **CURRENT** accounts: Some users have 1

To see accounts for a specific user:
```bash
cd backend
python -c "
from db.config import load_database_config
from db.engine import create_db_engine, get_session_factory
from db.models import Account
from sqlalchemy import select

config = load_database_config()
engine = create_db_engine(config)
SessionLocal = get_session_factory(engine)

with SessionLocal() as session:
    accounts = session.execute(
        select(Account).where(Account.user_id == '3370530d-376d-400d-870a-41b36be9abab')
    ).scalars().all()
    
    for acc in accounts:
        print(f'{acc.account_type.value}: {acc.account_number} - Balance: {acc.balance}')
"
```

## Verification

The AI should now correctly:
1. ✅ Receive user UUID from frontend
2. ✅ Look up user accounts using UUID
3. ✅ **Show ALL accounts when no type specified** ("Check balance")
4. ✅ **Show specific account when type mentioned** ("savings", "current")
5. ✅ Support Hindi keywords ("बचत", "चालू")
6. ✅ Format balances nicely with rupee symbol and commas

## Logs to Watch

### AI Backend logs show:
```
chat_request language=en-IN session_id=session-{uuid} user_id={uuid}
banking_agent_response response_length={characters}
```

### If you see:
- `response_length=18` → Still returning "No accounts found" (check user login)
- `response_length=50-100` → Working! Returning balance data
- Multiple lines in response → Showing all accounts correctly

## Database Schema

For reference:
- `users` table has `id` (UUID primary key)
- `accounts` table has `user_id` (UUID foreign key to users.id)
- Accounts are linked to users via UUID, not integers
