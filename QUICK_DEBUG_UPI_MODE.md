# Quick Debug: UPI Mode Routing Issue

## Issue
When UPI mode is active, balance queries are routing to normal banking flow instead of UPI balance check flow.

## Debugging Steps

### Step 1: Check Frontend Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Activate UPI mode (click "UPI Mode Inactive" button)
4. Send message: "Mera account balance kitna hai"
5. Look for these console logs:
   - `🔍 Chat.jsx - Current UPI mode state: true` ← Should be `true`
   - `🔍 Sending message with UPI mode: {upiMode: true, ...}` ← Should show `upiMode: true`

**If `upiMode` is `false` here:**
- The UPI mode state is not being set correctly when you click the button
- Check if consent was given (UPI mode only activates after consent)

### Step 2: Check Network Request
1. Open DevTools → Network tab
2. Send the balance query with UPI mode active
3. Find the POST request to `/api/chat`
4. Click on it → Payload tab
5. Verify `upi_mode: true` is in the request body

**If `upi_mode` is `false` or missing:**
- Frontend is not sending the UPI mode correctly
- Check `frontend/src/hooks/useChatHandler.js` line 91

### Step 3: Check Backend Logs
Check the backend terminal/logs for these entries (in order):

1. `chat_request` - Should show `upi_mode: true`
2. `using_upi_mode_from_frontend` - Should show `upi_mode: true`
3. `initial_state_created` - Should show `upi_mode: true`
4. `intent_classifier_upi_mode_check` - Should show `upi_mode_active: true`
5. `balance_keyword_detected` - Should show matched keywords
6. `upi_mode_active_detected` - Should appear
7. `upi_balance_check_routed` - Should show `intent: upi_payment`

**If any step shows `false` or is missing:**
- That's where the issue is occurring

## Common Issues

### Issue 1: UPI Mode Not Activating
**Symptom:** Console shows `upiMode: false` even after clicking button

**Cause:** Consent not given - UPI mode only activates after user accepts consent

**Fix:** Click "UPI Mode Inactive" → Accept consent → Then UPI mode activates

### Issue 2: Frontend Not Sending UPI Mode
**Symptom:** Network request shows `upi_mode: false` or missing

**Check:**
- `frontend/src/pages/Chat.jsx` line 120 - `upiMode` is passed to `useChatHandler`
- `frontend/src/hooks/useChatHandler.js` line 91 - `upiMode: upiMode` is passed to `sendChatMessage`
- `frontend/src/api/aiClient.js` line 44 - `upi_mode: upiMode` is in request body

### Issue 3: Backend Not Receiving UPI Mode
**Symptom:** Backend logs show `upi_mode: None` or `upi_mode_not_provided_from_frontend`

**Check:**
- `ai/main.py` line 46 - `ChatRequest` has `upi_mode` field
- `ai/main.py` line 208 - `request.upi_mode` is passed to `process_message`

### Issue 4: State Not Set Correctly
**Symptom:** Backend logs show `initial_state_created` with `upi_mode: false`

**Check:**
- `ai/agents/agent_graph.py` line 120-122 - `upi_mode` parameter is used correctly

### Issue 5: Intent Classifier Not Routing
**Symptom:** Backend logs show `upi_mode_active: true` but intent is `banking_operation`

**Check:**
- `ai/agents/intent_classifier.py` line 112-136 - Routing logic for UPI mode active + balance keyword

## Test Message
Use this exact message to test:
```
Mera account balance kitna hai
```

This should match:
- `"mera account balance"` keyword
- `"kitna hai"` keyword
- `"balance"` keyword

## Expected Flow (UPI Mode Active)

1. User clicks "UPI Mode Inactive" → Shows consent modal
2. User accepts consent → `upiMode` state set to `true`
3. User sends: "Mera account balance kitna hai"
4. Frontend sends request with `upi_mode: true`
5. Backend receives and sets `upi_mode: true` in state
6. Intent classifier detects:
   - `upi_mode_active: true`
   - `has_balance_keyword: true`
7. Routes to `upi_payment` intent (UPI agent)
8. UPI agent shows account selection cards
9. User selects account → PIN modal appears
10. User enters PIN → Balance displayed

## Current Behavior (WRONG)

1. User sends: "Mera account balance kitna hai" with UPI mode active
2. System routes to `banking_operation` intent (Banking agent)
3. Banking agent shows normal balance directly

## Next Steps

1. Check frontend console logs when sending message
2. Check network request payload
3. Check backend logs for the entries listed above
4. Identify which step is failing
5. Report the findings

