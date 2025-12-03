# Guardrails Implementation Guide

## Overview

The Vaani AI chat agent now includes comprehensive guardrails for both Hindi and English languages, implemented using **only open-source, free tools** with no external API dependencies.

## Implementation Status

✅ **Fully Implemented** - All guardrails are active and integrated into the chat endpoint.

## Features

### 1. Input Guardrails (Pre-Processing)

- ✅ **Content Moderation**: Detects toxic/harmful content in both Hindi and English
- ✅ **PII Detection**: Identifies sensitive information (Aadhaar, PAN, account numbers, PINs, CVV)
- ✅ **Prompt Injection Detection**: Prevents attempts to override system instructions
- ✅ **Rate Limiting**: Prevents abuse with per-user limits (30/min, 500/hour)

### 2. Output Guardrails (Post-Processing)

- ✅ **Language Consistency**: Verifies response matches requested language
- ✅ **Response Safety**: Checks AI output for toxic content
- ✅ **PII Leakage Prevention**: Detects accidental PII in responses

## Architecture

```
User Input → Input Guardrails → Agent Processing → Output Guardrails → Response
                ↓                        ↓                ↓
         [Moderation]            [Processing]      [Safety Check]
         [PII Detection]         [LLM Call]        [Language Check]
         [Injection Check]                        [PII Check]
         [Rate Limit]
```

## Files

### Core Implementation

- **`ai/services/guardrail_service.py`**: Main guardrail service implementation
- **`ai/main.py`**: Integration into chat endpoint
- **`ai/config.py`**: Configuration settings

### Testing

- **`ai/test_guardrails.py`**: Test script for guardrail functionality

## Configuration

### Environment Variables

Add to `.env` file (optional, defaults provided):

```bash
# Guardrail Settings
ENABLE_INPUT_GUARDRAILS=true
ENABLE_OUTPUT_GUARDRAILS=true
GUARDRAIL_RATE_LIMIT_PER_MINUTE=30
GUARDRAIL_RATE_LIMIT_PER_HOUR=500
GUARDRAIL_MAX_LANGUAGE_MIXING_RATIO=0.3
```

### Code Configuration

Settings are in `ai/config.py`:

```python
# Guardrail Settings
enable_input_guardrails: bool = True
enable_output_guardrails: bool = True
guardrail_rate_limit_per_minute: int = 30
guardrail_rate_limit_per_hour: int = 500
guardrail_max_language_mixing_ratio: float = 0.3  # 30% mixing allowed
```

## Usage

### Automatic Integration

Guardrails are automatically applied to all chat requests via `/api/chat` endpoint. No additional code needed.

### Manual Usage

```python
from services import get_guardrail_service

guardrail = get_guardrail_service()

# Check input
result = await guardrail.check_input(
    message="User message",
    language="en-IN",
    user_id="user123"
)

if not result.passed:
    print(f"Violation: {result.violation_type}")
    print(f"Message: {result.message}")

# Check output
result = await guardrail.check_output(
    response="AI response",
    language="en-IN"
)
```

## Detection Patterns

### Toxic Content

**English Keywords:**
- Profanity: "damn", "hell", "crap"
- Threats: "kill you", "hurt you", "attack you"
- Hate speech: "hate you", "stupid", "idiot"
- Harassment: "shut up", "be quiet"

**Hindi Keywords (Devanagari):**
- Profanity: "बकवास", "गंदा", "मूर्ख"
- Threats: "मार दूंगा", "हत्या", "नुकसान"
- Hate speech: "नफरत", "बेवकूफ", "गधा"
- Harassment: "चुप रहो", "बंद करो"

**Hindi Keywords (Romanized):**
- "bakwas", "ganda", "murkha", "maar dunga", "chup raho"

### PII Patterns

- **Aadhaar**: `XXXX XXXX XXXX` (12 digits, optionally space-separated)
- **PAN**: `ABCDE1234F` (5 letters + 4 digits + 1 letter)
- **Account Number**: 9-18 digits
- **CVV**: 3-4 digits (with "cvv" or "cvc" keyword)
- **PIN**: 4-6 digits (with "pin" or "password" keyword)
- **Phone**: 10 digits starting with 6-9
- **Card Number**: 16 digits (optionally space-separated)
- **IFSC**: `XXXX0XXXXXX` (4 letters + 0 + 6 alphanumeric)

### Prompt Injection Patterns

**English:**
- "ignore all previous instructions"
- "forget everything"
- "you are now..."
- "system:"
- "<|system|>"
- "override system"
- "pretend you are"

