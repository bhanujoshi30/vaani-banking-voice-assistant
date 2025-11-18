"""
OpenAI LLM Service
Handles communication with OpenAI API for GPT-3.5 Turbo
"""
import time
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings
from utils import logger, log_llm_call, OpenAIServiceError


class OpenAIService:
    """Service for interacting with OpenAI models"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model or "gpt-3.5-turbo"
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 60.0
        
        if not self.api_key:
            raise OpenAIServiceError("OpenAI API key not configured")
        
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        
        logger.info(
            "openai_service_initialized",
            model=self.model,
            base_url=self.base_url,
            api_key_suffix=f"...{self.api_key[-10:]}" if self.api_key else "None",
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
        Send chat request to OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            use_fast_model: Not used for OpenAI (kept for interface compatibility)
            temperature: Sampling temperature (0-2 for OpenAI)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            OpenAIServiceError: If request fails
        """
        temperature = temperature if temperature is not None else settings.llm_temperature
        max_tokens = max_tokens or settings.llm_max_tokens
        
        start_time = time.time()
        
        try:
            logger.debug(
                "openai_chat_request",
                model=self.model,
                num_messages=len(messages),
                temperature=temperature,
            )
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": settings.llm_top_p,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            duration = time.time() - start_time
            
            # Log the call
            prompt_text = " ".join([m["content"] for m in messages])
            log_llm_call(
                model=self.model,
                prompt=prompt_text,
                response=content,
                duration=duration,
            )
            
            logger.info(
                "openai_chat_success",
                model=self.model,
                duration_seconds=duration,
                response_length=len(content),
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
            )
            
            return content
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(
                "openai_http_error",
                status_code=e.response.status_code,
                error=error_detail,
            )
            raise OpenAIServiceError(f"OpenAI HTTP error: {error_detail}")
            
        except httpx.RequestError as e:
            logger.error(
                "openai_connection_error",
                error=str(e),
            )
            raise OpenAIServiceError(f"Failed to connect to OpenAI: {e}")
            
        except Exception as e:
            logger.error(
                "openai_unexpected_error",
                error=str(e),
            )
            raise OpenAIServiceError(f"Unexpected error: {e}")
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        use_fast_model: bool = False,
        temperature: float = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from OpenAI
        
        Args:
            messages: List of message dicts
            use_fast_model: Not used for OpenAI
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they're generated
        """
        temperature = temperature if temperature is not None else settings.llm_temperature
        
        try:
            logger.debug(
                "openai_stream_request",
                model=self.model,
                num_messages=len(messages),
            )
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": settings.llm_top_p,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(
                "openai_stream_error",
                model=self.model,
                error=str(e),
            )
            raise OpenAIServiceError(f"Stream error: {e}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                json={
                    "model": "text-embedding-ada-002",
                    "input": text,
                },
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["data"][0]["embedding"]
            
        except Exception as e:
            logger.error(
                "openai_embeddings_error",
                error=str(e),
            )
            raise OpenAIServiceError(f"Embeddings error: {e}")
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Make a minimal request to check API key validity
            response = await self.client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Create singleton instance
_openai_service: Optional[OpenAIService] = None


async def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
