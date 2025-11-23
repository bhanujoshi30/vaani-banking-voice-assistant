# Guardrails Quick Reference Guide

## Overview

This is a quick reference for the **fully implemented** guardrails in the Vaani AI chat agent for both Hindi and English languages.

**Status**: ✅ **Production Ready** - All guardrails are active and tested.

## Key Guardrail Categories

### 1. Input Guardrails (Pre-Processing)

**Purpose**: Validate and sanitize user input before processing

**Checks**:
- ✅ Content Moderation (toxic/harmful content)
- ✅ PII Detection (Aadhaar, PAN, account numbers, PINs)
- ✅ Prompt Injection Detection
- ✅ Rate Limiting
- ✅ Intent Validation

**Implementation Location**: `ai/services/guardrail_service.py`

### 2. Output Guardrails (Post-Processing)

**Purpose**: Validate AI-generated responses before sending to user

**Checks**:
- ✅ Language Consistency (matches requested language)
- ✅ Response Safety (no toxic content in output)
- ✅ Fact Verification (financial data accuracy)
- ✅ Response Quality (not generic/unhelpful)

**Implementation Location**: `ai/services/guardrail_service.py`

## Common Patterns

### Toxic Content Patterns (English)

```
- Profanity, hate speech, threats
- Personal attacks, harassment
- Discriminatory language
```

### Toxic Content Patterns (Hindi)

```
- अपमानजनक भाषा (Abusive language)
- धमकी (Threats)
- भेदभावपूर्ण भाषा (Discriminatory language)
```

### PII Patterns (Indian Context)

```
- Aadhaar: XXXX XXXX XXXX (12 digits, space-separated)
- PAN: ABCDE1234F (5 letters + 4 digits + 1 letter)
- Account Number: 9-18 digits
- CVV: 3-4 digits
- PIN: 4-6 digits
- Phone: 10 digits starting with 6-9
```

### Prompt Injection Patterns

**English**:
- "Ignore all previous instructions"
- "Forget everything"
- "You are now..."
- "System: ..."
- "<|system|>"

**Hindi**:
- "पिछले निर्देश नजरअंदाज करो"
- "सब भूल जाओ"
- "अब तुम..."

## Integration Points

### 1. Main Entry Point

**File**: `ai/main.py`

```python
# Before processing
input_check = await guardrail_service.check_input(
    message=request.message,
    language=request.language,
    user_id=request.user_id
)

# After processing
output_check = await guardrail_service.check_output(
    response=result.get("response", ""),
    language=request.language,
    original_query=request.message
)
```

### 2. Agent System Prompts

**Files**: `ai/agents/*.py`

Add safety rules to system prompts:

```python
system_prompt = f"""
SAFETY RULES:
- Never share sensitive information
- Stay within banking domain
- Always respond in {language} only
"""
```

## Error Messages

### English

- **Toxic Content**: "Your message contains inappropriate content. Please rephrase."
- **PII Detected**: "Please do not share sensitive information like Aadhaar, PAN, or account numbers in chat."
- **Prompt Injection**: "Your request could not be processed. Please rephrase your question."
- **Rate Limit**: "Too many requests. Please wait a moment and try again."

### Hindi

- **Toxic Content**: "आपके संदेश में अनुचित सामग्री है। कृपया अपना प्रश्न दोबारा बताएं।"
- **PII Detected**: "कृपया चैट में आधार, PAN, या खाता संख्या जैसी संवेदनशील जानकारी साझा न करें।"
- **Prompt Injection**: "आपका अनुरोध संसाधित नहीं किया जा सका। कृपया अपना प्रश्न दोबारा बताएं।"
- **Rate Limit**: "बहुत सारे अनुरोध। कृपया एक क्षण प्रतीक्षा करें और पुनः प्रयास करें।"

## Configuration

**File**: `ai/config.py`

```python
class GuardrailSettings:
    ENABLE_INPUT_GUARDRAILS = True
    ENABLE_OUTPUT_GUARDRAILS = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 30
    RATE_LIMIT_REQUESTS_PER_HOUR = 500
    REDACT_PII = True
    MAX_LANGUAGE_MIXING_RATIO = 0.3
```

## Testing Checklist

- [x] Toxic content blocked (English) ✅
- [x] Toxic content blocked (Hindi) ✅
- [x] PII detected and blocked ✅
- [x] Prompt injection detected ✅
- [x] Language consistency verified ✅
- [x] Rate limiting works ✅
- [x] Error messages in correct language ✅
- [x] Performance impact acceptable (<5ms) ✅

**All tests passing** - See `ai/test_guardrails.py` for test results.

## Monitoring

**Key Metrics**:
- Guardrail violations by type
- False positive rate
- Latency impact
- Coverage percentage

**Logging**:
```python
logger.info("guardrail_check",
           check_type="input",
           passed=True,
           violation_type=None,
           latency_ms=5.2)
```

## External Tools (Optional)

1. **Azure Content Moderator** - Enterprise-grade moderation
2. **Perspective API** - Google's toxicity detection
3. **Microsoft Presidio** - PII detection
4. **PolyGuard** - Multilingual safety (research)

## Priority Order

1. **High**: Input moderation, PII detection, prompt injection
2. **Medium**: Rate limiting, output safety, fact verification
3. **Low**: Advanced ML models, custom training

---

**Quick Start**: See `ai_chat_guardrails_analysis.md` for detailed implementation guide.

