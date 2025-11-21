"""
UPI Payment Agent
Handles Hello UPI voice-assisted payment transactions
"""
from langchain_core.messages import AIMessage, HumanMessage
from utils import logger
import re


async def upi_agent(state):
    """
    Handle UPI payment requests via voice commands
    
    Args:
        state: AgentState with messages, user_id, user_context, etc.
        
    Returns:
        Updated state with AI response
    """
    from services import get_llm_service
    
    # Get unified LLM service
    llm = get_llm_service()
    user_context = state.get("user_context", {})
    language = state.get("language", "en-IN")
    
    # Get last user message
    last_user_message = state["messages"][-1].content
    
    user_id = state.get("user_id")
    if not user_id:
        response = "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)
        state["next_action"] = "end"
        return state
    
    # Check UPI mode status
    upi_mode_active = state.get("upi_mode", False)
    
    # Check if this is just a wake-up phrase without payment command
    msg_lower = last_user_message.lower()
    wake_up_phrases = [
        "hello vaani", "hello upi", "hey vaani", "hey upi",
        "हेलो वाणी", "हेलो upi", "हेलो यूपीआई"
    ]
    is_wake_up_only = any(phrase in msg_lower for phrase in wake_up_phrases) and not any(
        word in msg_lower for word in ["pay", "send", "transfer", "भेजें", "भुगतान"]
    )
    
    # Check if message explicitly mentions UPI (both English and Hindi)
    upi_keywords = ["upi", "यूपीआई", "यूपी", "yupi", "you pee", "you p i"]
    has_explicit_upi = any(keyword in msg_lower for keyword in upi_keywords) or is_wake_up_only
    
    # If UPI keyword detected but UPI mode is inactive, activate it
    if has_explicit_upi and not upi_mode_active:
        state["upi_mode"] = True
        logger.info("upi_keyword_detected_activating_mode", 
                   message=last_user_message,
                   upi_keywords_found=[kw for kw in upi_keywords if kw in msg_lower])
    
    # If UPI mode is inactive and message doesn't explicitly mention UPI, redirect to banking agent
    # Exception: If there's a pending UPI operation (account selection), continue with UPI agent
    existing_structured_data = state.get("structured_data")
    has_pending_upi_operation = (
        existing_structured_data and 
        existing_structured_data.get("type") in ["upi_balance_check", "upi_payment"] and
        existing_structured_data.get("pending_account_selection") == True
    )
    
    # Update upi_mode_active after potential activation above
    upi_mode_active = state.get("upi_mode", False)
    
    if not upi_mode_active and not has_explicit_upi and not has_pending_upi_operation:
        # Redirect to banking agent for normal balance/transaction queries
        from .banking_agent import banking_agent
        logger.info("redirecting_to_banking_agent", reason="upi_mode_inactive_no_upi_keyword", message=last_user_message)
        return await banking_agent(state)
    
    # Preserve existing structured_data if it's UPI mode activation
    # Note: existing_structured_data is already defined above in the redirect check (line 56)
    is_upi_mode_activation = existing_structured_data and existing_structured_data.get("type") == "upi_mode_activation"
    
    # Check if there's a pending account selection and what type it is
    is_pending_balance_check = (
        existing_structured_data and 
        existing_structured_data.get("type") == "upi_balance_check" and
        existing_structured_data.get("pending_account_selection") == True
    )
    
    is_pending_payment_account_selection = (
        existing_structured_data and 
        existing_structured_data.get("type") == "upi_payment" and
        existing_structured_data.get("pending_account_selection") == True
    )
    
    # Also check previous messages for account selection context (in case structured_data wasn't preserved)
    if not is_pending_balance_check and not is_pending_payment_account_selection:
        messages = state.get("messages", [])
        if len(messages) > 1:
            # Check last few assistant messages for account selection prompts
            for msg in reversed(messages[-5:]):
                if hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
                    content = msg.content.lower()
                    # Check if previous message asked for account selection for balance check
                    if any(phrase in content for phrase in [
                        "upi balance check", "upi बैलेंस", "select account for upi balance",
                        "खाता चुनें.*balance", "account for upi balance"
                    ]):
                        is_pending_balance_check = True
                        logger.info("detected_balance_check_account_selection_from_history", message=last_user_message)
                        break
                    # Check if previous message asked for account selection for payment
                    elif any(phrase in content for phrase in [
                        "select.*account.*payment", "select.*source account", "select account.*transfer",
                        "खाता चुनें.*भुगतान", "source account"
                    ]):
                        is_pending_payment_account_selection = True
                        logger.info("detected_payment_account_selection_from_history", message=last_user_message)
                        break
    
    # If this is just a wake-up phrase (no payment command), ensure structured_data is set for UPI mode activation
    if is_wake_up_only and not is_upi_mode_activation:
        state["structured_data"] = {
            "type": "upi_mode_activation",
            "intent": "upi_mode_activation",
            "message": last_user_message,
        }
        is_upi_mode_activation = True
    
    # If structured_data already set for UPI mode activation and no payment command, just return greeting
    if is_upi_mode_activation and is_wake_up_only:
        if language == "hi-IN":
            response_content = "नमस्ते! मैं UPI मोड में हूं। आप कह सकते हैं: '₹100 प्राप्तकर्ता को भेजें' या 'पहले लाभार्थी को ₹500 भेजें'।"
        else:
            response_content = "Hello! I'm in UPI mode with Vaani by Sun National Bank. You can say: 'Send ₹100 to recipient' or 'Transfer ₹500 to first beneficiary'."
        ai_message = AIMessage(content=response_content)
        state["messages"].append(ai_message)
        state["next_action"] = "end"
        # Keep the structured_data for UPI mode activation
        return state
    
    # Check for balance check intent in UPI mode OR if account selection is pending for balance check
    balance_check_keywords = [
        "balance check", "kitne paise hain", "bakaaya rashi", "balance",
        "बैलेंस", "कितने पैसे हैं", "बकाया राशि", "शेष राशि",
        "account balance", "mera account balance", "kitna hai", "कितना है",
        "मेरा अकाउंट बैलेंस", "बैलेंस कितना है", "खाता बैलेंस"
    ]
    is_balance_check = any(keyword in msg_lower for keyword in balance_check_keywords)
    
    # Check if message indicates account selection
    # Messages like "Account 1444 selected" or "खाता 1444 चुना"
    account_selection_indicators = [
        "account", "selected", "चुना", "खाता"
    ]
    has_account_selection_phrase = any(indicator in msg_lower for indicator in account_selection_indicators)
    has_account_digits = bool(re.search(r'\d{3,4}', msg_lower))  # Account ending digits
    
    # Route based on pending operation type:
    # - If pending balance check account selection → balance check handler
    # - If pending payment account selection → payment handler
    # - If account selection phrase + digits but no pending operation → check context
    if is_pending_balance_check:
        # Account selection for balance check → route to balance check handler
        response_content = await handle_upi_balance_check(state, user_context, language, last_user_message)
    elif is_pending_payment_account_selection:
        # Account selection for payment → route to payment handler
        response_content = await handle_upi_payment(state, user_context, language, last_user_message)
    elif is_balance_check:
        # Explicit balance check request → route to balance check handler
        response_content = await handle_upi_balance_check(state, user_context, language, last_user_message)
    elif has_account_selection_phrase and has_account_digits and not any(word in msg_lower for word in ["pay", "send", "transfer", "भेजें", "भुगतान"]):
        # Account selection without payment keywords and no pending operation → check context from previous messages
        # If previous message was about balance check, route to balance check, otherwise payment
        messages = state.get("messages", [])
        previous_was_balance_check = False
        if len(messages) > 1:
            for msg in reversed(messages[-3:]):
                if hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
                    content = msg.content.lower()
                    if any(phrase in content for phrase in ["balance", "बैलेंस", "kitne paise"]):
                        previous_was_balance_check = True
                        break
        if previous_was_balance_check:
            response_content = await handle_upi_balance_check(state, user_context, language, last_user_message)
        else:
            response_content = await handle_upi_payment(state, user_context, language, last_user_message)
    else:
        # Default: Handle UPI payment request
        response_content = await handle_upi_payment(state, user_context, language, last_user_message)
    
    # Add AI response to state
    ai_message = AIMessage(content=response_content)
    state["messages"].append(ai_message)
    state["next_action"] = "end"
    
    logger.info("upi_agent_response", response_length=len(response_content))
    
    return state


