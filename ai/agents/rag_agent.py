"""Hybrid RAG supervisor agent that orchestrates specialist sub-agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage

from agents.rag_agents.customer_support_agent import handle_customer_support_query
from agents.rag_agents.investment_agent import (
    handle_general_investment_query,
    handle_investment_query,
)
from agents.rag_agents.loan_agent import (
    handle_general_loan_query,
    handle_loan_query,
)
from utils import logger


@dataclass
class QuerySignals:
    """Represents detected intents for the RAG supervisor."""

    is_loan_query: bool
    is_general_loan_query: bool
    is_investment_query: bool
    is_general_investment_query: bool
    detected_loan_type: Optional[str]
    detected_investment_type: Optional[str]


async def rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for the RAG supervisor. Delegates to specialist agents."""
    from services import get_llm_service

    llm = get_llm_service()
    language = state.get("language", "en-IN")
    user_query = _extract_latest_user_query(state) or "Hello"
    current_intent = state.get("current_intent", "")

    # Check if this is a language change request
    # BUT: Only process if it's actually a language change (not a false positive)
    if current_intent == "language_change":
        result = await handle_language_change(state, user_query, language, llm)
        # If handle_language_change cleared the intent (false positive), continue processing
        if state.get("current_intent") != "language_change":
            # Intent was cleared, process as regular query
            current_intent = state.get("current_intent", "other")
        else:
            # Language change was successful, return
            return result

    # Extract conversation context to help detect loan/investment queries
    conversation_context = _extract_conversation_context(state, max_pairs=3)
    
    signals = _detect_query_signals(user_query, conversation_context=conversation_context)
    logger.info(
        "rag_supervisor_signals",
        is_loan=signals.is_loan_query,
        is_investment=signals.is_investment_query,
        detected_loan=signals.detected_loan_type,
        detected_investment=signals.detected_investment_type,
        has_conversation_context=bool(conversation_context),
    )

    # IMPORTANT: Only show general investment list if:
    # 1. It's a general investment query AND
    # 2. No specific investment type was detected
    # This prevents showing the list when user asks about a specific scheme like "सुकन्या समृद्धि योजना"
    if signals.is_general_investment_query and not signals.detected_investment_type:
        return handle_general_investment_query(state, language)

    if signals.is_general_loan_query and not signals.detected_loan_type:
        return handle_general_loan_query(state, language)

    if signals.is_investment_query:
        await handle_investment_query(
            state,
            user_query=user_query,
            language=language,
            llm=llm,
            detected_investment_type=signals.detected_investment_type,
        )
        return state

    if signals.is_loan_query:
        await handle_loan_query(
            state,
            user_query=user_query,
            language=language,
            llm=llm,
            detected_loan_type=signals.detected_loan_type,
        )
        return state

    await handle_customer_support_query(state, user_query=user_query, llm=llm)
    return state


def _extract_latest_user_query(state: Dict[str, Any]) -> Optional[str]:
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    return user_messages[-1].content if user_messages else None


def _extract_conversation_context(state: Dict[str, Any], max_pairs: int = 3) -> str:
    """Extract conversation context from previous message pairs."""
    messages = state.get("messages", [])
    conversation_context = ""
    
    if len(messages) > 1:
        # Get exactly the last max_pairs pairs (excluding current message)
        recent_messages = []
        pairs_collected = 0
        i = len(messages) - 2  # Start from second-to-last message (skip current)
        
        while i >= 0 and pairs_collected < max_pairs:
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
        
        # Build conversation context from collected pairs
        if recent_messages:
            for msg in recent_messages:
                content = msg.content if hasattr(msg, "content") else str(msg)
                conversation_context += f" {content}"
    
    return conversation_context.lower()


