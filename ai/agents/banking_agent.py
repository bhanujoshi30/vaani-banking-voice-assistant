"""
Banking Operations Agent
Handles account balance, transactions, and transfers
"""
from langchain_core.messages import AIMessage, HumanMessage
from utils import logger


async def banking_agent(state):
    """
    Handle banking operations like balance inquiry, transactions, transfers
    
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
    
    # Build message history for context
    messages = state["messages"]
    
    # For now, use simple keyword-based tool selection
    # In production, you'd use LangChain's AgentExecutor with ReAct
    
    response_content = ""
    
    # Simple keyword-based tool selection (in production, use better intent detection)
    # Priority order: reminders > statements > balance > transactions > transfers
    # This ensures statement requests are handled even if balance is also mentioned
    msg_lower = last_user_message.lower()
    
    reminder_keywords = ["reminder", "reminders", "अनुस्मारक", "set reminder", "create reminder", "view reminder", "show reminder", "remind me"]
    statement_keywords = [
        "statement", "स्टेटमेंट", "bank statement", "account statement",
        "download", "डाउनलोड", "nikalna", "nikal", "export", 
        "statement download", "download statement", "bank statement nikalna",
        "account statement download", "statement nikalna", "statement nikalo"
    ]

    if any(keyword in msg_lower for keyword in reminder_keywords):
        response_content = await handle_reminder_query(state, user_context, language)

    elif any(keyword in msg_lower for keyword in statement_keywords):
        response_content = await handle_statement_request(state, last_user_message, language)
    
    elif any(word in msg_lower for word in ["balance", "बैलेंस"]):
        response_content = await handle_balance_query(state, last_user_message, language)
    
    elif any(word in msg_lower for word in ["transaction", "लेनदेन", "transactions"]):
        response_content = await handle_transaction_query(state, user_context, language)
    
    elif any(word in msg_lower for word in ["transfer", "send", "pay", "ट्रांसफर", "भेजें", "भुगतान"]):
        # Check for UPI keywords (both English and Hindi)
        upi_keywords = ["upi", "यूपीआई", "यूपी", "yupi", "you pee", "you p i"]
        has_upi_keyword = any(keyword in msg_lower for keyword in upi_keywords)
        
        # If UPI keyword detected, activate UPI mode and route to UPI agent
        if has_upi_keyword:
            state["upi_mode"] = True
            from .upi_agent import upi_agent
            logger.info("upi_keyword_detected_in_banking_agent", 
                       message=last_user_message,
                       upi_keywords_found=[kw for kw in upi_keywords if kw in msg_lower])
            return await upi_agent(state)
        
        # Check if UPI mode is active - redirect to UPI agent
        if state.get("upi_mode", False):
            # Route to UPI agent instead of handling as normal transfer
            from .upi_agent import upi_agent
            return await upi_agent(state)
        response_content = await handle_transfer_request(state, user_context, language, last_user_message)
    
    else:
        # General response using LLM with language enforcement
        # Build system prompt with language enforcement
        user_name = user_context.get("name")
        user_name_context = f"\n\nIMPORTANT: The user's name is '{user_name}'. Always use this name when addressing the user." if user_name else ""
        
        if language == "hi-IN":
            system_prompt = f"""तुम Vaani हो, एक मददगार बैंकिंग असिस्टेंट जो Sun National Bank (भारतीय बैंक) के लिए काम करती है।

CRITICAL: उपयोगकर्ता ने हिंदी भाषा चुनी है। तुम्हें केवल हिंदी (देवनागरी लिपि) में जवाब देना चाहिए, भले ही प्रश्न अंग्रेजी में पूछा गया हो। कभी भी अंग्रेजी या किसी अन्य भाषा में जवाब न दें।

महत्वपूर्ण: सभी राशियों को भारतीय रुपये (₹) में दिखाओ।{user_name_context}

