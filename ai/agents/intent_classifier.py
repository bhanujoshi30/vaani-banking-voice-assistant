"""
Intent Classification Agent
Determines user intent to route to appropriate agent

SIMPLE LOGIC:
- When UPI mode is active:
  * Balance check → UPI agent (for UPI balance check with PIN)
  * Transfer/Payment → UPI agent (for UPI payment)
- When UPI mode is inactive:
  * Balance check → Banking agent (normal balance check)
  * Transfer → Banking agent (normal transfer, unless explicitly mentions UPI)
"""
from langchain_core.messages import AIMessage
from utils import logger, log_agent_decision
import re


async def classify_intent(state):
    """
    Classify user intent to route to appropriate agent
    
    SIMPLE ROUTING RULES:
    1. If UPI mode is active:
       - Balance query → UPI agent
       - Transfer/Payment → UPI agent
    2. If UPI mode is inactive:
       - Balance query → Banking agent
       - Transfer → Banking agent (unless explicitly mentions UPI)
    3. Otherwise → Use LLM classification
    
    Args:
        state: AgentState with messages, language, etc.
        
    Returns:
        Updated state with current_intent set
    """
    from services import get_llm_service
    
    # Get unified LLM service
    llm = get_llm_service()
    
    # Get messages and last user message
    messages = state.get("messages", [])
    last_message = messages[-1].content if messages else ""
    msg_lower = last_message.lower()
    language = state.get("language", "en-IN")
    
    # Check if UPI mode is active (from frontend or previous state)
    upi_mode_active = state.get("upi_mode", False)
    
    # DEBUG: Log UPI mode status with full state info
    logger.info("intent_classifier_upi_mode_check",
               upi_mode_active=upi_mode_active,
               upi_mode_from_state=state.get("upi_mode"),
               message=last_message[:100],
               state_keys=list(state.keys()),
               full_state_upi_mode=str(state.get("upi_mode")))
    
    # CRITICAL: If UPI mode is not in state but should be, log warning
    if not upi_mode_active:
        logger.warning("upi_mode_not_active_in_intent_classifier",
                      upi_mode_value=state.get("upi_mode"),
                      message=last_message[:100])
    
    # Check if there's a pending UPI operation (account selection)
    existing_structured_data = state.get("structured_data", {})
    has_pending_upi_operation = (
        existing_structured_data.get("type") in ["upi_balance_check", "upi_payment"] and
        existing_structured_data.get("pending_account_selection") == True
    )
    
    # If there's a pending UPI operation, route to UPI agent
    if has_pending_upi_operation:
        intent = "upi_payment"
        state["upi_mode"] = True
        state["current_intent"] = intent
        logger.info("pending_upi_operation_detected", 
                   message=last_message, 
                   structured_data_type=existing_structured_data.get("type"))
        return state
    
    # Check for wake-up phrases to activate UPI mode
    wake_up_phrases = [
        "hello vaani", "hello upi", "hey vaani", "hey upi",
        "हेलो वाणी", "हेलो upi", "हेलो यूपीआई"
    ]
    is_wake_up = any(phrase in msg_lower for phrase in wake_up_phrases)
    if is_wake_up:
        state["upi_mode"] = True
        state["structured_data"] = {
            "type": "upi_mode_activation",
            "intent": "upi_mode_activation",
            "message": last_message,
        }
        logger.info("wake_up_phrase_detected", message=last_message)
        # Route to UPI agent to handle activation
        intent = "upi_payment"
        state["current_intent"] = intent
        return state
    
    # SIMPLE ROUTING LOGIC: Check for balance and transfer keywords
    balance_keywords = [
        "balance", "बैलेंस", "kitne paise", "कितने पैसे", "bakaaya", "बकाया", "शेष",
        "balance check", "kitne paise hain", "bakaaya rashi", "शेष राशि",
        "account balance", "mera account balance", "kitna hai", "कितना है",
        "मेरा अकाउंट बैलेंस", "बैलेंस कितना है", "खाता बैलेंस", "बकाया राशि"
    ]
    has_balance_keyword = any(keyword in msg_lower for keyword in balance_keywords)
    
    # DEBUG: Log keyword detection
    if has_balance_keyword:
        matched_keywords = [kw for kw in balance_keywords if kw in msg_lower]
        logger.info("balance_keyword_detected",
                   message=last_message[:100],
                   matched_keywords=matched_keywords,
                   has_balance_keyword=True)
    
    transfer_keywords = [
        "transfer", "send", "pay", "भेजें", "भुगतान", "ट्रांसफर",
        "send money", "transfer money", "pay money"
    ]
    has_transfer_keyword = any(keyword in msg_lower for keyword in transfer_keywords)
    
    # Check if message contains amount (numbers, rupees, etc.)
    has_amount = bool(re.search(r'\d+|rupees?|rs\.?|₹|hundred|thousand|lakh|crore', msg_lower))
    
    # CRITICAL: Check for reminder keywords FIRST, regardless of UPI mode
    # Reminder operations should always go to banking_operation, not UPI agent
    reminder_keywords = ["reminder", "remind", "set reminder", "create reminder", "view reminder", "show reminder", "अनुस्मारक"]
    has_reminder_keyword = any(keyword in msg_lower for keyword in reminder_keywords)
    
    if has_reminder_keyword:
        intent = "banking_operation"
        state["current_intent"] = intent
        logger.info("reminder_keyword_detected", 
                   message=last_message[:100], 
                   upi_mode_active=upi_mode_active,
                   intent=intent)
        return state
    
    # CRITICAL ROUTING: When UPI mode is active
    if upi_mode_active:
        logger.info("upi_mode_active_detected", 
                   message=last_message[:100],
                   has_balance_keyword=has_balance_keyword,
                   has_transfer_keyword=has_transfer_keyword,
                   has_amount=has_amount,
                   upi_mode_value=state.get("upi_mode"))
        
        # Balance query → UPI agent
        if has_balance_keyword:
            intent = "upi_payment"  # Route to UPI agent for balance check
            state["upi_mode"] = True
            state["current_intent"] = intent
            logger.info("upi_balance_check_routed", 
                       message=last_message[:100], 
                       upi_mode_active=True,
                       intent=intent,
                       state_after_setting=state.get("current_intent"))
            return state
        
        # Transfer/Payment → UPI agent
        if has_transfer_keyword or has_amount:
            intent = "upi_payment"  # Route to UPI agent for payment
            state["upi_mode"] = True
            state["current_intent"] = intent
            logger.info("upi_payment_routed", message=last_message, upi_mode_active=True)
            return state
    
    # When UPI mode is inactive: Route to banking agent for balance/transfer
    if not upi_mode_active:
        # Balance query → Banking agent (normal balance check)
        if has_balance_keyword:
            intent = "banking_operation"
            state["current_intent"] = intent
            logger.info("normal_balance_check_routed", message=last_message, upi_mode_active=False)
            return state
        
        # Transfer (without explicit UPI mention) → Banking agent
        if has_transfer_keyword and "upi" not in msg_lower:
            intent = "banking_operation"
            state["current_intent"] = intent
            logger.info("normal_transfer_routed", message=last_message, upi_mode_active=False)
            return state
    
    # For other queries, use LLM classification
    intent_prompt = f"""You are a banking assistant. Classify the user's intent into ONE of these categories:
    - upi_payment: UPI payments, sending money via UPI, "pay via UPI", "UPI payment", "send money via UPI", "pay ₹X to Y via UPI", or explicitly mentions UPI
    - banking_operation: Balance check (when UPI mode is NOT active), transactions, transfers (non-UPI), account operations, setting reminders, viewing reminders, managing reminders, downloading statements, account statements, bank statements
    - general_faq: Questions about interest rates, products, services, branches
    - greeting: Hi, hello, namaste, how are you
    - feedback: Complaints, suggestions, feedback
    - other: Small talk or unclear intent

CRITICAL RULES:
    - "set reminder", "create reminder", "view reminders", "show reminders", "remind me" → "banking_operation"
    - "download statement", "bank statement", "account statement", "statement download", "nikalna", "स्टेटमेंट" → "banking_operation"
    - If message explicitly mentions "UPI" → "upi_payment"
    - Otherwise, classify based on the message content

User message: "{last_message}"

Reply with ONLY the intent category name, nothing else."""
    
    # Use fast model for quick classification
    intent = await llm.chat([{"role": "user", "content": intent_prompt}], use_fast_model=True)
    intent = intent.strip().lower()
    
    # Validate intent
    valid_intents = ["upi_payment", "banking_operation", "general_faq", "greeting", "feedback", "other"]
    if intent not in valid_intents:
        intent = "other"
    
    # Final keyword-based fallback (reminder keywords already checked above)
    statement_keywords = [
        "statement", "स्टेटमेंट", "bank statement", "account statement", 
        "download", "डाउनलोड", "nikalna", "nikal", "export"
    ]
    
    if any(keyword in msg_lower for keyword in statement_keywords):
        intent = "banking_operation"
        logger.info("banking_keyword_detected", message=last_message, forced_intent=intent)
    
    state["current_intent"] = intent
    
    log_agent_decision(
        agent="intent_classifier",
        intent=intent,
        confidence=0.8,
    )
    
    logger.info("intent_classified", intent=intent, user_message=last_message, upi_mode_active=upi_mode_active)
    
    return state
