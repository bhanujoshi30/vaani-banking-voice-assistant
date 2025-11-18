"""
FAQ Agent
Handles general banking questions and information
"""
from langchain_core.messages import AIMessage, HumanMessage
from utils import logger


async def faq_agent(state):
    """
    Handle general FAQ questions about banking products, services, rates, etc.
    
    Args:
        state: AgentState with messages, language, etc.
        
    Returns:
        Updated state with AI response
    """
    from services import get_llm_service
    
    # Get unified LLM service
    llm = get_llm_service()
    language = state.get("language", "en-IN")
    
    # Get the last user message
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    user_query = user_messages[-1].content if user_messages else "Hello"
    
    # Build system prompt for non-banking questions
    system_prompt = """You are Vaani, a friendly and helpful AI assistant for Sun National Bank, an Indian bank.

IMPORTANT: Always use Indian Rupee (₹ or INR) for all monetary amounts. Never use dollars ($) or other currencies.

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

Examples:
User: "What's the weather like?"
You: "I appreciate your question! However, I'm Vaani, your banking assistant, and I specialize in helping with banking services. I'd be happy to help you check your account balance, view transactions, or answer questions about our banking products. How can I assist you with your banking needs today?"

User: "Tell me a joke"
You: "I'd love to share a laugh, but I'm better with banking than comedy! 😊 I'm here to help you with your accounts, transactions, loans, and other banking services. Is there anything related to your banking needs I can assist you with?"

Remember: All amounts must be in Indian Rupees (₹).
Keep responses brief (2-3 sentences), warm, and helpful."""

    # Build message list for LLM
    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    # Use the main model for better, more natural responses
    response = await llm.chat(
        llm_messages,
        use_fast_model=False
    )
    
    # Add AI response to state
    ai_message = AIMessage(content=response)
    state["messages"].append(ai_message)
    state["next_action"] = "end"
    
    logger.info("faq_agent_response", response_length=len(response), query_type="non_banking")
    
    return state
