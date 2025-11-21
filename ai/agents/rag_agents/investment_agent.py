"""Specialist investment agent invoked by the RAG supervisor."""
from __future__ import annotations

from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage
from utils import logger


def create_fallback_investment_info(investment_type: str) -> Optional[Dict[str, Any]]:
    """Create fallback investment info when RAG extraction fails."""
    fallback_data: Dict[str, Dict[str, Any]] = {
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
                "Partial withdrawal after 7 years",
            ],
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
                "Pension after retirement",
            ],
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
                "Government guaranteed",
            ],
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
                "Equity exposure for growth",
            ],
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
                "Premature withdrawal available",
            ],
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
                "Disciplined savings habit",
            ],
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
                "5-year tenure",
            ],
        },
    }

    return fallback_data.get(investment_type.lower()) if investment_type else None


def handle_general_investment_query(state: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Return interactive card for generic investment discovery."""
    available_investments = [
        {"type": "ppf", "name": "PPF", "description": "Long-term tax-saving scheme", "icon": "🏦"},
        {"type": "nps", "name": "NPS", "description": "Market-linked retirement scheme", "icon": "👴"},
        {"type": "ssy", "name": "Sukanya Samriddhi Yojana", "description": "Girl child savings scheme", "icon": "👧"},
        {"type": "elss", "name": "ELSS", "description": "Tax-saving mutual funds", "icon": "📈"},
        {"type": "fd", "name": "Fixed Deposit", "description": "Safe investment with fixed returns", "icon": "💎"},
        {"type": "rd", "name": "Recurring Deposit", "description": "Regular monthly savings scheme", "icon": "💰"},
        {"type": "nsc", "name": "NSC", "description": "Tax-saving savings certificate", "icon": "📜"},
    ]

    if language == "hi-IN":
        response = "यहाँ उपलब्ध निवेश योजनाएं हैं। विस्तृत जानकारी के लिए किसी भी योजना पर क्लिक करें या बोलें:"
    else:
        response = "Here are the available investment schemes. Click or speak any scheme for detailed information:"

    state["structured_data"] = {"type": "investment_selection", "investments": available_investments}
    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"

    logger.info(
        "rag_investment_selection_response",
        response_type="investment_selection_table",
        investments_count=len(available_investments),
    )
    return state


async def handle_investment_query(
    state: Dict[str, Any],
    *,
    user_query: str,
    language: str,
    llm,
    detected_investment_type: Optional[str],
) -> Dict[str, Any]:
    """Provide detailed investment information using RAG and fallback cards."""
    from services.rag_service import get_rag_service

    rag_context = ""
    try:
        rag_service = get_rag_service(documents_type="investment")
        rag_filter = None
        if detected_investment_type:
            rag_filter = {"scheme_type": detected_investment_type}
        rag_context = rag_service.get_context_for_query(
            user_query,
            k=2 if rag_filter else 3,
            filter=rag_filter,
        )
        logger.info(
            "rag_investment_context_retrieved",
            query_length=len(user_query),
            context_length=len(rag_context),
            metadata_filtered=bool(rag_filter),
        )
    except Exception as exc:
        logger.error("rag_investment_retrieval_error", error=str(exc))

    system_prompt = _build_rag_system_prompt(rag_context)
    investment_info_extracted: Optional[Dict[str, Any]] = None

    if detected_investment_type and not rag_context:
        rag_context = _build_detected_investment_context(detected_investment_type)

    if detected_investment_type:
        investment_info_extracted = await _extract_investment_card(
            state,
            llm,
            rag_context,
            detected_investment_type,
        )

    if detected_investment_type and not investment_info_extracted:
        investment_info_extracted = create_fallback_investment_info(detected_investment_type)
        if investment_info_extracted:
            state["structured_data"] = {"type": "investment", "investmentInfo": investment_info_extracted}
            logger.info("investment_fallback_created_final", scheme_type=detected_investment_type)

    if investment_info_extracted:
        response = _build_investment_response_text(investment_info_extracted, language)
        state["messages"].append(AIMessage(content=response))
        state["next_action"] = "end"
        logger.info("rag_investment_agent_response", has_structured=True)
        return state

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]
    response = await llm.chat(llm_messages, use_fast_model=False)

    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    logger.info("rag_investment_agent_response", has_structured=False)
    return state


def _build_detected_investment_context(investment_type: str) -> str:
    scheme_contexts = {
        "ppf": "PPF (Public Provident Fund) is a long-term savings scheme with 7.1% interest rate, 15 years tenure, tax benefits under Section 80C up to Rs. 1.5 lakhs.",
        "nps": "NPS (National Pension System) is a market-linked retirement scheme with 8-12% returns, tax benefits under Section 80C (Rs. 1.5L) and 80CCD(1B) (Rs. 50K).",
        "ssy": "Sukanya Samriddhi Yojana (SSY) is a girl child savings scheme with 8.2% interest rate, 21 years tenure, tax benefits under Section 80C up to Rs. 1.5 lakhs.",
        "elss": "ELSS (Equity Linked Savings Scheme) are tax-saving mutual funds with 3-year lock-in, market-linked returns, tax benefits under Section 80C.",
        "fd": "Fixed Deposit offers fixed interest rates 6-8% based on tenure, safe investment, flexible tenure options.",
        "rd": "Recurring Deposit allows monthly savings with fixed interest rates, suitable for regular savings habit.",
        "nsc": "NSC (National Savings Certificate) offers 7-9% interest rate, 5-year tenure, tax benefits under Section 80C.",
    }
    return scheme_contexts.get(investment_type, f"{investment_type.replace('_', ' ').upper()} investment scheme information.")


async def _extract_investment_card(state, llm, rag_context: str, investment_type: str) -> Optional[Dict[str, Any]]:
    import json

    investment_type_hint = ""
    if investment_type:
        investment_type_hint = f"\nNote: The user is asking about {investment_type.replace('_', ' ').upper()}."

    extraction_prompt = f"""Extract investment scheme information from the following context and return as JSON:
{rag_context if rag_context else "No specific context available, but extract general information about the investment scheme."}
{investment_type_hint}

Extract the following fields:
- name: Investment scheme name (e.g., \"PPF\", \"NPS\", \"Sukanya Samriddhi Yojana\") - REQUIRED
- interest_rate: Interest rate or returns as string (e.g., \"7.1% p.a.\" or \"8-12% market-linked\")
- min_amount: Minimum investment amount with \"Rs.\" prefix (e.g., \"Rs. 500\" or \"Rs. 250\")
- max_amount: Maximum investment amount with \"Rs.\" prefix (e.g., \"Rs. 1.5 lakhs\" or \"No limit\")
- investment_amount: Alternative single string with range (e.g., \"Rs. 500 to Rs. 1.5 lakhs per year\")
- tenure: Investment tenure/duration (e.g., \"15 years\" or \"Until 60 years\")
- eligibility: Key eligibility criteria (concise, 1-2 sentences)
- tax_benefits: Tax benefits description (e.g., \"Section 80C: Up to Rs. 1.5 lakhs deduction\")
- description: Brief one-sentence description of the scheme
- features: Array of 3-5 key features as strings

IMPORTANT RULES:
1. All amounts MUST include \"Rs.\" prefix (e.g., \"Rs. 10,000\", \"Rs. 1.5 lakhs\")
2. Extract actual values from the context, don't make up values
3. If a field is not found, omit it (don't include null or empty values)
4. Return ONLY valid JSON object, no markdown, no code blocks
"""

    try:
        extracted_json = await llm.chat([{ "role": "user", "content": extraction_prompt }], use_fast_model=True)
        extracted_json = extracted_json.strip()
        if extracted_json.startswith("```json"):
            extracted_json = extracted_json[7:]
        elif extracted_json.startswith("```"):
            extracted_json = extracted_json[3:]
        if extracted_json.endswith("```"):
            extracted_json = extracted_json[:-3]
        extracted_json = extracted_json.strip()

        investment_info = json.loads(_extract_json_block(extracted_json))
        if investment_info and isinstance(investment_info, dict):
            state["structured_data"] = {"type": "investment", "investmentInfo": investment_info}
            logger.info(
                "investment_info_extracted",
                scheme_name=investment_info.get("name", "unknown"),
                has_amount=bool(investment_info.get("min_amount") or investment_info.get("investment_amount")),
                has_rate=bool(investment_info.get("interest_rate")),
            )
            return investment_info
    except json.JSONDecodeError as err:
        logger.warning("investment_json_parse_error", error=str(err))
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("investment_data_extraction_error", error=str(exc))

    return None


def _extract_json_block(raw_response: str) -> str:
    if raw_response.startswith("{") and raw_response.endswith("}"):
        return raw_response

    start_idx = raw_response.find("{")
    if start_idx == -1:
        return "{}"

    brace_count = 0
    for idx in range(start_idx, len(raw_response)):
        if raw_response[idx] == "{":
            brace_count += 1
        elif raw_response[idx] == "}":
            brace_count -= 1
            if brace_count == 0:
                return raw_response[start_idx : idx + 1]
    return raw_response[start_idx:]


def _build_investment_response_text(investment_info: Dict[str, Any], language: str) -> str:
    investment_name = investment_info.get("name") or "investment scheme"
    if isinstance(investment_name, str):
        investment_name = investment_name.replace("_", " ").replace("-", " ").title()

    if language == "hi-IN":
        investment_name_hi = {
            "Ppf": "पीपीएफ",
            "Nps": "एनपीएस",
            "Sukanya Samriddhi Yojana": "सुकन्या समृद्धि योजना",
            "Ssy": "सुकन्या समृद्धि योजना",
            "Elss": "ईएलएसएस",
            "Fixed Deposit": "फिक्स्ड डिपॉजिट",
            "Recurring Deposit": "रिकरिंग डिपॉजिट",
            "Nsc": "नेशनल सेविंग्स सर्टिफिकेट",
        }.get(investment_name, investment_name)
        return f"यहाँ {investment_name_hi} की विस्तृत जानकारी है।"

    return f"Here are the details for {investment_name}."


def _build_rag_system_prompt(rag_context: str) -> str:
    if rag_context:
        return f"""You are Vaani, a helpful AI assistant for Sun National Bank (an Indian bank).

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

    return """You are Vaani, a friendly and helpful AI assistant for Sun National Bank, an Indian bank.

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
