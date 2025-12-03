# UPI Payment Flow Documentation

## Overview

Vaani implements **Hello UPI** - a voice-assisted UPI payment system compliant with NPCI/RBI guidelines. Users can make UPI payments using natural language commands with voice or text input.

---

## Features

### Hello UPI Implementation

- **Wake Phrase Detection**: "Hello Vaani" or "Hello UPI" (English/Hindi)
- **Natural Language**: Speak payment intent naturally
- **Multi-language**: Full Hindi and English support
- **Secure PIN Entry**: Manual PIN entry (not spoken)
- **RBI Compliant**: Follows all regulatory guidelines
- **UPI ID Resolution**: Supports UPI ID, phone number, or name
- **Transaction Tracking**: Complete audit trail with UPI reference IDs

---

## Complete Transaction Flow

### Step 1: Wake-up Phrase Detection

User activates UPI mode with wake phrase:

**English:**
- "Hello Vaani"
- "Hello UPI"

**Hindi:**
- "हेलो वाणी"
- "हेलो UPI"

**System Response:**
- Activates UPI mode
- Shows orange UPI badge in top-right
- Intent classifier routes to `upi_payment` intent

### Step 2: Payment Command Parsing

User provides payment details via voice or text:

**Example Commands:**

**English:**
```
"Hello Vaani, pay ₹500 to John via UPI"
"Send ₹1000 to 9876543210@sunbank"
"UPI payment of ₹2000 to first beneficiary"
"Pay ₹5000 from account ending with 41 to Arvind"
```

**Hindi:**
```
"हेलो वाणी, UPI से जॉन को ₹500 भेजें"
"₹1000 भेजो 9876543210@sunbank को"
```

**Extracted Information:**
- **Amount**: Numeric value (₹500, ₹1000, etc.)
- **Recipient**: Can be:
  - UPI ID: `9876543210@sunbank`, `john.doe@sunbank`
  - Phone number: `9876543210`
  - Name: `John Doe`, `Arvind`
  - Beneficiary selector: `first`, `last`, `recent`
- **Source Account**: Last 2-4 digits if specified (e.g., "account ending with 41")
- **Remarks**: Optional payment description

### Step 3: User Consent (First Time Only)

**When**: First UPI payment by user

**UPI Consent Modal displays:**
- UPI terms and conditions
- PIN security guidelines
- RBI compliance notice
- Transaction verification requirements

**User must accept:**
✓ UPI PIN must be entered manually (not spoken)  
✓ Compliance with RBI guidelines  
✓ Transaction verification requirements  
✓ PIN confidentiality  

**Consent Storage:**
- Saved in `localStorage`
- Key: `upiConsent:{userId}`
- Persistent across sessions

### Step 4: Recipient Resolution

System resolves recipient using `resolve_upi_id` tool:

**Resolution Methods:**

**1. UPI ID Lookup**
```javascript
Input: "9876543210@sunbank"
Query: WHERE upi_id = '9876543210@sunbank'
Result: User account found
```

**2. Phone Number Lookup**
```javascript
Input: "9876543210"
Query: WHERE phone_number = '9876543210'
Result: UPI ID retrieved: "9876543210@sunbank"
```

**3. Name Lookup**
```javascript
Input: "John Doe"
Query: WHERE first_name LIKE '%John%' AND last_name LIKE '%Doe%'
Result: Account resolved
```

**4. Beneficiary Lookup**
```javascript
Input: "first beneficiary"
Query: Get user's beneficiaries, select first
Result: Beneficiary UPI ID/account
```

**Returned Data:**
```json
{
  "success": true,
  "account_number": "ACC002",
  "upi_id": "9876543210@sunbank",
  "name": "John Doe",
  "phone_number": "9876543210"
}
```

### Step 5: PIN Entry

**UPI PIN Modal Appears:**

**Display Information:**
- Amount: ₹500
- Recipient: John Doe (or UPI ID)
- Source Account: ACC001
- Payment Description: (if provided)

**PIN Input Features:**
- 6-digit numeric input
- 6 separate input fields
- Auto-focus between fields
- Paste support (6 digits)
- Auto-submit when complete
- Masked input (password type)
- Format validation