SAFETY & SCOPE:
- तुम एक बैंकिंग असिस्टेंट हो। तुम कोडिंग, गणित, सामान्य ज्ञान, या राजनीति के बारे में प्रश्नों के जवाब नहीं देती हो।
- यदि ऐसे प्रश्न पूछे जाएं, तो विनम्रता से मना करो और बैंकिंग सेवाओं के बारे में पूछने के लिए कहो।
- वित्तीय सलाह न दो (जैसे "इस स्टॉक को खरीदो")। केवल बैंक योजनाओं के बारे में तथ्यात्मक जानकारी दो।
- कभी भी संवेदनशील जानकारी जैसे Aadhaar, PAN, खाता संख्या, PIN, या CVV साझा न करो।

यदि तुम्हें उपयोगकर्ता के प्रश्न को समझने में कठिनाई हो रही है या तुम सामान्य जवाब दे रहे हो, तो विनम्रता से उपयोगकर्ता से पूछो कि क्या वे अपना प्रश्न दोबारा बता सकते हैं या अधिक विशिष्ट बना सकते हैं।"""
        else:
            system_prompt = f"""You are Vaani, a helpful banking assistant for Sun National Bank (an Indian bank).

CRITICAL: The user has selected English language. You MUST respond ONLY in English. NEVER respond in Hindi, Devanagari script, or any other language. Use only English words and characters.

IMPORTANT: Always use Indian Rupees (₹ or INR) for all amounts. Never use dollars ($).{user_name_context}

SAFETY & SCOPE:
- You are a Banking Assistant. You DO NOT answer questions about coding, math, general knowledge, or politics. If asked, politely decline and ask them to ask banking-related questions.
- Do not provide financial advice (e.g., "buy this stock"). Only provide factual information about bank schemes.
- Never share sensitive information like Aadhaar, PAN, account numbers, PINs, or CVV.

If you are having difficulty understanding the user's question or are generating generic answers, politely ask the user to rephrase their question or be more specific."""
        
        # Convert LangChain messages to dict format for LLM service
        messages_dict = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                messages_dict.append({"role": role, "content": msg.content})
        response_content = await llm.chat(messages_dict, use_fast_model=False)
        
        # Detect generic answers and ask for clarification
        generic_indicators = [
            "i'm not sure", "i don't know", "i'm not certain", "i cannot",
            "मुझे नहीं पता", "मुझे यकीन नहीं", "मैं नहीं जानती", "मैं निश्चित नहीं"
        ]
        is_generic = any(indicator in response_content.lower() for indicator in generic_indicators)
        
        # Check if response is too generic (very short or doesn't contain specific information)
        if is_generic or (len(response_content) < 50 and "loan" in msg_lower or "investment" in msg_lower):
            if language == "hi-IN":
                clarification = "\n\nकृपया अपना प्रश्न दोबारा बताएं या अधिक विशिष्ट बनाएं ताकि मैं आपकी बेहतर मदद कर सकूं।"
            else:
                clarification = "\n\nCould you please rephrase your question or be more specific so I can help you better?"
            response_content = response_content + clarification
    
    # Add AI response to state
    ai_message = AIMessage(content=response_content)
    state["messages"].append(ai_message)
    state["next_action"] = "end"
    
    logger.info("banking_agent_response", response_length=len(response_content))
    
    return state


