"""Utils package initialization"""
from .logging import logger, log_llm_call, log_tool_execution, log_agent_decision
from .exceptions import (
    VaaniAIException,
    OllamaServiceError,
    OpenAIServiceError,
    DatabaseToolError,
    AuthenticationError,
    RateLimitError,
    AzureTTSError,
    AgentExecutionError,
)

__all__ = [
    "logger",
    "log_llm_call",
    "log_tool_execution",
    "log_agent_decision",
    "VaaniAIException",
    "OllamaServiceError",
    "OpenAIServiceError",
    "DatabaseToolError",
    "AuthenticationError",
    "RateLimitError",
    "AzureTTSError",
    "AgentExecutionError",
]
