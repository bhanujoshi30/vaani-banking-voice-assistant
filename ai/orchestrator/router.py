"""Intent routing helpers for the hybrid supervisor."""
from __future__ import annotations

from typing import Dict

from utils import logger
from agents.intent_classifier import classify_intent

from .state import ConversationState


DEFAULT_ROUTE = "faq_agent"
INTENT_TO_ROUTE: Dict[str, str] = {
    "upi_payment": "upi_agent",
    "banking_operation": "banking_agent",
    "general_faq": "faq_agent",
    "greeting": "greeting_agent",
    "feedback": "feedback_agent",
    "other": "faq_agent",
}


class IntentRouter:
    """Delegates to the legacy classifier and normalises the result."""

    async def assign_intent(self, context: ConversationState) -> str:
        """Classify the current turn and update the context object."""
        state_payload = context.to_agent_payload()
        updated_state = await classify_intent(state_payload)
        context.apply_agent_state(updated_state)
        context.current_intent = updated_state.get("current_intent", context.current_intent)
        logger.info(
            "intent_router_decision",
            intent=context.current_intent,
            upi_mode=context.upi_mode,
        )
        return context.current_intent or "other"

    def resolve_route(self, intent: str) -> str:
        """Map a classified intent to a concrete specialist agent key."""
        return INTENT_TO_ROUTE.get(intent, DEFAULT_ROUTE)
