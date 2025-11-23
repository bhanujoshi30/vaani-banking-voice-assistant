# Investment and Loan Cards Missing Data Fix

## Issues Identified

1. **ELSS Blocked**: "Tell me about elss" was being blocked by guardrail as off-topic
2. **Missing Card Data**: Investment and loan cards showing "missing data" (empty Interest Rate, Loan Amount fields)

## Root Causes

### Issue 1: ELSS Blocked
- "elss" was not in the `banking_keywords` list
- "tell me about" pattern was matching before checking if it's a banking product
- Guardrail was blocking legitimate banking queries

### Issue 2: Missing Card Data
- LLM extraction might return empty/null values for some fields
- No validation to ensure critical fields (name, interest_rate) are present
- If extraction fails partially, incomplete data was being used instead of triggering fallback

## Fixes Applied

### 1. Enhanced Banking Keywords

**File**: `ai/services/guardrail_service.py`

**Changes**:
- Added investment scheme abbreviations: "elss", "equity linked", "sukanya", "ssy", "nsc"
- Added full names: "fixed deposit", "recurring deposit", "public provident fund", "national pension"
- Added loan types: "auto loan", "home loan", "personal loan", "business loan", "education loan", "gold loan", "loan against property", "lap"
- Added Hindi equivalents: "ईएलएसएस", "सुकन्या", "एनएससी", "होम लोन", "पर्सनल लोन", "ऑटो लोन"

```python
banking_keywords = [
    # ... existing keywords ...
    # Investment schemes
    "elss", "equity linked", "equity linked savings", "sukanya", "ssy", "nsc",
    "fixed deposit", "recurring deposit", "public provident fund",
    "national pension", "tax saving", "tax-saving",
    # Loan types
    "home loan", "personal loan", "auto loan", "car loan", "business loan",
    "education loan", "gold loan", "loan against property", "lap",
    # Hindi equivalents
    "ईएलएसएस", "सुकन्या", "एनएससी", "होम लोन", "पर्सनल लोन", "ऑटो लोन",
]
```

### 2. Enhanced Extraction Validation

**Files**: 
- `ai/agents/rag_agents/loan_agent.py`
- `ai/agents/rag_agents/investment_agent.py`

**Changes**:
- Remove empty/null values before processing
- Validate critical fields (name, interest_rate) are present
- Return None to trigger fallback if critical fields are missing

```python
# Remove empty/null values to avoid missing data in cards
loan_info = {k: v for k, v in loan_info.items() if v is not None and v != "" and v != []}

# Ensure critical fields are present
critical_fields = ["name", "interest_rate"]
missing_critical = [field for field in critical_fields if not loan_info.get(field)]
if missing_critical:
    logger.warning("loan_extraction_missing_critical_fields", ...)
    return None  # Trigger fallback
```

## Flow After Fix

```
User: "Tell me about elss"
  ↓
Guardrail: Check banking keywords
  ├─ "elss" found in banking_keywords ✅
  └─ Allow query
  ↓
RAG Agent: Detect investment type
  ├─ Detect "elss"
  └─ Extract investment card
  ↓
Extraction: Validate critical fields
  ├─ If name and interest_rate present → Use extracted data ✅
  └─ If missing → Return None → Trigger fallback ✅
  ↓
Fallback: Use fallback data with complete fields
  ├─ All fields populated ✅
  └─ Card shows complete data ✅
```

## Test Cases

| Query | Before | After |
|-------|--------|-------|
| "Tell me about elss" | Blocked ❌ | Allowed ✅ |
| "Tell me about rd" | Allowed ✅ | Allowed ✅ |
| "Tell me about auto loan" | Allowed ✅ | Allowed ✅ |
| Card with missing data | Empty fields ❌ | Fallback with complete data ✅ |

## Benefits

1. ✅ **No False Blocks**: Banking products like ELSS, RD, FD are recognized
2. ✅ **Complete Cards**: Missing data triggers fallback with complete information
3. ✅ **Better Validation**: Critical fields are checked before using extracted data
4. ✅ **Improved UX**: Users see complete card information, not empty fields

---

**Status**: ✅ **Fixed**  
**Date**: 2025-01-27  
**Version**: 2.8

