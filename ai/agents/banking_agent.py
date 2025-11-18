"""
Banking Operations Agent
Handles account balance, transactions, and transfers
"""
from langchain_core.messages import AIMessage
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
    if any(word in last_user_message.lower() for word in ["balance", "बैलेंस"]):
        response_content = await handle_balance_query(state, last_user_message, language)
    
    elif any(word in last_user_message.lower() for word in ["statement", "स्टेटमेंट", "download", "डाउनलोड", "export"]):
        response_content = await handle_statement_request(state, last_user_message, language)
    
    elif any(word in last_user_message.lower() for word in ["transaction", "लेनदेन", "transactions"]):
        response_content = await handle_transaction_query(state, user_context, language)
    
    else:
        # General response using LLM
        response_content = await llm.chat(messages, use_fast_model=False)
    
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
    """Handle transaction history queries"""
    if not user_context.get("account_number"):
        return "कृपया अपना खाता नंबर बताएं।" if language == "hi-IN" else "Please provide your account number."
    
    from tools import get_transaction_history
    result = get_transaction_history.invoke({
        "account_number": user_context["account_number"],
        "days": 30,
        "limit": 5
    })
    
    if not result["success"]:
        return "लेनदेन जानकारी प्राप्त करने में समस्या हुई।" if language == "hi-IN" else "Error fetching transaction information."
    
    if not result["transactions"]:
        return "कोई लेनदेन नहीं मिला।" if language == "hi-IN" else "No transactions found."
    
    # Prepare transaction data for LLM
    transactions_info = []
    for txn in result["transactions"]:
        transactions_info.append({
            "date": txn["date"],
            "type": txn["type"],
            "amount": txn["amount"],
            "description": txn["description"],
            "counterparty": txn.get("counterparty", "")
        })
    
    # Use LLM to generate natural response
    from services import get_llm_service
    llm = get_llm_service()
    
    # Get last user message for context
    last_user_message = state["messages"][-1].content if state["messages"] else "transaction history"
    
    # Build prompt for LLM
    if language == "hi-IN":
        system_prompt = """तुम Vaani हो, एक मददगार बैंकिंग असिस्टेंट जो Sun National Bank (भारतीय बैंक) के लिए काम करती है।
उपयोगकर्ता ने अपने लेनदेन के बारे में पूछा है।
नीचे दी गई जानकारी का उपयोग करके एक संक्षिप्त और स्पष्ट सारांश दो।
महत्वपूर्ण लेनदेन को उजागर करें और तारीख, राशि और विवरण शामिल करें।
महत्वपूर्ण: सभी राशियों को भारतीय रुपये (₹) में दिखाओ।"""
        user_prompt = f"लेनदेन जानकारी: {transactions_info}\n\nउपयोगकर्ता का प्रश्न: {last_user_message}"
    else:
        system_prompt = """You are Vaani, a helpful banking assistant for Sun National Bank (an Indian bank).
The user asked about their transactions.
Use the information below to provide a brief and clear summary.
Highlight important transactions and include date, amount, and description.
IMPORTANT: Always use Indian Rupees (₹ or INR) for all amounts. Never use dollars ($)."""
        user_prompt = f"Transaction information: {transactions_info}\n\nUser's question: {last_user_message}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await llm.chat(messages, use_fast_model=False)
    return response


