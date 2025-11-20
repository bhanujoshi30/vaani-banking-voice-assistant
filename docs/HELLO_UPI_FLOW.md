# Hello UPI Implementation - Transaction Flow

## Overview
This document explains how Hello UPI voice-assisted payments work in the Vaani banking assistant, following NPCI/RBI guidelines.

## Complete Transaction Flow

### 1. **Wake-up Phrase Detection**
- User says: "Hello Vaani" or "Hello UPI" (English) or "हेलो वाणी" (Hindi)
- System detects wake-up phrase in voice input
- Activates UPI mode (indicated by orange badge in top-right)
- Intent classifier routes to `upi_payment` intent

### 2. **Payment Command Parsing**
User provides payment details via voice:
- **Example**: "Hello Vaani, pay ₹500 to John via UPI"
- **Example**: "Send ₹1000 to 9876543210@sunbank"
- **Example**: "UPI payment of ₹2000 to first beneficiary"

The UPI agent extracts:
- **Amount**: Numeric value (₹500, ₹1000, etc.)
- **Recipient**: Can be:
  - UPI ID (e.g., `9876543210@sunbank`, `john.doe@sunbank`)
  - Phone number (e.g., `9876543210`)
  - Name (e.g., "John Doe", "Arvind")
  - Beneficiary selector ("first", "last")
- **Source Account**: Last 2-4 digits if specified (e.g., "account ending with 41")
- **Remarks**: Optional payment description

### 3. **User Consent (First Time Only)**
- If user hasn't accepted Hello UPI terms, consent modal appears
- User must accept:
  - UPI PIN must be entered manually (not spoken)
  - Compliance with RBI guidelines
  - Transaction verification requirements
  - PIN confidentiality
- Consent stored in localStorage

### 4. **Recipient Resolution**
System resolves recipient using `resolve_upi_id` tool:
- **UPI ID lookup**: Searches users by `upi_id` field
- **Phone number lookup**: Matches by phone number
- **Name lookup**: Partial match on first/last name
- Returns account number and user details

### 5. **PIN Entry**
- PIN modal appears with payment details:
  - Amount: ₹500
  - Recipient: John Doe (or UPI ID)
- User enters 6-digit UPI PIN manually (RBI compliant)
- PIN input features:
  - Auto-focus between fields
  - Paste support (6 digits)
  - Auto-submit when complete
  - Format validation

### 6. **PIN Verification**
- Frontend calls `/api/v1/upi/verify-pin` endpoint
- Backend validates PIN format (6 digits)
- **Note**: This is a mock implementation - in production, would verify against encrypted PIN storage

### 7. **Payment Processing**
After PIN verification:
- System calls `initiate_upi_payment` tool with:
  - Source account number
  - Destination account number (resolved from recipient)
  - Amount
  - Remarks
  - User ID
  - Session ID
- Tool generates UPI reference ID: `UPI-YYYYMMDD-HHMMSS`
- Uses existing `transfer_between_accounts` service with `channel=TransactionChannel.UPI`
- Creates debit and credit transactions
- Updates account balances

### 8. **Transaction Completion**
- Success response includes:
  - Transaction reference ID
  - Amount
  - Recipient name
  - Timestamp
- Transaction appears in user's transaction history
- Marked with UPI channel for tracking

## Key Features

### Multi-language Support
- **English**: "Hello Vaani, pay ₹500 to John"
- **Hindi**: "हेलो वाणी, UPI से जॉन को ₹500 भेजें"
- All UI elements and responses translated

### UPI ID Resolution
Users have predefined UPI IDs in seed data:
- Format: `{phone}@sunbank` or `{name}@sunbank`
- Example: `9876543210@sunbank` or `john.doe@sunbank`
- Stored in `users.upi_id` field

### Security & Compliance
- ✅ Manual PIN entry (not voice)
- ✅ User consent required
- ✅ Transaction verification
- ✅ RBI guideline compliance
- ✅ UPI reference ID generation
- ✅ Transaction channel tracking

### Error Handling
- Recipient not found → Error message
- Invalid PIN format → Validation error
- Insufficient balance → Transaction failure
- Network errors → Retry prompt

## Database Schema

### User Model
```python
upi_id = Column(String(100), nullable=True)  # Unique UPI ID
```

### Transaction Model
```python
channel = TransactionChannel.UPI  # Marked as UPI transaction
reference_id = "UPI-20250120-143022"  # UPI reference format
```

## API Endpoints

### POST `/api/v1/upi/verify-pin`
- **Request**: `{ pin: "123456", paymentDetails: {...} }`
- **Response**: `{ success: true, message: "UPI PIN verified successfully" }`
- **Note**: Mock implementation - validates format only

## Voice Commands Supported

1. **Wake-up + Payment**: "Hello Vaani, pay ₹500 to John"
2. **Direct Payment**: "Send ₹1000 via UPI to 9876543210@sunbank"
3. **With Account**: "Pay ₹2000 from account ending 41 to Arvind"
4. **With Remarks**: "UPI payment ₹500 to first beneficiary for rent"

## Quick Actions
- "Pay via UPI" button in chat sidebar
- Pre-filled command: "Hello Vaani, pay ₹500 to John via UPI"

## Testing Flow
1. Login to application
2. Navigate to Chat
3. Click "Pay via UPI" quick action OR say "Hello Vaani, pay ₹500 to John"
4. Accept consent (first time)
5. Enter 6-digit PIN
6. Verify transaction in transaction history

## Mock Implementation Notes
- All transactions use internal transfer system
- UPI IDs are predefined in seed data
- PIN validation is format-only (not actual encryption)
- No actual NPCI integration
- Transactions marked with UPI channel for tracking