async def handle_balance_query(state, last_user_message, language):
    """Handle balance check queries"""
    # Detect account type from message
    account_type_requested = None
    if any(word in last_user_message.lower() for word in ["savings", "बचत", "saving"]):
        account_type_requested = "savings"
    elif any(word in last_user_message.lower() for word in ["current", "चालू", "checking"]):
        account_type_requested = "current"
    
    # Get user's accounts to find the right one
    user_id = state.get("user_id")
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
    
    from tools import get_user_accounts
    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    
    if not accounts_result["success"] or not accounts_result["accounts"]:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    # Prepare account data for LLM
    account_data = []
    if account_type_requested:
        # Find matching account type
        for acc in accounts_result["accounts"]:
            if account_type_requested.lower() in acc["account_type"].lower():
                account_data.append(acc)
                break
    else:
        # Include all accounts
        account_data = accounts_result["accounts"]
    
    if not account_data:
        # Account type requested but not found
        if language == "hi-IN":
            return f"आपके पास {account_type_requested} खाता नहीं है।"
        else:
            return f"You don't have a {account_type_requested} account."
    
    # Format account info for LLM
    accounts_info = []
    for acc in account_data:
        acc_type = acc["account_type"].replace("AccountType.", "")
        accounts_info.append({
            "type": acc_type,
            "balance": acc["balance"],
            "currency": acc["currency"]
        })
    
    # Store structured data for UI
    state["structured_data"] = {
        "type": "balance",
        "accounts": account_data
    }
    
    # Use LLM to generate natural response
    from services import get_llm_service
    llm = get_llm_service()
    
    # Build prompt for LLM
    if language == "hi-IN":
        system_prompt = """तुम Vaani हो, एक मददगार बैंकिंग असिस्टेंट जो Sun National Bank (भारतीय बैंक) के लिए काम करती है। 
उपयोगकर्ता ने अपने खाते की बैलेंस पूछी है।
नीचे दी गई जानकारी का उपयोग करके एक संक्षिप्त, मैत्रीपूर्ण और स्पष्ट उत्तर दो।
केवल बैलेंस की जानकारी दो, अनावश्यक विवरण न जोड़ें।
महत्वपूर्ण: सभी राशियों को भारतीय रुपये (₹) में दिखाओ।"""
        user_prompt = f"खाता जानकारी: {accounts_info}\n\nउपयोगकर्ता का प्रश्न: {last_user_message}"
    else:
        system_prompt = """You are Vaani, a helpful banking assistant for Sun National Bank (an Indian bank).
The user asked about their account balance.
Use the information below to provide a brief, friendly, and clear response.
Only provide the balance information, don't add unnecessary details.
IMPORTANT: Always use Indian Rupees (₹ or INR) for all amounts. Never use dollars ($)."""
        user_prompt = f"Account information: {accounts_info}\n\nUser's question: {last_user_message}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await llm.chat(messages, use_fast_model=False)
    return response


async def handle_transaction_query(state, user_context, language):
    """Handle transaction history queries - fetches from all accounts"""
    user_id = state.get("user_id")
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
    
    from tools import get_user_accounts, get_transaction_history
    
    # Get all user accounts
    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    
    if not accounts_result["success"] or not accounts_result["accounts"]:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    # Fetch transactions from all accounts
    all_transactions = []
    accounts_data = []
    per_account_transactions = {}
    
    for account in accounts_result["accounts"]:
        account_number = account["account_number"]
        result = get_transaction_history.invoke({
            "account_number": account_number,
            "days": 30,
            "limit": 5  # Top 5 per account
        })
        
        transactions = []
        if result["success"] and result["transactions"]:
            transactions = result["transactions"]
            # Add account number/type to each transaction
            for txn in transactions:
                txn["account_number"] = account_number
                txn["account_type"] = account["account_type"]
            all_transactions.extend(transactions)
        
        per_account_transactions[account_number] = transactions
        accounts_data.append({
            "account_number": account_number,
            "account_type": account["account_type"],
            "transaction_count": len(transactions)
        })
    
    if not all_transactions:
        return "कोई लेनदेन नहीं मिला।" if language == "hi-IN" else "No transactions found."
    
    # Sort all transactions by date (most recent first)
    all_transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Take top 5 across all accounts
    top_transactions = all_transactions[:5]
    
    # Store structured data for UI with account information
    state["structured_data"] = {
        "type": "transactions",
        "transactions": top_transactions,
        "accounts": accounts_data,
        "total_count": len(all_transactions),
        "accountTransactions": per_account_transactions
    }
    
    # Prepare transaction data for LLM
    transactions_info = []
    for txn in top_transactions:
        transactions_info.append({
            "date": txn["date"],
            "type": txn["type"],
            "amount": txn["amount"],
            "description": txn["description"],
            "counterparty": txn.get("counterparty", ""),
            "account": txn.get("account_number", "")
        })
    
    # Since we have structured data, return minimal/empty text
    # The UI will display the structured table
    # Only return a very brief acknowledgment if needed
    if language == "hi-IN":
        return ""  # Empty - let the table speak for itself
    else:
        return ""  # Empty - let the table speak for itself