async def handle_statement_request(state, last_user_message, language):
    """Handle account statement download requests"""
    from services import get_llm_service
    from tools import download_statement, get_user_accounts
    from datetime import datetime, timedelta
    
    llm = get_llm_service()
    user_id = state.get("user_id")
    
    if not user_id:
        return "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
    
    # Get user's accounts
    accounts_result = get_user_accounts.invoke({"user_id": user_id})
    
    if not accounts_result["success"] or not accounts_result["accounts"]:
        return "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
    
    # Determine account - use first account or detect from message
    account = accounts_result["accounts"][0]
    account_number = account["account_number"]
    
    # Check if specific account type mentioned
    if any(word in last_user_message.lower() for word in ["savings", "बचत"]):
        for acc in accounts_result["accounts"]:
            if "savings" in acc["account_type"].lower():
                account = acc
                account_number = acc["account_number"]
                break
    elif any(word in last_user_message.lower() for word in ["current", "चालू"]):
        for acc in accounts_result["accounts"]:
            if "current" in acc["account_type"].lower():
                account = acc
                account_number = acc["account_number"]
                break
    
    # Detect period type and calculate dates
    period_type = "custom"
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)  # Default: last month
    
    msg_lower = last_user_message.lower()
    
    if any(word in msg_lower for word in ["week", "सप्ताह", "7 days"]):
        period_type = "week"
        from_date = to_date - timedelta(days=7)
    elif any(word in msg_lower for word in ["month", "महीना", "30 days"]):
        period_type = "month"
        from_date = to_date - timedelta(days=30)
    elif any(word in msg_lower for word in ["year", "साल", "365 days", "12 months"]):
        period_type = "year"
        from_date = to_date - timedelta(days=365)
    elif any(word in msg_lower for word in ["3 months", "quarter", "तिमाही"]):
        period_type = "quarter"
        from_date = to_date - timedelta(days=90)
    
    # Format dates
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    
    # Prepare statement
    result = download_statement.invoke({
        "account_number": account_number,
        "from_date": from_date_str,
        "to_date": to_date_str,
        "period_type": period_type
    })
    
    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        if language == "hi-IN":
            return f"स्टेटमेंट तैयार करने में समस्या: {error_msg}"
        else:
            return f"Error preparing statement: {error_msg}"
    
    # Generate natural response using LLM
    if language == "hi-IN":
        system_prompt = """तुम Vaani हो, एक मददगार बैंकिंग असिस्टेंट जो Sun National Bank (भारतीय बैंक) के लिए काम करती है।
उपयोगकर्ता ने अपना खाता स्टेटमेंट डाउनलोड करने के लिए कहा है।
स्टेटमेंट तैयार है और डाउनलोड के लिए उपलब्ध है।
एक विनम्र, संक्षिप्त संदेश दो जो:
1. पुष्टि करे कि स्टेटमेंट तैयार है
2. अवधि और लेनदेन की संख्या बताए
3. उपयोगकर्ता को डाउनलोड बटन पर क्लिक करने के लिए कहे
महत्वपूर्ण: सभी राशियों को भारतीय रुपये (₹) में दिखाओ।"""
        
        user_prompt = f"""स्टेटमेंट जानकारी:
- खाता प्रकार: {account['account_type']}
- खाता नंबर: {account_number}
- अवधि: {period_type}
- शुरुआत की तारीख: {from_date_str}
- अंत की तारीख: {to_date_str}
- लेनदेन संख्या: {result['transaction_count']}
- वर्तमान बैलेंस: ₹{result['current_balance']:,.2f}

उपयोगकर्ता का अनुरोध: {last_user_message}"""
    else:
        system_prompt = """You are Vaani, a helpful banking assistant for Sun National Bank (an Indian bank).
The user requested to download their account statement.
The statement is prepared and ready for download.
Provide a polite, concise message that:
1. Confirms the statement is ready
2. Mentions the period and number of transactions
3. Asks the user to click the download button
IMPORTANT: Always use Indian Rupees (₹ or INR) for all amounts. Never use dollars ($)."""
        
        user_prompt = f"""Statement information:
- Account type: {account['account_type']}
- Account number: {account_number}
- Period: {period_type}
- From date: {from_date_str}
- To date: {to_date_str}
- Transaction count: {result['transaction_count']}
- Current balance: ₹{result['current_balance']:,.2f}

User's request: {last_user_message}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = await llm.chat(messages, use_fast_model=False)
    
    # Store statement data in state for frontend to access
    state["statement_data"] = result
    
    return response
