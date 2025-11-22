"""Specialist investment agent invoked by the RAG supervisor."""
from __future__ import annotations
import re

from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage
from utils import logger


def _clean_english_text(text: str) -> str:
    """Remove Hindi Devanagari characters and convert Hindi numerals/words to English."""
    if not text or not isinstance(text, str):
        return text
    
    cleaned = text
    
    # First, replace common Hindi phrases/words with English equivalents BEFORE removing Devanagari
    hindi_to_english = {
        'प्रति वर्ष': 'p.a.',
        'प्रति': 'per',
        'लाख': 'lakhs',
        'करोड़': 'crores',
        'वर्ष': 'years',
        'महीने': 'months',
        'महीना': 'month',
    }
    
    for hindi_word, english_word in hindi_to_english.items():
        cleaned = cleaned.replace(hindi_word, english_word)
    
    # Convert Hindi numerals (०-९) to English (0-9)
    hindi_to_english_numerals = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    for hindi_num, english_num in hindi_to_english_numerals.items():
        cleaned = cleaned.replace(hindi_num, english_num)
    
    # Remove any remaining Devanagari script characters (Unicode range \u0900-\u097F)
    cleaned = re.sub(r'[\u0900-\u097F]+', '', cleaned)
    
    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def create_fallback_investment_info(investment_type: str) -> Optional[Dict[str, Any]]:
    """Create fallback investment info when RAG extraction fails."""
    # Normalize investment_type for lookup
    investment_type_normalized = investment_type.lower().replace(" ", "_")
    
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

    investment_info = fallback_data.get(investment_type_normalized) if investment_type else None
    
    # Add scheme_type to investment_info for frontend to use for document download
    if investment_info:
        investment_info["scheme_type"] = investment_type_normalized.upper()
    
    return investment_info