async def handle_statement_request(state, last_user_message, language):
    """Handle account statement download requests"""
    from services import get_llm_service
    from tools import download_statement, get_user_accounts
    from datetime import datetime, timedelta
    import re
    
    llm = get_llm_service()
    user_id = state.get("user_id")
    
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
    
    # Get user's accounts
    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    
    if not accounts_result["success"] or not accounts_result["accounts"]:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    msg_lower = last_user_message.lower()
    
    # Determine account selection
    selected_account = None
    account_specified = False
    
    # First, try to match by last digits (2, 3, or 4 digits)
    # Handle patterns like:
    # - "ending with 44", "last digit 44", "account 44"
    # - "double four" = "44"
    # - "account ka last digit 44 hai" (Hindi: account whose last digit is 44)
    # - "44" as standalone number
    
    # Convert "double four", "double 4", etc. to "44"
    digit_word_map = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }
    msg_for_digit_extraction = msg_lower
    for word, digit in digit_word_map.items():
        # Replace "double four" with "44", "double 4" with "44", etc.
        msg_for_digit_extraction = re.sub(
            rf"double\s+{word}\b|double\s+{digit}\b",
            digit + digit,
            msg_for_digit_extraction,
            flags=re.IGNORECASE
        )
    
    account_digit_patterns = [
        r"ending\s+with\s+(\d{2,4})",
        r"last\s+(?:four\s+)?digits?\s+(\d{2,4})",
        r"last\s+digit\s+(\d{1,4})",  # "last digit 44"
        r"account\s+(?:ka\s+)?(?:ending\s+with\s+)?last\s+digit\s+(\d{1,4})",  # "account ka last digit 44"
        r"account\s+(?:ending\s+with\s+)?(\d{2,4})",
        r"(\d{2,4})\s*(?:digit|digits)",
        r"jis\s+account\s+ka\s+last\s+digit\s+(\d{1,4})",  # Hindi: "jis account ka last digit 44"
        r"\b(\d{2,4})\b",  # Any 2-4 digit number (but prefer longer matches)
    ]
    
    account_digits = None
    for pattern in account_digit_patterns:
        matches = re.findall(pattern, msg_for_digit_extraction, re.IGNORECASE)
        if matches:
            # Prefer longer matches (4 digits > 3 > 2)
            account_digits = max(matches, key=len)
            logger.info("account_digits_extracted", pattern=pattern, digits=account_digits, original_message=last_user_message)
            break
    
    if account_digits:
        logger.info("account_digits_detected", digits=account_digits)
        for acc in accounts_result["accounts"]:
            account_number = acc.get("accountNumber") or acc.get("account_number") or ""
            if account_number and account_number.endswith(account_digits):
                selected_account = acc
                account_specified = True
                logger.info("account_matched_by_digits", 
                           account_number=account_number, 
                           matched_digits=account_digits)
                break
    
    # If not matched by digits, check for explicit account number (at least 6 consecutive digits)
    if not account_specified:
        digit_matches = re.findall(r"\d{6,}", last_user_message)
        for candidate in digit_matches:
            for acc in accounts_result["accounts"]:
                account_number = acc.get("accountNumber") or acc.get("account_number") or ""
                if account_number and candidate in account_number:
                    selected_account = acc
                    account_specified = True
                    break
            if account_specified:
                break
    
    # If still not matched, try by account type
    if not account_specified:
        if any(word in msg_lower for word in ["savings", "बचत"]):
            for acc in accounts_result["accounts"]:
                account_type = acc.get("accountType") or acc.get("account_type") or ""
                if "savings" in str(account_type).lower():
                    selected_account = acc
                    account_specified = True
                    break
        elif any(word in msg_lower for word in ["current", "चालू", "business"]):
            for acc in accounts_result["accounts"]:
                account_type = acc.get("accountType") or acc.get("account_type") or ""
                if "current" in str(account_type).lower():
                    selected_account = acc
                    account_specified = True
                    break
    
    if not selected_account:
        selected_account = accounts_result["accounts"][0]
    
    account_number = selected_account.get("accountNumber") or selected_account.get("account_number") or ""
    
    # Detect period type and calculate dates
    # Map to frontend preset IDs: 'week', 'month', 'quarter', 'half_year', 'year', 'custom'
    period_type = None
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)  # Default
    period_specified = False
    
    # Check for "7 days" or "last 7 days" or Hindi equivalents
    # Handle: "last 7 din", "last 7 days", "पिछले 7 दिन", "la saat din" (Hindi transliteration)
    seven_days_phrases = [
        "7 days", "7 din", "पिछले 7 दिन", "last 7 days", "past 7 days",
        "last 7 din", "la saat din", "la 7 din", "last seven days", "last seven din",
        "seven days", "seven din", "7 दिन", "सात दिन", "7 day", "seven day"
    ]
    if any(phrase in msg_lower for phrase in seven_days_phrases):
        period_type = "week"
        from_date = to_date - timedelta(days=7)
        period_specified = True
        logger.info("period_detected", period="7 days", period_type=period_type)
    elif any(phrase in msg_lower for phrase in ["30 days", "30 din", "पिछले 30 दिन", "last 30 days", "last month", "past month"]):
        period_type = "month"
        from_date = to_date - timedelta(days=30)
        period_specified = True
    elif any(phrase in msg_lower for phrase in ["3 months", "3 महीने", "पिछले 3 महीने", "last 3 months", "quarter", "90 days"]):
        period_type = "quarter"
        from_date = to_date - timedelta(days=90)
        period_specified = True
    elif any(phrase in msg_lower for phrase in ["6 months", "6 महीने", "पिछले 6 महीने", "last 6 months", "half year", "180 days"]):
        period_type = "half_year"
        from_date = to_date - timedelta(days=180)
        period_specified = True
    elif any(phrase in msg_lower for phrase in ["12 months", "12 महीने", "पिछले 12 महीने", "last 12 months", "year", "साल", "365 days"]):
        period_type = "year"
        from_date = to_date - timedelta(days=365)
        period_specified = True
    elif any(word in msg_lower for word in ["week", "सप्ताह"]):
        period_type = "week"
        from_date = to_date - timedelta(days=7)
        period_specified = True
    elif any(word in msg_lower for word in ["month", "महीना"]):
        period_type = "month"
        from_date = to_date - timedelta(days=30)
        period_specified = True
    
    # Detect explicit YYYY-MM-DD dates
    date_matches = re.findall(r"\d{4}-\d{2}-\d{2}", msg_lower)
    if len(date_matches) >= 2:
        try:
            from_date = datetime.strptime(date_matches[0], "%Y-%m-%d")
            to_date = datetime.strptime(date_matches[1], "%Y-%m-%d")
            period_type = "custom"
            period_specified = True
        except ValueError:
            pass
    
    # Always show the card with detected values pre-filled
    # This gives user a chance to review before downloading
    state["structured_data"] = {
        "type": "statement_request",
        "accounts": accounts_result["accounts"],
        "detectedAccount": account_number if account_specified else None,
        "detectedPeriod": {
            "periodType": period_type if period_specified else None,
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d"),
        } if period_specified else None,
        "requiresAccount": not account_specified,
        "requiresPeriod": not period_specified,
    }
    
    # Return appropriate message based on what was detected
    if language == "hi-IN":
        if account_specified and period_specified:
            return "यहाँ स्टेटमेंट डाउनलोड करने के लिए खाता और अवधि पहले से चुनी गई है।"
        elif account_specified:
            return "कृपया अवधि चुनें जिसके लिए आपको स्टेटमेंट चाहिए।"
        elif period_specified:
            return "कृपया वह खाता चुनें जिसके लिए आपको स्टेटमेंट चाहिए।"
        return "कृपया बताएँ कि किस खाते और किस अवधि का स्टेटमेंट डाउनलोड करना है।"
    
    if account_specified and period_specified:
        return "Here's the statement download form with your selected account and period pre-filled."
    elif account_specified:
        return "Please select the time period for which you need the statement."
    elif period_specified:
        return "Please select the account for which you need the statement."
    return "Please let me know which account and time period you need the statement for."


