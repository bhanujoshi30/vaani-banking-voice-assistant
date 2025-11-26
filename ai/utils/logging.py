"""
Structured logging configuration for AI backend
Provides consistent logging across all modules
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import structlog
from config import settings


def setup_logging():
    """Configure structured logging for the application"""
    
    # Configure standard logging (always use stdout/stderr on Vercel)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Try to add file handler, but don't fail if filesystem is read-only (e.g., Vercel)
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path(settings.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Add file handler with rotation
        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=10_485_760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, settings.log_level.upper()))
        logging.root.addHandler(file_handler)
    except (OSError, PermissionError, IOError) as e:
        # On Vercel or other read-only filesystems, file logging isn't available
        # This is OK - we'll just use stdout/stderr logging
        import warnings
        warnings.warn(f"File logging not available (filesystem may be read-only): {e}. Using stdout/stderr only.")
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.is_development else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


# Create logger instance (with error handling to prevent import failures)
try:
    logger = setup_logging()
except Exception as e:
    # If logging setup fails, create a minimal logger to prevent import errors
    import logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to setup structured logging: {e}. Using basic logging.")


def log_llm_call(model: str, prompt: str, response: str, tokens: int = 0, duration: float = 0):
    """Log LLM API calls for monitoring"""
    logger.info(
        "llm_call",
        model=model,
        prompt_length=len(prompt),
        response_length=len(response),
        tokens=tokens,
        duration_seconds=duration,
    )


def log_tool_execution(tool_name: str, success: bool, duration: float = 0, error: str = None):
    """Log tool execution for debugging"""
    logger.info(
        "tool_execution",
        tool_name=tool_name,
        success=success,
        duration_seconds=duration,
        error=error,
    )


def log_agent_decision(agent: str, intent: str, confidence: float = 0):
    """Log agent routing decisions"""
    logger.info(
        "agent_decision",
        agent=agent,
        intent=intent,
        confidence=confidence,
    )