def _detect_query_signals(user_query: str, conversation_context: str = "") -> QuerySignals:
    query_lower = user_query.lower()
    
    # Combine current query with conversation context for better detection
    combined_text = f"{conversation_context} {query_lower}".lower() if conversation_context else query_lower

    loan_keywords = [
        "loan",
        "interest rate",
        "emi",
        "eligibility",
        "documents required",
        "home loan",
        "personal loan",
        "auto loan",
        "car loan",
        "education loan",
        "business loan",
        "gold loan",
        "property loan",
        "mortgage",
        "down payment",
        "processing fee",
        "prepayment",
        "tenure",
        "collateral",
        # Context-aware keywords (check in combined text)
        "against property",  # When combined with loan context
        "loan against property",
        # Hindi keywords
        "udhar",
        "udhaar",
        "कर्ज",
        "ऋण",
        "लोन",
        "उधार",
        "उधारी",
        "ब्याज दर",
        "होम लोन",
        "पर्सनल लोन",
        "ऑटो लोन",
        "एजुकेशन लोन",
        "बिजनेस लोन",
        "गोल्ड लोन",
    ]

    general_loan_queries = [
        "what loans",
        "which loans",
        "available loans",
        "types of loans",
        "loan types",
        "loan products",
        "tell me about loans",
        "loans available",
        "what kind of loans",
        "loan options",
        "loan schemes",
        "loan information",
        "loan info",
        "show me loans",
        "list loans",
        "all loans",
        # Hindi general loan queries (only when NO specific loan type is mentioned)
        "कौन से लोन",
        "कौन सी लोन",
        "कौन सा लोन",
        "कौन से ऋण",
        "कौन सी ऋण",
        "कौन सा ऋण",
        # Note: "लोन के बारे में" and "ऋण के बारे में" are removed from general queries
        # because they match specific queries like "home loan ke baare mein" or "होम लोन के बारे में"
        # Only match if it's just "लोन" or "ऋण" without a specific type before "के बारे में"
        "उधार के बारे में",
        "कर्ज के बारे में",
        "मुझे लोन चाहिए",
        "मुझे ऋण चाहिए",
        "मुझे उधार चाहिए",
        "मुझे कर्ज चाहिए",
        "बैंक से उधार",
        "बैंक से कर्ज",
        "बैंक से लोन",
        "बैंक से ऋण",
        "पैसे उधार",
        "पैसे कर्ज",
        "लोन की जानकारी",
        "लोन जानकारी",
        "ऋण की जानकारी",
        "ऋण जानकारी",
    ]

    investment_keywords = [
        "investment",
        "invest",
        "scheme",
        "ppf",
        "nps",
        "ssy",
        "sukanya",
        "elss",
        "fixed deposit",
        "fd",
        "recurring deposit",
        "rd",
        "nsc",
        "tax saving",
        "retirement",
        "pension",
        "savings",
        "mutual fund",
        "public provident fund",
        "national pension",
        "sukanya samriddhi",
        "equity linked",
        "national savings certificate",
        # Hindi keywords
        "nivesh",
        "निवेश",
        "निवेश करना",
        "योजना",
        "स्कीम",
        "पीपीएफ",
        "एनपीएस",
        "सुकन्या",
        "फिक्स्ड डिपॉजिट",
        "एफडी",
        "रिकरिंग डिपॉजिट",
        "आरडी",
        "टैक्स सेविंग",
        "बचत",
        "पेंशन",
        "रिटायरमेंट",
    ]

    general_investment_queries = [
        "what investments",
        "which investments",
        "available investments",
        "investment schemes",
        "investment types",
        "investment options",
        "tell me about investments",
        "investments available",
        "what investment schemes",
        "investment plans",
        "savings schemes",
        "tax saving schemes",
        "show me investment",
        "investment options available",
        # Hindi general investment queries
        "कौन सी योजना",
        "कौन सी स्कीम",
        "कौन से निवेश",
        "कौन सी निवेश योजना",
        "निवेश योजना",
        "निवेश स्कीम",
        "निवेश के बारे में",
        "योजना के बारे में",
        "स्कीम के बारे में",
        "मुझे निवेश करना है",
        "पैसे निवेश करना",
        "पैसे निवेश",
        "निवेश करने के लिए",
        "कुछ योजना",
        "कुछ स्कीम",
        "कुछ निवेश",
        "निवेश की जानकारी",
        "योजना की जानकारी",
        "स्कीम की जानकारी",
    ]

    specific_loan_types = {
        # English loan types
        "home loan": "home_loan",
        "home_loan": "home_loan",
        "personal loan": "personal_loan",
        "personal_loan": "personal_loan",
        "auto loan": "auto_loan",
        "auto_loan": "auto_loan",
        "car loan": "auto_loan",
        "education loan": "education_loan",
        "education_loan": "education_loan",
        "business loan": "business_loan",
        "business_loan": "business_loan",
        "gold loan": "gold_loan",
        "gold_loan": "gold_loan",
        "loan against property": "loan_against_property",
        "loan_against_property": "loan_against_property",
        "property loan": "loan_against_property",
        "lap": "loan_against_property",
        # Hindi loan types
        "होम लोन": "home_loan",
        "होमलोन": "home_loan",
        "पर्सनल लोन": "personal_loan",
        "पर्सनललोन": "personal_loan",
        "ऑटो लोन": "auto_loan",
        "ऑटोलोन": "auto_loan",
        "एजुकेशन लोन": "education_loan",
        "एजुकेशनलोन": "education_loan",
        "बिजनेस लोन": "business_loan",
        "बिजनेसलोन": "business_loan",
        "गोल्ड लोन": "gold_loan",
        "गोल्डलोन": "gold_loan",
        "प्रॉपर्टी लोन": "loan_against_property",
        "प्रॉपर्टी के खिलाफ लोन": "loan_against_property",
    }

    specific_investment_types = {
        "ppf": "ppf",
        "public provident fund": "ppf",
        "nps": "nps",
        "national pension": "nps",
        "national pension system": "nps",
        "ssy": "ssy",
        "sukanya": "ssy",
        "sukanya samriddhi": "ssy",
        "sukanya samriddhi yojana": "ssy",
        "sukanya samridhi": "ssy",
        "sukanya samridhi yojana": "ssy",
        "elss": "elss",
        "tax saving mutual fund": "elss",
        "equity linked savings scheme": "elss",
        "fixed deposit": "fd",
        "fd": "fd",
        "recurring deposit": "rd",
        "rd": "rd",
        "nsc": "nsc",
        "national savings certificate": "nsc",
        # Hindi investment types
        "पीपीएफ": "ppf",
        "पब्लिक प्रोविडेंट फंड": "ppf",
        "एनपीएस": "nps",
        "नेशनल पेंशन": "nps",
        "नेशनल पेंशन सिस्टम": "nps",
        "सुकन्या": "ssy",
        "सुकन्या समृद्धि": "ssy",
        "सुकन्या समृद्धि योजना": "ssy",
        "ईएलएसएस": "elss",
        "टैक्स सेविंग म्यूचुअल फंड": "elss",
        "फिक्स्ड डिपॉजिट": "fd",
        "एफडी": "fd",
        "रिकरिंग डिपॉजिट": "rd",
        "आरडी": "rd",
        "नेशनल सेविंग्स सर्टिफिकेट": "nsc",
        "एनएससी": "nsc",
    }

    # CRITICAL: Check if this is a general loan query FIRST
    # If it's a general query, don't use conversation context to detect loan types
    # This prevents showing previous loan details when user asks for loan list again
    is_general_loan_query = any(phrase in query_lower for phrase in general_loan_queries)
    
    # IMPORTANT: Check for specific loan types FIRST (before general queries)
    # PRIORITIZE CURRENT QUERY over conversation context to avoid false matches
    # Sort by length (longest first) to match longer phrases first (e.g., "home loan" before "loan")
    detected_loan_type = None
    sorted_loan_types = sorted(specific_loan_types.items(), key=lambda item: len(item[0]), reverse=True)
    
    # FIRST: Check in current query ONLY (prioritize what user is asking NOW)
    for loan_name, loan_type in sorted_loan_types:
        if loan_name in query_lower:
            detected_loan_type = loan_type
            logger.info(
                "loan_type_detected_from_current_query",
                loan_name=loan_name,
                loan_type=loan_type,
                query=user_query
            )
            break
    
    # SECOND: If not found in current query AND it's NOT a general loan query,
    # check combined text (with context) for context-aware matches
    # This handles follow-up queries like "tell me more" after "business loan"
    # BUT: Skip context check if user is asking for general loan information (fresh start)
    if not detected_loan_type and not is_general_loan_query:
        for loan_name, loan_type in sorted_loan_types:
            if loan_name in combined_text:
                # Special handling for "against property" - only match if there's loan context
                if loan_name == "loan against property" or loan_name == "property loan":
                    # Check if previous context mentions loans
                    if "loan" in conversation_context or "लोन" in conversation_context or "ऋण" in conversation_context:
                        detected_loan_type = loan_type
                        logger.info(
                            "loan_type_detected_from_context",
                            loan_name=loan_name,
                            loan_type=loan_type,
                            context=conversation_context[:100]
                        )
                        break
                else:
                    # Only use context if current query doesn't mention a different loan type
                    # This prevents "business loan" in context from matching when user asks "gold loan"
                    current_query_has_other_loan = any(
                        other_loan in query_lower 
                        for other_loan in specific_loan_types.keys() 
                        if other_loan != loan_name
                    )
                    if not current_query_has_other_loan:
                        detected_loan_type = loan_type
                        logger.info(
                            "loan_type_detected_from_combined_text",
                            loan_name=loan_name,
                            loan_type=loan_type,
                            query=user_query,
                            context=conversation_context[:100]
                        )
                        break

    # IMPORTANT: Check for specific investment types FIRST (before general queries)
    # PRIORITIZE CURRENT QUERY over conversation context to avoid false matches
    # Sort by length (longest first) to match longer phrases first (e.g., "sukanya samriddhi yojana" before "sukanya")
    detected_investment_type = None
    sorted_investment_types = sorted(specific_investment_types.items(), key=lambda item: len(item[0]), reverse=True)
    
    # FIRST: Check in current query ONLY (prioritize what user is asking NOW)
    for investment_name, investment_type in sorted_investment_types:
        if investment_name in query_lower:
            detected_investment_type = investment_type
            logger.info(
                "investment_type_detected_from_current_query",
                investment_name=investment_name,
                investment_type=investment_type,
                query=user_query
            )
            break
    
    # SECOND: If not found in current query, check combined text (with context) for context-aware matches
    # This handles follow-up queries like "tell me more" after "ppf"
    if not detected_investment_type:
        for investment_name, investment_type in sorted_investment_types:
            if investment_name in combined_text:
                detected_investment_type = investment_type
                logger.info(
                    "investment_type_detected_from_combined_text",
                    investment_name=investment_name,
                    investment_type=investment_type,
                    query=user_query,
                    context=conversation_context[:100]
                )
                break

    # Check if it's a general loan query (only if no specific loan type was detected)
    # Use the pre-computed is_general_loan_query value
    is_general_loan = False
    if not detected_loan_type:
        # Only check general queries if no specific loan type was found
        is_general_loan = is_general_loan_query
    else:
        # If specific loan type detected, don't treat as general query
        is_general_loan = False

    # Check loan keywords in combined text (with context) for better detection
    # Special handling for context-aware keywords
    is_loan_query = False
    for keyword in loan_keywords:
        if keyword in combined_text:
            # For "against property", only match if there's loan context
            if keyword == "against property":
                if "loan" in conversation_context or "लोन" in conversation_context or "ऋण" in conversation_context:
                    is_loan_query = True
                    break
            else:
                is_loan_query = True
                break
    
    # Also check if conversation context mentions loans and current query is brief follow-up
    # BUT: Skip this if it's a general loan query (user wants fresh start, not follow-up)
    if not is_loan_query and conversation_context and not is_general_loan_query:
        # If previous context has loans and current query is brief (likely a follow-up)
        has_loan_context = any(word in conversation_context for word in ["loan", "लोन", "ऋण", "loans", "products", "options"])
        is_brief_followup = len(user_query.split()) <= 3  # 3 words or less
        
        # Common follow-up patterns
        followup_patterns = ["against property", "property", "gold", "home", "personal", "business", "education", "auto"]
        is_followup = any(pattern in query_lower for pattern in followup_patterns)
        
        if has_loan_context and (is_brief_followup or is_followup):
            is_loan_query = True
            # Try to detect loan type from follow-up
            if not detected_loan_type:
                if "property" in query_lower or "against property" in query_lower:
                    detected_loan_type = "loan_against_property"
                elif "gold" in query_lower:
                    detected_loan_type = "gold_loan"
                elif "home" in query_lower:
                    detected_loan_type = "home_loan"
                elif "personal" in query_lower:
                    detected_loan_type = "personal_loan"
                elif "business" in query_lower:
                    detected_loan_type = "business_loan"
                elif "education" in query_lower:
                    detected_loan_type = "education_loan"
                elif "auto" in query_lower or "car" in query_lower:
                    detected_loan_type = "auto_loan"

    # Check if it's a general investment query (only if no specific investment type was detected)
    is_general_investment = False
    if not detected_investment_type:
        # Only check general queries if no specific investment type was found
        is_general_investment = any(phrase in query_lower for phrase in general_investment_queries)
    else:
        # If specific investment type detected, don't treat as general query
        is_general_investment = False

    return QuerySignals(
        is_loan_query=is_loan_query,
        is_general_loan_query=is_general_loan,
        is_investment_query=any(keyword in query_lower for keyword in investment_keywords),
        is_general_investment_query=is_general_investment,
        detected_loan_type=detected_loan_type,
        detected_investment_type=detected_investment_type,
    )