**Security:**
- No autocomplete
- No browser save
- Cleared on close
- Not logged anywhere

**User Experience:**
```
[●] [●] [●] [●] [●] [●]
```

Each box auto-focuses on digit entry.

### Step 6: PIN Verification

**Frontend Call:**
```javascript
POST /api/v1/upi/verify-pin

Request:
{
  "pin": "123456",
  "payment_details": {
    "amount": 500,
    "recipient": "John Doe",
    "upi_id": "9876543210@sunbank"
  }
}

Response:
{
  "success": true,
  "message": "UPI PIN verified successfully"
}
```

**Backend Validation:**
1. Checks PIN format (6 digits)
2. **Note**: Mock implementation - validates format only
3. **Production**: Would verify against encrypted PIN storage

**Mock vs Production:**

| Feature | Mock (Current) | Production |
|---------|----------------|------------|
| Validation | Format only | Encrypted PIN match |
| Storage | None | HSM-backed encrypted PIN |
| Attempts | Unlimited | 3 attempts, then lock |
| Verification | Client-side | Server-side with encryption |

### Step 7: Payment Processing

After successful PIN verification:

**Tool Execution:**
```javascript
initiate_upi_payment({
  source_account: "ACC001",
  destination_account: "ACC002",
  amount: 500.00,
  remarks: "Payment to John",
  user_id: "user-uuid",
  session_id: "session-uuid"
})
```

**Backend Processing:**

1. **Validate Accounts**
   - Check source account exists
   - Check destination account exists
   - Verify source account belongs to user

2. **Check Balance**
   - Ensure sufficient funds
   - Account for minimum balance requirements

3. **Generate Reference ID**
   ```
   Format: UPI-YYYYMMDD-HHMMSS
   Example: UPI-20251120-143022
   ```

4. **Create Transactions**
   - **Debit Transaction** on source account
   - **Credit Transaction** on destination account
   - Both marked with `channel=TransactionChannel.UPI`

5. **Update Balances**
   - Deduct from source account
   - Add to destination account
   - Atomic operation (all or nothing)

6. **Log Transaction**
   - UPI reference ID stored
   - Timestamp recorded
   - Full audit trail

**Database Operations:**
```sql
BEGIN TRANSACTION;

-- Create debit transaction
INSERT INTO transactions (
  account_id, transaction_type, amount, 
  channel, reference_id, description
) VALUES (
  source_account_id, 'DEBIT', 500.00,
  'UPI', 'UPI-20251120-143022', 'UPI Payment to John Doe'
);

-- Create credit transaction
INSERT INTO transactions (
  account_id, transaction_type, amount,
  channel, reference_id, description
) VALUES (
  dest_account_id, 'CREDIT', 500.00,
  'UPI', 'UPI-20251120-143022', 'UPI Payment from Sender'
);

-- Update source balance
UPDATE accounts 
SET balance = balance - 500.00 
WHERE id = source_account_id;

-- Update destination balance
UPDATE accounts 
SET balance = balance + 500.00 
WHERE id = dest_account_id;

COMMIT;
```

### Step 8: Transaction Completion

**Success Response:**
```json
{
  "success": true,
  "reference_id": "UPI-20251120-143022",
  "amount": 500.00,
  "recipient_name": "John Doe",
  "recipient_upi": "9876543210@sunbank",
  "timestamp": "2025-11-20T14:30:22",
  "source_account": "ACC001",
  "destination_account": "ACC002"
}
```

**AI Agent Response:**
```
English: "Payment of ₹500 to John Doe was successful. 
          Reference ID: UPI-20251120-143022"

Hindi: "जॉन डो को ₹500 का भुगतान सफल रहा। 
        संदर्भ ID: UPI-20251120-143022"
```

**Transaction Appears In:**
- User's transaction history
- Marked with UPI channel badge
- Searchable by reference ID
- Visible in account statement

---

## UPI Mode Features

### Frontend UPI Mode Toggle

**Location**: Chat page sidebar

