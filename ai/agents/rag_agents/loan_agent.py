"""Specialist loan agent invoked by the RAG supervisor."""
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


def create_fallback_loan_info(loan_type: str, language: str = "en-IN") -> Optional[Dict[str, Any]]:
    """Create fallback loan info when RAG extraction fails."""
    if language == "hi-IN":
        fallback_data: Dict[str, Dict[str, Any]] = {
            "home_loan": {
                "name": "होम लोन",
                "interest_rate": "8.35% - 9.50% प्रति वर्ष",
                "min_amount": "Rs. 5 लाख",
                "max_amount": "Rs. 5 करोड़",
                "tenure": "30 वर्ष तक",
                "eligibility": "21-65 वर्ष की आयु, न्यूनतम आय Rs. 25,000 प्रति माह",
                "description": "अपने सपनों का घर खरीदने के लिए व्यापक होम लोन योजना",
                "features": [
                    "प्रतिस्पर्धी ब्याज दरें",
                    "लंबी अवधि तक (30 वर्ष तक)",
                    "लोन-टू-वैल्यू अनुपात 90% तक",
                    "फ्लोटिंग और फिक्स्ड रेट विकल्प",
                ],
            },
            "personal_loan": {
                "name": "पर्सनल लोन",
                "interest_rate": "10.49% - 18.00% प्रति वर्ष",
                "min_amount": "Rs. 50,000",
                "max_amount": "Rs. 25 लाख",
                "tenure": "12 से 60 महीने",
                "eligibility": "21-65 वर्ष की आयु, न्यूनतम आय Rs. 25,000 प्रति माह",
                "description": "तत्काल वित्तीय जरूरतों के लिए लचीला पर्सनल लोन",
                "features": [
                    "त्वरित अनुमोदन",
                    "न्यूनतम दस्तावेज",
                    "बिना गारंटी",
                    "ऑनलाइन आवेदन",
                ],
            },
            "auto_loan": {
                "name": "ऑटो लोन",
                "interest_rate": "8.75% - 12.50% प्रति वर्ष",
                "min_amount": "Rs. 1 लाख",
                "max_amount": "Rs. 50 लाख",
                "tenure": "12 से 84 महीने",
                "eligibility": "21-65 वर्ष की आयु, स्थिर आय",
                "description": "कार, बाइक और वाणिज्यिक वाहनों के लिए वित्तपोषण",
                "features": [
                    "नई और पुरानी कारों के लिए",
                    "100% वित्तपोषण",
                    "प्रतिस्पर्धी ब्याज दरें",
                    "त्वरित प्रसंस्करण",
                ],
            },
            "education_loan": {
                "name": "एजुकेशन लोन",
                "interest_rate": "8.50% - 12.00% प्रति वर्ष",
                "min_amount": "Rs. 50,000",
                "max_amount": "Rs. 50 लाख",
                "tenure": "15 वर्ष तक",
                "eligibility": "भारत या विदेश में शिक्षा के लिए",
                "description": "उच्च शिक्षा के लिए व्यापक एजुकेशन लोन",
                "features": [
                    "भारत और विदेश दोनों में शिक्षा",
                    "कोर्स फीस और रहने की लागत",
                    "मोरेटोरियम अवधि",
                    "कर लाभ",
                ],
            },
            "business_loan": {
                "name": "बिजनेस लोन",
                "interest_rate": "11.00% - 18.00% प्रति वर्ष",
                "min_amount": "Rs. 1 लाख",
                "max_amount": "Rs. 50 लाख",
                "tenure": "12 से 60 महीने",
                "eligibility": "MSME और SME व्यवसाय, न्यूनतम 2 वर्ष का व्यवसाय",
                "description": "व्यवसाय विस्तार और कार्यशील पूंजी के लिए",
                "features": [
                    "MSME और SME के लिए",
                    "त्वरित अनुमोदन",
                    "लचीली चुकौती",
                    "व्यवसाय वृद्धि के लिए",
                ],
            },
            "gold_loan": {
                "name": "गोल्ड लोन",
                "interest_rate": "10.00% - 15.00% प्रति वर्ष",
                "min_amount": "Rs. 10,000",
                "max_amount": "Rs. 25 लाख",
                "tenure": "12 से 24 महीने",
                "eligibility": "सोने के गहने, न्यूनतम 18 वर्ष की आयु",
                "description": "सोने के गहनों के खिलाफ तत्काल नकदी",
                "features": [
                    "त्वरित अनुमोदन",
                    "सोने को सुरक्षित रखा जाता है",
                    "लचीली चुकौती",
                    "न्यूनतम दस्तावेज",
                ],
            },
            "loan_against_property": {
                "name": "प्रॉपर्टी के खिलाफ लोन",
                "interest_rate": "9.50% - 12.50% प्रति वर्ष",
                "min_amount": "Rs. 10 लाख",
                "max_amount": "Rs. 5 करोड़",
                "tenure": "15 वर्ष तक",
                "eligibility": "संपत्ति मालिक, 25-70 वर्ष की आयु",
                "description": "अपनी संपत्ति के मूल्य का उपयोग करके बड़ी राशि प्राप्त करें",
                "features": [
                    "उच्च लोन राशि",
                    "लंबी अवधि",
                    "प्रतिस्पर्धी ब्याज दरें",
                    "व्यवसाय या व्यक्तिगत उपयोग",
                ],
            },
        }
    else:
        fallback_data: Dict[str, Dict[str, Any]] = {
            "home_loan": {
                "name": "Home Loan",
                "interest_rate": "8.35% - 9.50% p.a.",
                "min_amount": "Rs. 5 lakhs",
                "max_amount": "Rs. 5 crores",
                "tenure": "Up to 30 years",
                "eligibility": "Age 21-65 years, minimum income Rs. 25,000 per month",
                "description": "Comprehensive home loan scheme to buy your dream home",
                "features": [
                    "Competitive interest rates",
                    "Long tenure (up to 30 years)",
                    "Loan-to-value ratio up to 90%",
                    "Floating and fixed rate options",
                ],
            },
            "personal_loan": {
                "name": "Personal Loan",
                "interest_rate": "10.49% - 18.00% p.a.",
                "min_amount": "Rs. 50,000",
                "max_amount": "Rs. 25 lakhs",
                "tenure": "12 to 60 months",
                "eligibility": "Age 21-65 years, minimum income Rs. 25,000 per month",
                "description": "Flexible personal loan for immediate financial needs",
                "features": [
                    "Quick approval",
                    "Minimal documentation",
                    "No collateral required",
                    "Online application",
                ],
            },
            "auto_loan": {
                "name": "Auto Loan",
                "interest_rate": "8.75% - 12.50% p.a.",
                "min_amount": "Rs. 1 lakh",
                "max_amount": "Rs. 50 lakhs",
                "tenure": "12 to 84 months",
                "eligibility": "Age 21-65 years, stable income",
                "description": "Financing for cars, bikes and commercial vehicles",
                "features": [
                    "For new and used cars",
                    "100% financing",
                    "Competitive interest rates",
                    "Quick processing",
                ],
            },
            "education_loan": {
                "name": "Education Loan",
                "interest_rate": "8.50% - 12.00% p.a.",
                "min_amount": "Rs. 50,000",
                "max_amount": "Rs. 50 lakhs",
                "tenure": "Up to 15 years",
                "eligibility": "For education in India or abroad",
                "description": "Comprehensive education loan for higher studies",
                "features": [
                    "Education in India and abroad",
                    "Course fees and living expenses",
                    "Moratorium period",
                    "Tax benefits",
                ],
            },
            "business_loan": {
                "name": "Business Loan",
                "interest_rate": "11.00% - 18.00% p.a.",
                "min_amount": "Rs. 1 lakh",
                "max_amount": "Rs. 50 lakhs",
                "tenure": "12 to 60 months",
                "eligibility": "MSME and SME businesses, minimum 2 years in business",
                "description": "For business expansion and working capital",
                "features": [
                    "For MSME and SME",
                    "Quick approval",
                    "Flexible repayment",
                    "For business growth",
                ],
            },
            "gold_loan": {
                "name": "Gold Loan",
                "interest_rate": "10.00% - 15.00% p.a.",
                "min_amount": "Rs. 10,000",
                "max_amount": "Rs. 25 lakhs",
                "tenure": "12 to 24 months",
                "eligibility": "Gold ornaments, minimum age 18 years",
                "description": "Instant cash against gold ornaments",
                "features": [
                    "Quick approval",
                    "Gold kept secure",
                    "Flexible repayment",
                    "Minimal documentation",
                ],
            },
            "loan_against_property": {
                "name": "Loan Against Property",
                "interest_rate": "9.50% - 12.50% p.a.",
                "min_amount": "Rs. 10 lakhs",
                "max_amount": "Rs. 5 crores",
                "tenure": "Up to 15 years",
                "eligibility": "Property owner, age 25-70 years",
                "description": "Get large amounts by leveraging your property value",
                "features": [
                    "High loan amount",
                    "Long tenure",
                    "Competitive interest rates",
                    "Business or personal use",
                ],
            },
        }
    
    return fallback_data.get(loan_type)


