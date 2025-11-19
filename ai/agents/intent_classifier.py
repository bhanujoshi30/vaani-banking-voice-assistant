"""
Intent Classification Agent
Determines user intent from conversation
"""
from langchain_core.messages import AIMessage
from utils import logger, log_agent_decision


async def classify_intent(state):
    """
    Classify user intent to route to appropriate agent
    
    Intents:
    - banking_operation: Balance, transactions, transfers
    - general_faq: Interest rates, products, branch info
    - greeting: Hi, hello, namaste
    - feedback: Complaints, suggestions
    - other: Unknown or small talk
    
    Args:
        state: AgentState with messages, language, etc.
        
    Returns:
        Updated state with current_intent set
    """
    from services import get_llm_service
    
    # Get unified LLM service (uses config to decide ollama/openai)
    llm = get_llm_service()
    
    # Get last user message
    last_message = state["messages"][-1].content if state["messages"] else ""
    language = state.get("language", "en-IN")
    
    # Simple prompt for intent classification
    intent_prompt = f"""You are a banking assistant. Classify the user's intent into ONE of these categories:
- banking_operation: Balance check, transactions, transfers, account operations, setting reminders, viewing reminders, managing reminders, downloading statements, account statements, bank statements
- general_faq: Questions about interest rates, products, services, branches
- greeting: Hi, hello, namaste, how are you
- feedback: Complaints, suggestions, feedback
- other: Small talk or unclear intent

Important: 
- "set reminder", "create reminder", "view reminders", "show reminders", "remind me" should be classified as "banking_operation".
- "download statement", "bank statement", "account statement", "statement download", "nikalna" (Hindi for download), "स्टेटमेंट" should be classified as "banking_operation".

User message: "{last_message}"

Reply with ONLY the intent category name, nothing else."""
    
    # Use fast model for quick classification
    intent = await llm.chat([{"role": "user", "content": intent_prompt}], use_fast_model=True)
    intent = intent.strip().lower()
    
    # Validate intent
    valid_intents = ["banking_operation", "general_faq", "greeting", "feedback", "other"]
    if intent not in valid_intents:
        intent = "other"
    
    # Keyword-based fallback: Force banking operation requests to banking_operation
    msg_lower = last_message.lower()
    
    # Statement/download keywords
    statement_keywords = [
        "statement", "स्टेटमेंट", "bank statement", "account statement", 
        "download", "डाउनलोड", "nikalna", "nikal", "export", "statement download",
        "download statement", "bank statement nikalna", "account statement download"
    ]
    
    # Reminder keywords
    reminder_keywords = ["reminder", "remind", "set reminder", "create reminder", "view reminder", "show reminder", "अनुस्मारक"]
    
    # Balance/transaction keywords
    banking_keywords = ["balance", "बैलेंस", "transaction", "transfer", "ट्रांसफर", "send money", "pay"]
    
    if any(keyword in msg_lower for keyword in statement_keywords + reminder_keywords + banking_keywords):
        intent = "banking_operation"
        logger.info("banking_keyword_detected", message=last_message, forced_intent=intent)
    
    state["current_intent"] = intent
    
    log_agent_decision(
        agent="intent_classifier",
        intent=intent,
        confidence=0.8,
    )
    
    logger.info("intent_classified", intent=intent, user_message=last_message)
    
    return state