**States:**
- **Inactive** (Gray badge): Normal banking chat
- **Active** (Orange badge): UPI payment mode

**Behavior:**
- Click toggle to activate UPI mode
- UPI mode flag sent to AI backend
- Intent classifier prioritizes UPI payment intent
- Balance queries in UPI mode route to UPI agent

### UPI Mode Routing

**Without UPI Mode:**
```
User: "Check my balance"
→ Intent: banking_operation
→ Agent: Banking Agent
→ Response: Shows balance directly
```

**With UPI Mode:**
```
User: "Check my balance"
→ Intent: upi_payment
→ Agent: UPI Agent
→ Response: Shows balance with account selection for UPI
```

### Quick Actions

**Chat Sidebar Provides:**
- "Pay via UPI" button
- Pre-filled command: "Hello Vaani, pay ₹500 to John via UPI"
- One-click activation

---

## Multi-language Support

### English Commands

```
"Hello Vaani, pay ₹500 to John"
"Send ₹1000 to 9876543210@sunbank"
"Transfer ₹2000 from savings to Arvind via UPI"
"Pay ₹5000 to first beneficiary"
```

### Hindi Commands

```
"हेलो वाणी, UPI से जॉन को ₹500 भेजें"
"₹1000 भेजो 9876543210@sunbank को"
"अर्विंद को ₹2000 ट्रांसफर करो"
```

### Hinglish (Code-Switching)

```
"Hello Vaani, John ko ₹500 bhejo"
"UPI se ₹1000 transfer karo Arvind ko"
"₹2000 pay karo first beneficiary ko"
```

All UI elements, responses, and errors are translated to user's preferred language.

---

## UPI ID Resolution

### Predefined UPI IDs

Users have UPI IDs in seed data:

**Format Options:**
- `{phone}@sunbank`: `9876543210@sunbank`
- `{name}@sunbank`: `john.doe@sunbank`
- Custom UPI IDs

**Database Field:**
```sql
users.upi_id VARCHAR(100) UNIQUE
```

**Example Data:**
```sql
INSERT INTO users (upi_id, phone_number, first_name, last_name)
VALUES 
  ('9876543210@sunbank', '9876543210', 'John', 'Doe'),
  ('john.doe@sunbank', '9876543210', 'John', 'Doe');
```

### Resolution Priority

1. **Exact UPI ID match**: Highest priority
2. **Phone number**: Convert to UPI ID
3. **Name match**: Fuzzy search on first/last name
4. **Beneficiary**: Look up in beneficiaries table

---

## Security & Compliance

### RBI Guidelines Compliance

✅ **PIN Security**
- PIN must be entered manually (keyboard/screen)
- Never spoken aloud
- Not visible during entry
- Immediately cleared after use

✅ **User Consent**
- Explicit consent before first UPI payment
- Terms and conditions displayed
- Consent recorded and stored

✅ **Transaction Verification**
- Amount, recipient, and account displayed
- User confirms before PIN entry
- Can cancel at any time

✅ **Audit Trail**
- Every transaction has unique reference ID
- UPI channel marked
- Complete transaction log
- Timestamps in IST

✅ **Transaction Limits**
- Amount validation (future)
- Daily transaction limits (future)
- Velocity checks (future)

### Data Security

**What's Stored:**
- UPI reference ID
- Transaction amount and parties
- Timestamp
- Channel (UPI)

**What's NOT Stored:**
- PIN (never stored anywhere)
- Raw voice commands containing PIN
- Intermediate verification data

**Encryption:**
- UPI PIN hash (future - HSM encryption)
- Database encryption at rest (production)
- TLS for all API calls

---

## Error Handling

### Common Errors

**1. Recipient Not Found**
```
Error: "We couldn't find a UPI ID or account for 'John'. 
        Please check the name or provide UPI ID."

Hindi: "हम 'जॉन' के लिए UPI ID या खाता नहीं ढूंढ सके। 
        कृपया नाम जांचें या UPI ID प्रदान करें।"
```

**2. Invalid PIN Format**
```
Error: "Invalid PIN. Please enter a 6-digit PIN."

Hindi: "अमान्य PIN। कृपया 6 अंकों का PIN दर्ज करें।"
```