async def handle_reminder_query(state, user_context, language):
    """Handle reminder queries by surfacing reminder manager UI with extracted details"""
    user_id = state.get("user_id")
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."

    from tools import get_user_accounts
    from services import get_llm_service
    from datetime import datetime, timedelta
    import re

    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    accounts = accounts_result["accounts"] if accounts_result.get("success") else []

    last_message = state["messages"][-1].content
    last_message_lower = last_message.lower()
    view_keywords = ["view", "show", "list", "see", "display"]
    create_keywords = ["set", "create", "add", "schedule", "remind"]

    intent = "create"
    if any(keyword in last_message_lower for keyword in view_keywords):
        intent = "view"
    elif any(keyword in last_message_lower for keyword in create_keywords):
        intent = "create"

    # Extract details from user message if creating a reminder
    extracted_data = {}
    if intent == "create":
        llm = get_llm_service()
        
        # Build extraction prompt
        extraction_prompt = f"""Extract reminder details from this user message: "{last_message}"

Return a JSON object with these fields:
- message: The reminder message/text (e.g., "pay electricity bill", "pay rent") or null
- date_time: The date and time mentioned in ISO 8601 format (YYYY-MM-DDTHH:MM) or null. 
  Examples: "tomorrow at 10:00 am" -> calculate tomorrow's date with 10:00, "next week Monday 2pm" -> calculate that date
  If only date is given, default to 9:00 AM. If only time is given, assume today or tomorrow based on context.
- account_last_four: Last digits of account number mentioned (could be 2, 3, or 4 digits). 
  Examples: "ending with 41" -> "41", "last 4 digits 1234" -> "1234", "account 5678" -> "5678"
  Extract the numeric digits only, as a string (e.g., "41", "1234"). Return null if no account mentioned.
- channel: "voice", "sms", or "push" if mentioned, or null

Current date/time context: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Return ONLY valid JSON, no other text. Example:
{{"message": "pay electricity bill", "date_time": "2025-11-20T10:00", "account_last_four": "41", "channel": "voice"}}
"""
        
        try:
            extraction_response = await llm.chat([{"role": "user", "content": extraction_prompt}], use_fast_model=True)
            # Clean the response - remove markdown code blocks if present
            extraction_response = extraction_response.strip()
            if extraction_response.startswith("```json"):
                extraction_response = extraction_response[7:]
            if extraction_response.startswith("```"):
                extraction_response = extraction_response[3:]
            if extraction_response.endswith("```"):
                extraction_response = extraction_response[:-3]
            extraction_response = extraction_response.strip()
            
            import json
            extracted_data = json.loads(extraction_response)
        except Exception as e:
            logger.warning("reminder_extraction_failed", error=str(e), message=last_message)
            extracted_data = {}
        
        # Process extracted data
        prefilled_data = {}
        
        # Extract message
        if extracted_data.get("message"):
            prefilled_data["message"] = extracted_data["message"]
        
        # Extract and parse date/time
        if extracted_data.get("date_time"):
            try:
                date_time_str = extracted_data["date_time"].strip()
                parsed_dt = None
                
                # Handle different ISO formats
                if "T" in date_time_str:
                    # ISO format: YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS
                    if date_time_str.endswith("Z"):
                        # UTC timezone - convert to local naive datetime
                        from datetime import timezone
                        parsed_dt = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
                        # Convert UTC to local time (naive)
                        parsed_dt = parsed_dt.astimezone().replace(tzinfo=None)
                    elif "+" in date_time_str or date_time_str.count("-") > 2:
                        # Has timezone offset
                        parsed_dt = datetime.fromisoformat(date_time_str)
                        if parsed_dt.tzinfo:
                            parsed_dt = parsed_dt.astimezone().replace(tzinfo=None)
                    else:
                        # No timezone - assume local time
                        # Remove seconds/microseconds if present
                        if "." in date_time_str:
                            date_time_str = date_time_str.split(".")[0]
                        if len(date_time_str.split("T")[1].split(":")) > 2:
                            # Has seconds, remove them
                            parts = date_time_str.split("T")
                            time_part = ":".join(parts[1].split(":")[:2])
                            date_time_str = f"{parts[0]}T{time_part}"
                        parsed_dt = datetime.fromisoformat(date_time_str)
                else:
                    # Try other formats like "YYYY-MM-DD HH:MM"
                    try:
                        parsed_dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        parsed_dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
                
                if parsed_dt:
                    # Format for datetime-local input (YYYY-MM-DDTHH:MM)
                    prefilled_data["remindAt"] = parsed_dt.strftime("%Y-%m-%dT%H:%M")
            except Exception as e:
                logger.warning("date_parsing_failed", error=str(e), date_time=extracted_data.get("date_time"))
        
        # Match account by last digits (could be 2, 3, or 4 digits)
        if extracted_data.get("account_last_four"):
            account_last_digits = str(extracted_data["account_last_four"]).strip()
            logger.info("matching_account_by_digits", digits=account_last_digits, total_accounts=len(accounts))
            
            matched_account = None
            for account in accounts:
                account_number = account.get("accountNumber") or account.get("account_number") or ""
                if account_number:
                    # Try to match by last N digits (where N is the length of the provided digits)
                    if account_number.endswith(account_last_digits):
                        matched_account = account
                        logger.info("account_matched", 
                                   account_number=account_number, 
                                   account_id=account.get("id") or account.get("accountId"),
                                   matched_digits=account_last_digits)
                        break
            
            if matched_account:
                account_id = matched_account.get("id") or matched_account.get("accountId")
                if account_id:
                    prefilled_data["accountId"] = account_id
                    logger.info("account_id_set_in_prefilled", account_id=account_id)
                else:
                    logger.warning("matched_account_has_no_id", account_number=matched_account.get("accountNumber") or matched_account.get("account_number"))
            else:
                logger.warning("no_account_matched", digits=account_last_digits, available_accounts=[acc.get("accountNumber") or acc.get("account_number") for acc in accounts])
        
        # Extract channel
        if extracted_data.get("channel"):
            channel = extracted_data["channel"].lower()
            if channel in ["voice", "sms", "push"]:
                prefilled_data["channel"] = channel

    state["structured_data"] = {
        "type": "reminder_manager",
        "intent": intent,
        "accounts": accounts,
        **({"prefilled": prefilled_data} if intent == "create" and prefilled_data else {}),
    }

    if language == "hi-IN":
        if intent == "create":
            return "आप यहाँ अपने भुगतान अनुस्मारक बना सकते हैं। नीचे दिए गए फॉर्म में तारीख, समय, खाता और संदेश दर्ज करें। अनुस्मारक आवाज, SMS या पुश नोटिफिकेशन के माध्यम से भेजा जा सकता है।"
        else:
            return "यहाँ आप अपने सभी भुगतान अनुस्मारक देख और प्रबंधित कर सकते हैं।"
    else:
        if intent == "create":
            return "You can create payment reminders here. Fill in the form below with date, time, account, and message. Reminders can be sent via voice, SMS, or push notifications."
        else:
            return "Here's the reminder panel to create or review reminders."


