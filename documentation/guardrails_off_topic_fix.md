# Guardrails Off-Topic Detection Enhancement

## Issue

When users asked off-topic questions (like "what does an airplane do"), the AI was responding with general knowledge answers instead of redirecting them to banking-related questions.

**User Requirement**: For questions outside of banking, the response should be:
- **English**: "I am a banking agent. Please ask questions related to banking at Sun National Bank."
- **Hindi**: "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"

## Root Cause

1. **Limited Off-Topic Keywords**: The guardrail only checked for specific topics (politics, religion, coding, illegal acts) but missed general knowledge questions
2. **No Pattern Matching**: Questions like "what does an airplane do" weren't caught
3. **Generic Refusal Message**: The supervisor used a generic message instead of the specific guardrail message

## Fix Applied

### 1. Enhanced Off-Topic Detection

**File**: `ai/services/guardrail_service.py`

**Changes**:
- **Expanded Keywords**: Added general knowledge topics:
  - Airplanes, aircraft, flights
  - Weather, temperature, rain
  - Sports (cricket, football, etc.)
  - Movies, films, actors
  - Recipes, cooking, food
  - Science, physics, chemistry, math
  - History, geography
  - Animals, wildlife
  - Vehicles, cars, bikes
  - Question patterns: "what does a", "what is a", "how does", "tell me about"

- **Banking Keyword Check**: Added positive check for banking keywords to avoid false positives
  - If query contains banking terms (account, balance, loan, etc.), allow it even if it matches some patterns

- **Pattern Matching**: Added regex patterns to catch general knowledge questions:
  ```python
  general_knowledge_patterns = [
      r"what\s+(does|is|are|was|were)\s+(a|an|the)?\s*\w+",
      r"how\s+(does|do|is|are|was|were)\s+(a|an|the)?\s*\w+",
      r"why\s+(is|are|was|were|does|do)\s+(a|an|the)?\s*\w+",
      r"tell\s+me\s+about\s+(a|an|the)?\s*\w+",
      r"explain\s+(a|an|the)?\s*\w+",
  ]
  ```

- **Updated Message**: Changed refusal message to match user requirement:
  - English: "I am a banking agent. Please ask questions related to banking at Sun National Bank."
  - Hindi: "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"

### 2. Updated validate_input() Return Value

**File**: `ai/services/guardrail_service.py`

**Changes**:
- Changed return type from `bool` to `Tuple[bool, Optional[str]]`
- Returns `(True, None)` if valid
- Returns `(False, refusal_message)` if blocked, with specific message from guardrail

### 3. Updated Supervisor to Use Guardrail Message

**File**: `ai/orchestrator/supervisor.py`

**Changes**:
- Updated to unpack tuple from `validate_input()`
- Uses guardrail's specific message instead of generic refusal
- Falls back to default message if guardrail doesn't provide one

## Example Scenarios

### Before Fix:
```
User: "what does an airplane do"
AI: "मैं आपकी मदद कर सकती हूँ। विमान का प्रमुख कार्य लोगों को अन्य जगहों से इस्तेमाल करने के लिए चालक दूरी में यात्रा करना होता है..."
```

### After Fix:
```
User: "what does an airplane do"
AI: "I am a banking agent. Please ask questions related to banking at Sun National Bank."
```

## Testing

**Test Cases**:
1. ✅ "what does an airplane do" → Blocked with banking redirect
2. ✅ "tell me about weather" → Blocked with banking redirect
3. ✅ "how does a car work" → Blocked with banking redirect
4. ✅ "what is my account balance" → Allowed (contains banking keyword)
5. ✅ "tell me about home loan" → Allowed (contains banking keyword)

## Benefits

1. ✅ **Comprehensive Detection**: Catches general knowledge questions, not just specific topics
2. ✅ **Pattern-Based**: Uses regex patterns to catch question formats
3. ✅ **Banking-Aware**: Checks for banking keywords to avoid false positives
4. ✅ **Consistent Messaging**: Uses standardized message across all off-topic queries
5. ✅ **User-Friendly**: Clear, professional redirect message

---

**Status**: ✅ **Fixed**  
**Date**: 2025-01-27  
**Version**: 2.3

