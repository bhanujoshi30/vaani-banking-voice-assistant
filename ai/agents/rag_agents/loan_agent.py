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
            # Sub-loan types for business loans
            "business_loan_mudra": {
                "name": "MUDRA लोन",
                "interest_rate": "7.50% - 10.00% प्रति वर्ष",
                "min_amount": "Rs. 10,000",
                "max_amount": "Rs. 10 लाख",
                "tenure": "7 वर्ष तक",
                "eligibility": "सूक्ष्म उद्यमों के लिए सरकारी योजना",
                "description": "MSME के लिए छोटे व्यवसाय लोन",
                "features": [
                    "शिशु: Rs. 50,000 तक",
                    "किशोर: Rs. 50,001 से Rs. 5 लाख",
                    "तरुण: Rs. 5,00,001 से Rs. 10 लाख",
                    "गारंटी की आवश्यकता नहीं (Rs. 10 लाख तक)",
                ],
            },
            "business_loan_term": {
                "name": "टर्म लोन",
                "interest_rate": "10.00% - 14.00% प्रति वर्ष",
                "min_amount": "Rs. 10 लाख",
                "max_amount": "Rs. 50 करोड़",
                "tenure": "10 वर्ष तक",
                "eligibility": "पूंजीगत व्यय के लिए - मशीनरी, उपकरण, फैक्टरी सेटअप, विस्तार",
                "description": "दीर्घकालिक व्यवसाय वित्तपोषण",
                "features": [
                    "मासिक/त्रैमासिक EMI के साथ निश्चित अवधि",
                    "मशीनरी और उपकरण खरीद के लिए",
                    "फैक्टरी सेटअप और विस्तार के लिए",
                    "Rs. 25 लाख से ऊपर गारंटी आवश्यक",
                ],
            },
            "business_loan_working_capital": {
                "name": "वर्किंग कैपिटल लोन",
                "interest_rate": "11.00% - 15.00% प्रति वर्ष",
                "min_amount": "Rs. 5 लाख",
                "max_amount": "Rs. 25 करोड़",
                "tenure": "12 महीने (नवीकरणीय)",
                "eligibility": "दैनिक संचालन के लिए - कच्चा माल, वेतन, किराया",
                "description": "दैनिक व्यवसाय संचालन के लिए",
                "features": [
                    "ओवरड्राफ्ट या कैश क्रेडिट सीमा सुविधा",
                    "केवल उपयोग की गई राशि पर ब्याज",
                    "Rs. 50 लाख से ऊपर गारंटी आवश्यक",
                    "12 महीने के लिए नवीकरणीय",
                ],
            },
            "business_loan_equipment": {
                "name": "इक्विपमेंट फाइनेंसिंग",
                "interest_rate": "10.00% - 14.00% प्रति वर्ष",
                "min_amount": "Rs. 10 लाख",
                "max_amount": "Rs. 50 करोड़",
                "tenure": "10 वर्ष तक",
                "eligibility": "मशीनरी, वाहन, कंप्यूटर, उपकरण वित्तपोषण",
                "description": "मशीनरी और उपकरण खरीद के लिए",
                "features": [
                    "उपकरण गारंटी के रूप में कार्य करता है",
                    "90% तक वित्तपोषण",
                    "मशीनरी, वाहन, कंप्यूटर, उपकरण के लिए",
                    "Rs. 25 लाख से ऊपर गारंटी आवश्यक",
                ],
            },
            "business_loan_invoice": {
                "name": "इनवॉइस फाइनेंसिंग",
                "interest_rate": "11.00% - 15.00% प्रति वर्ष",
                "min_amount": "Rs. 5 लाख",
                "max_amount": "Rs. 25 करोड़",
                "tenure": "12 महीने (नवीकरणीय)",
                "eligibility": "लंबित इनवॉइस/बिलों के खिलाफ तत्काल धन प्राप्त करें",
                "description": "इनवॉइस के खिलाफ वित्तपोषण",
                "features": [
                    "इनवॉइस मूल्य का 80% तक",
                    "केवल उपयोग की गई राशि पर ब्याज",
                    "लंबित बिलों के खिलाफ तत्काल धन",
                    "कार्यशील पूंजी प्रबंधन में मदद",
                ],
            },
            "business_loan_overdraft": {
                "name": "बिजनेस ओवरड्राफ्ट",
                "interest_rate": "11.00% - 15.00% प्रति वर्ष",
                "min_amount": "Rs. 5 लाख",
                "max_amount": "Rs. 25 करोड़",
                "tenure": "12 महीने (नवीकरणीय)",
                "eligibility": "आवश्यकता के अनुसार धन निकालने के लिए",
                "description": "लचीला क्रेडिट सुविधा",
                "features": [
                    "स्वीकृत सीमा तक आवश्यकतानुसार धन निकालें",
                    "केवल उपयोग की गई राशि पर ब्याज, पूरी सीमा पर नहीं",
                    "लचीला पुनर्भुगतान",
                    "Rs. 50 लाख से ऊपर गारंटी आवश्यक",
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
            # Sub-loan types for business loans
            "business_loan_mudra": {
                "name": "MUDRA Loan",
                "interest_rate": "7.50% - 10.00% p.a.",
                "min_amount": "Rs. 10,000",
                "max_amount": "Rs. 10 lakhs",
                "tenure": "Up to 7 years",
                "eligibility": "Government scheme for micro enterprises",
                "description": "Small business loans for MSME",
                "features": [
                    "Shishu: Up to Rs. 50,000",
                    "Kishore: Rs. 50,001 to Rs. 5 lakhs",
                    "Tarun: Rs. 5,00,001 to Rs. 10 lakhs",
                    "No collateral required (up to Rs. 10 lakhs)",
                ],
            },
            "business_loan_term": {
                "name": "Term Loan",
                "interest_rate": "10.00% - 14.00% p.a.",
                "min_amount": "Rs. 10 lakhs",
                "max_amount": "Rs. 50 crores",
                "tenure": "Up to 10 years",
                "eligibility": "For capital expenditure - machinery, equipment, factory setup, expansion",
                "description": "Long-term business financing",
                "features": [
                    "Fixed tenure with monthly/quarterly EMI",
                    "For machinery and equipment purchase",
                    "For factory setup and expansion",
                    "Collateral required above Rs. 25 lakhs",
                ],
            },
            "business_loan_working_capital": {
                "name": "Working Capital Loan",
                "interest_rate": "11.00% - 15.00% p.a.",
                "min_amount": "Rs. 5 lakhs",
                "max_amount": "Rs. 25 crores",
                "tenure": "12 months (renewable)",
                "eligibility": "For day-to-day operations - raw material, salaries, rent",
                "description": "For daily business operations",
                "features": [
                    "Overdraft or cash credit limit facility",
                    "Interest only on utilized amount",
                    "Collateral required above Rs. 50 lakhs",
                    "Renewable for 12 months",
                ],
            },
            "business_loan_equipment": {
                "name": "Equipment Financing",
                "interest_rate": "10.00% - 14.00% p.a.",
                "min_amount": "Rs. 10 lakhs",
                "max_amount": "Rs. 50 crores",
                "tenure": "Up to 10 years",
                "eligibility": "Finance machinery, vehicles, computers, tools",
                "description": "For machinery and equipment purchase",
                "features": [
                    "Equipment acts as collateral",
                    "Up to 90% funding",
                    "For machinery, vehicles, computers, tools",
                    "Collateral required above Rs. 25 lakhs",
                ],
            },
            "business_loan_invoice": {
                "name": "Invoice Financing",
                "interest_rate": "11.00% - 15.00% p.a.",
                "min_amount": "Rs. 5 lakhs",
                "max_amount": "Rs. 25 crores",
                "tenure": "12 months (renewable)",
                "eligibility": "Get instant funds against pending invoices/bills",
                "description": "Financing against invoices",
                "features": [
                    "Up to 80% of invoice value",
                    "Interest only on utilized amount",
                    "Instant funds against pending bills",
                    "Helps in working capital management",
                ],
            },
            "business_loan_overdraft": {
                "name": "Business Overdraft",
                "interest_rate": "11.00% - 15.00% p.a.",
                "min_amount": "Rs. 5 lakhs",
                "max_amount": "Rs. 25 crores",
                "tenure": "12 months (renewable)",
                "eligibility": "Withdraw funds as needed up to sanctioned limit",
                "description": "Flexible credit facility",
                "features": [
                    "Withdraw funds as needed up to sanctioned limit",
                    "Interest only on utilized amount, not entire limit",
                    "Flexible repayment",
                    "Collateral required above Rs. 50 lakhs",
                ],
            },
        }
    
    # Normalize loan_type to lowercase for lookup
    loan_type_normalized = loan_type.lower().replace(" ", "_")
    loan_info = fallback_data.get(loan_type_normalized)
    
    # Add loan_type to loan_info for frontend to use for document download
    if loan_info:
        # Convert normalized type back to uppercase format (e.g., "business_loan_mudra" -> "BUSINESS_LOAN_MUDRA")
        loan_info["loan_type"] = loan_type_normalized.upper().replace(" ", "_")
    
    return loan_info


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
            conversation_context = "\n\nPREVIOUS CONVERSATION CONTEXT (Last 3 pairs only):\n"
            for msg in recent_messages:
                role = "User" if hasattr(msg, "content") and msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content if hasattr(msg, "content") else str(msg)
                conversation_context += f"{role}: {content}\n"
            conversation_context += "\nIMPORTANT: Use the context from the previous conversation to understand what the user is referring to. If the user's current message is brief (like 'against property'), it likely refers to something mentioned in the previous conversation.\n"
    
    return conversation_context


def _detect_sub_loan_types(rag_service, main_loan_type: str, language: str) -> List[str]:
    """Detect all available sub-loan types for a main loan type from the RAG database.
    
    This queries the vector database intelligently to find all chunks that have sub-loan type loan_type values.
    It queries multiple times with different search terms to ensure we find all sub-types.
    """
    # Normalize main_loan_type
    main_loan_normalized = main_loan_type.lower().replace(" ", "_")
    main_type_upper = main_loan_normalized.upper().replace(" ", "_")
    
    # Map main loan types to their possible sub-types (for reference and fallback)
    expected_sub_types = {
        "business_loan": ["BUSINESS_LOAN_MUDRA", "BUSINESS_LOAN_TERM", "BUSINESS_LOAN_WORKING_CAPITAL", 
                          "BUSINESS_LOAN_INVOICE", "BUSINESS_LOAN_EQUIPMENT", "BUSINESS_LOAN_OVERDRAFT"],
        "home_loan": ["HOME_LOAN_PURCHASE", "HOME_LOAN_CONSTRUCTION", "HOME_LOAN_PLOT_CONSTRUCTION",
                      "HOME_LOAN_EXTENSION", "HOME_LOAN_RENOVATION", "HOME_LOAN_BALANCE_TRANSFER"],
    }
    
    if main_loan_normalized not in expected_sub_types:
        return []
    
    # Query the database with multiple search terms to find all related chunks
    # Use language-specific queries
    if language == "hi-IN":
        query_terms = {
            "business_loan": ["बिजनेस लोन", "business loan", "msme", "mudra", "term loan", "working capital", "invoice", "equipment"],
            "home_loan": ["होम लोन", "home loan", "house loan", "property loan", "construction", "purchase"],
        }
    else:
        query_terms = {
            "business_loan": ["business loan", "msme", "mudra", "term loan", "working capital", "invoice financing", "equipment financing"],
            "home_loan": ["home loan", "house loan", "property loan", "construction loan", "purchase loan"],
        }
    
    # Collect all unique loan_type values from multiple queries
    all_loan_types = set()
    queries = query_terms.get(main_loan_normalized, [main_loan_normalized.replace("_", " ")])
    
    # Query with each search term to maximize coverage
    for query_term in queries[:3]:  # Use first 3 queries to avoid too many calls
        try:
            results = rag_service.retrieve(query_term, k=30)
            for doc in results:
                loan_type = doc.metadata.get("loan_type", "")
                if loan_type:
                    all_loan_types.add(loan_type)
        except Exception as e:
            logger.warning("sub_loan_detection_query_failed", query=query_term, error=str(e))
            continue
    
    # Extract sub-types (those that start with main_type + "_")
    found_sub_types = set()
    main_type_found = False
    
    for loan_type in all_loan_types:
        if loan_type == main_type_upper:
            main_type_found = True
        elif loan_type.startswith(main_type_upper + "_"):
            found_sub_types.add(loan_type)
    
    logger.info(
        "sub_loan_types_detection",
        main_type=main_loan_normalized,
        all_loan_types_found=list(all_loan_types),
        sub_types_found=list(found_sub_types),
        main_type_found=main_type_found,
        queries_used=queries[:3]
    )
    
    # If main type exists, return all expected sub-types (they represent available product options)
    # This ensures users see all available options, not just what's explicitly in the current PDF
    if main_type_found or main_loan_normalized in ["business_loan", "home_loan"]:
        # Double-check: query specifically for the main type to confirm it exists
        try:
            main_type_results = rag_service.retrieve(
                main_loan_normalized.replace("_", " "), 
                k=5,
                filter={"loan_type": main_type_upper}
            )
            if main_type_results or main_loan_normalized in ["business_loan", "home_loan"]:
                # Return all expected sub-types, but prioritize those found in database
                expected = expected_sub_types[main_loan_normalized]
                found_list = sorted(list(found_sub_types))
                
                # If we found some sub-types, log them but still return all expected ones
                if found_list:
                    logger.info(
                        "sub_loan_types_detected_from_db",
                        main_type=main_loan_normalized,
                        count=len(found_list),
                        sub_types=found_list,
                        note="Returning all expected sub-types to show complete product options"
                    )
                
                logger.info(
                    "sub_loan_types_returning_all_expected",
                    main_type=main_loan_normalized,
                    found_in_db=found_list,
                    returning_all=expected,
                    reason="Main loan type exists. Showing all available product sub-types."
                )
                return expected
        except Exception as e:
            logger.warning("sub_loan_fallback_check_failed", error=str(e))
            # Still return expected sub-types if it's business/home loan
            if main_loan_normalized in ["business_loan", "home_loan"]:
                return expected_sub_types[main_loan_normalized]
    
    # If we found sub-types but main type not confirmed, return what we found
    if found_sub_types:
        logger.info(
            "sub_loan_types_detected_from_db",
            main_type=main_loan_normalized,
            count=len(found_sub_types),
            sub_types=sorted(list(found_sub_types))
        )
        return sorted(list(found_sub_types))
    
    # No main type found - return empty
    logger.warning(
        "sub_loan_types_not_found",
        main_type=main_loan_normalized,
        message="Loan type not found in database"
    )
    return []


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

    # Extract conversation context from previous messages
    conversation_context = _extract_conversation_context(state, max_pairs=3)
    
    # Build enhanced query with conversation context for better RAG retrieval
    enhanced_query = user_query
    if conversation_context:
        # Extract key loan-related terms from conversation context for better RAG matching
        if "loan" in conversation_context.lower() or "लोन" in conversation_context:
            # If previous context mentions loans, include it in the query
            enhanced_query = f"{conversation_context}\n\nCurrent question: {user_query}"

    rag_service = get_rag_service(documents_type="loan", language=language)
    
    # Normalize detected_loan_type for checking sub-types
    normalized_loan_type = None
    if detected_loan_type:
        # Normalize to lowercase with underscores (e.g., "business_loan")
        normalized_loan_type = detected_loan_type.lower().replace(" ", "_")
    
    # Check if user query mentions a SPECIFIC sub-loan type
    # If yes, retrieve that specific sub-loan type instead of showing selection
    user_query_lower = user_query.lower()
    specific_sub_loan_mentioned = None
    
    # Map sub-loan type keywords to their normalized types
    sub_loan_keywords = {
        "business_loan": {
            "mudra": "BUSINESS_LOAN_MUDRA",
            "term loan": "BUSINESS_LOAN_TERM",
            "term": "BUSINESS_LOAN_TERM",  # Check "term" after checking "term loan"
            "working capital": "BUSINESS_LOAN_WORKING_CAPITAL",
            "working": "BUSINESS_LOAN_WORKING_CAPITAL",  # Check "working" after checking "working capital"
            "invoice": "BUSINESS_LOAN_INVOICE",
            "equipment": "BUSINESS_LOAN_EQUIPMENT",
            "overdraft": "BUSINESS_LOAN_OVERDRAFT",
            # Hindi keywords
            "मुद्रा": "BUSINESS_LOAN_MUDRA",
            "टर्म": "BUSINESS_LOAN_TERM",
            "कार्यशील": "BUSINESS_LOAN_WORKING_CAPITAL",
        },
        "home_loan": {
            "purchase": "HOME_LOAN_PURCHASE",
            "construction": "HOME_LOAN_CONSTRUCTION",
            "plot": "HOME_LOAN_PLOT_CONSTRUCTION",
            "extension": "HOME_LOAN_EXTENSION",
            "renovation": "HOME_LOAN_RENOVATION",
            "balance transfer": "HOME_LOAN_BALANCE_TRANSFER",
        }
    }
    
    # Check if user query mentions a specific sub-loan type
    # First, check if normalized_loan_type is in sub_loan_keywords
    if normalized_loan_type in sub_loan_keywords:
        keywords = sub_loan_keywords[normalized_loan_type]
        # Sort by length (longest first) to match "term loan" before "term"
        sorted_keywords = sorted(keywords.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, sub_type in sorted_keywords:
            if keyword in user_query_lower:
                specific_sub_loan_mentioned = sub_type
                logger.info(
                    "specific_sub_loan_type_detected_in_query",
                    keyword=keyword,
                    sub_type=sub_type,
                    query=user_query
                )
                break
    
    # Also check ALL sub-loan keywords if normalized_loan_type is None or not found
    # This handles cases like "Tell me about mudra loan" where business_loan wasn't detected
    # Also handle cases where loan type is passed directly (e.g., "business_loan_mudra")
    if not specific_sub_loan_mentioned:
        # First, check if the query contains a direct sub-loan type (e.g., "business_loan_mudra")
        # Normalize underscores to spaces for matching
        query_normalized = user_query_lower.replace("_", " ").replace("-", " ")
        
        # Check all sub-loan keywords across all loan types
        for loan_type, keywords in sub_loan_keywords.items():
            sorted_keywords = sorted(keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, sub_type in sorted_keywords:
                # Check both the keyword and the sub_type (normalized) in the query
                sub_type_normalized = sub_type.lower().replace("_", " ")
                if keyword in query_normalized or sub_type_normalized in query_normalized:
                    specific_sub_loan_mentioned = sub_type
                    # Also set normalized_loan_type to the parent loan type
                    if not normalized_loan_type:
                        normalized_loan_type = loan_type
                        detected_loan_type = loan_type
                    logger.info(
                        "specific_sub_loan_type_detected_directly",
                        keyword=keyword,
                        sub_type=sub_type,
                        parent_type=loan_type,
                        query=user_query,
                        query_normalized=query_normalized
                    )
                    break
            if specific_sub_loan_mentioned:
                break
    
    # Check if this loan type has multiple sub-types
    # For business_loan and home_loan, show sub-type selection ONLY if no specific sub-type mentioned
    sub_loan_types = []
    if normalized_loan_type in ["business_loan", "home_loan"]:
        sub_loan_types = _detect_sub_loan_types(rag_service, normalized_loan_type, language)
        
        # If user mentioned a specific sub-loan type, use that instead of showing selection
        if specific_sub_loan_mentioned:
            # Override detected_loan_type with the specific sub-loan type
            detected_loan_type = specific_sub_loan_mentioned
            logger.info(
                "using_specific_sub_loan_type",
                original_type=normalized_loan_type,
                specific_sub_type=specific_sub_loan_mentioned,
                query=user_query
            )
        # If we have sub-types but NO specific sub-type mentioned, show selection interface
        elif sub_loan_types and len(sub_loan_types) > 0:
            # Show selection interface for business/home loans when asked generically
            # This matches user expectation to see all available options
            logger.info(
                "showing_sub_loan_selection",
                main_type=normalized_loan_type,
                sub_types=sub_loan_types,
                query=user_query
            )
            return _create_sub_loan_selection(state, normalized_loan_type, sub_loan_types, language)
    
    rag_context = ""
    try:
        rag_filter = None
        if detected_loan_type:
            # Map sub-loan types to their parent loan types for RAG filtering
            # Documents are indexed with parent loan types (e.g., "home_loan"), not sub-types
            sub_loan_to_parent = {
                # Business loan sub-types -> business_loan
                "BUSINESS_LOAN_MUDRA": "business_loan",
                "BUSINESS_LOAN_TERM": "business_loan",
                "BUSINESS_LOAN_WORKING_CAPITAL": "business_loan",
                "BUSINESS_LOAN_INVOICE": "business_loan",
                "BUSINESS_LOAN_EQUIPMENT": "business_loan",
                "BUSINESS_LOAN_OVERDRAFT": "business_loan",
                # Home loan sub-types -> home_loan
                "HOME_LOAN_PURCHASE": "home_loan",
                "HOME_LOAN_CONSTRUCTION": "home_loan",
                "HOME_LOAN_PLOT_CONSTRUCTION": "home_loan",
                "HOME_LOAN_EXTENSION": "home_loan",
                "HOME_LOAN_RENOVATION": "home_loan",
                "HOME_LOAN_BALANCE_TRANSFER": "home_loan",
            }
            
            # Normalize detected_loan_type
            normalized_detected = detected_loan_type.upper().replace(" ", "_")
            
            # Map to parent loan type if it's a sub-loan type
            parent_loan_type = sub_loan_to_parent.get(normalized_detected, normalized_detected.lower())
            
            # Documents are indexed with parent loan types
            # The format depends on ingestion method:
            # - Basic loader: lowercase (e.g., "home_loan") from PDF filename
            # - Semantic chunker: uppercase (e.g., "HOME_LOAN") from normalization
            # Try lowercase first (most common), but ChromaDB filter is case-sensitive
            # So we need to match the exact format used during indexing
            # For now, use uppercase to match semantic chunker format (if used)
            # If that doesn't work, we can fall back to lowercase or try both
            rag_filter = {"loan_type": parent_loan_type.upper()}
            
            logger.info(
                "rag_filter_set",
                detected_loan_type=detected_loan_type,
                normalized_detected=normalized_detected,
                parent_loan_type=parent_loan_type,
                filter_value=rag_filter["loan_type"]
            )
        
        rag_context = rag_service.get_context_for_query(
            enhanced_query,
            k=5 if rag_filter else 3,  # Increase k to get more relevant chunks when filtering
            filter=rag_filter,
        )
        
        # If no context retrieved with uppercase filter, try lowercase (documents might be indexed with lowercase)
        if not rag_context and rag_filter:
            parent_lower = parent_loan_type.lower()
            if rag_filter["loan_type"] != parent_lower:
                logger.info("retrying_with_lowercase_filter", 
                           original_filter=rag_filter["loan_type"],
                           new_filter=parent_lower)
                rag_filter_lower = {"loan_type": parent_lower}
                rag_context = rag_service.get_context_for_query(
                    enhanced_query,
                    k=5,
                    filter=rag_filter_lower,
                )
                if rag_context:
                    logger.info("retry_successful_with_lowercase", context_length=len(rag_context))
        
        logger.info(
            "rag_loan_context_retrieved",
            query_length=len(user_query),
            context_length=len(rag_context),
            metadata_filtered=bool(rag_filter),
            filter_value=rag_filter.get("loan_type") if rag_filter else None,
            has_conversation_context=bool(conversation_context),
            context_preview=rag_context[:300].replace("\n", " ") if rag_context else "EMPTY"
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
        # Normalize detected_loan_type for fallback lookup (handle both formats)
        normalized_for_fallback = detected_loan_type.lower().replace(" ", "_")
        loan_info_fallback = create_fallback_loan_info(normalized_for_fallback, language)
        if loan_info_fallback:
            state["structured_data"] = {"type": "loan", "loanInfo": loan_info_fallback}
            response = _build_loan_response_text(loan_info_fallback, language)
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            logger.info(
                "rag_loan_agent_response", 
                has_structured=True, 
                used_fallback=True,
                detected_loan_type=detected_loan_type,
                normalized_for_fallback=normalized_for_fallback,
                fallback_available=True
            )
            return state
        else:
            logger.warning(
                "rag_loan_agent_fallback_not_found",
                detected_loan_type=detected_loan_type,
                normalized_for_fallback=normalized_for_fallback,
                language=language
            )

    # Build user query with conversation context for LLM
    user_query_with_context = user_query
    if conversation_context:
        user_query_with_context = f"{conversation_context}\n\nUser's current question: {user_query}"

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query_with_context},
    ]
    response = await llm.chat(llm_messages, use_fast_model=False)
    
    # Clean response text if language is English to remove any Hindi characters
    if language == "en-IN":
        response = _clean_english_text(response)
    
    # Detect generic answers and ask for clarification
    generic_indicators = [
        "i'm not sure", "i don't know", "i'm not certain", "i cannot", "i'm unable",
        "मुझे नहीं पता", "मुझे यकीन नहीं", "मैं नहीं जानती", "मैं निश्चित नहीं", "मैं असमर्थ हूं"
    ]
    is_generic = any(indicator in response.lower() for indicator in generic_indicators)
    
    # Check if RAG context was empty or very short (indicating no relevant document retrieval)
    rag_context_empty = not rag_context or len(rag_context.strip()) < 100
    
    # HALLUCINATION CHECK: If RAG retrieval returns 0 documents, force refusal instead of making up answer
    if rag_context_empty:
        logger.warning("rag_context_empty_forced_refusal",
                     detected_loan_type=detected_loan_type,
                     query=user_query)
        if language == "hi-IN":
            refusal_response = "मुझे खेद है, मुझे उस विशिष्ट उत्पाद के बारे में जानकारी नहीं है। कृपया किसी अन्य बैंकिंग उत्पाद के बारे में पूछें।"
        else:
            refusal_response = "I'm sorry, I don't have information on that specific product. Please ask about other banking products."
        
        state["messages"].append(AIMessage(content=refusal_response))
        state["next_action"] = "end"
        return state
    
    # If response is generic and RAG context was empty, ask for clarification
    if (is_generic or rag_context_empty) and detected_loan_type:
        if language == "hi-IN":
            clarification = "\n\nमुझे खेद है, मुझे इस प्रश्न के लिए विशिष्ट जानकारी नहीं मिल रही है। कृपया अपना प्रश्न दोबारा बताएं या अधिक विशिष्ट बनाएं, जैसे कि 'होम लोन की ब्याज दर क्या है?' या 'ऑटो लोन के लिए क्या योग्यता है?'"
        else:
            clarification = "\n\nI'm sorry, I'm having trouble finding specific information for this question. Could you please rephrase your question or be more specific? For example, 'What is the interest rate for home loan?' or 'What is the eligibility for auto loan?'"
        response = response + clarification
        logger.warning("generic_response_detected", 
                      detected_loan_type=detected_loan_type,
                      rag_context_length=len(rag_context) if rag_context else 0,
                      response_length=len(response))

    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    logger.info("rag_loan_agent_response", has_structured=False, rag_context_length=len(rag_context) if rag_context else 0)
    return state


async def _handle_multiple_sub_loan_types(
    state: Dict[str, Any],
    main_loan_type: str,
    sub_loan_types: List[str],
    language: str,
    user_query: str,
    llm,
) -> Dict[str, Any]:
    """Handle queries for loan types with multiple sub-types - return multiple cards or selection."""
    from services.rag_service import get_rag_service
    
    rag_service = get_rag_service(documents_type="loan", language=language)
    
    # Try to extract cards for all sub-types
    all_loan_cards = []
    
    for sub_type in sub_loan_types:
        # Retrieve context for this sub-type
        rag_context = rag_service.get_context_for_query(
            user_query,
            k=2,
            filter={"loan_type": sub_type}
        )
        
        if rag_context:
            # Extract card for this sub-type
            temp_state = {"structured_data": {}}
            loan_card = await _extract_loan_card(
                temp_state,
                llm,
                rag_context,
                sub_type,
                language=language,
            )
            if loan_card:
                all_loan_cards.append(loan_card)
    
    # If we got multiple cards, return them all
    if len(all_loan_cards) > 1:
        # Build response text mentioning all available options
        if language == "hi-IN":
            main_loan_name = {
                "business_loan": "बिजनेस लोन",
                "home_loan": "होम लोन",
            }.get(main_loan_type, main_loan_type.replace("_", " ").title())
            
            sub_type_names = {
                "BUSINESS_LOAN_MUDRA": "MUDRA लोन",
                "BUSINESS_LOAN_TERM": "टर्म लोन",
                "BUSINESS_LOAN_WORKING_CAPITAL": "वर्किंग कैपिटल लोन",
                "BUSINESS_LOAN_INVOICE": "इनवॉइस फाइनेंसिंग",
                "BUSINESS_LOAN_EQUIPMENT": "इक्विपमेंट फाइनेंसिंग",
                "BUSINESS_LOAN_OVERDRAFT": "बिजनेस ओवरड्राफ्ट",
                "HOME_LOAN_PURCHASE": "होम पर्चेज लोन",
                "HOME_LOAN_CONSTRUCTION": "होम कंस्ट्रक्शन लोन",
                "HOME_LOAN_PLOT_CONSTRUCTION": "प्लॉट कंस्ट्रक्शन लोन",
                "HOME_LOAN_EXTENSION": "होम एक्सटेंशन लोन",
                "HOME_LOAN_RENOVATION": "होम रेनोवेशन लोन",
                "HOME_LOAN_BALANCE_TRANSFER": "बैलेंस ट्रांसफर लोन",
            }
            
            sub_names_list = [sub_type_names.get(st, st.replace("_", " ")) for st in sub_loan_types if st in [c.get("name", "").upper().replace(" ", "_") for c in all_loan_cards]]
            response_text = f"{main_loan_name} के लिए हमारे पास {len(all_loan_cards)} विकल्प उपलब्ध हैं: {', '.join(sub_names_list)}. नीचे दिए गए कार्ड में विस्तृत जानकारी देखें।"
        else:
            main_loan_name = main_loan_type.replace("_", " ").title()
            sub_type_names = {
                "BUSINESS_LOAN_MUDRA": "MUDRA Loan",
                "BUSINESS_LOAN_TERM": "Term Loan",
                "BUSINESS_LOAN_WORKING_CAPITAL": "Working Capital Loan",
                "BUSINESS_LOAN_INVOICE": "Invoice Financing",
                "BUSINESS_LOAN_EQUIPMENT": "Equipment Financing",
                "BUSINESS_LOAN_OVERDRAFT": "Business Overdraft",
                "HOME_LOAN_PURCHASE": "Home Purchase Loan",
                "HOME_LOAN_CONSTRUCTION": "Home Construction Loan",
                "HOME_LOAN_PLOT_CONSTRUCTION": "Plot Construction Loan",
                "HOME_LOAN_EXTENSION": "Home Extension Loan",
                "HOME_LOAN_RENOVATION": "Home Renovation Loan",
                "HOME_LOAN_BALANCE_TRANSFER": "Balance Transfer Loan",
            }
            sub_names_list = [sub_type_names.get(st, st.replace("_", " ").title()) for st in sub_loan_types]
            response_text = f"For {main_loan_name}, we have {len(all_loan_cards)} options available: {', '.join(sub_names_list)}. See detailed information in the cards below."
        
        state["structured_data"] = {"type": "loan_multiple", "loanCards": all_loan_cards}
        state["messages"].append(AIMessage(content=response_text))
        state["next_action"] = "end"
        logger.info("rag_loan_agent_response", has_structured=True, multiple_cards=len(all_loan_cards))
        return state
    
    # If extraction failed, fall back to selection interface
    return _create_sub_loan_selection(state, main_loan_type, sub_loan_types, language)


def _create_sub_loan_selection(state: Dict[str, Any], main_loan_type: str, sub_loan_types: List[str], language: str) -> Dict[str, Any]:
    """Create a selection interface for sub-loan types."""
    if language == "hi-IN":
        main_loan_name = {
            "business_loan": "बिजनेस लोन",
            "home_loan": "होम लोन",
        }.get(main_loan_type, main_loan_type.replace("_", " ").title())
        
        sub_loan_options = []
        sub_type_names = {
            "BUSINESS_LOAN_MUDRA": ("MUDRA लोन", "MSME के लिए छोटे व्यवसाय लोन"),
            "BUSINESS_LOAN_TERM": ("टर्म लोन", "दीर्घकालिक व्यवसाय वित्तपोषण"),
            "BUSINESS_LOAN_WORKING_CAPITAL": ("वर्किंग कैपिटल लोन", "दैनिक व्यवसाय संचालन के लिए"),
            "BUSINESS_LOAN_INVOICE": ("इनवॉइस फाइनेंसिंग", "इनवॉइस के खिलाफ वित्तपोषण"),
            "BUSINESS_LOAN_EQUIPMENT": ("इक्विपमेंट फाइनेंसिंग", "मशीनरी और उपकरण खरीद के लिए"),
            "BUSINESS_LOAN_OVERDRAFT": ("बिजनेस ओवरड्राफ्ट", "लचीला क्रेडिट सुविधा"),
            "HOME_LOAN_PURCHASE": ("होम पर्चेज लोन", "नया घर खरीदने के लिए"),
            "HOME_LOAN_CONSTRUCTION": ("होम कंस्ट्रक्शन लोन", "घर बनाने के लिए"),
            "HOME_LOAN_PLOT_CONSTRUCTION": ("प्लॉट कंस्ट्रक्शन लोन", "प्लॉट और निर्माण के लिए"),
            "HOME_LOAN_EXTENSION": ("होम एक्सटेंशन लोन", "घर का विस्तार करने के लिए"),
            "HOME_LOAN_RENOVATION": ("होम रेनोवेशन लोन", "घर की मरम्मत और सुधार के लिए"),
            "HOME_LOAN_BALANCE_TRANSFER": ("बैलेंस ट्रांसफर लोन", "मौजूदा होम लोन ट्रांसफर करने के लिए"),
        }
        
        for sub_type in sub_loan_types:
            name, desc = sub_type_names.get(sub_type, (sub_type.replace("_", " "), ""))
            sub_loan_options.append({
                "type": sub_type.lower(),
                "name": name,
                "description": desc,
                "icon": "💼" if "BUSINESS" in sub_type else "🏠"
            })
        
        response = f"{main_loan_name} के लिए हमारे पास {len(sub_loan_types)} विकल्प उपलब्ध हैं। कृपया अपनी आवश्यकता के अनुसार चुनें:"
    else:
        main_loan_name = main_loan_type.replace("_", " ").title()
        
        sub_loan_options = []
        sub_type_names = {
            "BUSINESS_LOAN_MUDRA": ("MUDRA Loan", "Small business loans for MSME"),
            "BUSINESS_LOAN_TERM": ("Term Loan", "Long-term business financing"),
            "BUSINESS_LOAN_WORKING_CAPITAL": ("Working Capital Loan", "For daily business operations"),
            "BUSINESS_LOAN_INVOICE": ("Invoice Financing", "Financing against invoices"),
            "BUSINESS_LOAN_EQUIPMENT": ("Equipment Financing", "For machinery and equipment purchase"),
            "BUSINESS_LOAN_OVERDRAFT": ("Business Overdraft", "Flexible credit facility"),
            "HOME_LOAN_PURCHASE": ("Home Purchase Loan", "To buy a new home"),
            "HOME_LOAN_CONSTRUCTION": ("Home Construction Loan", "To build a home"),
            "HOME_LOAN_PLOT_CONSTRUCTION": ("Plot Construction Loan", "For plot and construction"),
            "HOME_LOAN_EXTENSION": ("Home Extension Loan", "To extend your home"),
            "HOME_LOAN_RENOVATION": ("Home Renovation Loan", "For home repair and improvement"),
            "HOME_LOAN_BALANCE_TRANSFER": ("Balance Transfer Loan", "To transfer existing home loan"),
        }
        
        for sub_type in sub_loan_types:
            name, desc = sub_type_names.get(sub_type, (sub_type.replace("_", " ").title(), ""))
            sub_loan_options.append({
                "type": sub_type.lower(),
                "name": name,
                "description": desc,
                "icon": "💼" if "BUSINESS" in sub_type else "🏠"
            })
        
        response = f"For {main_loan_name}, we have {len(sub_loan_types)} options available. Please select based on your requirement:"
    
    state["structured_data"] = {"type": "loan_selection", "loans": sub_loan_options}
    state["messages"].append(AIMessage(content=response))
    state["next_action"] = "end"
    logger.info("rag_loan_agent_response", has_structured=True, sub_loan_selection=True, count=len(sub_loan_types))
    return state


async def _extract_loan_card(state, llm, rag_context: str, detected_loan_type: Optional[str], language: str = "en-IN") -> Optional[Dict[str, Any]]:
    import json

    # Build explicit loan type instruction
    loan_type_instruction = ""
    if detected_loan_type:
        # Convert loan type to readable format
        loan_type_readable = detected_loan_type.replace("_", " ").title()
        
        # Map specific sub-loan types to their common names
        loan_type_mapping = {
            "BUSINESS_LOAN_MUDRA": "MUDRA Loan",
            "BUSINESS_LOAN_TERM": "Term Loan or SME Term Loan",
            "BUSINESS_LOAN_WORKING_CAPITAL": "Working Capital Loan",
            "BUSINESS_LOAN_INVOICE": "Invoice Financing",
            "BUSINESS_LOAN_EQUIPMENT": "Equipment Financing",
            "BUSINESS_LOAN_OVERDRAFT": "Business Overdraft",
            "HOME_LOAN_PURCHASE": "Home Purchase Loan",
            "HOME_LOAN_CONSTRUCTION": "Home Construction Loan",
            "HOME_LOAN_PLOT_CONSTRUCTION": "Plot Construction Loan",
            "HOME_LOAN_EXTENSION": "Home Extension Loan",
            "HOME_LOAN_RENOVATION": "Home Renovation Loan",
            "HOME_LOAN_BALANCE_TRANSFER": "Balance Transfer Loan",
        }
        
        # Use mapped name if available, otherwise use readable format
        loan_name = loan_type_mapping.get(detected_loan_type.upper(), loan_type_readable)
        
        if language == "hi-IN":
            # For Hindi, use the Hindi name from mapping
            hindi_loan_names = {
                "BUSINESS_LOAN_MUDRA": "MUDRA लोन",
                "BUSINESS_LOAN_TERM": "टर्म लोन",
                "BUSINESS_LOAN_WORKING_CAPITAL": "वर्किंग कैपिटल लोन",
                "BUSINESS_LOAN_EQUIPMENT": "इक्विपमेंट फाइनेंसिंग",
                "BUSINESS_LOAN_INVOICE": "इनवॉइस फाइनेंसिंग",
                "BUSINESS_LOAN_OVERDRAFT": "बिजनेस ओवरड्राफ्ट",
            }
            hindi_loan_name = hindi_loan_names.get(detected_loan_type.upper(), loan_name)
            loan_type_instruction = f"\nCRITICAL: आपको केवल \"{hindi_loan_name}\" के बारे में जानकारी निकालनी है। संदर्भ में अन्य ऋण प्रकारों (जैसे Loan Against Property, Gold Loan, आदि) की जानकारी को अनदेखा करें। 'name' फ़ील्ड में \"{hindi_loan_name}\" या इसका करीबी रूप होना चाहिए।"
        else:
            loan_type_instruction = f"\nCRITICAL: You MUST extract information ONLY about \"{loan_name}\". Ignore any information about other loan types (such as Loan Against Property, Gold Loan, etc.) that may appear in the context. The 'name' field MUST be \"{loan_name}\" or a close variation (e.g., 'MUDRA Loan', 'Mudra Loan', 'mudra loan' are all acceptable for MUDRA)."

    # Language-specific extraction instructions
    if language == "hi-IN":
        extraction_prompt = f"""निम्नलिखित संदर्भ से ऋण जानकारी निकालें और JSON के रूप में लौटाएं:
{rag_context}
{loan_type_instruction}

निम्नलिखित फ़ील्ड निकालें:
- name: ऋण उत्पाद का नाम (उदाहरण: \"होम लोन\", \"पर्सनल लोन\", \"इक्विपमेंट फाइनेंसिंग\", \"टर्म लोन\") - आवश्यक
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
6. CRITICAL: यदि संदर्भ में तालिका है जिसमें कई ऋण प्रकार हैं (जैसे MUDRA, Term Loan, Working Capital), तो केवल उस ऋण प्रकार की कॉलम जानकारी निकालें जिसके बारे में पूछा गया है। अन्य कॉलमों की जानकारी को पूरी तरह से अनदेखा करें।
7. CRITICAL: यदि संदर्भ में कई ऋण प्रकारों की जानकारी है, तो केवल उस ऋण प्रकार की जानकारी निकालें जो 'name' फ़ील्ड में निर्दिष्ट है। अन्य ऋण प्रकारों की जानकारी को अनदेखा करें।
"""
    else:
        extraction_prompt = f"""Extract loan information from the following context and return as JSON:
{rag_context}
{loan_type_instruction}

Extract the following fields:
- name: Loan product name (e.g., \"Home Loan\", \"Personal Loan\", \"Working Capital Loan\") - REQUIRED
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
            # Remove empty/null values to avoid missing data in cards
            loan_info = {k: v for k, v in loan_info.items() if v is not None and v != "" and v != []}
            
            # Clean all text fields if language is English
            if language == "en-IN":
                for key, value in loan_info.items():
                    if isinstance(value, str):
                        loan_info[key] = _clean_english_text(value)
                    elif isinstance(value, list):
                        loan_info[key] = [_clean_english_text(str(v)) if isinstance(v, str) else v for v in value]
            
            # Ensure critical fields are present - if missing, extraction might have failed
            critical_fields = ["name", "interest_rate"]
            missing_critical = [field for field in critical_fields if not loan_info.get(field)]
            if missing_critical:
                logger.warning(
                    "loan_extraction_missing_critical_fields",
                    missing_fields=missing_critical,
                    extracted_fields=list(loan_info.keys()),
                    detected_loan_type=detected_loan_type
                )
                # Return None to trigger fallback if critical fields are missing
                return None
            
            # Validate extracted loan name matches expected type
            extracted_name = loan_info.get("name", "").lower().strip()
            if detected_loan_type:
                # Map expected loan types to their common names (both English and Hindi)
                expected_names = {
                    "BUSINESS_LOAN_MUDRA": ["mudra", "mudra loan", "mudra लोन", "मुद्रा लोन", "मुद्रा"],
                    "BUSINESS_LOAN_TERM": ["term loan", "sme term loan", "term", "टर्म लोन", "टर्म"],
                    "BUSINESS_LOAN_WORKING_CAPITAL": ["working capital", "working capital loan", "वर्किंग कैपिटल", "वर्किंग कैपिटल लोन"],
                    "BUSINESS_LOAN_EQUIPMENT": ["equipment", "equipment financing", "equipment loan", "इक्विपमेंट", "इक्विपमेंट फाइनेंसिंग"],
                    "BUSINESS_LOAN_INVOICE": ["invoice", "invoice financing", "इनवॉइस", "इनवॉइस फाइनेंसिंग"],
                    "BUSINESS_LOAN_OVERDRAFT": ["overdraft", "business overdraft", "ओवरड्राफ्ट", "बिजनेस ओवरड्राफ्ट"],
                    "HOME_LOAN_PURCHASE": ["purchase", "home purchase"],
                    "HOME_LOAN_CONSTRUCTION": ["construction", "home construction"],
                    "HOME_LOAN_PLOT_CONSTRUCTION": ["plot", "plot construction"],
                    "HOME_LOAN_EXTENSION": ["extension", "home extension"],
                    "HOME_LOAN_RENOVATION": ["renovation", "home renovation"],
                    "HOME_LOAN_BALANCE_TRANSFER": ["balance transfer"],
                }
                
                expected_loan_type_upper = detected_loan_type.upper()
                expected_name_list = expected_names.get(expected_loan_type_upper, [])
                
                # Check if extracted name matches expected type
                name_matches = any(
                    expected_name in extracted_name 
                    for expected_name in expected_name_list
                ) if expected_name_list else True
                
                if not name_matches and expected_name_list:
                    logger.warning(
                        "extracted_loan_name_mismatch",
                        expected_type=detected_loan_type,
                        expected_names=expected_name_list,
                        extracted_name=extracted_name,
                        action="Will use extracted data but name doesn't match expected type"
                    )
                    # Try to fix the name if we can identify it
                    for expected_name in expected_name_list:
                        if expected_name.lower() in extracted_name or any(
                            word.lower() in extracted_name for word in expected_name.split()
                        ):
                            # Update name to match expected format
                            if language == "hi-IN":
                                # Use Hindi name from mapping
                                hindi_loan_names = {
                                    "BUSINESS_LOAN_MUDRA": "MUDRA लोन",
                                    "BUSINESS_LOAN_TERM": "टर्म लोन",
                                    "BUSINESS_LOAN_WORKING_CAPITAL": "वर्किंग कैपिटल लोन",
                                    "BUSINESS_LOAN_EQUIPMENT": "इक्विपमेंट फाइनेंसिंग",
                                    "BUSINESS_LOAN_INVOICE": "इनवॉइस फाइनेंसिंग",
                                    "BUSINESS_LOAN_OVERDRAFT": "बिजनेस ओवरड्राफ्ट",
                                }
                                loan_info["name"] = hindi_loan_names.get(expected_loan_type_upper, loan_info.get("name", ""))
                            else:
                                # Use the expected name format
                                loan_info["name"] = expected_name.title() if "loan" in expected_name.lower() else f"{expected_name.title()} Loan"
                            name_matches = True
                            logger.info(
                                "loan_name_corrected",
                                original=extracted_name,
                                corrected=loan_info.get("name")
                            )
                            break
                
                # CRITICAL: If name is still missing or empty after validation, use fallback
                if not loan_info.get("name") or loan_info.get("name", "").strip() == "":
                    logger.warning(
                        "extracted_loan_name_still_missing",
                        expected_type=detected_loan_type,
                        action="Using fallback loan name"
                    )
                    if language == "hi-IN":
                        hindi_fallback_names = {
                            "BUSINESS_LOAN_MUDRA": "MUDRA लोन",
                            "BUSINESS_LOAN_TERM": "टर्म लोन",
                            "BUSINESS_LOAN_WORKING_CAPITAL": "वर्किंग कैपिटल लोन",
                            "BUSINESS_LOAN_EQUIPMENT": "इक्विपमेंट फाइनेंसिंग",
                            "BUSINESS_LOAN_INVOICE": "इनवॉइस फाइनेंसिंग",
                            "BUSINESS_LOAN_OVERDRAFT": "बिजनेस ओवरड्राफ्ट",
                        }
                        loan_info["name"] = hindi_fallback_names.get(expected_loan_type_upper, loan_type_readable)
                    else:
                        loan_info["name"] = loan_type_readable
            
            # Add loan_type to loan_info for frontend to use for document download
            if detected_loan_type:
                loan_info["loan_type"] = detected_loan_type.upper()
            
            state["structured_data"] = {"type": "loan", "loanInfo": loan_info}
            logger.info(
                "loan_info_extracted",
                loan_name=loan_info.get("name", "unknown"),
                expected_type=detected_loan_type,
                loan_type_added=loan_info.get("loan_type"),
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
            language_instruction = "\n\nCRITICAL: The user has selected Hindi language. You MUST respond ONLY in Hindi (Devanagari script), regardless of the language the question is asked in. Even if the user asks in English, you MUST respond in Hindi. NEVER respond in English or any other language."
        elif language == "en-IN":
            language_instruction = "\n\nCRITICAL: The user has selected English language. You MUST respond ONLY in English. NEVER respond in Hindi, Devanagari script, or any other language. Use only English words and characters."
        return f"""You are Vaani, a helpful AI assistant for Sun National Bank (an Indian bank).

The user has asked a question about banking products/loans. Below is relevant information from our official product documentation:

{rag_context}{user_name_context}{language_instruction}

SAFETY & SCOPE:
- You are a Banking Assistant. You DO NOT answer questions about coding, math, general knowledge, or politics. If asked, politely decline and ask them to ask banking-related questions.
- Do not provide financial advice (e.g., "buy this stock"). Only provide factual information about bank schemes.
- Never share sensitive information like Aadhaar, PAN, account numbers, PINs, or CVV.

Based on the above information, provide a clear, accurate, and helpful answer to the user's question.

IMPORTANT GUIDELINES:
- Always use Indian Rupees (₹ or INR) for all monetary amounts
- Base your answer ONLY on the provided documentation above
- If the documentation doesn't contain the information, say "I don't have information on that specific product" - DO NOT make up or guess answers
- Be concise but comprehensive
- Use bullet points for lists of features, requirements, or steps
- If mentioning interest rates or fees, include the range (e.g., "8.50% - 11.50% p.a.")
- For eligibility or documents, distinguish between salaried and self-employed if relevant

ENGLISH LANGUAGE GUIDELINES (when responding in English):
- CRITICAL: Use ONLY English. NEVER use Hindi, Devanagari script, or any other language
- Use clear, professional English
- Keep sentences simple and conversational
- ALWAYS use the user's actual name from user_context if available

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
        language_instruction = "\n\nCRITICAL: The user has selected Hindi language. You MUST respond ONLY in Hindi (Devanagari script), regardless of the language the question is asked in. Even if the user asks in English, you MUST respond in Hindi. NEVER respond in English or any other language."
    elif language == "en-IN":
        language_instruction = "\n\nCRITICAL: The user has selected English language. You MUST respond ONLY in English. NEVER respond in Hindi, Devanagari script, or any other language. Use only English words and characters."
    return f"""You are Vaani, a friendly and helpful AI assistant for Sun National Bank, an Indian bank.

IMPORTANT: Always use Indian Rupee (₹ or INR) for all monetary amounts. Never use dollars ($) or other currencies.{user_name_context}{language_instruction}

SAFETY & SCOPE:
- You are a Banking Assistant. You DO NOT answer questions about coding, math, general knowledge, or politics. If asked, politely decline and ask them to ask banking-related questions.
- Do not provide financial advice (e.g., "buy this stock"). Only provide factual information about bank schemes.
- Never share sensitive information like Aadhaar, PAN, account numbers, PINs, or CVV.

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