def handle_general_loan_query(state: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Return interactive card for general loan exploration."""
    if language == "hi-IN":
        # Hindi loan names and descriptions
        available_loans = [
            {"type": "home_loan", "name": "होम लोन", "description": "अपने सपनों का घर खरीदें", "icon": "🏠"},
            {"type": "personal_loan", "name": "पर्सनल लोन", "description": "तत्काल वित्तीय समाधान", "icon": "💳"},
            {"type": "auto_loan", "name": "ऑटो लोन", "description": "कार, बाइक और वाणिज्यिक वाहन", "icon": "🚗"},
            {"type": "education_loan", "name": "एजुकेशन लोन", "description": "भारत या विदेश में शिक्षा", "icon": "🎓"},
            {"type": "business_loan", "name": "बिजनेस लोन", "description": "MSME और SME वित्तपोषण", "icon": "💼"},
            {"type": "gold_loan", "name": "गोल्ड लोन", "description": "सोने के गहनों के खिलाफ तत्काल नकदी", "icon": "🥇"},
            {
                "type": "loan_against_property",
                "name": "प्रॉपर्टी के खिलाफ लोन",
                "description": "संपत्ति मूल्य का उपयोग करें",
                "icon": "🏢",
            },
        ]
        response = "यहाँ उपलब्ध लोन के प्रकार हैं। किसी भी लोन पर क्लिक करें या बोलें:"
    else:
        # English loan names and descriptions
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
        rag_service = get_rag_service(documents_type="loan", language=language)
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

    # Get user context for name
    user_context = state.get("user_context", {})
    user_name = user_context.get("name")
    
    system_prompt = _build_rag_system_prompt(rag_context, user_name=user_name, language=language)
    loan_info_extracted: Optional[Dict[str, Any]] = None
    if rag_context:
        loan_info_extracted = await _extract_loan_card(
            state,
            llm,
            rag_context,
            detected_loan_type,
            language=language,
        )

    if loan_info_extracted:
        response = _build_loan_response_text(loan_info_extracted, language)
        state["messages"].append(AIMessage(content=response))
        state["next_action"] = "end"
        logger.info("rag_loan_agent_response", has_structured=True)
        return state

    # Fallback: If extraction failed but we have detected_loan_type, use fallback data
    if detected_loan_type:
        loan_info_fallback = create_fallback_loan_info(detected_loan_type, language)
        if loan_info_fallback:
            state["structured_data"] = {"type": "loan", "loanInfo": loan_info_fallback}
            response = _build_loan_response_text(loan_info_fallback, language)
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            logger.info("rag_loan_agent_response", has_structured=True, used_fallback=True)
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
    logger.info("rag_loan_agent_response", has_structured=False)
    return state


async def _extract_loan_card(state, llm, rag_context: str, detected_loan_type: Optional[str], language: str = "en-IN") -> Optional[Dict[str, Any]]:
    import json

    loan_type_hint = ""
    if detected_loan_type:
        loan_type_hint = f"\nNote: The user is asking about {detected_loan_type.replace('_', ' ').title()}."

    # Language-specific extraction instructions
    if language == "hi-IN":
        extraction_prompt = f"""निम्नलिखित संदर्भ से ऋण जानकारी निकालें और JSON के रूप में लौटाएं:
{rag_context}
{loan_type_hint}

निम्नलिखित फ़ील्ड निकालें:
- name: ऋण उत्पाद का नाम (उदाहरण: \"होम लोन\", \"पर्सनल लोन\") - आवश्यक
- interest_rate: ब्याज दर स्ट्रिंग के रूप में (उदाहरण: \"8.35% - 9.50% प्रति वर्ष\" या \"10.49% - 18.00% प्रति वर्ष\")
- min_amount: न्यूनतम ऋण राशि \"Rs.\" उपसर्ग के साथ (उदाहरण: \"Rs. 5 लाख\" या \"Rs. 50,000\")
- max_amount: अधिकतम ऋण राशि \"Rs.\" उपसर्ग के साथ (उदाहरण: \"Rs. 5 करोड़\" या \"Rs. 25 लाख\")
- loan_amount: वैकल्पिक एकल स्ट्रिंग रेंज के साथ (उदाहरण: \"Rs. 5 लाख से Rs. 5 करोड़\")
- tenure: ऋण अवधि (उदाहरण: \"30 वर्ष तक\" या \"12 से 60 महीने\")
- eligibility: मुख्य पात्रता मानदंड (संक्षिप्त, 1-2 वाक्य)
- description: ऋण का संक्षिप्त एक-वाक्य विवरण
- features: 3-5 मुख्य विशेषताओं की सरणी स्ट्रिंग के रूप में

महत्वपूर्ण नियम:
1. सभी राशियों में \"Rs.\" उपसर्ग शामिल होना चाहिए (उदाहरण: \"Rs. 10,000\", \"Rs. 1 करोड़\")
2. संदर्भ से वास्तविक मान निकालें, मान न बनाएं
3. यदि कोई फ़ील्ड नहीं मिला, इसे छोड़ दें (null या खाली मान शामिल न करें)
4. केवल वैध JSON ऑब्जेक्ट लौटाएं, कोई markdown या code blocks नहीं
5. सभी पाठ हिंदी (देवनागरी लिपि) में होना चाहिए
"""
    else:
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
5. CRITICAL: ALL text MUST be in English ONLY. Use English words: \"lakhs\" (not \"लाख\"), \"crores\" (not \"करोड़\"), \"years\" (not \"वर्ष\"), \"months\" (not \"महीने\"). Convert any Hindi text from context to English.
6. For numbers: Use English format like \"8.35\" (not \"८.३५\"), \"5 lakhs\" (not \"5 लाख\"), \"9.50\" (not \"९.५०\")
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
            # Clean all text fields if language is English
            if language == "en-IN":
                for key, value in loan_info.items():
                    if isinstance(value, str):
                        loan_info[key] = _clean_english_text(value)
                    elif isinstance(value, list):
                        loan_info[key] = [_clean_english_text(str(v)) if isinstance(v, str) else v for v in value]
            
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
    """Build descriptive text before loan card with key details."""
    loan_name = loan_info.get("name") or loan_info.get("title") or "loan"
    interest_rate = loan_info.get("interest_rate", "")
    loan_amount = loan_info.get("loan_amount") or (
        f"{loan_info.get('min_amount', '')} - {loan_info.get('max_amount', '')}" 
        if loan_info.get("min_amount") or loan_info.get("max_amount") 
        else ""
    )
    tenure = loan_info.get("tenure", "")
    features = loan_info.get("features", [])
    
    if language == "hi-IN":
        loan_name_hi = loan_name  # Already in Hindi from extraction/fallback
        
        # Build descriptive text with key details
        parts = [f"यहाँ {loan_name_hi} की जानकारी है:"]
        
        if interest_rate:
            parts.append(f"ब्याज दर: {interest_rate}")
        
        if loan_amount:
            parts.append(f"लोन राशि: {loan_amount}")
        
        if tenure:
            parts.append(f"अवधि: {tenure}")
        
        if features and isinstance(features, list) and len(features) > 0:
            # Mention first 2-3 key features
            key_features = features[:3]
            features_text = ", ".join(key_features)
            parts.append(f"मुख्य विशेषताएं: {features_text}")
        
        return " ".join(parts) + " नीचे दिए गए कार्ड में विस्तृत जानकारी देखें।"

    # English version - clean all values to ensure no Hindi characters
    loan_name = _clean_english_text(str(loan_name))
    interest_rate = _clean_english_text(str(interest_rate)) if interest_rate else ""
    loan_amount = _clean_english_text(str(loan_amount)) if loan_amount else ""
    tenure = _clean_english_text(str(tenure)) if tenure else ""
    
    parts = [f"Here are the details for {loan_name}:"]
    
    if interest_rate:
        parts.append(f"Interest Rate: {interest_rate}")
    
    if loan_amount:
        parts.append(f"Loan Amount: {loan_amount}")
    
    if tenure:
        parts.append(f"Tenure: {tenure}")
    
    if features and isinstance(features, list) and len(features) > 0:
        key_features = features[:3]
        # Clean each feature text
        cleaned_features = [_clean_english_text(str(f)) for f in key_features]
        features_text = ", ".join(cleaned_features)
        parts.append(f"Key Features: {features_text}")
    
    response_text = " ".join(parts) + " See the card below for detailed information."
    # Final cleanup of the entire response
    return _clean_english_text(response_text)


def _build_rag_system_prompt(rag_context: str, user_name: Optional[str] = None, language: str = "en-IN") -> str:
    if rag_context:
        user_name_context = f"\n\nIMPORTANT: The user's name is '{user_name}'. Always use this name when addressing the user. NEVER use generic terms or regional language terms." if user_name else ""
        language_instruction = ""
        if language == "hi-IN":
            language_instruction = "\n\nCRITICAL: The user is asking in Hindi. You MUST respond ONLY in Hindi (Devanagari script). NEVER respond in English or any other language."
        return f"""You are Vaani, a helpful AI assistant for Sun National Bank (an Indian bank).

The user has asked a question about banking products/loans. Below is relevant information from our official product documentation:

{rag_context}{user_name_context}{language_instruction}

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
- Use common words: "पैसे" (money), "जानकारी" (information), "बताइए" (tell me), "लोन" (loan)
- Avoid complex words: use "बताइए" instead of "प्रदान करें", "जानकारी" instead of "सूचना"
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available. NEVER use generic terms like "गुजराती उपयोगकर्ता" or regional language terms
- If user name is available, use it directly (e.g., "Priya Grahak" or "प्रिया ग्राहक")

Keep your response helpful and professional."""

    user_name_context = f"\n\nIMPORTANT: The user's name is '{user_name}'. Always use this name when addressing the user. NEVER use generic terms or regional language terms." if user_name else ""
    language_instruction = ""
    if language == "hi-IN":
        language_instruction = "\n\nCRITICAL: The user is asking in Hindi. You MUST respond ONLY in Hindi (Devanagari script). NEVER respond in English or any other language."
    return f"""You are Vaani, a friendly and helpful AI assistant for Sun National Bank, an Indian bank.

IMPORTANT: Always use Indian Rupee (₹ or INR) for all monetary amounts. Never use dollars ($) or other currencies.{user_name_context}{language_instruction}

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
- Use common words: "पैसे" (money), "जानकारी" (information), "बताइए" (tell me), "लोन" (loan)
- Avoid complex words: use "बताइए" instead of "प्रदान करें", "जानकारी" instead of "सूचना"
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available. NEVER use generic terms like "गुजराती उपयोगकर्ता" or regional language terms
- If user name is available, use it directly (e.g., "Priya Grahak" or "प्रिया ग्राहक")
- Example: "मैं आपकी मदद कर सकती हूँ। मैं आपको लोन के बारे में बता सकती हूँ।" (I can help you. I can tell you about loans.)

Examples:
User: "What's the weather like?"
You: "I appreciate your question! However, I'm Vaani, your banking assistant, and I specialize in helping with banking services. I'd be happy to help you check your account balance, view transactions, or answer questions about our banking products. How can I assist you with your banking needs today?"

User: "Tell me a joke"
You: "I'd love to share a laugh, but I'm better with banking than comedy! 😊 I'm here to help you with your accounts, transactions, loans, and other banking services. Is there anything related to your banking needs I can assist you with?"

Remember: All amounts must be in Indian Rupees (₹).
Keep responses brief (2-3 sentences), warm, and helpful."""
