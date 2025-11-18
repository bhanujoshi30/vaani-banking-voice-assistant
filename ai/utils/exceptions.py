"""
Custom exceptions for AI backend
"""


class VaaniAIException(Exception):
    """Base exception for all AI-related errors"""
    pass


class OllamaServiceError(VaaniAIException):
    """Raised when Ollama service encounters an error"""
    pass


class OpenAIServiceError(VaaniAIException):
    """Raised when OpenAI service encounters an error"""
    pass


class DatabaseToolError(VaaniAIException):
    """Raised when database tool execution fails"""
    pass


class AuthenticationError(VaaniAIException):
    """Raised when authentication fails"""
    pass


class RateLimitError(VaaniAIException):
    """Raised when rate limit is exceeded"""
    pass


class AzureTTSError(VaaniAIException):
    """Raised when Azure TTS service fails"""
    pass


class AgentExecutionError(VaaniAIException):
    """Raised when agent execution fails"""
    pass
