"""Hybrid supervisor orchestrator for the banking assistant."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agents.banking_agent import banking_agent
from agents.feedback_agent import feedback_agent
from agents.rag_agent import rag_agent
from agents.greeting_agent import greeting_agent
from agents.upi_agent import upi_agent
from utils import logger
from utils.demo_logging import demo_logger
from services import get_guardrail_service

from .router import IntentRouter
from .state import ConversationState


SPECIALIST_MAP = {
    "banking_agent": banking_agent,
    "upi_agent": upi_agent,
    "rag_agent": rag_agent,
    "greeting_agent": greeting_agent,
    "feedback_agent": feedback_agent,
}


class HybridSupervisor:
    """Coordinates deterministic routing with specialist agents."""

    def __init__(self) -> None:
        self.router = IntentRouter()
        self.guardrail = get_guardrail_service()

    async def process(
        self,
        *,
        message: str,
        user_id: str,
        session_id: str,
        language: str = "en-IN",
        user_context: Optional[Dict[str, Any]] = None,
        message_history: Optional[List[Dict[str, Any]]] = None,
        upi_mode: Optional[bool] = None,
    ) -> Dict[str, Any]:
        context = self._build_context(
            message=message,
            user_id=user_id,
            session_id=session_id,
            language=language,
            user_context=user_context or {},
            message_history=message_history or [],
            upi_mode=upi_mode,
        )

        # Guardrail: Validate input before routing (intercept malicious queries early)
        is_valid, guardrail_message = self.guardrail.validate_input(message, language)
        if not is_valid:
            logger.warning("security_event",
                         event_type="input_blocked_by_guardrail",
                         user_id=user_id,
                         language=language,
                         message_preview=message[:100])
            
            # Use guardrail's specific message, or fallback to default
            if guardrail_message:
                refusal_message = guardrail_message
            else:
                # Fallback message
                if language == "hi-IN":
                    refusal_message = "मैं एक बैंकिंग एजेंट हूं। कृपया Sun National Bank से संबंधित बैंकिंग प्रश्न पूछें।"
                else:
                    refusal_message = "I am a banking agent. Please ask questions related to banking at Sun National Bank."
            
            return {
                "success": False,
                "response": refusal_message,
                "intent": "blocked",
                "language": language,
                "timestamp": datetime.now().isoformat(),
            }

        intent = await self.router.assign_intent(context)
        agent_key = self.router.resolve_route(intent)
        
        # Demo logging: Agent routing decision
        demo_logger.agent_decision(
            agent_name=agent_key,
            intent=intent,
            confidence=getattr(intent, 'confidence', None) if hasattr(intent, 'confidence') else None,
            language=context.language,
            upi_mode=context.upi_mode,
        )
        
        await self._invoke_specialist(agent_key, context)

        return self._build_response(context)

    def _build_context(
        self,
        *,
        message: str,
        user_id: str,
        session_id: str,
        language: str,
    user_context: Dict[str, Any],
    message_history: List[Dict[str, Any]],
        upi_mode: Optional[bool],
    ) -> ConversationState:
        messages: List[BaseMessage] = []
        for entry in message_history:
            role = entry.get("role")
            content = entry.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=message))

        inferred_upi_mode = self._infer_upi_mode(upi_mode, message_history)

        context = ConversationState(
            messages=messages,
            user_id=user_id,
            session_id=session_id,
            language=language,
            user_context=user_context,
            upi_mode=inferred_upi_mode,
            authenticated=bool(user_id),
        )
        logger.info(
            "conversation_context_created",
            upi_mode=context.upi_mode,
            language=context.language,
        )
        return context

    def _infer_upi_mode(
        self,
        upi_flag: Optional[bool],
        message_history: List[Dict[str, Any]],
    ) -> bool:
        if upi_flag is not None:
            return upi_flag

        for entry in reversed(message_history[-10:]):
            if entry.get("role") == "assistant":
                content = entry.get("content", "").lower()
                if any(
                    phrase in content
                    for phrase in [
                        "upi mode",
                        "upi मोड",
                        "upi mode active",
                        "upi mode activated",
                        "i'm in upi mode",
                        "मैं upi मोड में",
                    ]
                ):
                    return True
            structured = entry.get("structured_data")
            if structured and structured.get("type") in {
                "upi_mode_activation",
                "upi_payment",
                "upi_balance_check",
            }:
                return True
        return False

    async def _invoke_specialist(self, agent_key: str, context: ConversationState) -> None:
        handler = SPECIALIST_MAP.get(agent_key, rag_agent)
        logger.info("invoking_specialist", agent=agent_key)
        agent_state = await handler(context.to_agent_payload())
        context.apply_agent_state(agent_state)

    def _build_response(self, context: ConversationState) -> Dict[str, Any]:
        last_message = context.messages[-1] if context.messages else AIMessage(content="")
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # Guardrail: Sanitize output - redact PII and normalize refusals
        # Skip language consistency check for language_change intents (handled in main.py check_output)
        sanitized_response = self.guardrail.sanitize_output(response_text, context.language)
        
        payload: Dict[str, Any] = {
            "success": True,
            "response": sanitized_response,
            "intent": context.current_intent,
            "language": context.language,
            "timestamp": datetime.now().isoformat(),
        }
        if context.statement_data:
            payload["statement_data"] = context.statement_data
        if context.structured_data:
            payload["structured_data"] = context.structured_data
        return payload
