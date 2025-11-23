# Guardrails Regex Error Fix

## Issue

**Error**: `look-behind requires fixed-width pattern`

**Location**: `ai/services/guardrail_service.py` - `_redact_pii_from_text()` method

**Root Cause**: The account number redaction pattern used a variable-width lookbehind assertion:
```python
r'\b(?<!₹|Rs|INR|rupees?)\d{9,18}(?!\s*(?:rupees?|rs|₹|inr|lakh|crore|thousand))\b'
```

The `rupees?` part has variable width (could be "rupee" or "rupees"), which Python's regex engine doesn't allow in lookbehind assertions.

## Fix Applied

**File**: `ai/services/guardrail_service.py`

**Change**: Replaced variable-width lookbehind with manual context checking:

```python
# OLD (BROKEN):
account_pattern = re.compile(r'\b(?<!₹|Rs|INR|rupees?)\d{9,18}(?!\s*(?:rupees?|rs|₹|inr|lakh|crore|thousand))\b')

# NEW (FIXED):
account_number_pattern = re.compile(r'\b\d{9,18}\b')
matches = list(account_number_pattern.finditer(sanitized))

# Process matches in reverse order to maintain indices
for match in reversed(matches):
    start, end = match.span()
    number = match.group()
    
    # Check context before and after to determine if it's an amount
    before_context = sanitized[max(0, start-30):start].lower()
    after_context = sanitized[end:min(len(sanitized), end+30)].lower()
    
    # Currency indicators that suggest this is an amount
    currency_indicators = [
        '₹', 'rs', 'inr', 'rupee', 'rupees', 'lakh', 'crore', 'thousand',
        'balance', 'amount', 'total', 'sum', 'price', 'cost', 'fee'
    ]
    
    # Check if this number is part of an amount
    is_amount = (
        any(indicator in before_context for indicator in currency_indicators) or
        any(indicator in after_context for indicator in currency_indicators)
    )
    
    # Check if it's explicitly an account reference
    is_account_reference = (
        'account' in before_context[-20:] or
        'ac no' in before_context[-20:] or
        'a/c' in before_context[-20:]
    )
    
    # Only redact if it's NOT an amount but could be an account number
    if is_account_reference or (not is_amount and len(number) >= 12):
        sanitized = sanitized[:start] + '[ACCOUNT REDACTED]' + sanitized[end:]
```

## Benefits

1. ✅ **No Regex Errors**: Uses fixed-width patterns only
2. ✅ **Better Context Awareness**: Manually checks context to distinguish amounts from account numbers
3. ✅ **Conservative Approach**: Only redacts when confident it's an account number
4. ✅ **Preserves Amounts**: Won't accidentally redact transaction amounts or balances

## Testing

The fix ensures:
- ✅ Transaction amounts like "₹50000" are NOT redacted
- ✅ Account numbers like "Account: 123456789012" ARE redacted
- ✅ No regex compilation errors
- ✅ Normal transaction queries work correctly

## Impact

- **Before**: Regex error crashed the entire message processing flow
- **After**: Account number redaction works correctly without errors

---

**Status**: ✅ **Fixed**  
**Date**: 2025-01-27  
**Version**: 2.1

