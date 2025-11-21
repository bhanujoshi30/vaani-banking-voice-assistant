"""Specialist loan agent invoked by the RAG supervisor."""
from __future__ import annotations

from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage
from utils import logger


def handle_general_loan_query(state: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Return interactive card for general loan exploration."""
    available_loans = [
        {"type": "home_loan", "name": "Home Loan", "description": "Buy your dream home", "icon": "🏠"},
        {"type": "personal_loan", "name": "Personal Loan", "description": "Instant financial solutions", "icon": "💳"},
        {"type": "auto_loan", "name": "Auto Loan", "description": "Cars, bikes & commercial vehicles", "icon": "🚗"},
        {"type": "education_loan", "name": "Education Loan", "description": "Study in India or abroad", "icon": "🎓"},
        {"type": "business_loan", "name": "Business Loan", "description": "MSME & SME financing", "icon": "💼"},
        {"type": "gold_loan", "name": "Gold Loan", "description": "Instant cash against gold ornaments", "icon": "🥇"},
        {
            "type": "loan_against_property",
            "name": "Loan Against Property",
            "description": "Unlock your property value",
            "icon": "🏢",
        },
    ]

    if language == "hi-IN":
        response = "हमारे पास निम्नलिखित ऋण प्रकार उपलब्ध हैं। विस्तृत जानकारी के लिए किसी भी ऋण प्रकार पर क्लिक करें या बोलें:"
    else:
        response = "We offer the following types of loans. Click or speak any loan type for detailed information:"

    state["structured_data"] = {"type": "loan_selection", "loans": available_loans}
    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"

    logger.info(
        "rag_loan_selection_response",
        response_type="loan_selection_table",
        loans_count=len(available_loans),
    )
    return state


async def handle_loan_query(
    state: Dict[str, Any],
    *,
    user_query: str,
    language: str,
    llm,
    detected_loan_type: Optional[str],
) -> Dict[str, Any]:
    """Answer loan questions using RAG context and structured cards."""
    from services.rag_service import get_rag_service

    rag_context = ""
    try:
        rag_service = get_rag_service(documents_type="loan")
        rag_filter = None
        if detected_loan_type:
            rag_filter = {"loan_type": detected_loan_type}
        rag_context = rag_service.get_context_for_query(
            user_query,
            k=2 if rag_filter else 3,
            filter=rag_filter,
        )
        logger.info(
            "rag_loan_context_retrieved",
            query_length=len(user_query),
            context_length=len(rag_context),
            metadata_filtered=bool(rag_filter),
        )
    except Exception as exc:
        logger.error("rag_loan_retrieval_error", error=str(exc))

    system_prompt = _build_rag_system_prompt(rag_context)
    loan_info_extracted: Optional[Dict[str, Any]] = None
    if rag_context:
        loan_info_extracted = await _extract_loan_card(
            state,
            llm,
            rag_context,
            detected_loan_type,
        )

    if loan_info_extracted:
        response = _build_loan_response_text(loan_info_extracted, language)
        state["messages"].append(AIMessage(content=response))
        state["next_action"] = "end"
        logger.info("rag_loan_agent_response", has_structured=True)
        return state

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]
    response = await llm.chat(llm_messages, use_fast_model=False)

    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    logger.info("rag_loan_agent_response", has_structured=False)
    return state


async def _extract_loan_card(state, llm, rag_context: str, detected_loan_type: Optional[str]) -> Optional[Dict[str, Any]]:
    import json

    loan_type_hint = ""
    if detected_loan_type:
        loan_type_hint = f"\nNote: The user is asking about {detected_loan_type.replace('_', ' ').title()}."

    extraction_prompt = f"""Extract loan information from the following context and return as JSON:
{rag_context}
{loan_type_hint}

Extract the following fields:
- name: Loan product name (e.g., \"Home Loan\", \"Personal Loan\") - REQUIRED
- interest_rate: Interest rate as string (e.g., \"8.35% - 9.50% p.a.\" or \"10.49% - 18.00% p.a.\")
- min_amount: Minimum loan amount with \"Rs.\" prefix (e.g., \"Rs. 5 lakhs\" or \"Rs. 50,000\")
- max_amount: Maximum loan amount with \"Rs.\" prefix (e.g., \"Rs. 5 crores\" or \"Rs. 25 lakhs\")
- loan_amount: Alternative single string with range (e.g., \"Rs. 5 lakhs to Rs. 5 crores\")
- tenure: Loan tenure/duration (e.g., \"Up to 30 years\" or \"12 to 60 months\")
- eligibility: Key eligibility criteria (concise, 1-2 sentences)
- description: Brief one-sentence description of the loan
- features: Array of 3-5 key features as strings

IMPORTANT RULES:
1. All amounts MUST include \"Rs.\" prefix (e.g., \"Rs. 10,000\", \"Rs. 1 crore\")
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

        loan_info = json.loads(_extract_json_block(extracted_json))
        if loan_info and isinstance(loan_info, dict):
            state["structured_data"] = {"type": "loan", "loanInfo": loan_info}
            logger.info(
                "loan_info_extracted",
                loan_name=loan_info.get("name", "unknown"),
                has_amount=bool(loan_info.get("min_amount") or loan_info.get("loan_amount")),
                has_rate=bool(loan_info.get("interest_rate")),
            )
            return loan_info
    except json.JSONDecodeError as err:
        logger.warning("loan_json_parse_error", error=str(err))
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("loan_data_extraction_error", error=str(exc))

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


def _build_loan_response_text(loan_info: Dict[str, Any], language: str) -> str:
    loan_name = loan_info.get("name") or loan_info.get("title") or "loan"
    if isinstance(loan_name, str):
        loan_name = loan_name.replace("_", " ").replace("-", " ").title()

    if language == "hi-IN":
        loan_name_hi = {
            "Home Loan": "होम लोन",
            "Personal Loan": "पर्सनल लोन",
            "Auto Loan": "ऑटो लोन",
            "Education Loan": "एजुकेशन लोन",
            "Business Loan": "बिजनेस लोन",
            "Gold Loan": "गोल्ड लोन",
            "Loan Against Property": "प्रॉपर्टी के खिलाफ लोन",
        }.get(loan_name, loan_name)
        return f"यहाँ {loan_name_hi} की विस्तृत जानकारी है।"

    return f"Here are the details for {loan_name}."


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
