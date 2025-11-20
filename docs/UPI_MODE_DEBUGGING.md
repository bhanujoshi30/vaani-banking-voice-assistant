# UPI Mode Routing Debugging Guide

## Issue
When UPI mode is active, balance queries are still routing to normal banking flow instead of UPI balance check flow.

## Test Cases

### Test Case 1: UPI Mode Active + Balance Query
**Expected Behavior:**
- Frontend sends `upi_mode: true` in request
- Backend receives it and sets `upi_mode: true` in state
- Intent classifier detects `upi_mode: true` and `has_balance_keyword: true`
- Routes to `upi_payment` intent (UPI agent)
- UPI agent handles balance check with account selection → PIN → Balance

**How to Test:**
1. Activate UPI mode in frontend (click "UPI Mode Inactive" button)
2. Send message: "Mera account balance kitna hai"
3. Check backend logs for:
   - `chat_request` with `upi_mode: true`
   - `using_upi_mode_from_frontend` with `upi_mode: true`
   - `initial_state_created` with `upi_mode: true`
   - `intent_classifier_upi_mode_check` with `upi_mode_active: true`
   - `upi_balance_check_routed` with `intent: upi_payment`

### Test Case 2: UPI Mode Inactive + Balance Query
**Expected Behavior:**
- Frontend sends `upi_mode: false` (or omits it)
- Backend sets `upi_mode: false` in state
- Intent classifier detects `upi_mode: false` and `has_balance_keyword: true`
- Routes to `banking_operation` intent (Banking agent)
- Banking agent shows normal balance

**How to Test:**
1. Ensure UPI mode is inactive in frontend
2. Send message: "Mera account balance kitna hai"
3. Check backend logs for:
   - `chat_request` with `upi_mode: false` (or None)
   - `initial_state_created` with `upi_mode: false`
   - `intent_classifier_upi_mode_check` with `upi_mode_active: false`
   - `normal_balance_check_routed` with `intent: banking_operation`

## Debugging Steps

### Step 1: Check Frontend is Sending UPI Mode
**Location:** `frontend/src/api/aiClient.js`

Check that `sendChatMessage` includes `upi_mode`:
```javascript
body: JSON.stringify({
  message,
  user_id: userId,
  session_id: sessionId,
  language,
  user_context: userContext,
  message_history: messageHistory,
  voice_mode: voiceMode,
  upi_mode: upiMode,  // ← Should be included
}),
```

**How to Verify:**
1. Open browser DevTools → Network tab
2. Send a message with UPI mode active
3. Check the POST request to `/api/chat`
4. Verify `upi_mode: true` is in the request body

### Step 2: Check Backend Receives UPI Mode
**Location:** `ai/main.py`

Check that `ChatRequest` includes `upi_mode` and it's passed to `process_message`:
```python
class ChatRequest(BaseModel):
    upi_mode: Optional[bool] = Field(default=None, description="Whether UPI mode is active")

# In chat endpoint:
result = await process_message(
    ...
    upi_mode=request.upi_mode  # ← Should be passed
)
```

**How to Verify:**
1. Check backend logs for `chat_request` entry
2. Verify `upi_mode` value is logged

### Step 3: Check State Initialization
**Location:** `ai/agents/agent_graph.py`

Check that `upi_mode` from frontend is used to set initial state:
```python
if upi_mode is not None:
    upi_mode_active = upi_mode
    logger.info("using_upi_mode_from_frontend", upi_mode=upi_mode)

initial_state = AgentState(
    ...
    upi_mode=upi_mode_active,  # ← Should be set correctly
)
```

**How to Verify:**
1. Check backend logs for `using_upi_mode_from_frontend` or `upi_mode_not_provided_from_frontend`
2. Check `initial_state_created` log entry
3. Verify `upi_mode` value matches what was sent from frontend

### Step 4: Check Intent Classifier
**Location:** `ai/agents/intent_classifier.py`

Check that intent classifier reads `upi_mode` from state and routes correctly:
```python
upi_mode_active = state.get("upi_mode", False)

# When UPI mode is active and balance keyword detected:
if upi_mode_active:
    if has_balance_keyword:
        intent = "upi_payment"  # ← Should route to UPI agent
        return state
```

**How to Verify:**
1. Check backend logs for `intent_classifier_upi_mode_check`
2. Verify `upi_mode_active: true` when UPI mode is active
3. Check for `upi_balance_check_routed` log entry
4. Verify `intent: upi_payment` in the log

## Common Issues

### Issue 1: Frontend Not Sending UPI Mode
**Symptom:** Backend logs show `upi_mode: None` or `upi_mode_not_provided_from_frontend`

**Fix:**
1. Check `frontend/src/pages/Chat.jsx` - ensure `upiMode` is passed to `useChatHandler`
2. Check `frontend/src/hooks/useChatHandler.js` - ensure `upiMode` is passed to `sendChatMessage`
3. Check `frontend/src/api/aiClient.js` - ensure `upiMode` is included in request body

### Issue 2: Backend Not Receiving UPI Mode
**Symptom:** Backend logs show `chat_request` without `upi_mode` field

**Fix:**
1. Check `ai/main.py` - ensure `ChatRequest` model includes `upi_mode` field
2. Check that `request.upi_mode` is passed to `process_message`

### Issue 3: State Not Set Correctly
**Symptom:** Backend logs show `initial_state_created` with `upi_mode: false` even when frontend sent `true`

**Fix:**
1. Check `ai/agents/agent_graph.py` - ensure `upi_mode` parameter is used correctly
2. Verify the logic: `if upi_mode is not None: upi_mode_active = upi_mode`

### Issue 4: Intent Classifier Not Reading State
**Symptom:** Backend logs show `intent_classifier_upi_mode_check` with `upi_mode_active: false` even when state has `upi_mode: true`

**Fix:**
1. Check that state is passed correctly through the graph
2. Verify `state.get("upi_mode", False)` is reading the correct value

### Issue 5: Routing Logic Not Working
**Symptom:** Backend logs show correct `upi_mode_active: true` but intent is still `banking_operation`

**Fix:**
1. Check `ai/agents/intent_classifier.py` - verify the routing logic:
   ```python
   if upi_mode_active:
       if has_balance_keyword:
           intent = "upi_payment"
           return state  # ← Should return early
   ```
2. Check that `has_balance_keyword` is detecting the balance query correctly

## Logging Checklist

When testing, check for these log entries in order:

1. ✅ `chat_request` - Should show `upi_mode: true/false`
2. ✅ `using_upi_mode_from_frontend` - Should show `upi_mode: true` when active
3. ✅ `initial_state_created` - Should show `upi_mode: true` when active
4. ✅ `intent_classifier_upi_mode_check` - Should show `upi_mode_active: true` when active
5. ✅ `upi_mode_active_detected` - Should appear when UPI mode is active
6. ✅ `upi_balance_check_routed` - Should appear with `intent: upi_payment` when balance query in UPI mode

## Quick Test Script

To test manually, you can use curl:

```bash
# Test with UPI mode active
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mera account balance kitna hai",
    "user_id": "test-user",
    "session_id": "test-session",
    "language": "hi-IN",
    "upi_mode": true
  }'

# Test with UPI mode inactive
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mera account balance kitna hai",
    "user_id": "test-user",
    "session_id": "test-session",
    "language": "hi-IN",
    "upi_mode": false
  }'
```

Check the response - when `upi_mode: true`, the `intent` should be `upi_payment`. When `upi_mode: false`, the `intent` should be `banking_operation`.

