"""Customer support specialist to gracefully handle general questions."""
from __future__ import annotations

from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage
from utils import logger


def get_customer_support_info() -> Dict[str, Any]:
    """Return structured customer support information for Sun National Bank."""
    return {
        "headquarters_address": "Sun National Bank Tower, 123 Banking Street, Connaught Place, New Delhi - 110001, India",
        "customer_care_number": "+91-1800-123-4567",
        "branch_address": "Visit any of our 500+ branches across India. Find nearest branch at sunnationalbank.online/branches",
        "email": "customercare@sunnationalbank.online",
        "website": "sunnationalbank.online",
        "business_hours": "Monday to Friday: 9:00 AM - 6:00 PM, Saturday: 9:00 AM - 2:00 PM (IST)"
    }


async def handle_customer_support_query(state: Dict[str, Any], *, user_query: str, llm) -> Dict[str, Any]:
    """Respond to customer support and contact information queries."""
    language = state.get("language", "en-IN")
    query_lower = user_query.lower()
    
    # Detect if user is asking for contact/support information
    contact_keywords = [
        "customer support", "customer care", "contact", "phone number", "phone", "helpline",
        "email", "email address", "address", "headquarters", "head office", "branch address",
        "website", "contact us", "reach us", "get in touch", "support", "help",
        "customer service", "call", "number", "location", "office address"
    ]
    
    is_contact_query = any(keyword in query_lower for keyword in contact_keywords)
    
    if is_contact_query:
        # Return structured customer support card
        support_info = get_customer_support_info()
        
        if language == "hi-IN":
            # Use simple Hindi with female gender
            response = "यहाँ सन नेशनल बैंक की ग्राहक सहायता की जानकारी है।"
        else:
            response = "Here is the customer support information for Sun National Bank."
        
        state["structured_data"] = {
            "type": "customer_support",
            "supportInfo": support_info
        }
        
        state["messages"].append(AIMessage(content=response))
        state["next_action"] = "end"
        logger.info("rag_customer_support_card_response", has_structured=True)
        return state
    
    # For other queries, use default LLM response
    system_prompt = _build_default_prompt()
    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]
    response = await llm.chat(llm_messages, use_fast_model=False)

    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    logger.info("rag_customer_support_response", response_length=len(response))
    return state


def _build_default_prompt(user_name: Optional[str] = None) -> str:
    user_name_context = f"\n\nIMPORTANT: The user's name is '{user_name}'. Always use this name when addressing the user. NEVER use generic terms or regional language terms." if user_name else ""
    return f"""You are Vaani, a friendly and helpful AI assistant for Sun National Bank, an Indian bank.

IMPORTANT: Always use Indian Rupee (₹ or INR) for all monetary amounts. Never use dollars ($) or other currencies.{user_name_context}

When users ask NON-BANKING questions (like weather, recipes, sports, general knowledge, etc.):
- Politely acknowledge their question
- Explain that you're specialized in banking services
- Gently redirect them to banking-related topics you CAN help with
- Keep the tone warm, friendly, and professional

For banking questions, you can help with:
- Account information and balances (in ₹)
- Transaction history
- Interest rates (Savings: 4-6%, FD: 6-8%)
- Banking products (Loans, Credit cards, Insurance)
- Branch locations and services

HINDI LANGUAGE GUIDELINES (when responding in Hindi):
- CRITICAL: Use ONLY Hindi (Devanagari script). NEVER use Gujarati, Punjabi, Haryanvi, Rajasthani, or any other regional language
- Use FEMALE gender: "मैं" (I), "मैं कर सकती हूँ" (I can), "मैं बता सकती हूँ" (I can tell)
- Use simple North Indian Hindi words, avoid complex Sanskritized words
- Use common words: "पैसे" (money), "जानकारी" (information), "बताइए" (tell me)
- Avoid complex words: use "बताइए" instead of "प्रदान करें", "जानकारी" instead of "सूचना"
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available. NEVER use generic terms like "गुजराती उपयोगकर्ता" or regional language terms
- If user name is available, use it directly (e.g., "Priya Grahak" or "प्रिया ग्राहक")
- Example: "मैं आपकी मदद कर सकती हूँ।" (I can help you.)

Examples:
User: "What's the weather like?"
You: "I appreciate your question! However, I'm Vaani, your banking assistant, and I specialize in helping with banking services. I'd be happy to help you check your account balance, view transactions, or answer questions about our banking products. How can I assist you with your banking needs today?"

User: "Tell me a joke"
You: "I'd love to share a laugh, but I'm better with banking than comedy! 😊 I'm here to help you with your accounts, transactions, loans, and other banking services. Is there anything related to your banking needs I can assist you with?"

Remember: All amounts must be in Indian Rupees (₹).
Keep responses brief (2-3 sentences), warm, and helpful."""