**3. Insufficient Balance**
```
Error: "Insufficient balance in your account. 
        Available: ₹1,000. Required: ₹5,000."

Hindi: "आपके खाते में पर्याप्त बैलेंस नहीं है। 
        उपलब्ध: ₹1,000। आवश्यक: ₹5,000।"
```

**4. Account Not Found**
```
Error: "Source account not found. Please check your account details."
```

**5. Network Error**
```
Error: "Payment failed due to network error. Please try again."

Hindi: "नेटवर्क त्रुटि के कारण भुगतान विफल। कृपया पुनः प्रयास करें।"
```

**6. Transaction Timeout**
```
Error: "Transaction timed out. Please check your transaction history."
```

### Error Recovery

**User Actions:**
- Retry payment
- Check balance
- Verify recipient details
- Contact support

**System Actions:**
- Log error with context
- Rollback partial transactions
- Send error notification
- Update transaction status

---

## Database Schema

### User Table Extension

```sql
ALTER TABLE users ADD COLUMN upi_id VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN upi_pin_hash VARCHAR(256);
```

**Fields:**
- `upi_id`: Unique UPI ID (`9876543210@sunbank`)
- `upi_pin_hash`: Encrypted UPI PIN (future)

### Transaction Table UPI Support

```sql
-- Existing transaction model supports UPI
channel = 'UPI'  -- TransactionChannel.UPI
reference_id = 'UPI-YYYYMMDD-HHMMSS'  -- UPI reference
```

**UPI-specific fields:**
- `channel`: Set to `TransactionChannel.UPI`
- `reference_id`: UPI transaction reference
- `description`: Includes "UPI Payment"

---

## API Endpoints

### Backend Endpoints

**POST /api/v1/upi/verify-pin**

Verify UPI PIN (mock implementation).