def validate_upi_id(upi_id: str):
    """
    Validate UPI ID format according to Indian UPI standards.
    
    Returns:
        (is_valid, error_message)
    """
    if not upi_id or not upi_id.strip():
        return False, "UPI ID is required"
    
    upi_id = upi_id.strip()
    
    # UPI ID format: username@payee
    # Username: 3-99 characters, alphanumeric, dots, hyphens, underscores
    # Payee: 2-20 characters, alphanumeric (e.g., paytm, ybl, phonepe, gpay, sunbank)
    
    if len(upi_id) < 5 or len(upi_id) > 100:
        return False, "UPI ID must be between 5-100 characters"
    
    if '@' not in upi_id:
        return False, "UPI ID must contain @ symbol (format: username@payee)"
    
    parts = upi_id.split('@')
    if len(parts) != 2:
        return False, "UPI ID must have exactly one @ symbol"
    
    username, payee = parts
    
    # Validate username
    if len(username) < 3 or len(username) > 99:
        return False, "Username part must be 3-99 characters"
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
    
    # Validate payee
    if len(payee) < 2 or len(payee) > 20:
        return False, "Payee part must be 2-20 characters"
    
    if not re.match(r'^[a-zA-Z0-9]+$', payee):
        return False, "Payee can only contain letters and numbers"
    
    # Common valid payees (not exhaustive, but helps catch obvious errors)
    common_payees = ['paytm', 'ybl', 'phonepe', 'gpay', 'amazonpay', 'bhim', 'sunbank', 'axis', 'hdfc', 'icici', 'sbi']
    payee_lower = payee.lower()
    
    # Allow other payees but warn if format seems unusual
    # Handle (Right of @): 2-20 chars, a-z A-Z 0-9 (per validation rules)
    if payee_lower not in common_payees and not re.match(r'^[a-zA-Z0-9]{2,20}$', payee):
        return False, "Payee format appears invalid"
    
    return True, ""