async def handle_language_change(
    state: Dict[str, Any],
    user_query: str,
    current_language: str,
    llm
) -> Dict[str, Any]:
    """
    Handle language change requests from users.
    
    Args:
        state: Current agent state
        user_query: User's query requesting language change
        current_language: Current language code (e.g., "en-IN", "hi-IN")
        llm: LLM service instance
        
    Returns:
        Updated state with language change response
    """
    from langchain_core.messages import AIMessage
    
    query_lower = user_query.lower()
    
    # Detect requested language
    hindi_keywords = ["hindi", "हिंदी", "हिन्दी", "hindi me", "hindi mein", "हिंदी में"]
    english_keywords = ["english", "अंग्रेजी", "english me", "english mein", "अंग्रेजी में"]
    
    requested_language = None
    if any(keyword in query_lower for keyword in hindi_keywords):
        requested_language = "hi-IN"
    elif any(keyword in query_lower for keyword in english_keywords):
        requested_language = "en-IN"
    
    # If language not detected from keywords, check if user is just asking to change language
    # without specifying which one - in this case, ask them which language they want
    if not requested_language:
        # Check if this is a generic "change language" request
        generic_change_keywords = [
            "change language", "switch language", "change the language", "switch the language",
            "भाषा बदलें", "भाषा बदलो", "भाषा बदलना चाहता", "भाषा बदलना चाहती"
        ]
        is_generic_request = any(keyword in query_lower for keyword in generic_change_keywords)
        
        if is_generic_request:
            # Ask user which language they want
            if current_language == "hi-IN":
                response = "कृपया बताएं कि आप किस भाषा में बात करना चाहते हैं - हिंदी या अंग्रेजी?"
            else:
                response = "Which language would you like to use - Hindi or English?"
            
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            state["structured_data"] = {
                "type": "language_change",
                "requested_language": None,
                "current_language": current_language,
                "changed": False,
                "awaiting_selection": True,
            }
            
            logger.info(
                "language_change_awaiting_selection",
                current_language=current_language,
                user_query=user_query,
            )
            
            return state
    
    # If language not detected from keywords, use LLM to detect
    # BUT: Only use LLM if query explicitly mentions language change intent
    # Don't use LLM for queries that might be loan/product queries (e.g., "मुद्रा लोन")
    if not requested_language:
        # Check if query explicitly mentions language change intent
        explicit_language_intent = any(phrase in query_lower for phrase in [
            "change language", "switch language", "change to", "switch to",
            "भाषा बदल", "भाषा बदलें", "भाषा बदलो"
        ])
        
        # Also check for loan/product keywords that should NOT trigger language change
        loan_product_keywords = [
            "loan", "लोन", "ऋण", "mudra", "मुद्रा", "business", "बिजनेस",
            "home", "होम", "personal", "पर्सनल", "gold", "गोल्ड"
        ]
        has_loan_product_keyword = any(keyword in query_lower for keyword in loan_product_keywords)
        
        # Only use LLM if there's explicit language intent AND no loan/product keywords
        if explicit_language_intent and not has_loan_product_keyword:
            detection_prompt = f"""The user wants to change language. Current language is {current_language}.
User query: "{user_query}"

Determine which language they want:
- "hi-IN" for Hindi
- "en-IN" for English

IMPORTANT: Only respond with a language code if the user explicitly wants to change language.
If the query is about loans, products, or other topics, respond with "NO_CHANGE".

Reply with ONLY the language code or "NO_CHANGE", nothing else."""
            detected = await llm.chat([{"role": "user", "content": detection_prompt}], use_fast_model=True)
            detected = detected.strip().upper()
            if "NO_CHANGE" in detected or "NO" in detected:
                # Not a language change request, treat as regular query
                logger.info("language_change_llm_rejected", query=user_query[:100], detected=detected)
                requested_language = None
            elif "HI" in detected or "HINDI" in detected:
                requested_language = "hi-IN"
            elif "EN" in detected or "ENGLISH" in detected:
                requested_language = "en-IN"
        else:
            # No explicit language intent or has loan/product keywords - not a language change
            logger.info("language_change_not_detected", 
                       query=user_query[:100],
                       has_explicit_intent=explicit_language_intent,
                       has_loan_product_keyword=has_loan_product_keyword)
            requested_language = None
    
    # CRITICAL: If still not detected, DO NOT default to toggle
    # This prevents false positives (e.g., "मुद्रा लोन" being interpreted as language change)
    # Only change language if we have explicit confirmation
    if not requested_language:
        # No language detected - this is NOT a language change request
        # Clear the language_change intent and let the query be handled as a regular query
        logger.info("language_change_no_language_detected", 
                   query=user_query[:100],
                   current_language=current_language)
        # Clear the incorrect intent and let the query be processed normally
        state["current_intent"] = "other"
        # Don't return early - let the query fall through to normal processing
        # The rag_agent will handle it as a regular query
        # We'll just skip the language change logic and continue
    
    # Check if user is requesting the current language
    if requested_language == current_language:
        if current_language == "hi-IN":
            response = "आप पहले से ही हिंदी भाषा में बात कर रहे हैं। मैं आपकी कैसे मदद कर सकती हूं?"
        else:
            response = "You are already speaking in English. How can I help you?"
    else:
        # Update language in state
        state["language"] = requested_language
        
        # Generate response in the new language
        if requested_language == "hi-IN":
            response = "ठीक है! अब मैं हिंदी में बात करूंगी। मैं आपकी कैसे मदद कर सकती हूं?"
        else:
            response = "Sure! I'll now speak in English. How can I help you?"
    
    # Add response to messages
    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    
    # Set structured data to indicate language change
    state["structured_data"] = {
        "type": "language_change",
        "requested_language": requested_language,
        "current_language": current_language,
        "changed": requested_language != current_language,
    }
    
    logger.info(
        "language_change_handled",
        current_language=current_language,
        requested_language=requested_language,
        changed=requested_language != current_language,
        user_query=user_query,
    )
    
    return state
