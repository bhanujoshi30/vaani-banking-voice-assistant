# Check Backend Logs for UPI Mode Issue

## Quick Check

When you send "Mera account balance kitna hai" with UPI mode active, check your backend terminal/logs for these entries **in order**:

### Expected Log Sequence (UPI Mode Active):

1. ✅ `chat_request` - Should show `upi_mode: true`
2. ✅ `using_upi_mode_from_frontend` - Should show `upi_mode: true`
3. ✅ `initial_state_created` - Should show `upi_mode: true`
4. ✅ `intent_classifier_upi_mode_check` - Should show `upi_mode_active: true`
5. ✅ `balance_keyword_detected` - Should show matched keywords like `['mera account balance', 'kitna hai', 'balance']`
6. ✅ `upi_mode_active_detected` - Should appear
7. ✅ `upi_balance_check_routed` - Should show `intent: upi_payment`
8. ✅ `routing_decision` - Should show `intent: upi_payment, route: upi_agent`
9. ✅ `final_state_before_response` - Should show `final_intent: upi_payment`

### If You See This (WRONG):

- `intent_classifier_upi_mode_check` shows `upi_mode_active: false` → **State not being set correctly**
- `upi_mode_not_active_in_intent_classifier` warning → **UPI mode not in state**
- `normal_balance_check_routed` → **Routing to banking agent instead of UPI agent**
- `routing_decision` shows `intent: banking_operation` → **Intent classifier set wrong intent**

## What to Look For

### Issue 1: UPI Mode Not Received
**Look for:** `upi_mode_not_provided_from_frontend` or `upi_mode: None` in `chat_request`
**Fix:** Check frontend is sending `upi_mode: true` in request

### Issue 2: State Not Set
**Look for:** `initial_state_created` shows `upi_mode: false` even though `using_upi_mode_from_frontend` showed `true`
**Fix:** Check `agent_graph.py` line 162 - state initialization

### Issue 3: Intent Classifier Not Reading State
**Look for:** `intent_classifier_upi_mode_check` shows `upi_mode_active: false` even though state has `upi_mode: true`
**Fix:** Check LangGraph state passing

### Issue 4: Wrong Intent Set
**Look for:** `normal_balance_check_routed` instead of `upi_balance_check_routed`
**Fix:** Check `intent_classifier.py` routing logic

## Command to Check Logs

```bash
# If using file logging
tail -f ai/logs/ai_backend.log | grep -E "upi_mode|intent|routing"

# If using console logging
# Just watch your backend terminal
```

## Next Steps

1. Send the balance query with UPI mode active
2. Copy the backend logs
3. Check which step is failing (see Expected Log Sequence above)
4. Report which log entry shows the wrong value

