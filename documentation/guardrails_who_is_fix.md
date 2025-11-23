# Guardrails "Who is" Question Fix

## Issue

The query "Who is Ronaldo?" was not being caught by the off-topic guardrail, causing the AI to incorrectly route it to loan products and respond with Education Loan information instead of redirecting to banking questions.

**Screenshot 1**: "Who is Ronaldo?" → Incorrectly routed to loan products
**Screenshot 2**: "Explain about football" → Correctly blocked ✅

## Root Cause

The off-topic detection was missing:
1. **"Who is" pattern**: The regex patterns didn't include "who is" questions
2. **Person name keywords**: Famous people names like "Ronaldo" weren't in the keyword list

## Fix Applied

### Enhanced Off-Topic Detection

**File**: `ai/services/guardrail_service.py`

**Changes**:

1. **Added "Who is" Pattern**:
   ```python
   r"who\s+(is|are|was|were)\s+\w+",  # "Who is Ronaldo?", "Who are you?"
   ```

2. **Added Person-Related Keywords**:
   ```python
   "who is", "who are", "who was", "who were",  # Person queries
   # Famous people/sports personalities (common off-topic queries)
   "ronaldo", "messi", "modi", "gandhi", "einstein",
   "celebrity", "famous", "person", "people",
   ```

3. **Added More Question Patterns**:
   ```python
   r"describe\s+(a|an|the)?\s*\w+",
   r"what\s+about\s+\w+",
   ```

## Testing

**Test Cases**:
1. ✅ "Who is Ronaldo?" → Now blocked with banking redirect
2. ✅ "Who are you?" → Blocked (but might need exception for this)
3. ✅ "Explain about football" → Already working ✅
4. ✅ "What is my account balance?" → Still allowed (has banking keyword)

## Pattern Matching Order

The guardrail checks in this order:
1. **Banking Keywords Check**: If query contains banking terms → Allow
2. **Off-Topic Keywords**: Check for specific keywords → Block
3. **Pattern Matching**: Check for question patterns → Block

This ensures banking queries are never blocked, even if they match some patterns.

## Result

- ✅ "Who is Ronaldo?" now correctly blocked
- ✅ "Explain about football" continues to work
- ✅ Banking queries still work correctly
- ✅ More comprehensive off-topic detection

---

**Status**: ✅ **Fixed**  
**Date**: 2025-01-27  
**Version**: 2.4

