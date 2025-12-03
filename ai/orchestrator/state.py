"""Conversation state models for the hybrid supervisor."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from langchain_core.messages import BaseMessage


@dataclass
class ConversationState:
    """Container that mirrors the shape of the legacy AgentState dictionary."""

    messages: List[BaseMessage]
    user_id: str
    session_id: str
    language: str
    user_context: Dict[str, Any]
    upi_mode: bool
    authenticated: bool
    statement_data: Dict[str, Any] = field(default_factory=dict)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    current_intent: str = "unknown"
    next_action: str = ""

    def to_agent_payload(self) -> Dict[str, Any]:
        """Return a mutable dict the specialist agents already understand."""
        return {
            "messages": self.messages,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "language": self.language,
            "user_context": self.user_context,
            "upi_mode": self.upi_mode,
            "authenticated": self.authenticated,
            "statement_data": self.statement_data,
            "structured_data": self.structured_data,
            "current_intent": self.current_intent,
            "next_action": self.next_action,
        }

    def apply_agent_state(self, agent_state: Dict[str, Any]) -> None:
        """Sync mutated values from an agent back into the dataclass."""
        for field_name in (
            "messages",
            "statement_data",
            "structured_data",
            "current_intent",
            "next_action",
            "upi_mode",
        ):
            if field_name in agent_state and agent_state[field_name] is not None:
                setattr(self, field_name, agent_state[field_name])

    def snapshot(self) -> Dict[str, Any]:
        """Provide a read-only copy for logging or response serialization."""
        return {
            "current_intent": self.current_intent,
            "upi_mode": self.upi_mode,
            "statement_data": self.statement_data,
            "structured_data": self.structured_data,
        }
