"""Supervisor-backed orchestration entrypoints."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils import logger

from orchestrator import HybridSupervisor

supervisor = HybridSupervisor()


async def process_message(
    message: str,
    user_id: str,
    session_id: str,
    language: str = "en-IN",
    user_context: Optional[Dict[str, Any]] = None,
    message_history: Optional[List[Dict[str, str]]] = None,
    upi_mode: Optional[bool] = None,
) -> Dict[str, Any]:
    try:
        return await supervisor.process(
            message=message,
            user_id=user_id,
            session_id=session_id,
            language=language,
            user_context=user_context,
            message_history=message_history,
            upi_mode=upi_mode,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("message_processing_error", error=str(exc), session_id=session_id)
        error_response = (
            "मुझे खेद है, मुझे आपकी मदद करने में समस्या हो रही है। कृपया पुनः प्रयास करें।"
            if language == "hi-IN"
            else "I'm sorry, I'm having trouble helping you right now. Please try again."
        )
        return {
            "success": False,
            "response": error_response,
            "language": language,
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }


__all__ = ["process_message"]
