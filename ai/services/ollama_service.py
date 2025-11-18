"""
Ollama LLM Service
Handles communication with local Ollama server for Qwen 2.5 7B
"""
import time
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings
from utils import logger, log_llm_call, OllamaServiceError


class OllamaService:
    """Service for interacting with Ollama models"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.fast_model = settings.ollama_fast_model
        self.timeout = settings.ollama_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
        logger.info(
            "ollama_service_initialized",
            base_url=self.base_url,
            model=self.model,
            fast_model=self.fast_model,
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def chat(
        self,
        messages: List[Dict[str, str]],
        use_fast_model: bool = False,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Send chat request to Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            use_fast_model: Use fast model (llama3.2:3b) instead of default
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            OllamaServiceError: If request fails
        """
        model = self.fast_model if use_fast_model else self.model
        temperature = temperature or settings.llm_temperature
        max_tokens = max_tokens or settings.llm_max_tokens
        
        start_time = time.time()
        
        try:
            logger.debug(
                "ollama_chat_request",
                model=model,
                num_messages=len(messages),
                temperature=temperature,
            )
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": settings.llm_top_p,
                        "num_ctx": settings.ollama_num_ctx,
                        "num_predict": max_tokens,
                    },
                },
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result.get("message", {}).get("content", "")
            duration = time.time() - start_time
            
            # Log the call
            prompt_text = " ".join([m["content"] for m in messages])
            log_llm_call(
                model=model,
                prompt=prompt_text,
                response=content,
                duration=duration,
            )
            
            logger.info(
                "ollama_chat_success",
                model=model,
                duration_seconds=duration,
                response_length=len(content),
            )
            
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "ollama_http_error",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise OllamaServiceError(f"Ollama HTTP error: {e}")
            
        except httpx.RequestError as e:
            logger.error(
                "ollama_connection_error",
                error=str(e),
            )
            raise OllamaServiceError(f"Failed to connect to Ollama: {e}")
            
        except Exception as e:
            logger.error(
                "ollama_unexpected_error",
                error=str(e),
            )
            raise OllamaServiceError(f"Unexpected error: {e}")
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        use_fast_model: bool = False,
        temperature: float = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from Ollama
        
        Args:
            messages: List of message dicts
            use_fast_model: Use fast model instead of default
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they're generated
        """
        model = self.fast_model if use_fast_model else self.model
        temperature = temperature or settings.llm_temperature
        
        try:
            logger.debug(
                "ollama_stream_request",
                model=model,
                num_messages=len(messages),
            )
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "top_p": settings.llm_top_p,
                        "num_ctx": settings.ollama_num_ctx,
                    },
                },
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            import json
                            chunk = json.loads(line)
                            if not chunk.get("done"):
                                content = chunk.get("message", {}).get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(
                "ollama_stream_error",
                model=model,
                error=str(e),
            )
            raise OllamaServiceError(f"Stream error: {e}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Ollama
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("embedding", [])
            
        except Exception as e:
            logger.error(
                "ollama_embeddings_error",
                error=str(e),
            )
            raise OllamaServiceError(f"Embeddings error: {e}")
    
    async def health_check(self) -> bool:
        """
        Check if Ollama service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Create singleton instance
_ollama_service: Optional[OllamaService] = None


async def get_ollama_service() -> OllamaService:
    """Get or create Ollama service instance"""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