def handle_general_investment_query(state: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Return interactive card for generic investment discovery."""
    if language == "hi-IN":
        # Hindi investment names and descriptions
        available_investments = [
            {"type": "ppf", "name": "पीपीएफ", "description": "दीर्घकालिक कर बचत योजना", "icon": "🏦"},
            {"type": "nps", "name": "एनपीएस", "description": "बाजार-लिंक्ड रिटायरमेंट योजना", "icon": "👴"},
            {"type": "ssy", "name": "सुकन्या समृद्धि योजना", "description": "बालिका बचत योजना", "icon": "👧"},
            {"type": "elss", "name": "ईएलएसएस", "description": "कर बचत म्यूचुअल फंड", "icon": "📈"},
            {"type": "fd", "name": "फिक्स्ड डिपॉजिट", "description": "निश्चित रिटर्न के साथ सुरक्षित निवेश", "icon": "💎"},
            {"type": "rd", "name": "रिकरिंग डिपॉजिट", "description": "नियमित मासिक बचत योजना", "icon": "💰"},
            {"type": "nsc", "name": "एनएससी", "description": "कर बचत बचत प्रमाणपत्र", "icon": "📜"},
        ]
        # Use simple North Indian Hindi with female gender
        response = "यहाँ उपलब्ध निवेश योजनाएं हैं। किसी भी योजना पर क्लिक करें या बोलें:"
    else:
        # English investment names and descriptions
        available_investments = [
            {"type": "ppf", "name": "PPF", "description": "Long-term tax-saving scheme", "icon": "🏦"},
            {"type": "nps", "name": "NPS", "description": "Market-linked retirement scheme", "icon": "👴"},
            {"type": "ssy", "name": "Sukanya Samriddhi Yojana", "description": "Girl child savings scheme", "icon": "👧"},
            {"type": "elss", "name": "ELSS", "description": "Tax-saving mutual funds", "icon": "📈"},
            {"type": "fd", "name": "Fixed Deposit", "description": "Safe investment with fixed returns", "icon": "💎"},
            {"type": "rd", "name": "Recurring Deposit", "description": "Regular monthly savings scheme", "icon": "💰"},
            {"type": "nsc", "name": "NSC", "description": "Tax-saving savings certificate", "icon": "📜"},
        ]
        response = "Here are the available investment schemes. Click or speak any scheme for detailed information:"

    state["structured_data"] = {"type": "investment_selection", "investments": available_investments}
    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"

    logger.info(
        "rag_investment_selection_response",
        response_type="investment_selection_table",
        investments_count=len(available_investments),
        language=language,
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
        rag_service = get_rag_service(documents_type="investment", language=language)
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

    # Get user context for name
    user_context = state.get("user_context", {})
    user_name = user_context.get("name")
    
    system_prompt = _build_rag_system_prompt(rag_context, user_name=user_name)
    investment_info_extracted: Optional[Dict[str, Any]] = None

    if detected_investment_type and not rag_context:
        rag_context = _build_detected_investment_context(detected_investment_type)

    if detected_investment_type:
        investment_info_extracted = await _extract_investment_card(
            state,
            llm,
            rag_context,
            detected_investment_type,
            language=language,
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
    
    # Clean response text if language is English to remove any Hindi characters
    if language == "en-IN":
        response = _clean_english_text(response)

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


async def _extract_investment_card(state, llm, rag_context: str, investment_type: str, language: str = "en-IN") -> Optional[Dict[str, Any]]:
    import json

    investment_type_hint = ""
    if investment_type:
        investment_type_hint = f"\nNote: The user is asking about {investment_type.replace('_', ' ').upper()}."

    extraction_prompt = f"""Extract investment scheme information from the following context and return as JSON:
{rag_context if rag_context else "No specific context available, but extract general information about the investment scheme."}
{investment_type_hint}

Extract the following fields:
- name: Investment scheme name (e.g., \"PPF\", \"NPS\", \"Sukanya Samriddhi Yojana\", \"Fixed Deposit\") - REQUIRED
- interest_rate: Interest rate or returns as string (e.g., \"7.1% per annum\" or \"6-8% per annum\" or \"8-12% market-linked\") - DO NOT add extra % symbol
- min_amount: Minimum investment amount with \"Rs.\" prefix (e.g., \"Rs. 500\", \"Rs. 1,000\", \"Rs. 250\")
- max_amount: Maximum investment amount with \"Rs.\" prefix (e.g., \"Rs. 1.5 lakhs\" or \"No limit\")
- investment_amount: ONLY use this for schemes with annual limits like PPF/SSY (e.g., \"Rs. 500 to Rs. 1.5 lakhs per year\"). For FD/RD, use min_amount and max_amount instead.
- tenure: Investment tenure/duration (e.g., \"15 years\", \"7 days to 10 years\", \"Until 60 years\")
- eligibility: Key eligibility criteria - who can invest (e.g., \"Any individual can open FD account\", \"Girl child below 10 years\")
- tax_benefits: Tax benefits description (e.g., \"Section 80C: Up to Rs. 1.5 lakhs deduction\" or \"TDS applicable on interest\")
- description: Brief one-sentence description of the scheme
- features: Array of 3-5 key features as strings

IMPORTANT RULES:
1. All amounts MUST include \"Rs.\" prefix (e.g., \"Rs. 10,000\", \"Rs. 1.5 lakhs\")
2. Extract actual values from the context, don't make up values
3. For Fixed Deposit (FD): min_amount should be \"Rs. 1,000\", max_amount should be \"No limit\", tenure should be \"7 days to 10 years\", eligibility should be \"Any individual can open FD account\"
4. For Recurring Deposit (RD): min_amount should be \"Rs. 100 per month\", max_amount should be \"No limit\"
5. DO NOT use investment_amount for FD or RD - use min_amount and max_amount instead
6. If a field is not found, omit it (don't include null or empty values)
7. Return ONLY valid JSON object, no markdown, no code blocks
8. CRITICAL: ALL text MUST be in English ONLY. Use English words: \"lakhs\" (not \"लाख\"), \"crores\" (not \"करोड़\"), \"years\" (not \"वर्ष\"), \"months\" (not \"महीने\"). Convert any Hindi text from context to English.
9. For numbers: Use English format like \"7.1\" (not \"७.१\"), \"1.5 lakhs\" (not \"1.5 लाख\"), \"8.2\" (not \"८.२\")
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
            # Clean all text fields if language is English
            if language == "en-IN":
                for key, value in investment_info.items():
                    if isinstance(value, str):
                        investment_info[key] = _clean_english_text(value)
                    elif isinstance(value, list):
                        investment_info[key] = [_clean_english_text(str(v)) if isinstance(v, str) else v for v in value]
            
            # Validate that extracted data matches the detected investment type
            # This prevents FD from showing PPF data or vice versa
            if investment_type:
                extracted_name = investment_info.get("name", "").lower()
                type_mapping = {
                    "fd": ["fixed deposit", "fd"],
                    "ppf": ["ppf", "public provident fund"],
                    "nps": ["nps", "national pension"],
                    "ssy": ["ssy", "sukanya", "sukanya samriddhi"],
                    "elss": ["elss", "equity linked"],
                    "rd": ["rd", "recurring deposit"],
                    "nsc": ["nsc", "national savings"],
                }
                expected_names = type_mapping.get(investment_type.lower(), [])
                # Check if extracted name matches expected type
                name_matches = any(
                    expected in extracted_name for expected in expected_names
                ) if expected_names else True
                
                if not name_matches:
                    logger.warning(
                        "investment_extraction_mismatch",
                        detected_type=investment_type,
                        extracted_name=investment_info.get("name"),
                    )
                    # Return None to trigger fallback
                    return None
            
            # Add scheme_type to investment_info for frontend to use for document download
            if investment_type:
                investment_info["scheme_type"] = investment_type.upper()
            
            state["structured_data"] = {"type": "investment", "investmentInfo": investment_info}
            logger.info(
                "investment_info_extracted",
                scheme_name=investment_info.get("name", "unknown"),
                scheme_type_added=investment_info.get("scheme_type"),
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
    """Build descriptive text before investment card with key details."""
    investment_name = investment_info.get("name") or "investment scheme"
    interest_rate = investment_info.get("interest_rate", "")
    investment_amount = investment_info.get("investment_amount") or (
        f"{investment_info.get('min_amount', '')} - {investment_info.get('max_amount', '')}" 
        if investment_info.get("min_amount") or investment_info.get("max_amount") 
        else ""
    )
    tenure = investment_info.get("tenure", "")
    tax_benefits = investment_info.get("tax_benefits", "")
    features = investment_info.get("features", [])
    
    if language == "hi-IN":
        investment_name_hi = investment_name  # Already in Hindi from extraction/fallback
        
        # Build descriptive text with key details
        parts = [f"यहाँ {investment_name_hi} की जानकारी है:"]
        
        if interest_rate:
            parts.append(f"ब्याज दर: {interest_rate}")
        
        if investment_amount:
            parts.append(f"निवेश राशि: {investment_amount}")
        
        if tenure:
            parts.append(f"अवधि: {tenure}")
        
        if tax_benefits:
            # Extract key part of tax benefits
            tax_short = tax_benefits.split(".")[0] if "." in tax_benefits else tax_benefits[:50]
            parts.append(f"कर लाभ: {tax_short}")
        
        if features and isinstance(features, list) and len(features) > 0:
            # Mention first 2-3 key features
            key_features = features[:3]
            features_text = ", ".join(key_features)
            parts.append(f"मुख्य विशेषताएं: {features_text}")
        
        return " ".join(parts) + " नीचे दिए गए कार्ड में विस्तृत जानकारी देखें।"

    # English version - clean all values to ensure no Hindi characters
    investment_name = _clean_english_text(str(investment_name))
    interest_rate = _clean_english_text(str(interest_rate)) if interest_rate else ""
    investment_amount = _clean_english_text(str(investment_amount)) if investment_amount else ""
    tenure = _clean_english_text(str(tenure)) if tenure else ""
    tax_benefits = _clean_english_text(str(tax_benefits)) if tax_benefits else ""
    
    parts = [f"Here are the details for {investment_name}:"]
    
    if interest_rate:
        parts.append(f"Interest Rate: {interest_rate}")
    
    if investment_amount:
        parts.append(f"Investment Amount: {investment_amount}")
    
    if tenure:
        parts.append(f"Tenure: {tenure}")
    
    if tax_benefits:
        tax_short = tax_benefits.split(".")[0] if "." in tax_benefits else tax_benefits[:50]
        parts.append(f"Tax Benefits: {tax_short}")
    
    if features and isinstance(features, list) and len(features) > 0:
        key_features = features[:3]
        # Clean each feature text
        cleaned_features = [_clean_english_text(str(f)) for f in key_features]
        features_text = ", ".join(cleaned_features)
        parts.append(f"Key Features: {features_text}")
    
    response_text = " ".join(parts) + " See the card below for detailed information."
    # Final cleanup of the entire response
    return _clean_english_text(response_text)


def _build_rag_system_prompt(rag_context: str, user_name: Optional[str] = None) -> str:
    if rag_context:
        user_name_context = f"\n\nIMPORTANT: The user's name is '{user_name}'. Always use this name when addressing the user. NEVER use generic terms or regional language terms." if user_name else ""
        return f"""You are Vaani, a helpful AI assistant for Sun National Bank (an Indian bank).

The user has asked a question about banking products/loans. Below is relevant information from our official product documentation:

{rag_context}{user_name_context}

Based on the above information, provide a clear, accurate, and helpful answer to the user's question.

IMPORTANT GUIDELINES:
- Always use Indian Rupees (₹ or INR) for all monetary amounts
- Base your answer primarily on the provided documentation
- If the documentation doesn't fully answer the question, acknowledge that and provide general guidance
- Be concise but comprehensive
- Use bullet points for lists of features, requirements, or steps
- If mentioning interest rates or fees, include the range (e.g., "8.50% - 11.50% p.a.")
- For eligibility or documents, distinguish between salaried and self-employed if relevant

HINDI LANGUAGE GUIDELINES (when responding in Hindi):
- CRITICAL: Use ONLY Hindi (Devanagari script). NEVER use Gujarati, Punjabi, Haryanvi, Rajasthani, or any other regional language
- Use FEMALE gender: "मैं" (I), "मैं कर सकती हूँ" (I can), "मैं बता सकती हूँ" (I can tell)
- Use simple North Indian Hindi words, avoid complex Sanskritized words
- Use common words: "पैसे" (money), "जानकारी" (information), "बताइए" (tell me)
- Avoid complex words: use "बताइए" instead of "प्रदान करें", "जानकारी" instead of "सूचना"
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available. NEVER use generic terms like "गुजराती उपयोगकर्ता" or regional language terms
- If user name is available, use it directly (e.g., "Priya Grahak" or "प्रिया ग्राहक")

Keep your response helpful and professional."""

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
- Use common words: "पैसे" (money), "जानकारी" (information), "बताइए" (tell me), "योजना" (scheme)
- Avoid complex words: use "बताइए" instead of "प्रदान करें", "जानकारी" instead of "सूचना", "योजना" instead of "अभियान"
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available. NEVER use generic terms like "गुजराती उपयोगकर्ता" or regional language terms
- If user name is available, use it directly (e.g., "Priya Grahak" or "प्रिया ग्राहक")
- Example: "मैं आपकी मदद कर सकती हूँ। मैं आपको निवेश योजनाओं के बारे में बता सकती हूँ।" (I can help you. I can tell you about investment schemes.)

Examples:
User: "What's the weather like?"
You: "I appreciate your question! However, I'm Vaani, your banking assistant, and I specialize in helping with banking services. I'd be happy to help you check your account balance, view transactions, or answer questions about our banking products. How can I assist you with your banking needs today?"

User: "Tell me a joke"
You: "I'd love to share a laugh, but I'm better with banking than comedy! 😊 I'm here to help you with your accounts, transactions, loans, and other banking services. Is there anything related to your banking needs I can assist you with?"

Remember: All amounts must be in Indian Rupees (₹).
Keep responses brief (2-3 sentences), warm, and helpful."""
