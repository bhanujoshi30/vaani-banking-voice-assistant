# Guardrails Non-Banking Investments & Shopping Fix

## Requirement

Any query that is off-topic from banking operations or banking related to Sun National Bank should be handled with proper guardrail. Specifically:
- **Non-banking investments**: "investment in bitcoin", "investment in air purifier", "invest in crypto"
- **Shopping/e-commerce**: "shopping at Amazon", "buy from Amazon"
- These should be caught by the guardrail and redirected to banking questions

## Implementation

### Enhanced Off-Topic Detection

**File**: `ai/services/guardrail_service.py`

**Changes**:

1. **Added Non-Banking Investment Keywords**:
   ```python
   non_banking_investment_keywords = [
       "bitcoin", "btc", "crypto", "cryptocurrency", "ethereum", "eth",
       "trading", "stock market", "stocks", "shares", "share market",
       "nft", "blockchain", "defi", "altcoin", "dogecoin", "shiba",
       "forex", "forex trading", "commodity", "commodities",
       "air purifier", "amazon", "shopping", "online shopping", "e-commerce",
       "buy", "purchase", "shop", "shopping at", "buy from",
       "investment in bitcoin", "investment in crypto", "investment in air purifier",
       "invest in bitcoin", "invest in crypto", "invest in air purifier",
   ]
   ```

2. **Added Investment/Shopping Pattern Matching**:
   ```python
   investment_shopping_patterns = [
       r"investment\s+in\s+\w+",  # "investment in bitcoin", "investment in air purifier"
       r"invest\s+in\s+\w+",  # "invest in crypto", "invest in stocks"
       r"shopping\s+at\s+\w+",  # "shopping at Amazon", "shopping at Flipkart"
       r"buy\s+(from|on|at)\s+\w+",  # "buy from Amazon", "buy on Amazon"
       r"purchase\s+(from|on|at)\s+\w+",  # "purchase from Amazon"
   ]
   ```

3. **Smart Banking Keyword Check**:
   - Checks for banking keywords FIRST
   - If banking keywords present → Allow (e.g., "buy mutual fund", "investment plan")
   - If non-banking investment keywords present AND no banking keywords → Block

4. **Updated Banking Keywords**:
   - Added context-specific keywords: "banking investment", "bank investment", "bank scheme", "bank plan"
   - Removed standalone "investment" from banking keywords (now context-dependent)

## Logic Flow

```
Query Received
  ↓
Check for Banking Keywords
  ├─ If found → ALLOW (e.g., "buy mutual fund", "investment plan")
  └─ If not found → Continue
  ↓
Check for Non-Banking Investment Keywords
  ├─ If found → BLOCK (e.g., "investment in bitcoin", "shopping at Amazon")
  └─ If not found → Continue
  ↓
Check Investment/Shopping Patterns
  ├─ If matches pattern AND no banking keywords → BLOCK
  └─ If matches pattern AND has banking keywords → ALLOW
  ↓
Continue with other off-topic checks
```

## Test Cases

| Query | Expected | Result |
|-------|----------|--------|
| "investment in bitcoin" | BLOCK | ✅ |
| "investment in air purifier" | BLOCK | ✅ |
| "shopping at Amazon" | BLOCK | ✅ |
| "buy mutual fund" | ALLOW | ✅ (has banking keyword) |
| "investment plan" | ALLOW | ✅ (has banking keyword) |
| "invest in crypto" | BLOCK | ✅ |
| "buy from Amazon" | BLOCK | ✅ |
| "what is PPF investment" | ALLOW | ✅ (has banking keyword) |

## Benefits

1. ✅ **Comprehensive Detection**: Catches cryptocurrency, stocks, shopping, and non-banking investments
2. ✅ **Context-Aware**: Distinguishes between banking investments ("buy mutual fund") and non-banking ("investment in bitcoin")
3. ✅ **Pattern-Based**: Uses regex patterns to catch various phrasings
4. ✅ **No False Positives**: Banking-related queries are never blocked
5. ✅ **Consistent Messaging**: All off-topic queries get the same redirect message

## Response Message

**English**: "I am a banking agent. Please ask questions related to banking at Sun National Bank."

**Hindi**: "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"

---

**Status**: ✅ **Implemented**  
**Date**: 2025-01-27  
**Version**: 2.5

