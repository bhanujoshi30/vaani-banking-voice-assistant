# Guardrails Language Change Fix

## Issue

When a user requests a language change (e.g., from English to Hindi), the guardrail was incorrectly flagging the response as a language mismatch violation.

**Scenario**:
1. User types in English: "I want to change the language"
2. Bot asks: "Which language would you like to use - Hindi or English?"
3. User responds: "hindi"
4. System correctly changes language to `hi-IN`
5. Bot generates Hindi response: "ठीक है! अब मैं हिंदी में बात करूंगी।"
6. **Problem**: Guardrail checks response against original request language (`en-IN`) instead of updated language (`hi-IN`)
7. **Result**: Language mismatch violation, response blocked

## Root Cause

The `check_output()` method was:
- Checking language consistency against the **original request language**
- Not aware of **language_change** intent
- Not using the **updated language** from the processing result

## Fix Applied

### 1. Updated `check_output()` Method

**File**: `ai/services/guardrail_service.py`

**Changes**:
- Added `intent` parameter to `check_output()` method
- Skip language consistency check when `intent == "language_change"`
- This allows language change responses to be in the new language without violation

```python
async def check_output(
    self,
    response: str,
    language: str = "en-IN",
    original_query: Optional[str] = None,
    intent: Optional[str] = None  # NEW: Intent parameter
) -> GuardrailResult:
    # Skip language consistency check for language_change intents
    if intent != "language_change":
        lang_check = self._check_language_consistency(response, language)
        # ... rest of check
```

### 2. Updated Main Endpoint

**File**: `ai/main.py`

**Changes**:
- Pass `intent` from result to `check_output()`
- Use **updated language** from result instead of original request language

```python
output_check = await guardrail_service.check_output(
    response=result.get("response", ""),
    language=result.get("language", request.language),  # Use updated language
    original_query=request.message,
    intent=result.get("intent")  # Pass intent
)
```

## Benefits

1. ✅ **Language Changes Work**: Users can successfully change language without guardrail blocking
2. ✅ **Correct Language Check**: Uses updated language from processing result
3. ✅ **Intent-Aware**: Guardrail knows when to skip language check
4. ✅ **Backward Compatible**: Other intents still get language consistency check

## Testing

**Test Case**: Language Change
1. User: "I want to change the language" (English)
2. Bot: "Which language would you like to use - Hindi or English?"
3. User: "hindi" (English word, but requesting Hindi)
4. **Expected**: Bot responds in Hindi without guardrail violation
5. **Result**: ✅ Language change works correctly

## Flow After Fix

```
User Request (en-IN) → Language Change Intent Detected
  ↓
Language Changed: en-IN → hi-IN
  ↓
Response Generated in Hindi
  ↓
Guardrail Check:
  - Intent = "language_change" → Skip language consistency check ✅
  - Check other guardrails (toxicity, PII) ✅
  ↓
Response Sent Successfully
```

---

**Status**: ✅ **Fixed**  
**Date**: 2025-01-27  
**Version**: 2.2

