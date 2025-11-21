"""Lightweight agent that handles greeting intents."""
from __future__ import annotations

from datetime import datetime
from langchain_core.messages import AIMessage

from utils import logger


def _local_greeting(language: str) -> str:
    hour = datetime.now().hour
    if language == "hi-IN":
        if 4 <= hour < 12:
            return "सुप्रभात"
        if 12 <= hour < 17:
            return "नमस्कार"
        return "शुभ संध्या"
    if 4 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    return "Good evening"


async def greeting_agent(state):
    """Append a friendly welcome message without invoking the LLM."""
    language = state.get("language", "en-IN")
    user_name = state.get("user_context", {}).get("name")
    base = _local_greeting(language)

    if language == "hi-IN":
        body = (
            f"{base} {user_name or 'जी'}! मैं वाणी हूँ—आप की बैंकिंग असिस्टेंट। "
            "आप बैलेंस, स्टेटमेंट, रिमाइंडर या UPI भुगतान जैसी किसी भी मदद के लिए पूछ सकते हैं।"
        )
    else:
        body = (
            f"{base}, {user_name or 'there'}! I'm Vaani, your banking copilot. "
            "Feel free to ask about balances, statements, reminders, or even switch to UPI mode for payments."
        )

    state.setdefault("messages", []).append(AIMessage(content=body))
    state["current_intent"] = "greeting"
    state.setdefault("structured_data", {})
    state["structured_data"].update({
        "type": "system_hint",
        "hint": "greeting",
    })

    logger.info("greeting_agent_response", language=language)
    return state
