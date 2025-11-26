"""Services package initialization"""
# Conditional imports for optional services
try:
    from .ollama_service import get_ollama_service, OllamaService
except ImportError:
    # Ollama not available (e.g., in Vercel deployment)
    get_ollama_service = None
    OllamaService = None

# OpenAI service - wrap in try/except
try:
    from .openai_service import get_openai_service, OpenAIService
except Exception:
    # OpenAI service not available
    get_openai_service = None
    OpenAIService = None

# Web TTS (gTTS) - conditional import
try:
    from .web_tts_service import get_web_tts_service, WebTTSService
except ImportError:
    # gTTS not available (e.g., not installed)
    get_web_tts_service = None
    WebTTSService = None

# Legacy Azure TTS (optional, deprecated in favor of Web TTS)
try:
    from .azure_tts_service import get_azure_tts_service, AzureTTSService
except ImportError:
    # Azure TTS not available (e.g., in Vercel deployment)
    get_azure_tts_service = None
    AzureTTSService = None

# LLM service - wrap in try/except
try:
    from .llm_service import get_llm_service, LLMService, LLMProvider
except Exception:
    # LLM service not available
    get_llm_service = None
    LLMService = None
    LLMProvider = None

# Guardrail service - wrap in try/except
try:
    from .guardrail_service import get_guardrail_service, GuardrailService, GuardrailViolationType, GuardrailResult
except Exception:
    # Guardrail service not available
    get_guardrail_service = None
    GuardrailService = None
    GuardrailViolationType = None
    GuardrailResult = None

__all__ = [
    "get_ollama_service",
    "OllamaService",
    "get_openai_service",
    "OpenAIService",
    "get_web_tts_service",
    "WebTTSService",
    "get_azure_tts_service",
    "AzureTTSService",
    "get_llm_service",
    "LLMService",
    "LLMProvider",
    "get_guardrail_service",
    "GuardrailService",
    "GuardrailViolationType",
    "GuardrailResult",
]
