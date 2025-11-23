"""
Guardrail Service for AI Chat Agent
Handles input validation, content moderation, and safety checks using only open-source tools
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re
from collections import defaultdict
import time

from utils import logger
from config import settings


class GuardrailViolationType(str, Enum):
    """Types of guardrail violations"""
    TOXIC_CONTENT = "toxic_content"
    PII_DETECTED = "pii_detected"
    PROMPT_INJECTION = "prompt_injection"
    OFF_TOPIC = "off_topic"
    RATE_LIMIT = "rate_limit"
    LANGUAGE_MISMATCH = "language_mismatch"
    INVALID_CONTENT = "invalid_content"


@dataclass
class GuardrailResult:
    """Result of guardrail check"""
    passed: bool
    violation_type: Optional[GuardrailViolationType] = None
    message: Optional[str] = None
    confidence: float = 0.0
    detected_entities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class GuardrailService:
    """Service for enforcing guardrails on user inputs and AI outputs"""
    
    def __init__(self):
        """Initialize guardrail service with keyword lists and patterns"""
        # Load keyword lists
        self.toxic_keywords_en = self._load_toxic_keywords_en()
        self.toxic_keywords_hi = self._load_toxic_keywords_hi()
        self.toxic_keywords_romanized_hi = self._load_toxic_keywords_romanized_hi()
        
        # Load PII patterns
        self.pii_patterns = self._load_pii_patterns()
        
        # Load prompt injection patterns
        self.injection_patterns = self._load_injection_patterns()
        
        # Rate limiting storage (in-memory, per user)
        self.rate_limit_store: Dict[str, List[float]] = defaultdict(list)
        self.rate_limit_lock = {}  # Simple lock mechanism
        
        # Configuration from settings
        self.max_requests_per_minute = getattr(settings, 'guardrail_rate_limit_per_minute', 30)
        self.max_requests_per_hour = getattr(settings, 'guardrail_rate_limit_per_hour', 500)
        self.max_language_mixing_ratio = getattr(settings, 'guardrail_max_language_mixing_ratio', 0.3)
        self.enable_input_guardrails = getattr(settings, 'enable_input_guardrails', True)
        self.enable_output_guardrails = getattr(settings, 'enable_output_guardrails', True)
        
        logger.info("guardrail_service_initialized",
                   toxic_keywords_en=len(self.toxic_keywords_en),
                   toxic_keywords_hi=len(self.toxic_keywords_hi),
                   pii_patterns=len(self.pii_patterns),
                   injection_patterns=len(self.injection_patterns))
    
    def validate_input(self, message: str, language: str = "en-IN") -> tuple[bool, Optional[str]]:
        """
        Validate input message - returns (is_valid, message) tuple.
        This is the main entry point for input validation as per security architect requirements.
        
        Args:
            message: User's message to validate
            language: Language code (en-IN or hi-IN)
            
        Returns:
            Tuple of (is_valid: bool, message: Optional[str])
            - If valid: (True, None)
            - If blocked: (False, refusal_message)
        """
        if not self.enable_input_guardrails:
            return (True, None)
        
        # 1. Jailbreak Detection
        injection_check = self._check_prompt_injection(message, language)
        if not injection_check.passed:
            logger.warning("security_event",
                         event_type="jailbreak_detected",
                         message_preview=message[:100])
            return (False, injection_check.message)
        
        # 2. Topic Filtering
        topic_check = self._check_off_topic(message, language)
        if not topic_check.passed:
            logger.warning("security_event",
                         event_type="off_topic_detected",
                         message_preview=message[:100])
            return (False, topic_check.message)
        
        # 3. Gibberish Detection
        if self._check_gibberish(message):
            logger.warning("security_event",
                         event_type="gibberish_detected",
                         message_preview=message[:100])
            if language == "hi-IN":
                gibberish_message = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
            else:
                gibberish_message = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
            return (False, gibberish_message)
        
        # 4. Content Moderation (Toxicity)
        toxicity_check = self._check_toxicity(message, language)
        if not toxicity_check.passed:
            logger.warning("security_event",
                         event_type="toxic_content_detected",
                         message_preview=message[:100])
            return (False, toxicity_check.message)
        
        # 5. PII Detection
        pii_check = self._check_pii(message, language)
        if not pii_check.passed:
            logger.warning("security_event",
                         event_type="pii_detected",
                         message_preview=message[:100])
            return (False, pii_check.message)
        
        return (True, None)
    
    def sanitize_output(self, response: str, language: str = "en-IN") -> str:
        """
        Sanitize AI-generated output - redacts PII and normalizes refusals.
        
        Args:
            response: AI-generated response text
            language: Language code (en-IN or hi-IN)
            
        Returns:
            Sanitized response string
        """
        if not self.enable_output_guardrails:
            return response
        
        # 1. PII Redaction in text response
        sanitized = self._redact_pii_from_text(response)
        
        # 2. Refusal Normalization
        sanitized = self._normalize_refusal(sanitized, language)
        
        return sanitized
    
    async def check_input(
        self, 
        message: str, 
        language: str = "en-IN",
        user_id: Optional[str] = None
    ) -> GuardrailResult:
        """
        Check user input against all guardrails
        
        Args:
            message: User's message
            language: Language code (en-IN or hi-IN)
            user_id: Optional user ID for rate limiting
            
        Returns:
            GuardrailResult indicating if input passes all checks
        """
        # Skip if guardrails disabled
        if not self.enable_input_guardrails:
            return GuardrailResult(passed=True, metadata={"disabled": True})
        
        start_time = time.time()
        
        # 1. Content Moderation
        toxicity_check = self._check_toxicity(message, language)
        if not toxicity_check.passed:
            logger.warning("guardrail_violation",
                         violation_type=toxicity_check.violation_type,
                         check_type="input",
                         language=language)
            return toxicity_check
        
        # 2. PII Detection
        pii_check = self._check_pii(message, language)
        if not pii_check.passed:
            logger.warning("guardrail_violation",
                         violation_type=pii_check.violation_type,
                         check_type="input",
                         language=language,
                         detected_entities=pii_check.detected_entities)
            return pii_check
        
        # 3. Prompt Injection Detection
        injection_check = self._check_prompt_injection(message, language)
        if not injection_check.passed:
            logger.warning("guardrail_violation",
                         violation_type=injection_check.violation_type,
                         check_type="input",
                         language=language)
            return injection_check
        
        # 4. Rate Limiting (if user_id provided)
        if user_id:
            rate_check = self._check_rate_limit(user_id)
            if not rate_check.passed:
                logger.warning("guardrail_violation",
                             violation_type=rate_check.violation_type,
                             check_type="input",
                             user_id=user_id)
                return rate_check
        
        duration_ms = (time.time() - start_time) * 1000
        logger.debug("guardrail_check_passed",
                    check_type="input",
                    duration_ms=duration_ms,
                    language=language)
        
        return GuardrailResult(passed=True, metadata={"duration_ms": duration_ms})
    
    async def check_output(
        self,
        response: str,
        language: str = "en-IN",
        original_query: Optional[str] = None,
        intent: Optional[str] = None
    ) -> GuardrailResult:
        """
        Check AI-generated response against guardrails
        
        Args:
            response: AI-generated response
            language: Expected language code
            original_query: Original user query for context
            intent: Current intent (e.g., "language_change") - used to skip certain checks
            
        Returns:
            GuardrailResult indicating if output passes all checks
        """
        # Skip if guardrails disabled
        if not self.enable_output_guardrails:
            return GuardrailResult(passed=True, metadata={"disabled": True})
        
        start_time = time.time()
        
        # 1. Language Consistency
        # Skip language consistency check for language_change intents
        # (response language will intentionally differ from request language)
        if intent != "language_change":
            lang_check = self._check_language_consistency(response, language)
            if not lang_check.passed:
                logger.warning("guardrail_violation",
                             violation_type=lang_check.violation_type,
                             check_type="output",
                             language=language,
                             intent=intent)
                return lang_check
        
        # 2. Response Safety (check for toxic content in output)
        safety_check = self._check_toxicity(response, language)
        if not safety_check.passed:
            logger.warning("guardrail_violation",
                         violation_type=safety_check.violation_type,
                         check_type="output",
                         language=language)
            return safety_check
        
        # 3. Check for PII leakage in response
        pii_check = self._check_pii(response, language)
        if not pii_check.passed:
            logger.warning("guardrail_violation",
                         violation_type=pii_check.violation_type,
                         check_type="output",
                         language=language)
            return pii_check
        
        duration_ms = (time.time() - start_time) * 1000
        logger.debug("guardrail_check_passed",
                    check_type="output",
                    duration_ms=duration_ms,
                    language=language)
        
        return GuardrailResult(passed=True, metadata={"duration_ms": duration_ms})
    
    def _load_toxic_keywords_en(self) -> Set[str]:
        """Load English toxic keywords - comprehensive list for banking context"""
        return {
            # Profanity (common words)
            "fuck", "fucking", "fucked", "fucker", "shit", "shitting", "shitted",
            "damn", "damned", "dammit", "hell", "crap", "crap", "ass", "asshole",
            "bitch", "bastard", "piss", "pissed", "piss off",
            # Threats
            "kill you", "hurt you", "attack you", "destroy you", "sue you",
            "sue", "lawsuit", "legal action", "file complaint",
            # Hate speech indicators
            "hate you", "stupid", "idiot", "moron", "fool", "dumb", "dumbass",
            "retard", "retarded", "imbecile",
            # Harassment
            "shut up", "shut your mouth", "be quiet", "shut the fuck up",
            "fuck off", "piss off", "go to hell",
            # Aggressive language
            "useless", "worthless", "pathetic", "terrible", "worst",
        }
    
    def _load_toxic_keywords_hi(self) -> Set[str]:
        """Load Hindi toxic keywords (Devanagari script)"""
        return {
            # Profanity
            "बकवास", "गंदा", "मूर्ख",
            # Threats
            "मार दूंगा", "हत्या", "नुकसान",
            # Hate speech
            "नफरत", "बेवकूफ", "मूर्ख", "गधा",
            # Harassment
            "चुप रहो", "बंद करो", "खामोश",
        }
    
    def _load_toxic_keywords_romanized_hi(self) -> Set[str]:
        """Load Romanized Hindi toxic keywords"""
        return {
            # Common Romanized Hindi profanity
            "bakwas", "ganda", "murkha", "chutiya", "bhosdike", "madarchod",
            "behenchod", "lund", "gaand", "chut", "bhenchod",
            "maar dunga", "hate", "stupid", "fuck", "shit",
            "chup raho", "band karo", "teri maa", "teri behen",
        }
    
    def _load_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Load PII detection patterns for Indian context"""
        return {
            # Aadhaar: 12 digits, optionally space-separated
            "aadhaar": re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
            
            # PAN: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)
            "pan": re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
            
            # Account numbers: 9-18 digits (common Indian bank account lengths)
            "account_number": re.compile(r'\b\d{9,18}\b'),
            
            # CVV: 3-4 digits
            "cvv": re.compile(r'\b(?:cvv|cvc)\s*:?\s*\d{3,4}\b', re.IGNORECASE),
            
            # PIN: 4-6 digits (banking PINs)
            "pin": re.compile(r'\b(?:pin|password)\s*:?\s*\d{4,6}\b', re.IGNORECASE),
            
            # Indian phone numbers: 10 digits starting with 6-9
            "phone": re.compile(r'\b[6-9]\d{9}\b'),
            
            # Credit/Debit card: 16 digits (optionally space-separated)
            "card_number": re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b'),
            
            # IFSC code: 11 characters (4 letters + 0 + 6 alphanumeric)
            "ifsc": re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),
        }
    
    def _load_injection_patterns(self) -> List[re.Pattern]:
        """Load prompt injection detection patterns - enhanced with DAN and other jailbreaks"""
        return [
            # English patterns
            re.compile(r'ignore\s+(previous|above|all|all\s+previous)\s+(instructions|rules|prompts|directives)', re.IGNORECASE),
            re.compile(r'forget\s+(everything|all|previous|all\s+previous)', re.IGNORECASE),
            re.compile(r'you\s+are\s+(now|nowadays|currently)\s+(a|an|the)', re.IGNORECASE),
            re.compile(r'system\s*:\s*', re.IGNORECASE),
            re.compile(r'<\|(system|assistant|user)\|>', re.IGNORECASE),
            re.compile(r'\[SYSTEM\]|\[ASSISTANT\]|\[USER\]', re.IGNORECASE),
            re.compile(r'override\s+(system|instructions|rules)', re.IGNORECASE),
            re.compile(r'disregard\s+(previous|above|all)', re.IGNORECASE),
            re.compile(r'pretend\s+you\s+are', re.IGNORECASE),
            re.compile(r'act\s+as\s+if\s+you\s+are', re.IGNORECASE),
            # DAN (Do Anything Now) jailbreak patterns
            re.compile(r'you\s+are\s+DAN', re.IGNORECASE),
            re.compile(r'do\s+anything\s+now', re.IGNORECASE),
            re.compile(r'you\s+are\s+now\s+unrestricted', re.IGNORECASE),
            re.compile(r'break\s+character', re.IGNORECASE),
            re.compile(r'roleplay\s+as', re.IGNORECASE),
            re.compile(r'jailbreak', re.IGNORECASE),
            re.compile(r'developer\s+mode', re.IGNORECASE),
            re.compile(r'admin\s+mode', re.IGNORECASE),
            
            # Hindi patterns (Devanagari)
            re.compile(r'पिछले\s+(निर्देश|नियम|प्रॉम्प्ट)\s+को\s+नजरअंदाज', re.IGNORECASE),
            re.compile(r'सब\s+भूल\s+जाओ', re.IGNORECASE),
            re.compile(r'अब\s+तुम\s+(हो|हैं)', re.IGNORECASE),
            re.compile(r'सिस्टम\s*:\s*', re.IGNORECASE),
            
            # Hindi patterns (Romanized)
            re.compile(r'pichle\s+(nirdesh|niyam)\s+ko\s+nazarandaz', re.IGNORECASE),
            re.compile(r'sab\s+bhool\s+jao', re.IGNORECASE),
            re.compile(r'ab\s+tum\s+(ho|hain)', re.IGNORECASE),
        ]
    
    def _check_off_topic(self, message: str, language: str) -> GuardrailResult:
        """Check if message is about off-topic subjects (non-banking topics)"""
        message_lower = message.lower()
        
        # Banking-related keywords (if query contains these, it's likely banking-related)
        # Note: "investment" is included but we need to check context (banking investment vs non-banking)
        banking_keywords = [
            "account", "balance", "transaction", "loan", "credit", "debit", "deposit",
            "withdraw", "transfer", "upi", "payment", "bill", "statement", "interest",
            "rate", "fd", "rd", "savings", "checking", "bank", "banking",
            "atm", "card", "pin", "password", "branch", "ifsc", "aadhaar", "pan",
            "emi", "scheme", "plan", "insurance", "mutual fund", "ppf", "nps",
            "banking investment", "bank investment", "bank scheme", "bank plan",
            "खाता", "बैलेंस", "लेनदेन", "लोन", "क्रेडिट", "डेबिट", "जमा",
            "निकासी", "ट्रांसफर", "यूपीआई", "भुगतान", "बिल", "स्टेटमेंट", "ब्याज",
            "दर", "निवेश", "एफडी", "आरडी", "बचत", "बैंक", "बैंकिंग",
            "एटीएम", "कार्ड", "पिन", "पासवर्ड", "शाखा", "आईएफएससी", "आधार", "पैन",
            "ईएमआई", "योजना", "बीमा", "म्यूचुअल फंड", "पीपीएफ", "एनपीएस",
            "बैंक निवेश", "बैंक योजना", "बैंक प्लान",
        ]
        
        # Non-banking investment keywords (cryptocurrency, stocks, etc.)
        non_banking_investment_keywords = [
            "bitcoin", "btc", "crypto", "cryptocurrency", "ethereum", "eth",
            "trading", "stock market", "stocks", "shares", "share market",
            "nft", "blockchain", "defi", "altcoin", "dogecoin", "shiba",
            "forex", "forex trading", "commodity", "commodities",
            "air purifier", "amazon", "shopping", "online shopping", "e-commerce",
            "buy", "purchase", "shop", "shopping at", "buy from",
            "investment in bitcoin", "investment in crypto", "investment in air purifier",
            "invest in bitcoin", "invest in crypto", "invest in air purifier",
        ]
        
        # Check if query contains banking keywords - if yes, it's likely banking-related
        has_banking_keyword = any(keyword in message_lower for keyword in banking_keywords)
        
        # Off-topic keywords (general knowledge, non-banking topics)
        off_topic_keywords = [
            # Politics
            "politics", "political", "election", "vote", "president", "prime minister",
            "government", "parliament", "congress", "bjp", "modi", "rahul",
            # Religion
            "religion", "religious", "hindu", "muslim", "christian", "sikh", "buddhist",
            "temple", "mosque", "church", "god", "allah", "jesus", "krishna",
            # Coding/Programming
            "code", "coding", "programming", "python", "javascript", "java", "c++",
            "function", "variable", "algorithm", "debug", "compile", "syntax",
            # Illegal acts
            "hack", "hacking", "steal", "stealing", "rob", "robbery", "fraud",
            "scam", "illegal", "crime", "criminal", "drug", "weapon",
            # General knowledge topics
            "airplane", "aircraft", "plane", "airport", "flight", "fly", "flying",
            "weather", "temperature", "rain", "sunny", "cloud", "storm",
            "sports", "cricket", "football", "soccer", "basketball", "tennis",
            "movie", "film", "actor", "actress", "cinema", "hollywood",
            "recipe", "cooking", "food", "restaurant", "cuisine",
            "science", "physics", "chemistry", "biology", "math", "mathematics",
            "history", "geography", "country", "capital", "city",
            "animal", "dog", "cat", "bird", "fish", "wildlife",
            "car", "vehicle", "bike", "motorcycle", "transport",
            "what is", "what does", "how does", "tell me about", "explain",
            # Question patterns that are likely general knowledge
            "what does a", "what does an", "what is a", "what is an",
            "how do", "how does", "why is", "why are",
            "who is", "who are", "who was", "who were",  # Person queries
            # Famous people/sports personalities (common off-topic queries)
            "ronaldo", "messi", "ronaldo", "messi", "modi", "gandhi", "einstein",
            "celebrity", "famous", "person", "people",
        ]
        
        # Hindi off-topic keywords
        off_topic_keywords_hi = [
            "राजनीति", "चुनाव", "सरकार", "धर्म", "मंदिर", "मस्जिद",
            "कोडिंग", "प्रोग्रामिंग", "अवैध", "अपराध",
            "विमान", "हवाई जहाज", "मौसम", "खेल", "फिल्म", "खाना",
            "विज्ञान", "इतिहास", "भूगोल", "जानवर", "गाड़ी",
        ]
        
        # Check for non-banking investments/shopping keywords
        # But exclude if banking keywords are present (e.g., "buy mutual fund" should be allowed)
        has_non_banking_investment = False
        for keyword in non_banking_investment_keywords:
            if keyword in message_lower:
                # Skip if it's a banking-related query (e.g., "buy mutual fund", "investment plan")
                if not has_banking_keyword:
                    has_non_banking_investment = True
                    break
        
        # If query has banking keywords, it's likely banking-related - allow it
        if has_banking_keyword:
            return GuardrailResult(passed=True)
        
        # If non-banking investment/shopping detected and no banking keywords, block it
        if has_non_banking_investment:
            if language == "hi-IN":
                message_text = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
            else:
                message_text = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
            
            return GuardrailResult(
                passed=False,
                violation_type=GuardrailViolationType.OFF_TOPIC,
                message=message_text,
                confidence=0.9
            )
        
        # Check English keywords
        for keyword in off_topic_keywords:
            if keyword in message_lower:
                if language == "hi-IN":
                    message_text = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
                else:
                    message_text = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
                
                return GuardrailResult(
                    passed=False,
                    violation_type=GuardrailViolationType.OFF_TOPIC,
                    message=message_text,
                    confidence=0.8
                )
        
        # Check Hindi keywords
        for keyword in off_topic_keywords_hi:
            if keyword in message:
                if language == "hi-IN":
                    message_text = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
                else:
                    message_text = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
                
                return GuardrailResult(
                    passed=False,
                    violation_type=GuardrailViolationType.OFF_TOPIC,
                    message=message_text,
                    confidence=0.8
                )
        
        # Additional check: Investment/shopping patterns (non-banking)
        investment_shopping_patterns = [
            r"investment\s+in\s+\w+",  # "investment in bitcoin", "investment in air purifier"
            r"invest\s+in\s+\w+",  # "invest in crypto", "invest in stocks"
            r"shopping\s+at\s+\w+",  # "shopping at Amazon", "shopping at Flipkart"
            r"buy\s+(from|on|at)\s+\w+",  # "buy from Amazon", "buy on Amazon"
            r"purchase\s+(from|on|at)\s+\w+",  # "purchase from Amazon"
        ]
        
        for pattern_str in investment_shopping_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(message_lower):
                # Check if it's NOT a banking-related investment
                if not any(bank_kw in message_lower for bank_kw in ["bank", "banking", "fd", "rd", "ppf", "nps", "mutual fund", "scheme", "plan"]):
                    if language == "hi-IN":
                        message_text = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
                    else:
                        message_text = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
                    
                    return GuardrailResult(
                        passed=False,
                        violation_type=GuardrailViolationType.OFF_TOPIC,
                        message=message_text,
                        confidence=0.85
                    )
        
        # Additional check: If query starts with general knowledge question patterns and has no banking keywords
        general_knowledge_patterns = [
            r"what\s+(does|is|are|was|were)\s+(a|an|the)?\s*\w+",
            r"how\s+(does|do|is|are|was|were)\s+(a|an|the)?\s*\w+",
            r"why\s+(is|are|was|were|does|do)\s+(a|an|the)?\s*\w+",
            r"who\s+(is|are|was|were)\s+\w+",  # "Who is Ronaldo?", "Who are you?"
            r"tell\s+me\s+about\s+(a|an|the)?\s*\w+",
            r"explain\s+(a|an|the)?\s*\w+",
            r"describe\s+(a|an|the)?\s*\w+",
            r"what\s+about\s+\w+",
        ]
        
        for pattern_str in general_knowledge_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(message_lower) and not has_banking_keyword:
                if language == "hi-IN":
                    message_text = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
                else:
                    message_text = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
                
                return GuardrailResult(
                    passed=False,
                    violation_type=GuardrailViolationType.OFF_TOPIC,
                    message=message_text,
                    confidence=0.7
                )
        
        return GuardrailResult(passed=True)
    
    def _check_gibberish(self, message: str) -> bool:
        """
        Detect gibberish - random characters or nonsensical input.
        Returns True if gibberish detected, False otherwise.
        """
        if len(message.strip()) < 3:
            return False  # Too short to be meaningful
        
        # Check for excessive random characters (more than 50% non-alphanumeric)
        alphanumeric_count = len(re.findall(r'[a-zA-Z0-9\u0900-\u097F]', message))
        total_chars = len(message.replace(' ', ''))
        
        if total_chars > 0 and alphanumeric_count / total_chars < 0.5:
            return True  # More than 50% non-alphanumeric = likely gibberish
        
        # Check for repeated characters (e.g., "aaaaaa", "123123123")
        if len(message) > 5:
            # Check for 4+ repeated characters
            repeated_pattern = re.compile(r'(.)\1{3,}')
            if repeated_pattern.search(message):
                return True
        
        # Check for random character sequences (no vowels/consonants pattern)
        if len(message) > 10:
            # Count vowels (English + Hindi)
            vowels = len(re.findall(r'[aeiouAEIOU\u0904-\u0914\u0960-\u0961]', message))
            consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ\u0915-\u0939\u0958-\u095F]', message))
            total_letters = vowels + consonants
            
            if total_letters > 10 and vowels == 0:
                return True  # No vowels in long text = likely gibberish
        
        return False
    
    def _redact_pii_from_text(self, text: str) -> str:
        """Redact PII from text response (16-digit card numbers, PAN, etc.)"""
        sanitized = text
        
        # Redact 16-digit card numbers (with or without spaces)
        card_pattern = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
        sanitized = card_pattern.sub('[CARD REDACTED]', sanitized)
        
        # Redact PAN numbers
        pan_pattern = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')
        sanitized = pan_pattern.sub('[PAN REDACTED]', sanitized)
        
        # Redact Aadhaar numbers
        aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
        sanitized = aadhaar_pattern.sub('[AADHAAR REDACTED]', sanitized)
        
        # Redact account numbers (9-18 digits) - but be careful not to redact amounts
        # Only redact if it looks like an account number (not an amount)
        # Use fixed-width lookbehind (Python requires fixed-width for lookbehind)
        # Find all potential account numbers and check context manually
        account_number_pattern = re.compile(r'\b\d{9,18}\b')
        matches = list(account_number_pattern.finditer(sanitized))
        
        # Process matches in reverse order to maintain indices
        for match in reversed(matches):
            start, end = match.span()
            number = match.group()
            
            # Check context before and after to determine if it's an amount
            before_context = sanitized[max(0, start-30):start].lower()
            after_context = sanitized[end:min(len(sanitized), end+30)].lower()
            
            # Currency indicators that suggest this is an amount, not an account number
            currency_indicators = [
                '₹', 'rs', 'inr', 'rupee', 'rupees', 'lakh', 'crore', 'thousand',
                'balance', 'amount', 'total', 'sum', 'price', 'cost', 'fee'
            ]
            
            # Check if this number is part of an amount
            is_amount = (
                any(indicator in before_context for indicator in currency_indicators) or
                any(indicator in after_context for indicator in currency_indicators)
            )
            
            # Also check if it's part of structured data patterns (like "Account: 123456789")
            is_account_reference = (
                'account' in before_context[-20:] or
                'ac no' in before_context[-20:] or
                'a/c' in before_context[-20:]
            )
            
            # Only redact if it's NOT an amount but could be an account number
            # Be conservative - only redact if it's explicitly mentioned as account number
            # or if it's clearly not an amount
            if is_account_reference or (not is_amount and len(number) >= 12):
                # More likely to be account number if 12+ digits and not an amount
                sanitized = sanitized[:start] + '[ACCOUNT REDACTED]' + sanitized[end:]
        
        return sanitized
    
    def _normalize_refusal(self, response: str, language: str) -> str:
        """Normalize LLM refusal responses to be polite and localized"""
        response_lower = response.lower()
        
        # Check for refusal patterns
        refusal_patterns_en = [
            r"i\s+cannot\s+help",
            r"i\s+can't\s+help",
            r"i\s+am\s+unable\s+to",
            r"i\s+don't\s+have",
            r"i\s+do\s+not\s+have",
            r"sorry,\s*i\s+cannot",
        ]
        
        refusal_patterns_hi = [
            r"मैं\s+नहीं\s+कर\s+सकती",
            r"मैं\s+असमर्थ\s+हूं",
            r"मुझे\s+नहीं\s+पता",
        ]
        
        # Check if response contains refusal
        is_refusal = False
        for pattern in refusal_patterns_en + refusal_patterns_hi:
            if re.search(pattern, response_lower, re.IGNORECASE):
                is_refusal = True
                break
        
        if is_refusal:
            # Replace with polite, localized refusal
            if language == "hi-IN":
                return "मुझे खेद है, मैं केवल बैंकिंग सेवाओं के बारे में मदद कर सकती हूं। कृपया बैंकिंग से संबंधित प्रश्न पूछें।"
            else:
                return "I'm sorry, I can only help with banking services. Please ask banking-related questions."
        
        return response
    
    def _check_toxicity(self, message: str, language: str) -> GuardrailResult:
        """Check for toxic/harmful content using word boundary matching to avoid false positives"""
        message_lower = message.lower()
        
        # Check against language-specific keywords
        if language == "hi-IN":
            # Check Devanagari keywords (use word boundary for multi-word phrases)
            for keyword in self.toxic_keywords_hi:
                # For single words, use word boundary; for phrases, use simple containment
                if len(keyword.split()) == 1:
                    # Single word: use word boundary to avoid false positives (e.g., "hell" in "hello")
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    if pattern.search(message):
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message=(
                                "आपके संदेश में अनुचित सामग्री है। कृपया अपना प्रश्न दोबारा बताएं।"
                                if language == "hi-IN"
                                else "Your message contains inappropriate content. Please rephrase."
                            ),
                            confidence=0.8
                        )
                else:
                    # Multi-word phrase: use simple containment
                    if keyword in message:
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message=(
                                "आपके संदेश में अनुचित सामग्री है। कृपया अपना प्रश्न दोबारा बताएं।"
                                if language == "hi-IN"
                                else "Your message contains inappropriate content. Please rephrase."
                            ),
                            confidence=0.8
                        )
            
            # Check Romanized Hindi keywords
            for keyword in self.toxic_keywords_romanized_hi:
                if len(keyword.split()) == 1:
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    if pattern.search(message_lower):
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message=(
                                "आपके संदेश में अनुचित सामग्री है। कृपया अपना प्रश्न दोबारा बताएं।"
                                if language == "hi-IN"
                                else "Your message contains inappropriate content. Please rephrase."
                            ),
                            confidence=0.7
                        )
                else:
                    if keyword in message_lower:
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message=(
                                "आपके संदेश में अनुचित सामग्री है। कृपया अपना प्रश्न दोबारा बताएं।"
                                if language == "hi-IN"
                                else "Your message contains inappropriate content. Please rephrase."
                            ),
                            confidence=0.7
                        )
        else:  # English
            for keyword in self.toxic_keywords_en:
                if len(keyword.split()) == 1:
                    # Single word: use word boundary to avoid false positives
                    # Example: "hell" should match "go to hell" but NOT "hello"
                    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    if pattern.search(message_lower):
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message="Your message contains inappropriate content. Please rephrase.",
                            confidence=0.8
                        )
                else:
                    # Multi-word phrase: use simple containment
                    if keyword in message_lower:
                        return GuardrailResult(
                            passed=False,
                            violation_type=GuardrailViolationType.TOXIC_CONTENT,
                            message="Your message contains inappropriate content. Please rephrase.",
                            confidence=0.8
                        )
        
        return GuardrailResult(passed=True)
    
    def _check_pii(self, message: str, language: str) -> GuardrailResult:
        """Detect PII in message"""
        detected_entities = []
        entity_types = []
        
        for entity_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(message)
            if matches:
                detected_entities.extend(matches)
                entity_types.append(entity_type)
        
        if detected_entities:
            # Create user-friendly message
            if language == "hi-IN":
                if "aadhaar" in entity_types or "pan" in entity_types:
                    message_text = "कृपया चैट में आधार, PAN, या खाता संख्या जैसी संवेदनशील जानकारी साझा न करें।"
                elif "pin" in entity_types or "cvv" in entity_types:
                    message_text = "कृपया PIN, CVV, या पासवर्ड जैसी संवेदनशील जानकारी साझा न करें।"
                else:
                    message_text = "कृपया संवेदनशील जानकारी साझा न करें।"
            else:
                if "aadhaar" in entity_types or "pan" in entity_types:
                    message_text = "Please do not share sensitive information like Aadhaar, PAN, or account numbers in chat."
                elif "pin" in entity_types or "cvv" in entity_types:
                    message_text = "Please do not share sensitive information like PIN, CVV, or passwords in chat."
                else:
                    message_text = "Please do not share sensitive information in chat."
            
            return GuardrailResult(
                passed=False,
                violation_type=GuardrailViolationType.PII_DETECTED,
                message=message_text,
                detected_entities=detected_entities[:5],  # Limit to first 5
                confidence=0.9,
                metadata={"entity_types": entity_types}
            )
        
        return GuardrailResult(passed=True)
    
    def _check_prompt_injection(self, message: str, language: str) -> GuardrailResult:
        """Detect prompt injection attempts"""
        message_lower = message.lower()
        
        for pattern in self.injection_patterns:
            if pattern.search(message):
                if language == "hi-IN":
                    message_text = "आपका अनुरोध संसाधित नहीं किया जा सका। कृपया अपना प्रश्न दोबारा बताएं।"
                else:
                    message_text = "Your request could not be processed. Please rephrase your question."
                
                return GuardrailResult(
                    passed=False,
                    violation_type=GuardrailViolationType.PROMPT_INJECTION,
                    message=message_text,
                    confidence=0.85
                )
        
        return GuardrailResult(passed=True)
    
    def _check_language_consistency(self, response: str, expected_language: str) -> GuardrailResult:
        """Verify response matches requested language"""
        if not response.strip():
            return GuardrailResult(passed=True)  # Empty response is OK
        
        if expected_language == "hi-IN":
            # Check if response contains Devanagari script
            devanagari_pattern = re.compile(r'[\u0900-\u097F]+')
            has_devanagari = bool(devanagari_pattern.search(response))
            
            # Count words
            words = response.split()
            if not words:
                return GuardrailResult(passed=True)
            
            # Count English words (Latin script)
            english_words = len(re.findall(r'\b[a-zA-Z]+\b', response))
            total_words = len(words)
            
            # Calculate ratio
            if total_words > 0:
                english_ratio = english_words / total_words
                
                # If more than 70% English and no Devanagari, likely wrong language
                if english_ratio > 0.7 and not has_devanagari:
                    return GuardrailResult(
                        passed=False,
                        violation_type=GuardrailViolationType.LANGUAGE_MISMATCH,
                        message="Response language mismatch detected",
                        confidence=0.8,
                        metadata={"english_ratio": english_ratio, "has_devanagari": has_devanagari}
                    )
        else:  # English expected
            # Check for excessive Hindi/Devanagari
            devanagari_pattern = re.compile(r'[\u0900-\u097F]+')
            has_devanagari = bool(devanagari_pattern.search(response))
            
            if has_devanagari:
                # Count Devanagari characters
                devanagari_chars = len(devanagari_pattern.findall(response))
                total_chars = len(response)
                
                if total_chars > 0 and devanagari_chars / total_chars > 0.1:  # More than 10% Hindi
                    return GuardrailResult(
                        passed=False,
                        violation_type=GuardrailViolationType.LANGUAGE_MISMATCH,
                        message="Response language mismatch detected",
                        confidence=0.8,
                        metadata={"devanagari_ratio": devanagari_chars / total_chars}
                    )
        
        return GuardrailResult(passed=True)
    
    def _check_rate_limit(self, user_id: str) -> GuardrailResult:
        """Check rate limiting for user"""
        now = time.time()
        
        # Get user's request history
        user_requests = self.rate_limit_store[user_id]
        
        # Remove requests older than 1 hour
        one_hour_ago = now - 3600
        user_requests = [req_time for req_time in user_requests if req_time > one_hour_ago]
        self.rate_limit_store[user_id] = user_requests
        
        # Check per-minute limit
        one_minute_ago = now - 60
        recent_requests = [req_time for req_time in user_requests if req_time > one_minute_ago]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            return GuardrailResult(
                passed=False,
                violation_type=GuardrailViolationType.RATE_LIMIT,
                message="Too many requests. Please wait a moment and try again.",
                confidence=1.0,
                metadata={"requests_per_minute": len(recent_requests)}
            )
        
        # Check per-hour limit
        if len(user_requests) >= self.max_requests_per_hour:
            return GuardrailResult(
                passed=False,
                violation_type=GuardrailViolationType.RATE_LIMIT,
                message="Too many requests. Please try again later.",
                confidence=1.0,
                metadata={"requests_per_hour": len(user_requests)}
            )
        
        # Add current request
        user_requests.append(now)
        self.rate_limit_store[user_id] = user_requests
        
        return GuardrailResult(passed=True)
    
    def clear_rate_limit(self, user_id: str) -> None:
        """Clear rate limit for a user (useful for testing or admin actions)"""
        if user_id in self.rate_limit_store:
            del self.rate_limit_store[user_id]


# Singleton instance
_guardrail_service: Optional[GuardrailService] = None


def get_guardrail_service() -> GuardrailService:
    """Get or create guardrail service instance"""
    global _guardrail_service
    if _guardrail_service is None:
        _guardrail_service = GuardrailService()
    return _guardrail_service

