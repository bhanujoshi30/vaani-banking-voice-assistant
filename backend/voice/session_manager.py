"""Dialogue state management for the voice assistant."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

from ..db.utils.enums import ReminderType

DEFAULT_TTL = timedelta(minutes=10)


@dataclass(slots=True)
class DialogueState:
    session_id: str
    created_at: datetime
    last_updated: datetime
    last_intent: Optional[str] = None
    filled_slots: Dict[str, str] = field(default_factory=dict)
    pending_slots: Dict[str, str] = field(default_factory=dict)
    confirmation_required: bool = False
    retry_count: int = 0

    def touch(self) -> None:
        self.last_updated = datetime.utcnow()


class VoiceSessionManager:
    """Thread-safe in-memory session store with TTL cleanup."""

    def __init__(self, ttl: timedelta = DEFAULT_TTL):
        self._ttl = ttl
        self._lock = threading.Lock()
        self._sessions: Dict[str, DialogueState] = {}

    def get(self, session_id: str) -> DialogueState:
        with self._lock:
            state = self._sessions.get(session_id)
            now = datetime.utcnow()
            if state and now - state.last_updated > self._ttl:
                del self._sessions[session_id]
                state = None
            if state is None:
                state = DialogueState(
                    session_id=session_id,
                    created_at=now,
                    last_updated=now,
                )
                self._sessions[session_id] = state
            return state

    def update_intent(self, session_id: str, intent: str, slots: Dict[str, str]) -> DialogueState:
        state = self.get(session_id)
        state.last_intent = intent
        state.filled_slots.update(slots)
        state.touch()
        return state

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup(self) -> None:
        with self._lock:
            now = datetime.utcnow()
            expired = [sid for sid, state in self._sessions.items() if now - state.last_updated > self._ttl]
            for sid in expired:
                del self._sessions[sid]


# Singleton for app lifetime usage
voice_session_manager = VoiceSessionManager()

__all__ = ["VoiceSessionManager", "voice_session_manager", "DialogueState"]