async def handle_upi_balance_check(state, user_context, language, last_user_message):
    """Handle UPI balance check requests - asks for account selection if multiple accounts, then prompts for PIN"""
    from tools import get_user_accounts
    
    # Get user's accounts
    accounts_result = get_user_accounts.invoke({"user_id": state.get("user_id")})
    accounts = accounts_result["accounts"] if accounts_result.get("success") else []
    
    if not accounts:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    # Check if user specified an account in the message
    msg_lower = last_user_message.lower()
    source_account_id = None
    source_account_number = None
    source_account_digits = None
    
    # Try to extract account digits from message
    account_patterns = [
        r"account\s+(?:se|from|jiska|whose)\s+(?:last\s+)?(?:digit|digits?)\s+(\d{1,4})",
        r"jiska\s+last\s+(?:mein\s+)?digit\s+(\d{1,4})",
        r"ending\s+with\s+(\d{2,4})",
        r"last\s+digit\s+(\d{1,4})",
        r"account\s+(\d{2,4})",
    ]
    
    for pattern in account_patterns:
        matches = re.findall(pattern, msg_lower, re.IGNORECASE)
        if matches:
            source_account_digits = max(matches, key=len)
            break
    
    # If account digits found, try to match to an account
    if source_account_digits:
        source_account_digits = str(source_account_digits).strip()
        for acc in accounts:
            account_number = acc.get("accountNumber") or acc.get("account_number") or ""
            if account_number and account_number.endswith(source_account_digits):
                source_account_id = acc.get("id") or acc.get("accountId")
                source_account_number = account_number
                break
    
    # Check if there's a pending balance check waiting for account selection
    existing_structured_data = state.get("structured_data")
    is_pending_account_selection = (
        existing_structured_data and 
        existing_structured_data.get("type") == "upi_balance_check" and
        existing_structured_data.get("pending_account_selection")
    )
    
    # Also check previous assistant messages for account selection prompts (in case structured_data wasn't preserved)
    if not is_pending_account_selection:
        messages = state.get("messages", [])
        if len(messages) > 1:
            # Check last few assistant messages for account selection prompts
            for msg in reversed(messages[-5:]):
                if hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
                    content = msg.content.lower()
                    # Check if previous message asked for account selection
                    if any(phrase in content for phrase in [
                        "which account", "किस खाते", "specify which account",
                        "account balance to check", "खाते की शेष राशि"
                    ]):
                        is_pending_account_selection = True
                        logger.info("detected_account_selection_from_history", message=last_user_message)
                        break
    
    # If multiple accounts and no account specified, show account selection cards
    if len(accounts) > 1 and not source_account_id and not is_pending_account_selection:
        # No text response needed - the UI will show account selection cards directly
        response = ""  # Empty response - cards will be shown via structured_data
        
        # Set structured data to indicate we're waiting for account selection (cards will be shown)
        state["structured_data"] = {
            "type": "upi_balance_check",
            "intent": "upi_balance_check",
            "message": last_user_message,
            "accounts": accounts,
            "pending_account_selection": True,
        }
        return response
    
    # If account selection was pending, try to extract account from current message
    if is_pending_account_selection and not source_account_id:
        # Get accounts from structured_data if available (preserves order from previous message)
        accounts_from_context = existing_structured_data.get("accounts", accounts)
        
        # Try to match by account number digits first (handle "Account 1444 selected" or "खाता 1444 चुना")
        account_digits_in_message = re.findall(r'\d{2,4}', msg_lower)
        for acc in accounts_from_context:
            acc_num = acc.get("accountNumber") or acc.get("account_number") or ""
            # Check if message mentions this account's last digits
            if acc_num:
                last_digits = acc_num[-4:] if len(acc_num) >= 4 else acc_num
                # Match if any digits in message match the account's last digits
                if any(d == last_digits[-len(d):] or last_digits.endswith(d) for d in account_digits_in_message if len(d) >= 2):
                    source_account_id = acc.get("id") or acc.get("accountId")
                    source_account_number = acc_num
                    break
        
        # If not found by digits, try to match by ordinal words (first, second, etc.)
        if not source_account_id:
            # Hindi/English ordinal patterns
            ordinal_patterns = [
                (r"(?:first|1st|1|pehla|pehli|पहला|पहली)", 0),
                (r"(?:second|2nd|2|doosra|dusra|doosri|दूसरा|दूसरी)", 1),
                (r"(?:third|3rd|3|teesra|teesri|तीसरा|तीसरी)", 2),
                (r"(?:fourth|4th|4|chautha|chauthi|चौथा|चौथी)", 3),
                (r"(?:fifth|5th|5|paanchva|पांचवा)", 4),
            ]
            
            for pattern, index in ordinal_patterns:
                if re.search(pattern, msg_lower, re.IGNORECASE):
                    if index < len(accounts_from_context):
                        source_account_id = accounts_from_context[index].get("id") or accounts_from_context[index].get("accountId")
                        source_account_number = accounts_from_context[index].get("accountNumber") or accounts_from_context[index].get("account_number")
                        break
            
            # Also check for "other", "dusra wala", "doosra wala" (the other one)
            if not source_account_id:
                other_patterns = [
                    r"other|dusra\s+wala|doosra\s+wala|dusri\s+wali|doosri\s+wali|दूसरा\s+वाला|दूसरी\s+वाली"
                ]
                for pattern in other_patterns:
                    if re.search(pattern, msg_lower, re.IGNORECASE):
                        # "other" or "dusra wala" typically means the second one if there are 2 accounts
                        if len(accounts_from_context) >= 2:
                            source_account_id = accounts_from_context[1].get("id") or accounts_from_context[1].get("accountId")
                            source_account_number = accounts_from_context[1].get("accountNumber") or accounts_from_context[1].get("account_number")
                        break
        
        # If still not found, default to second account if available, else first
        if not source_account_id:
            if len(accounts_from_context) >= 2:
                # Default to second account if user said "other" or similar
                source_account_id = accounts_from_context[1].get("id") or accounts_from_context[1].get("accountId")
                source_account_number = accounts_from_context[1].get("accountNumber") or accounts_from_context[1].get("account_number")
            else:
                source_account_id = accounts_from_context[0].get("id") or accounts_from_context[0].get("accountId")
                source_account_number = accounts_from_context[0].get("accountNumber") or accounts_from_context[0].get("account_number")
    
    # If no account specified and only one account, use that
    if not source_account_id and len(accounts) == 1:
        source_account_id = accounts[0].get("id") or accounts[0].get("accountId")
        source_account_number = accounts[0].get("accountNumber") or accounts[0].get("account_number")
    
    # Store UPI balance check intent in structured data for UI
    state["structured_data"] = {
        "type": "upi_balance_check",
        "intent": "upi_balance_check",
        "message": last_user_message,
        "source_account_id": source_account_id,
        "source_account_number": source_account_number,
        "accounts": accounts,
        "pending_account_selection": False,
    }
    
    # Return response prompting for PIN entry
    if language == "hi-IN":
        acc_type = next((acc.get("accountType") or acc.get("account_type") or "") for acc in accounts if (acc.get("id") or acc.get("accountId")) == source_account_id)
        last_digits = source_account_number[-4:] if source_account_number and len(source_account_number) >= 4 else source_account_number
        return f"UPI बैलेंस जांच: {acc_type} खाता (अंतिम 4 अंक: {last_digits})। कृपया UPI PIN दर्ज करें।"
    else:
        acc_type = next((acc.get("accountType") or acc.get("account_type") or "") for acc in accounts if (acc.get("id") or acc.get("accountId")) == source_account_id)
        last_digits = source_account_number[-4:] if source_account_number and len(source_account_number) >= 4 else source_account_number
        return f"UPI Balance Check: {acc_type} account (ending {last_digits}). Please enter your UPI PIN."


