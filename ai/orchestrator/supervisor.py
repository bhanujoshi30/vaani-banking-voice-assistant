"""Hybrid supervisor orchestrator for the banking assistant."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agents.banking_agent import banking_agent
from agents.feedback_agent import feedback_agent
from agents.faq_agent import faq_agent
from agents.greeting_agent import greeting_agent
from agents.upi_agent import upi_agent
from utils import logger

from .router import IntentRouter
from .state import ConversationState


SPECIALIST_MAP = {
    "banking_agent": banking_agent,
    "upi_agent": upi_agent,
    "faq_agent": faq_agent,
    "greeting_agent": greeting_agent,
    "feedback_agent": feedback_agent,
}


class HybridSupervisor:
    """Coordinates deterministic routing with specialist agents."""

    def __init__(self) -> None:
        self.router = IntentRouter()

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

        intent = await self.router.assign_intent(context)
        agent_key = self.router.resolve_route(intent)
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
        handler = SPECIALIST_MAP.get(agent_key, faq_agent)
        logger.info("invoking_specialist", agent=agent_key)
        agent_state = await handler(context.to_agent_payload())
        context.apply_agent_state(agent_state)

    def _build_response(self, context: ConversationState) -> Dict[str, Any]:
        last_message = context.messages[-1] if context.messages else AIMessage(content="")
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

        payload: Dict[str, any] = {
            "success": True,
            "response": response_text,
            "intent": context.current_intent,
            "language": context.language,
            "timestamp": datetime.now().isoformat(),
        }
        if context.statement_data:
            payload["statement_data"] = context.statement_data
        if context.structured_data:
            payload["structured_data"] = context.structured_data
        return payload
