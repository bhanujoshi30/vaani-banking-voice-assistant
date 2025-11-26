"""
Unified LLM Service
Provides a single interface to switch between Ollama (local) and OpenAI (cloud)
"""
from typing import List, Dict, Optional, AsyncGenerator
from enum import Enum
import time

# Defensive imports - don't crash if these fail
try:
    from config import settings
except Exception:
    # Fallback settings
    class Settings:
        llm_provider = "openai"
        openai_model = "gpt-3.5-turbo"
        openai_api_key = None
        openai_enabled = False
    settings = Settings()

try:
    from utils import logger
except Exception:
    import logging
    logger = logging.getLogger(__name__)

try:
    from utils.demo_logging import demo_logger
except Exception:
    import logging
    demo_logger = logging.getLogger("demo")

try:
    from .ollama_service import OllamaService
except ImportError:
    OllamaService = None

try:
    from .openai_service import OpenAIService
except ImportError:
    OpenAIService = None

try:
    from .langsmith_ollama_service import chat_with_tracing
except ImportError:
    chat_with_tracing = None


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OLLAMA = "ollama"  # Local Ollama models
    OPENAI = "openai"  # OpenAI GPT models


class LLMService:
    """
    Unified service for LLM interactions.
    Automatically switches between Ollama and OpenAI based on configuration.
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM service with specified provider
        
        Args:
            provider: LLMProvider.OLLAMA or LLMProvider.OPENAI
                     If None, uses settings.llm_provider (defaults to OLLAMA)
        """
        # Determine provider
        if provider is None:
            provider_str = getattr(settings, 'llm_provider', 'ollama').lower()
            self.provider = LLMProvider(provider_str)
        else:
            self.provider = provider
        
        # Initialize the appropriate service
        if self.provider == LLMProvider.OLLAMA:
            self.service = OllamaService()
            logger.info("llm_service_initialized", provider="ollama (local)")
        elif self.provider == LLMProvider.OPENAI:
            self.service = OpenAIService()
            logger.info("llm_service_initialized", provider="openai (cloud)")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        use_fast_model: bool = False,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Send chat request to configured LLM provider
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            use_fast_model: Use faster/cheaper model (only for Ollama)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        start_time = time.time()
        
        # Log which provider is being used
        provider_name = "🤖 Ollama (Local)" if self.provider == LLMProvider.OLLAMA else "🌐 OpenAI GPT (Cloud)"
        model_name = self.service.model if hasattr(self.service, 'model') else "unknown"
        
        # Calculate prompt length
        prompt_length = sum(len(msg.get('content', '')) for msg in messages)
        
        logger.info(
            "llm_request",
            provider=provider_name,
            model=model_name,
            message_count=len(messages)
        )
        
        # Decide whether to go through LangChain/LangSmith for tracing
        use_langsmith_tracing = (
            self.provider == LLMProvider.OLLAMA
            and bool(getattr(settings, "langchain_tracing_v2", False))
            and bool(getattr(settings, "langchain_api_key", None))
        )

        if use_langsmith_tracing:
            # Route via LangChain's ChatOllama so LangSmith captures traces
            response = await chat_with_tracing(
                messages=messages,
                use_fast_model=use_fast_model,
            )
        else:
            # Default path: direct provider implementation
            response = await self.service.chat(
                messages=messages,
                use_fast_model=use_fast_model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        
        # Calculate metrics
        duration_ms = (time.time() - start_time) * 1000
        response_length = len(response)
        
        # Demo logging: LLM call
        demo_logger.llm_call(
            model=model_name,
            prompt_length=prompt_length,
            response_length=response_length,
            duration_ms=duration_ms,
        )
        
        return response
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        use_fast_model: bool = False,
        temperature: float = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from configured LLM provider
        
        Args:
            messages: List of message dicts
            use_fast_model: Use faster/cheaper model (only for Ollama)
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they're generated
        """
        # Log which provider is being used
        provider_name = "🤖 Ollama (Local)" if self.provider == LLMProvider.OLLAMA else "🌐 OpenAI GPT (Cloud)"
        logger.info(
            "llm_stream_request",
            provider=provider_name,
            model=self.service.model if hasattr(self.service, 'model') else "unknown",
            message_count=len(messages)
        )
        
        async for chunk in self.service.chat_stream(
            messages=messages,
            use_fast_model=use_fast_model,
            temperature=temperature,
        ):
            yield chunk
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using configured provider
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        return await self.service.generate_embeddings(text)
    
    async def health_check(self) -> bool:
        """
        Check if LLM service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        return await self.service.health_check()
    
    async def close(self):
        """Close the service client"""
        await self.service.close()
    
    def get_provider_name(self) -> str:
        """Get the name of the current provider"""
        return self.provider.value


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service(provider: Optional[LLMProvider] = None) -> LLMService:
    """
    Get or create unified LLM service instance
    
    Args:
        provider: Optional provider to use. If None, uses config setting.
        
    Returns:
        LLMService instance
        
    Examples:
        # Use default from config (ollama)
        llm = get_llm_service()
        
        # Explicitly use Ollama
        llm = get_llm_service(LLMProvider.OLLAMA)
        
        # Explicitly use OpenAI
        llm = get_llm_service(LLMProvider.OPENAI)
    """
    global _llm_service
    
    # If provider is specified and different from current, recreate service
    if provider is not None:
        current_provider = _llm_service.provider if _llm_service else None
        if current_provider != provider:
            _llm_service = LLMService(provider=provider)
    
    # Create service if it doesn't exist
    if _llm_service is None:
        _llm_service = LLMService(provider=provider)
    
    return _llm_service


async def get_llm_service_async(provider: Optional[LLMProvider] = None) -> LLMService:
    """
    Async version of get_llm_service for consistency
    
    Args:
        provider: Optional provider to use
        
    Returns:
        LLMService instance
    """
    return get_llm_service(provider=provider)