async def handle_upi_payment(state, user_context, language, last_user_message):
    """Handle UPI payment requests - extracts details and prepares for PIN entry"""
    from tools import get_user_accounts, resolve_upi_id, initiate_upi_payment
    from services import get_llm_service
    import re
    
    # Get user's accounts
    accounts_result = get_user_accounts.invoke({"user_id": state.get("user_id")})
    accounts = accounts_result["accounts"] if accounts_result.get("success") else []
    
    if not accounts:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    # Extract UPI payment details from message using LLM
    llm = get_llm_service()
    
    # Build conversation context from previous messages
    # STRICTLY use only the previous 3 pairs of dialogues (user-assistant pairs)
    conversation_context = ""
    upi_ids_in_context = []  # Initialize to avoid NameError
    messages = state.get("messages", [])
    
    if len(messages) > 1:
        # Get exactly the last 3 pairs (6 messages total, excluding current message)
        # A pair consists of: User message followed by Assistant message
        # We need to go backwards from the second-to-last message and collect 3 complete pairs
        
        # Start from the second-to-last message (since last is current user message)
        recent_messages = []
        pairs_collected = 0
        target_pairs = 3
        
        # Go backwards through messages to collect exactly 3 pairs
        # We need to find user-assistant pairs in reverse order
        i = len(messages) - 2  # Start from second-to-last message (skip current)
        
        while i >= 0 and pairs_collected < target_pairs:
            msg = messages[i]
            msg_type = msg.__class__.__name__
            
            # If this is an Assistant message, look for the preceding User message to form a pair
            if msg_type == "AIMessage":
                # Check if there's a User message before this Assistant message
                if i > 0:
                    prev_msg = messages[i - 1]
                    prev_msg_type = prev_msg.__class__.__name__
                    
                    # If previous is User message, we have a complete pair
                    if prev_msg_type == "HumanMessage":
                        # Add both messages to recent_messages (in chronological order)
                        # We'll prepend them so they're in order when we iterate
                        recent_messages.insert(0, prev_msg)  # User message first
                        recent_messages.insert(1, msg)  # Assistant message second
                        pairs_collected += 1
                        i -= 2  # Skip both messages
                    else:
                        # Previous is also Assistant, skip this one
                        i -= 1
                else:
                    # No previous message, skip
                    i -= 1
            else:
                # Current message is User, but we need pairs, so skip
                i -= 1
        
        # Only use these 3 pairs (6 messages) for context
        if recent_messages:
            conversation_context = "\n\nPREVIOUS CONVERSATION CONTEXT (Last 3 pairs only):\n"
            for msg in recent_messages:
                role = "User" if hasattr(msg, "content") and msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content if hasattr(msg, "content") else str(msg)
                conversation_context += f"{role}: {content}\n"
            
            # Extract UPI IDs mentioned in these 3 pairs only (in chronological order)
            for msg in recent_messages:
                content = msg.content if hasattr(msg, "content") else str(msg)
                # Look for UPI ID patterns in previous messages
                upi_pattern = r'([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)'
                found_upis = re.findall(upi_pattern, content)
                # Append in order (so last one is most recent)
                upi_ids_in_context.extend(found_upis)
            
            # Remove duplicates while preserving order (most recent last)
            seen = set()
            unique_upi_ids = []
            for upi_id in upi_ids_in_context:
                if upi_id not in seen:
                    seen.add(upi_id)
                    unique_upi_ids.append(upi_id)
            upi_ids_in_context = unique_upi_ids  # Now contains unique UPI IDs in chronological order
            
            if upi_ids_in_context:
                # Show all UPI IDs but emphasize the most recent one
                most_recent_upi = upi_ids_in_context[-1]
                conversation_context += f"\nUPI IDs mentioned in previous messages (in order): {', '.join(upi_ids_in_context)}\n"
                conversation_context += f"IMPORTANT: The MOST RECENT UPI ID is: {most_recent_upi}\n"
                conversation_context += "If the current message refers to 'this UPI', 'the UPI', 'that UPI ID', 'the UPI from QR', 'yes', or just mentions an amount, use the MOST RECENT UPI ID from above.\n"
    
    # Word number mapping for reference in prompt
    word_number_examples = {
        "hundred": 100, "thousand": 1000, "lakh": 100000,
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
    }
    
    extraction_prompt = f"""Extract UPI payment details from this message: "{last_user_message}"
{conversation_context}

CRITICAL INSTRUCTIONS:
- STRICTLY use ONLY the conversation context provided above (last 3 pairs of dialogues only)
- Do NOT reference any messages outside of the provided context
- Extract UPI ID, amount, and remarks ONLY from the last 3 pairs shown above
1. AMOUNT EXTRACTION:
   - Convert word numbers to digits: "hundred" = 100, "thousand" = 1000, "fifty" = 50, "twenty" = 20, etc.
   - Handle combinations: "hundred rupees" = 100, "two thousand" = 2000
   - Extract numeric values even if written as words
   - Examples: "hundred" → 100, "five hundred" → 500, "thousand" → 1000
   - Recognize balance check phrases: "Balance check", "Kitne paise hain", "Bakaaya rashi" (Hindi for "How much money", "Balance amount") → These indicate CHECK_BALANCE intent

2. RECIPIENT EXTRACTION:
   - If message says "beneficiary", "the beneficiary", "my beneficiary", "first beneficiary" → extract as "first"
   - If message says "last beneficiary", "second beneficiary" → extract as "last"
   - If message says "this UPI", "the UPI", "that UPI ID", "the UPI from QR", "this UPI ID", "yes", "ok", or just mentions an amount without recipient → use the MOST RECENT UPI ID from previous conversation context
   - If a specific name, UPI ID, or phone number is mentioned, extract that instead
   - Examples: "transfer to beneficiary" → "first", "send to the beneficiary" → "first", "send money to this UPI" → use MOST RECENT UPI ID from context, "yes 1000" → use MOST RECENT UPI ID from context

3. Return JSON with these fields:
   - amount: numeric amount as integer (e.g., 100, 1000) or null if not found
   - recipient_identifier: Can be:
     * UPI ID (e.g., "9876543210@sunbank", "john.doe@sunbank")
     * Phone number (e.g., "9876543210")
     * Name (e.g., "John Doe", "Arvind")
     * Beneficiary selector: "first" (for first/any beneficiary), "last" (for last beneficiary), or null
   - remarks: any remarks/description or null
   - source_account_digits: Last 2-4 digits of source account mentioned (e.g., "41", "1234") or null

Example responses:
Message: "transfer hundred rupees to the beneficiary"
→ {{"amount": 100, "recipient_identifier": "first", "remarks": null, "source_account_digits": null}}

Message: "pay ₹500 to 9876543210@sunbank"
→ {{"amount": 500, "recipient_identifier": "9876543210@sunbank", "remarks": null, "source_account_digits": null}}

Message: "send thousand rupees to John"
→ {{"amount": 1000, "recipient_identifier": "John", "remarks": null, "source_account_digits": null}}

Message: "transfer hundred to this UPI" (if previous messages had "9920873847-1@okbizaxis" then "3218196001@sunbank")
→ {{"amount": 100, "recipient_identifier": "3218196001@sunbank", "remarks": null, "source_account_digits": null}}
Note: Always use the MOST RECENT UPI ID from the conversation context, not older ones.

Return ONLY valid JSON, nothing else."""
    
    try:
        extracted_json = await llm.chat(
            [{"role": "user", "content": extraction_prompt}],
            use_fast_model=True
        )
        
        import json
        json_match = re.search(r'\{[^{}]*\}', extracted_json, re.DOTALL)
        if json_match:
            payment_details = json.loads(json_match.group())
        else:
            payment_details = {}
    except Exception as e:
        logger.warning("upi_extraction_failed", error=str(e), message=last_user_message)
        payment_details = {}
    
    # Fallback: If no recipient_identifier extracted but we have UPI ID in context, use it
    if not payment_details.get("recipient_identifier") and upi_ids_in_context:
        # Check if message refers to "this UPI", "the UPI", etc., or if it's just an amount/confirmation
        msg_lower = last_user_message.lower()
        upi_references = ["this upi", "the upi", "that upi", "upi id", "the upi id", "this upi id", "that upi id", "upi from qr", "the upi from qr"]
        confirmation_words = ["yes", "ok", "okay", "sure", "confirm", "proceed", "go ahead", "हाँ", "ठीक", "जी"]
        has_confirmation = any(word in msg_lower for word in confirmation_words)
        has_explicit_recipient = any(word in msg_lower for word in ["to", "beneficiary", "@"])
        
        # If message has confirmation or just amount without explicit recipient, use UPI from context
        if any(ref in msg_lower for ref in upi_references) or (has_confirmation or not has_explicit_recipient):
            # Use the MOST RECENT UPI ID from context (last in list = most recent)
            most_recent_upi = upi_ids_in_context[-1]
            payment_details["recipient_identifier"] = most_recent_upi
            logger.info("using_most_recent_upi_from_context", upi_id=most_recent_upi, all_upis=upi_ids_in_context, message=last_user_message, has_confirmation=has_confirmation)
    
    # Match source account by last digits if mentioned
    source_account_id = None
    source_account_number = None
    msg_lower = last_user_message.lower()
    
    # Handle "double four" -> "44" conversion
    digit_word_map = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }
    msg_for_digit_extraction = msg_lower
    for word, digit in digit_word_map.items():
        msg_for_digit_extraction = re.sub(
            rf"double\s+{word}\b|double\s+{digit}\b",
            digit + digit,
            msg_for_digit_extraction,
            flags=re.IGNORECASE
        )
    
    source_digits = payment_details.get("source_account_digits")
    if not source_digits:
        source_account_patterns = [
            r"account\s+(?:se|from|jiska|whose)\s+(?:last\s+)?(?:digit|digits?)\s+(\d{1,4})",
            r"jiska\s+last\s+(?:mein\s+)?digit\s+(\d{1,4})",
            r"ending\s+with\s+(\d{2,4})",
            r"last\s+digit\s+(\d{1,4})",
            r"account\s+(\d{2,4})",
        ]
        for pattern in source_account_patterns:
            matches = re.findall(pattern, msg_for_digit_extraction, re.IGNORECASE)
            if matches:
                source_digits = max(matches, key=len)
                break
    
    if source_digits:
        source_digits = str(source_digits).strip()
        for acc in accounts:
            account_number = acc.get("accountNumber") or acc.get("account_number") or ""
            if account_number and account_number.endswith(source_digits):
                source_account_id = acc.get("id") or acc.get("accountId")
                source_account_number = account_number
                break
    
    # If no source account specified, use first account
    if not source_account_id and accounts:
        source_account_id = accounts[0].get("id") or accounts[0].get("accountId")
        source_account_number = accounts[0].get("accountNumber") or accounts[0].get("account_number")
    
    # Get recipient identifier
    recipient_identifier = payment_details.get("recipient_identifier")
    
    # If no recipient specified and we have amount, try to use UPI from context as final fallback
    # BUT: Don't do this if we're going to show the card anyway (when amount or recipient is missing)
    # We'll check for missing fields later and show the card
    if not recipient_identifier and payment_details.get("amount"):
        if upi_ids_in_context:
            # Use the MOST RECENT UPI ID from context (last in list = most recent)
            most_recent_upi = upi_ids_in_context[-1]
            recipient_identifier = most_recent_upi
            payment_details["recipient_identifier"] = recipient_identifier
            logger.info("using_most_recent_upi_final_fallback", upi_id=most_recent_upi, all_upis=upi_ids_in_context, message=last_user_message)
        # If no UPI in context, we'll show the card below (don't return error here)
    
    # Validate UPI ID format if it's not a beneficiary selector
    if recipient_identifier and recipient_identifier not in ["first", "last"]:
        # Check if it looks like a UPI ID (contains @)
        if "@" in recipient_identifier:
            is_valid, error_msg = validate_upi_id(recipient_identifier)
            if not is_valid:
                if language == "hi-IN":
                    return f"अमान्य UPI ID: {error_msg}. कृपया सही UPI ID प्रदान करें (उदाहरण: username@paytm, 9876543210@ybl)।"
                else:
                    return f"Invalid UPI ID: {error_msg}. Please provide a valid UPI ID (e.g., username@paytm, 9876543210@ybl)."
    
    # Resolve beneficiary if recipient_identifier is "first" or "last"
    if recipient_identifier in ["first", "last"]:
        try:
            from db.repositories import beneficiaries as beneficiary_repo
            from utils.db_helper import get_db
            
            with get_db() as db:
                beneficiaries = beneficiary_repo.list_beneficiaries(db, user_id=state.get("user_id"), include_blocked=False)
                beneficiaries_list = list(beneficiaries)
                
                if beneficiaries_list:
                    if recipient_identifier == "first":
                        beneficiary = beneficiaries_list[0]
                    else:  # "last"
                        beneficiary = beneficiaries_list[-1]
                    
                    # Try to resolve beneficiary to UPI ID or phone number
                    # First try to get user by account number
                    from db.models import User, Account
                    from sqlalchemy import select
                    
                    stmt = select(Account).where(Account.account_number == beneficiary.account_number)
                    account = db.execute(stmt).scalars().first()
                    if account:
                        stmt = select(User).where(User.id == account.user_id)
                        user = db.execute(stmt).scalars().first()
                        if user and user.upi_id:
                            recipient_identifier = user.upi_id
                        elif user and user.phone_number:
                            recipient_identifier = user.phone_number
                        else:
                            # Fallback to beneficiary name
                            recipient_identifier = beneficiary.name
                    else:
                        recipient_identifier = beneficiary.name
                else:
                    # No beneficiaries found, keep original identifier
                    pass
        except Exception as e:
            logger.warning("beneficiary_resolution_failed", error=str(e))
            # Keep original identifier if resolution fails
    
    # Always show card for UPI payment (similar to normal transfer flow)
    # User will fill account, amount, UPI ID, remarks, then click Proceed
    # Only then we'll validate and show PIN modal
    amount = payment_details.get("amount")
    
    # Store UPI payment intent in structured data for UI - show card (always)
    state["structured_data"] = {
        "type": "upi_payment_card",
        "intent": "upi_payment_request",
        "message": last_user_message,
        "amount": amount if amount and amount > 0 else None,
        "recipient_identifier": recipient_identifier if recipient_identifier and recipient_identifier.strip() else None,
        "remarks": payment_details.get("remarks"),
        "source_account_id": source_account_id,
        "source_account_number": source_account_number,
        "accounts": accounts,
    }
    
    # Return minimal response - card will handle the rest
    if language == "hi-IN":
        return "UPI भुगतान के लिए कृपया खाता, राशि और UPI ID दर्ज करें।"
    else:
        return "Please select account, enter amount and UPI ID for UPI payment."