**Hindi (Devanagari):**
- "पिछले निर्देश को नजरअंदाज"
- "सब भूल जाओ"
- "अब तुम हो"

**Hindi (Romanized):**
- "pichle nirdesh ko nazarandaz"
- "sab bhool jao"
- "ab tum ho"

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

## Testing

### Run Test Script

```bash
cd ai
python test_guardrails.py
```

### Test Scenarios Covered

1. ✅ Normal messages (should pass)
2. ✅ Toxic content detection (English)
3. ✅ Toxic content detection (Hindi)
4. ✅ PII detection (Aadhaar, PAN, Account Number)
5. ✅ Prompt injection detection (English & Hindi)
6. ✅ Language consistency verification
7. ✅ Rate limiting

### Example Test Output

```
============================================================
Testing Guardrail Service
============================================================

1. Testing normal message...
   Result: PASSED

2. Testing toxic content (English)...
   Result: FAILED
   Violation: toxic_content, Message: Your message contains inappropriate content...

3. Testing PII detection (Aadhaar)...
   Result: FAILED
   Violation: pii_detected, Message: Please do not share sensitive information...
   Detected entities: ['1234 5678 9012']
```

## Performance

- **Latency Impact**: < 5ms per request (typical)
- **Memory Usage**: Minimal (in-memory rate limiting)
- **No External Dependencies**: All checks run locally

## Monitoring

### Logging

Guardrail violations are logged with structured logging:

```python
logger.warning("guardrail_violation_input",
             user_id=user_id,
             violation_type=violation_type,
             language=language,
             message_preview=message[:100])
```

### Metrics to Track

- Guardrail violations by type
- False positive rate
- Latency impact
- Rate limit hits

## Customization

### Adding Custom Keywords

Edit `ai/services/guardrail_service.py`:

```python
def _load_toxic_keywords_en(self) -> Set[str]:
    return {
        # Add your custom keywords
        "custom_profanity",
        ...
    }
```

### Adding Custom PII Patterns

```python
def _load_pii_patterns(self) -> Dict[str, re.Pattern]:
    return {
        ...
        "custom_pii": re.compile(r'your_pattern_here'),
    }
```

### Adjusting Rate Limits

Update `ai/config.py`:

```python
guardrail_rate_limit_per_minute: int = 50  # Increase limit
guardrail_rate_limit_per_hour: int = 1000
```

## Disabling Guardrails

### Temporarily Disable

Set in `.env`:

```bash
ENABLE_INPUT_GUARDRAILS=false
ENABLE_OUTPUT_GUARDRAILS=false
```

### Programmatically

```python
from services import get_guardrail_service

guardrail = get_guardrail_service()
guardrail.enable_input_guardrails = False
guardrail.enable_output_guardrails = False
```

## Limitations

1. **Keyword-Based Detection**: Uses pattern matching, not ML models
   - May have false positives/negatives
   - Can be improved with custom keyword lists

2. **In-Memory Rate Limiting**: Not distributed across multiple servers
   - Use Redis for distributed deployments

3. **Language Detection**: Basic script-based detection
   - May allow some code-switching (up to 30%)

## Future Enhancements

- [ ] ML-based toxicity detection (using open-source models)
- [ ] Distributed rate limiting (Redis)
- [ ] Custom training for domain-specific patterns
- [ ] Advanced language detection
- [ ] Conversation context analysis

## Troubleshooting

### Guardrails Not Working

1. Check configuration: `enable_input_guardrails` and `enable_output_guardrails`
2. Check logs for errors
3. Run test script: `python test_guardrails.py`

### False Positives

1. Review detected patterns in logs
2. Add exceptions to keyword lists
3. Adjust confidence thresholds

### Performance Issues

1. Check rate limiting settings
2. Monitor guardrail latency in logs
3. Consider disabling non-critical checks

## Support

For issues or questions:
1. Check logs: `logs/ai_backend.log`
2. Run test script: `python test_guardrails.py`
3. Review documentation: `documentation/other/ai_chat_guardrails_analysis.md`

---

**Last Updated**: 2025-01-27  
**Version**: 1.0  
**Status**: ✅ **Production Ready - Fully Implemented and Tested**

## Related Documentation

- **Analysis**: `documentation/other/ai_chat_guardrails_analysis.md` - Comprehensive analysis and implementation details
- **Quick Reference**: `documentation/other/guardrails_quick_reference.md` - Quick reference guide
- **Architecture**: `documentation/ai_architecture.md` - Includes guardrails in system architecture
- **Summary**: `documentation/other/GUARDRAILS_SUMMARY.md` - Implementation summary

