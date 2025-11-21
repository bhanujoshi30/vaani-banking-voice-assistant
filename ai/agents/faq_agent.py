"""
FAQ Agent
Handles general banking questions and information with RAG support
"""
from langchain_core.messages import AIMessage, HumanMessage
from utils import logger


def create_fallback_investment_info(investment_type: str) -> dict:
    """
    Create fallback investment info when RAG extraction fails
    Based on known investment scheme details
    """
    fallback_data = {
        "ppf": {
            "name": "PPF",
            "interest_rate": "7.1% per annum",
            "min_amount": "Rs. 500",
            "max_amount": "Rs. 1.5 lakhs",
            "tenure": "15 years",
            "eligibility": "Any Indian resident can open PPF account",
            "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction, tax-free interest and maturity",
            "description": "Long-term tax-saving investment scheme backed by Government of India",
            "features": [
                "Government guaranteed - zero risk",
                "Tax-free interest and maturity",
                "Flexible investment options",
                "Partial withdrawal after 7 years"
            ]
        },
        "nps": {
            "name": "NPS",
            "interest_rate": "8-12% (market-linked)",
            "min_amount": "Rs. 500",
            "max_amount": "No limit",
            "tenure": "Until 60 years",
            "eligibility": "Age 18-70 years, Indian citizens (resident and NRI)",
            "tax_benefits": "Section 80C: Rs. 1.5 lakhs + Section 80CCD(1B): Rs. 50,000 additional deduction",
            "description": "Market-linked retirement savings scheme with flexible investment options",
            "features": [
                "Market-linked returns",
                "Additional Rs. 50,000 tax deduction",
                "Flexible asset allocation",
                "Pension after retirement"
            ]
        },
        "ssy": {
            "name": "Sukanya Samriddhi Yojana",
            "interest_rate": "8.2% per annum",
            "min_amount": "Rs. 250",
            "max_amount": "Rs. 1.5 lakhs",
            "tenure": "21 years",
            "eligibility": "Girl child below 10 years of age, parents/guardians can open account",
            "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction, tax-free interest and maturity",
            "description": "Girl child savings scheme with highest interest rate among small savings schemes",
            "features": [
                "Highest interest rate (8.2%)",
                "Tax-free returns",
                "50% withdrawal after girl turns 18",
                "Government guaranteed"
            ]
        },
        "elss": {
            "name": "ELSS",
            "interest_rate": "Market-linked (varies)",
            "min_amount": "Rs. 500",
            "max_amount": "No limit",
            "tenure": "3 years lock-in",
            "eligibility": "Any Indian resident can invest",
            "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction",
            "description": "Tax-saving mutual funds with equity exposure and 3-year lock-in period",
            "features": [
                "Tax benefits under Section 80C",
                "Market-linked returns",
                "3-year lock-in period",
                "Equity exposure for growth"
            ]
        },
        "fd": {
            "name": "Fixed Deposit",
            "interest_rate": "6-8% per annum",
            "min_amount": "Rs. 1,000",
            "max_amount": "No limit",
            "tenure": "7 days to 10 years",
            "eligibility": "Any individual can open FD account",
            "tax_benefits": "TDS applicable on interest, no specific tax deduction",
            "description": "Safe investment with fixed returns and flexible tenure options",
            "features": [
                "Fixed returns guaranteed",
                "Flexible tenure",
                "Safe investment",
                "Premature withdrawal available"
            ]
        },
        "rd": {
            "name": "Recurring Deposit",
            "interest_rate": "6-7.5% per annum",
            "min_amount": "Rs. 100 per month",
            "max_amount": "No limit",
            "tenure": "6 months to 10 years",
            "eligibility": "Any individual can open RD account",
            "tax_benefits": "TDS applicable on interest",
            "description": "Regular monthly savings scheme with fixed returns",
            "features": [
                "Regular monthly savings",
                "Fixed returns",
                "Flexible tenure",
                "Disciplined savings habit"
            ]
        },
        "nsc": {
            "name": "NSC",
            "interest_rate": "7-9% per annum",
            "min_amount": "Rs. 1,000",
            "max_amount": "No limit",
            "tenure": "5 years",
            "eligibility": "Any individual can invest",
            "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction",
            "description": "Tax-saving savings certificate with fixed returns and government backing",
            "features": [
                "Tax benefits under Section 80C",
                "Fixed returns",
                "Government backed",
                "5-year tenure"
            ]
        }
    }
    
    return fallback_data.get(investment_type.lower())


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
    
    # Check if it's a general loan query (asking about available loans)
    general_loan_queries = [
        "what loans", "which loans", "available loans", "types of loans",
        "loan types", "loan products", "tell me about loans", "loans available",
        "what kind of loans", "loan options", "loan schemes"
    ]
    
    # Check if query is investment-related
    # Include specific scheme names to catch queries like "Tell me about ssy"
    investment_keywords = [
        "investment", "invest", "scheme", "ppf", "nps", "ssy", "sukanya", "elss",
        "fixed deposit", "fd", "recurring deposit", "rd", "nsc",
        "tax saving", "retirement", "pension", "savings", "mutual fund",
        "public provident fund", "national pension", "sukanya samriddhi",
        "equity linked", "national savings certificate"
    ]
    
    # Check if it's a general investment query
    general_investment_queries = [
        "what investments", "which investments", "available investments", "investment schemes",
        "investment types", "investment options", "tell me about investments", "investments available",
        "what investment schemes", "investment plans", "savings schemes", "tax saving schemes",
        "show me investment", "investment options available"
    ]
    
    is_loan_query = any(keyword in user_query.lower() for keyword in loan_keywords)
    is_general_loan_query = any(phrase in user_query.lower() for phrase in general_loan_queries)
    is_investment_query = any(keyword in user_query.lower() for keyword in investment_keywords)
    is_general_investment_query = any(phrase in user_query.lower() for phrase in general_investment_queries)
    
    # Check if it's a specific loan type query
    specific_loan_types = {
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
        "lap": "loan_against_property"
    }
    
    detected_loan_type = None
    query_lower = user_query.lower()
    for loan_name, loan_type in specific_loan_types.items():
        if loan_name in query_lower:
            detected_loan_type = loan_type
            break
    
    # Check if it's a specific investment type query
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
        "sukanya samridhi": "ssy",  # Common misspelling
        "sukanya samridhi yojana": "ssy",  # Common misspelling
        "elss": "elss",
        "tax saving mutual fund": "elss",
        "equity linked savings scheme": "elss",
        "fixed deposit": "fd",
        "fd": "fd",
        "recurring deposit": "rd",
        "rd": "rd",
        "nsc": "nsc",
        "national savings certificate": "nsc"
    }
    
    detected_investment_type = None
    # Check for exact matches first (longer phrases first to avoid partial matches)
    sorted_types = sorted(specific_investment_types.items(), key=lambda x: len(x[0]), reverse=True)
    for investment_name, investment_type in sorted_types:
        if investment_name in query_lower:
            detected_investment_type = investment_type
            break
    
    # Initialize context for RAG
    rag_context = ""
    
    # If it's a general investment query, return investment selection table
    if is_general_investment_query and not detected_investment_type:
        available_investments = [
            {
                "type": "ppf",
                "name": "PPF",
                "description": "Long-term tax-saving scheme",
                "icon": "🏦"
            },
            {
                "type": "nps",
                "name": "NPS",
                "description": "Market-linked retirement scheme",
                "icon": "👴"
            },
            {
                "type": "ssy",
                "name": "Sukanya Samriddhi Yojana",
                "description": "Girl child savings scheme",
                "icon": "👧"
            },
            {
                "type": "elss",
                "name": "ELSS",
                "description": "Tax-saving mutual funds",
                "icon": "📈"
            },
            {
                "type": "fd",
                "name": "Fixed Deposit",
                "description": "Safe investment with fixed returns",
                "icon": "💎"
            },
            {
                "type": "rd",
                "name": "Recurring Deposit",
                "description": "Regular monthly savings scheme",
                "icon": "💰"
            },
            {
                "type": "nsc",
                "name": "NSC",
                "description": "Tax-saving savings certificate",
                "icon": "📜"
            }
        ]
        
        # Generate response text
        if language == "hi-IN":
            response = "यहाँ उपलब्ध निवेश योजनाएं हैं। विस्तृत जानकारी के लिए किसी भी योजना पर क्लिक करें या बोलें:"
        else:
            response = "Here are the available investment schemes. Click or speak any scheme for detailed information:"
        
        state["structured_data"] = {
            "type": "investment_selection",
            "investments": available_investments
        }
        
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)
        state["next_action"] = "end"
        
        logger.info("faq_agent_response",
                   response_type="investment_selection_table",
                   investments_count=len(available_investments))
        
        return state
    
    # If it's a general loan query, return loan selection table
    if is_general_loan_query and not detected_loan_type:
        available_loans = [
            {
                "type": "home_loan",
                "name": "Home Loan",
                "description": "Buy your dream home",
                "icon": "🏠"
            },
            {
                "type": "personal_loan",
                "name": "Personal Loan",
                "description": "Instant financial solutions",
                "icon": "💳"
            },
            {
                "type": "auto_loan",
                "name": "Auto Loan",
                "description": "Cars, bikes & commercial vehicles",
                "icon": "🚗"
            },
            {
                "type": "education_loan",
                "name": "Education Loan",
                "description": "Study in India or abroad",
                "icon": "🎓"
            },
            {
                "type": "business_loan",
                "name": "Business Loan",
                "description": "MSME & SME financing",
                "icon": "💼"
            },
            {
                "type": "gold_loan",
                "name": "Gold Loan",
                "description": "Instant cash against gold ornaments",
                "icon": "🥇"
            },
            {
                "type": "loan_against_property",
                "name": "Loan Against Property",
                "description": "Unlock your property value",
                "icon": "🏢"
            }
        ]
        
        # Generate response text
        if language == "hi-IN":
            response = "हमारे पास निम्नलिखित ऋण प्रकार उपलब्ध हैं। विस्तृत जानकारी के लिए किसी भी ऋण प्रकार पर क्लिक करें या बोलें:"
        else:
            response = "We offer the following types of loans. Click or speak any loan type for detailed information:"
        
        state["structured_data"] = {
            "type": "loan_selection",
            "loans": available_loans
        }
        
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)
        state["next_action"] = "end"
        
        logger.info("faq_agent_response",
                   response_type="loan_selection_table",
                   loans_count=len(available_loans))
        
        return state
    
    if is_loan_query or is_investment_query:
        try:
            # Get RAG service - use appropriate collection based on query type
            documents_type = "investment" if is_investment_query else "loan"
            rag_service = get_rag_service(documents_type=documents_type)
            rag_context = rag_service.get_context_for_query(user_query, k=3)
            logger.info("rag_context_retrieved", 
                       query_length=len(user_query),
                       context_length=len(rag_context),
                       is_loan_query=is_loan_query,
                       is_investment_query=is_investment_query)
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

    # Extract structured investment data FIRST if this is an investment query
    # Try extraction even if RAG context is limited - we can still extract from detected type
    investment_info_extracted = None
    if is_investment_query and not is_general_investment_query:
        try:
            # Determine investment type from query for better extraction
            investment_type_hint = ""
            if detected_investment_type:
                investment_type_hint = f"\nNote: The user is asking about {detected_investment_type.replace('_', ' ').upper()}."
            
            # If no RAG context but we detected investment type, create a basic context
            if not rag_context and detected_investment_type:
                # Create basic context based on detected type
                scheme_contexts = {
                    "ppf": "PPF (Public Provident Fund) is a long-term savings scheme with 7.1% interest rate, 15 years tenure, tax benefits under Section 80C up to Rs. 1.5 lakhs.",
                    "nps": "NPS (National Pension System) is a market-linked retirement scheme with 8-12% returns, tax benefits under Section 80C (Rs. 1.5L) and 80CCD(1B) (Rs. 50K).",
                    "ssy": "Sukanya Samriddhi Yojana (SSY) is a girl child savings scheme with 8.2% interest rate, 21 years tenure, tax benefits under Section 80C up to Rs. 1.5 lakhs.",
                    "elss": "ELSS (Equity Linked Savings Scheme) are tax-saving mutual funds with 3-year lock-in, market-linked returns, tax benefits under Section 80C.",
                    "fd": "Fixed Deposit offers fixed interest rates 6-8% based on tenure, safe investment, flexible tenure options.",
                    "rd": "Recurring Deposit allows monthly savings with fixed interest rates, suitable for regular savings habit.",
                    "nsc": "NSC (National Savings Certificate) offers 7-9% interest rate, 5-year tenure, tax benefits under Section 80C."
                }
                rag_context = scheme_contexts.get(detected_investment_type, f"{detected_investment_type.replace('_', ' ').upper()} investment scheme information.")
            
            # Use LLM to extract structured investment information
            extraction_prompt = f"""Extract investment scheme information from the following context and return as JSON:
{rag_context if rag_context else "No specific context available, but extract general information about the investment scheme."}
{investment_type_hint}

Extract the following fields:
- name: Investment scheme name (e.g., "PPF", "NPS", "Sukanya Samriddhi Yojana") - REQUIRED
- interest_rate: Interest rate or returns as string (e.g., "7.1% p.a." or "8-12% market-linked")
- min_amount: Minimum investment amount with "Rs." prefix (e.g., "Rs. 500" or "Rs. 250")
- max_amount: Maximum investment amount with "Rs." prefix (e.g., "Rs. 1.5 lakhs" or "No limit")
- investment_amount: Alternative single string with range (e.g., "Rs. 500 to Rs. 1.5 lakhs per year")
- tenure: Investment tenure/duration (e.g., "15 years" or "Until 60 years")
- eligibility: Key eligibility criteria (concise, 1-2 sentences)
- tax_benefits: Tax benefits description (e.g., "Section 80C: Up to Rs. 1.5 lakhs deduction")
- description: Brief one-sentence description of the scheme
- features: Array of 3-5 key features as strings

IMPORTANT RULES:
1. All amounts MUST include "Rs." prefix (e.g., "Rs. 10,000", "Rs. 1.5 lakhs")
2. Extract actual values from the context, don't make up values
3. If a field is not found, omit it (don't include null or empty values)
4. Return ONLY valid JSON object, no markdown, no code blocks

Example output format:
{{
  "name": "PPF",
  "interest_rate": "7.1% per annum",
  "min_amount": "Rs. 500",
  "max_amount": "Rs. 1.5 lakhs",
  "tenure": "15 years",
  "eligibility": "Any Indian resident can open PPF account",
  "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction, tax-free interest",
  "description": "Long-term tax-saving investment scheme backed by Government",
  "features": ["Government guaranteed", "Tax-free interest", "Flexible investment options"]
}}"""
            
            extracted_json = await llm.chat(
                [{"role": "user", "content": extraction_prompt}],
                use_fast_model=True
            )
            
            # Try to parse JSON from response
            import json
            
            # Clean the response - remove markdown code blocks if present
            extracted_json = extracted_json.strip()
            if extracted_json.startswith("```json"):
                extracted_json = extracted_json[7:]
            elif extracted_json.startswith("```"):
                extracted_json = extracted_json[3:]
            if extracted_json.endswith("```"):
                extracted_json = extracted_json[:-3]
            extracted_json = extracted_json.strip()
            
            # Try to parse JSON directly first
            try:
                investment_info = json.loads(extracted_json)
                if investment_info and isinstance(investment_info, dict) and len(investment_info) > 0:
                    investment_info_extracted = investment_info
                    state["structured_data"] = {
                        "type": "investment",
                        "investmentInfo": investment_info
                    }
                    logger.info("investment_info_extracted", 
                               scheme_name=investment_info.get("name", "unknown"),
                               has_amount=bool(investment_info.get("min_amount") or investment_info.get("investment_amount")),
                               has_rate=bool(investment_info.get("interest_rate")))
            except json.JSONDecodeError:
                # If direct parse fails, try to find JSON object
                import re
                start_idx = extracted_json.find('{')
                if start_idx != -1:
                    brace_count = 0
                    end_idx = start_idx
                    for i in range(start_idx, len(extracted_json)):
                        if extracted_json[i] == '{':
                            brace_count += 1
                        elif extracted_json[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    if end_idx > start_idx:
                        try:
                            json_str = extracted_json[start_idx:end_idx + 1]
                            investment_info = json.loads(json_str)
                            if investment_info and isinstance(investment_info, dict) and len(investment_info) > 0:
                                investment_info_extracted = investment_info
                                state["structured_data"] = {
                                    "type": "investment",
                                    "investmentInfo": investment_info
                                }
                                logger.info("investment_info_extracted", 
                                           scheme_name=investment_info.get("name", "unknown"))
                        except json.JSONDecodeError as e:
                            logger.warning("investment_json_parse_error", error=str(e), response_preview=extracted_json[:200])
            
            # If extraction failed but we detected investment type, create fallback card
            # Also check if extracted info is empty/invalid
            if (not investment_info_extracted or 
                (isinstance(investment_info_extracted, dict) and len(investment_info_extracted) == 0)) and detected_investment_type:
                investment_info_extracted = create_fallback_investment_info(detected_investment_type)
                if investment_info_extracted:
                    state["structured_data"] = {
                        "type": "investment",
                        "investmentInfo": investment_info_extracted
                    }
                    logger.info("investment_fallback_created", scheme_type=detected_investment_type)
        except Exception as e:
            logger.error("investment_data_extraction_error", error=str(e))
            # Try fallback even on error
            if detected_investment_type:
                investment_info_extracted = create_fallback_investment_info(detected_investment_type)
                if investment_info_extracted:
                    state["structured_data"] = {
                        "type": "investment",
                        "investmentInfo": investment_info_extracted
                    }
                    logger.info("investment_fallback_created_on_error", scheme_type=detected_investment_type)
    
    # If we detected investment type but no extraction happened (e.g., no RAG context), use fallback
    if is_investment_query and not is_general_investment_query and detected_investment_type:
        if not investment_info_extracted or (isinstance(investment_info_extracted, dict) and len(investment_info_extracted) == 0):
            investment_info_extracted = create_fallback_investment_info(detected_investment_type)
            if investment_info_extracted and "structured_data" not in state:
                state["structured_data"] = {
                    "type": "investment",
                    "investmentInfo": investment_info_extracted
                }
                logger.info("investment_fallback_created_final", scheme_type=detected_investment_type)
    
    # Extract structured loan data FIRST if this is a loan query with RAG context
    loan_info_extracted = None
    if is_loan_query and rag_context:
        try:
            # Determine loan type from query for better extraction
            loan_type_hint = ""
            if detected_loan_type:
                loan_type_hint = f"\nNote: The user is asking about {detected_loan_type.replace('_', ' ').title()}."
            
            # Use LLM to extract structured loan information
            extraction_prompt = f"""Extract loan information from the following context and return as JSON:
{rag_context}
{loan_type_hint}

Extract the following fields:
- name: Loan product name (e.g., "Home Loan", "Personal Loan") - REQUIRED
- interest_rate: Interest rate as string (e.g., "8.35% - 9.50% p.a." or "10.49% - 18.00% p.a.")
- min_amount: Minimum loan amount with "Rs." prefix (e.g., "Rs. 5 lakhs" or "Rs. 50,000")
- max_amount: Maximum loan amount with "Rs." prefix (e.g., "Rs. 5 crores" or "Rs. 25 lakhs")
- loan_amount: Alternative single string with range (e.g., "Rs. 5 lakhs to Rs. 5 crores")
- tenure: Loan tenure/duration (e.g., "Up to 30 years" or "12 to 60 months")
- eligibility: Key eligibility criteria (concise, 1-2 sentences)
- description: Brief one-sentence description of the loan
- features: Array of 3-5 key features as strings

IMPORTANT RULES:
1. All amounts MUST include "Rs." prefix (e.g., "Rs. 10,000", "Rs. 1 crore")
2. Extract actual values from the context, don't make up values
3. If a field is not found, omit it (don't include null or empty values)
4. Return ONLY valid JSON object, no markdown, no code blocks

Example output format:
{{
  "name": "Home Loan",
  "interest_rate": "8.35% - 9.50% p.a.",
  "min_amount": "Rs. 5 lakhs",
  "max_amount": "Rs. 5 crores",
  "tenure": "Up to 30 years",
  "eligibility": "Age 21-65 years, minimum income Rs. 25,000/month",
  "description": "Finance for purchasing, constructing, or renovating your home",
  "features": ["Up to 90% financing", "Flexible repayment options", "Tax benefits available"]
}}"""
            
            extracted_json = await llm.chat(
                [{"role": "user", "content": extraction_prompt}],
                use_fast_model=True
            )
            
            # Try to parse JSON from response
            import json
            import re
            
            # Clean the response - remove markdown code blocks if present
            extracted_json = extracted_json.strip()
            if extracted_json.startswith("```json"):
                extracted_json = extracted_json[7:]
            elif extracted_json.startswith("```"):
                extracted_json = extracted_json[3:]
            if extracted_json.endswith("```"):
                extracted_json = extracted_json[:-3]
            extracted_json = extracted_json.strip()
            
            # Try to parse JSON directly first
            try:
                loan_info = json.loads(extracted_json)
                if loan_info and isinstance(loan_info, dict) and len(loan_info) > 0:
                    loan_info_extracted = loan_info
                    state["structured_data"] = {
                        "type": "loan",
                        "loanInfo": loan_info
                    }
                    logger.info("loan_info_extracted", 
                               loan_name=loan_info.get("name", "unknown"),
                               has_amount=bool(loan_info.get("min_amount") or loan_info.get("loan_amount")),
                               has_rate=bool(loan_info.get("interest_rate")))
            except json.JSONDecodeError:
                # If direct parse fails, try to find JSON object (handle nested braces)
                # Find the first { and match it with the last }
                start_idx = extracted_json.find('{')
                if start_idx != -1:
                    # Count braces to find matching closing brace
                    brace_count = 0
                    end_idx = start_idx
                    for i in range(start_idx, len(extracted_json)):
                        if extracted_json[i] == '{':
                            brace_count += 1
                        elif extracted_json[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    if end_idx > start_idx:
                        try:
                            json_str = extracted_json[start_idx:end_idx + 1]
                            loan_info = json.loads(json_str)
                            if loan_info and isinstance(loan_info, dict) and len(loan_info) > 0:
                                loan_info_extracted = loan_info
                                state["structured_data"] = {
                                    "type": "loan",
                                    "loanInfo": loan_info
                                }
                                logger.info("loan_info_extracted", 
                                           loan_name=loan_info.get("name", "unknown"),
                                           has_amount=bool(loan_info.get("min_amount") or loan_info.get("loan_amount")),
                                           has_rate=bool(loan_info.get("interest_rate")))
                        except json.JSONDecodeError as e:
                            logger.warning("loan_json_parse_error", error=str(e), response_preview=extracted_json[:200])
        except Exception as e:
            logger.error("loan_data_extraction_error", error=str(e))
    
    # Final check: If we detected investment type but no card was created, create fallback
    if is_investment_query and not is_general_investment_query and detected_investment_type:
        if not investment_info_extracted or not state.get("structured_data") or state.get("structured_data", {}).get("type") != "investment":
            investment_info_extracted = create_fallback_investment_info(detected_investment_type)
            if investment_info_extracted:
                state["structured_data"] = {
                    "type": "investment",
                    "investmentInfo": investment_info_extracted
                }
                logger.info("investment_fallback_created_final_check", scheme_type=detected_investment_type)
    
    # Generate response text
    if investment_info_extracted:
        # If we successfully extracted investment info, return a brief sentence
        # The card will show all the details
        investment_name = investment_info_extracted.get("name") or detected_investment_type or "investment scheme"
        # Clean up investment name
        if isinstance(investment_name, str):
            investment_name = investment_name.replace("_", " ").replace("-", " ").title()
        
        if language == "hi-IN":
            # Hindi translations for common investment schemes
            investment_name_hi = {
                "PPF": "पीपीएफ",
                "NPS": "एनपीएस",
                "Sukanya Samriddhi Yojana": "सुकन्या समृद्धि योजना",
                "SSY": "सुकन्या समृद्धि योजना",
                "ELSS": "ईएलएसएस",
                "Fixed Deposit": "फिक्स्ड डिपॉजिट",
                "Recurring Deposit": "रिकरिंग डिपॉजिट",
                "NSC": "नेशनल सेविंग्स सर्टिफिकेट"
            }.get(investment_name, investment_name)
            response = f"यहाँ {investment_name_hi} की विस्तृत जानकारी है।"
        else:
            response = f"Here are the details for {investment_name}."
    elif loan_info_extracted:
        # If we successfully extracted loan info, return a brief sentence
        # The card will show all the details
        loan_name = loan_info_extracted.get("name") or loan_info_extracted.get("title") or detected_loan_type or "loan"
        # Clean up loan name (remove underscores, capitalize)
        if isinstance(loan_name, str):
            loan_name = loan_name.replace("_", " ").replace("-", " ").title()
        
        if language == "hi-IN":
            # Hindi translations for common loan types
            loan_name_hi = {
                "Home Loan": "होम लोन",
                "Personal Loan": "पर्सनल लोन",
                "Auto Loan": "ऑटो लोन",
                "Education Loan": "एजुकेशन लोन",
                "Business Loan": "बिजनेस लोन",
                "Gold Loan": "गोल्ड लोन",
                "Loan Against Property": "प्रॉपर्टी के खिलाफ लोन"
            }.get(loan_name, loan_name)
            response = f"यहाँ {loan_name_hi} की विस्तृत जानकारी है।"
        else:
            response = f"Here are the details for {loan_name}."
    else:
        # Build message list for LLM for full response
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
    
    logger.info("faq_agent_response", 
               response_length=len(response),
               query_type="loan_query" if is_loan_query else "general",
               used_rag=bool(rag_context))
    
    return state