**Request:**
```json
{
  "pin": "123456",
  "payment_details": {
    "amount": 500.00,
    "recipient": "John Doe",
    "upi_id": "9876543210@sunbank"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "UPI PIN verified successfully"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid PIN format
- 401: PIN verification failed
- 500: Server error

### AI Backend Tool

**Tool: `resolve_upi_id`**

Resolve recipient identifier to account details.

**Input:**
```json
{
  "recipient_identifier": "John Doe",
  "user_id": "user-uuid"
}
```

**Output:**
```json
{
  "success": true,
  "account_number": "ACC002",
  "upi_id": "9876543210@sunbank",
  "name": "John Doe",
  "phone_number": "9876543210"
}
```

**Tool: `initiate_upi_payment`**

Process UPI payment.

**Input:**
```json
{
  "source_account": "ACC001",
  "destination_account": "ACC002",
  "amount": 500.00,
  "remarks": "Payment to John",
  "user_id": "user-uuid",
  "session_id": "session-uuid"
}
```

**Output:**
```json
{
  "success": true,
  "reference_id": "UPI-20251120-143022",
  "amount": 500.00,
  "recipient_name": "John Doe",
  "timestamp": "2025-11-20T14:30:22"
}
```

---

## Testing Flow

### Manual Test Steps

1. **Login to application**
   - Use test credentials
   - Navigate to Chat page

2. **Activate UPI Mode**
   - Click "UPI Mode" toggle in sidebar
   - Verify orange badge appears

3. **Initiate Payment**
   - Type or speak: "Hello Vaani, pay ₹500 to John via UPI"
   - Or click "Pay via UPI" quick action

4. **Accept Consent** (first time only)
   - Read UPI terms
   - Check consent checkbox
   - Click "Accept"

5. **Enter PIN**
   - PIN modal appears with payment details
   - Enter 6-digit PIN (test PIN: any 6 digits)
   - Click "Verify" or auto-submit

6. **Verify Success**
   - Success message appears
   - Reference ID displayed
   - Check transaction history
   - Verify balance updated

### Test Cases

**Test Case 1: Happy Path**
- Command: "Pay ₹500 to John"
- Expected: Success, balance updated

**Test Case 2: UPI ID Resolution**
- Command: "Send ₹1000 to 9876543210@sunbank"
- Expected: Recipient found, payment successful

**Test Case 3: Phone Number**
- Command: "Transfer ₹2000 to 9876543210"
- Expected: UPI ID resolved, payment successful

**Test Case 4: First Beneficiary**
- Command: "Pay ₹500 to first beneficiary"
- Expected: Beneficiary resolved, payment successful

**Test Case 5: Insufficient Balance**
- Command: "Pay ₹100000 to John"
- Expected: Error message about insufficient funds

**Test Case 6: Invalid Recipient**
- Command: "Pay ₹500 to NonExistentPerson"
- Expected: Recipient not found error

**Test Case 7: Hindi Command**
- Command: "हेलो वाणी, जॉन को ₹500 भेजें"
- Expected: Payment successful with Hindi response

---

## Mock Implementation Notes

**Current Implementation:**
- All transactions use internal transfer system
- UPI IDs are predefined in seed data
- PIN validation is format-only (6 digits)
- No actual NPCI integration
- Transactions marked with UPI channel for tracking

**Production Requirements:**
- NPCI API integration
- Real UPI ID verification
- HSM-based PIN encryption
- Bank account verification
- Transaction limits and velocity checks
- Real-time NPCI communication
- Settlement and reconciliation
- Regulatory reporting

---

## Future Enhancements

### Planned Features

1. **QR Code Payments**
   - Scan merchant QR codes
   - Extract payment details
   - Auto-fill amount and merchant

2. **Request Money**
   - Send payment requests
   - Request from contacts
   - Track request status

3. **Transaction Limits**
   - Per-transaction limits
   - Daily limits
   - Monthly limits
   - KYC-based limits

4. **Recurring Payments**
   - Auto-pay setup
   - Recurring UPI payments
   - Mandate management

5. **Split Payments**
   - Split bill among multiple people
   - Each person pays via UPI
   - Track split payment status

6. **Bank Account Verification**
   - Real-time account verification
   - NPCI account validation
   - Beneficiary verification

7. **Enhanced Security**
   - Biometric authentication
   - Device binding for UPI
   - Location-based verification
   - Fraud detection

---

## Troubleshooting

### Issue: Recipient not found

**Cause**: Name doesn't match database exactly

**Solution**:
- Use UPI ID instead of name
- Check spelling of name
- Try phone number
- Use "first beneficiary" if saved

### Issue: PIN modal doesn't appear

**Cause**: Recipient resolution failed

**Solution**:
- Check AI backend logs
- Verify recipient exists in database
- Try different recipient identifier

### Issue: Payment failed after PIN entry

**Cause**: Insufficient balance or transaction error

**Solution**:
- Check account balance
- Verify recipient account exists
- Check backend logs for errors
- Retry payment

### Issue: UPI mode not activating

**Cause**: Frontend state not syncing

**Solution**:
- Refresh page
- Clear localStorage
- Check browser console for errors

---

## Compliance Checklist

✅ PIN Security
- [x] PIN entered manually
- [x] PIN not spoken
- [x] PIN masked during entry
- [x] PIN cleared after use

✅ User Consent
- [x] Terms displayed
- [x] Explicit consent required
- [x] Consent stored
- [x] Can be revoked

✅ Transaction Security
- [x] Amount displayed before PIN
- [x] Recipient verified
- [x] Can cancel before completion
- [x] Confirmation after success

✅ Audit & Logging
- [x] Unique reference ID
- [x] Complete transaction log
- [x] Timestamp recorded
- [x] Channel marked as UPI

✅ Error Handling
- [x] Graceful error messages
- [x] Transaction rollback
- [x] User notification
- [x] Retry mechanism

---

## Related Documentation

- [Setup Guide](./setup_guide.md) - Installation and setup
- [AI Modules](../ai_modules.md) - AI agent details
- [Backend Modules](../backend_modules.md) - Backend API
- [Frontend Modules](../frontend_modules.md) - Frontend components
- [Voice Authentication](./voice_authentication.md) - Voice login
- [API Reference](./api_reference.md) - Complete API docs
