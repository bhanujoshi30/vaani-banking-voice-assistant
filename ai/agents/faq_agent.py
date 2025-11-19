"""
FAQ Agent
Handles general banking questions and information with RAG support
"""
from langchain_core.messages import AIMessage, HumanMessage
from utils import logger


async def faq_agent(state):
    """
    Handle general FAQ questions about banking products, services, rates, etc.
    Uses RAG for loan-related queries to provide accurate, document-based answers.
    
    Args:
        state: AgentState with messages, language, etc.
        
    Returns:
        Updated state with AI response
    """
    from services import get_llm_service
    from services.rag_service import get_rag_service
    
    # Get unified LLM service
    llm = get_llm_service()
    language = state.get("language", "en-IN")
    
    # Get the last user message
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    user_query = user_messages[-1].content if user_messages else "Hello"
    
    # Check if query is loan-related
    loan_keywords = [
        "loan", "interest rate", "emi", "eligibility", "documents required",
        "home loan", "personal loan", "auto loan", "car loan", "education loan",
        "business loan", "gold loan", "property loan", "mortgage",
        "down payment", "processing fee", "prepayment", "tenure", "collateral"
    ]
    
    is_loan_query = any(keyword in user_query.lower() for keyword in loan_keywords)
    
    # Initialize context for RAG
    rag_context = ""
    
    if is_loan_query:
        try:
            # Get RAG service and retrieve relevant context
            rag_service = get_rag_service()
            rag_context = rag_service.get_context_for_query(user_query, k=3)
            logger.info("rag_context_retrieved", 
                       query_length=len(user_query),
                       context_length=len(rag_context),
                       is_loan_query=True)
        except Exception as e:
            logger.error("rag_retrieval_error", error=str(e))
            rag_context = ""
    
    # Build system prompt
    if rag_context:
        # RAG-enhanced prompt for loan queries
        system_prompt = f"""You are Vaani, a helpful AI assistant for Sun National Bank (an Indian bank).

The user has asked a question about banking products/loans. Below is relevant information from our official product documentation:

{rag_context}

Based on the above information, provide a clear, accurate, and helpful answer to the user's question.

IMPORTANT GUIDELINES:
- Always use Indian Rupees (₹ or INR) for all monetary amounts
- Base your answer primarily on the provided documentation
- If the documentation doesn't fully answer the question, acknowledge that and provide general guidance
- Be concise but comprehensive
- Use bullet points for lists of features, requirements, or steps
- If mentioning interest rates or fees, include the range (e.g., "8.50% - 11.50% p.a.")
- For eligibility or documents, distinguish between salaried and self-employed if relevant

Keep your response helpful and professional."""
    else:
        # Standard prompt for non-loan queries
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
    
    # Extract structured loan data if this is a loan query with RAG context
    if is_loan_query and rag_context:
        try:
            # Use LLM to extract structured loan information
            extraction_prompt = f"""Extract loan information from the following context and return as JSON:
{rag_context}

Extract:
- name/title of the loan product
- interest_rate (as number or range like "8.5-11.5")
- min_amount and max_amount (loan amount range)
- tenure (loan duration)
- eligibility (key eligibility criteria)
- description (brief description)
- features (list of key features)

Return only valid JSON with these fields, or empty object if not found."""
            
            extracted_json = await llm.chat(
                [{"role": "user", "content": extraction_prompt}],
                use_fast_model=True
            )
            
            # Try to parse JSON from response
            import json
            import re
            # Extract JSON from response (might be wrapped in markdown or text)
            json_match = re.search(r'\{[^{}]*\}', extracted_json, re.DOTALL)
            if json_match:
                try:
                    loan_info = json.loads(json_match.group())
                    if loan_info:
                        state["structured_data"] = {
                            "type": "loan",
                            "loanInfo": loan_info
                        }
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error("loan_data_extraction_error", error=str(e))
    
    # Add AI response to state
    ai_message = AIMessage(content=response)
    state["messages"].append(ai_message)
    state["next_action"] = "end"
    
    logger.info("faq_agent_response", 
               response_length=len(response),
               query_type="loan_query" if is_loan_query else "general",
               used_rag=bool(rag_context))
    
    return state