async def handle_transfer_request(state, user_context, language, last_user_message):
    """Handle transfer/payment requests - returns minimal response, UI handles the rest"""
    user_id = state.get("user_id")
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
    
    from tools import get_user_accounts
    from services import get_llm_service
    import re
    
    # Get user's accounts to match source account
    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    accounts = accounts_result["accounts"] if accounts_result.get("success") else []
    
    # Extract transfer details from message using LLM
    llm = get_llm_service()
    
    extraction_prompt = f"""Extract transfer details from this message: "{last_user_message}"

Return JSON with:
- amount: numeric amount (e.g., 100, 1000) or null
- beneficiary_selector: "first", "last", "name:<name>", "account:<number>", or null
- remarks: any remarks/description or null
- source_account_digits: Last 2-4 digits of source account mentioned (e.g., "41", "1234") or null
  Examples: "account ending with 41" -> "41", "jiska last mein digit 41 hai" -> "41", "last digit 44" -> "44"

Example responses:
{{"amount": 100, "beneficiary_selector": "first", "remarks": null, "source_account_digits": "41"}}
{{"amount": 5000, "beneficiary_selector": "last", "remarks": "payment", "source_account_digits": null}}
{{"amount": 2000, "beneficiary_selector": "name:John Doe", "remarks": null, "source_account_digits": null}}
{{"amount": null, "beneficiary_selector": null, "remarks": null, "source_account_digits": null}}

Return ONLY valid JSON, nothing else."""
    
    try:
        extracted_json = await llm.chat(
            [{"role": "user", "content": extraction_prompt}],
            use_fast_model=True
        )
        
        import json
        json_match = re.search(r'\{[^{}]*\}', extracted_json, re.DOTALL)
        if json_match:
            transfer_details = json.loads(json_match.group())
        else:
            transfer_details = {}
    except Exception as e:
        logger.warning("transfer_extraction_failed", error=str(e), message=last_user_message)
        transfer_details = {}
    
    # Match source account by last digits if mentioned
    source_account_id = None
    source_account_number = None
    msg_lower = last_user_message.lower()
    
    # Handle "double four" -> "44" conversion (similar to statement handler)
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
    
    # Try to extract source account digits from LLM response or directly from message
    source_digits = transfer_details.get("source_account_digits")
    if not source_digits:
        # Fallback: try to extract from message directly
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
        logger.info("source_account_digits_detected", digits=source_digits)
        
        # Match account by last digits
        for acc in accounts:
            account_number = acc.get("accountNumber") or acc.get("account_number") or ""
            if account_number and account_number.endswith(source_digits):
                source_account_id = acc.get("id") or acc.get("accountId")
                source_account_number = account_number
                logger.info("source_account_matched", 
                           account_number=account_number, 
                           account_id=source_account_id,
                           matched_digits=source_digits)
                break
    
    # Store transfer intent in structured data for UI - NO TEXT RESPONSE
    state["structured_data"] = {
        "type": "transfer",
        "intent": "transfer_request",
        "message": last_user_message,
        "amount": transfer_details.get("amount"),
        "beneficiary_selector": transfer_details.get("beneficiary_selector"),
        "remarks": transfer_details.get("remarks"),
        "source_account_id": source_account_id,
        "source_account_number": source_account_number,
    }
    
    # Return minimal/empty response - UI will handle everything
    return ""
