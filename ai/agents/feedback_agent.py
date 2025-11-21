"""Agent that acknowledges user feedback and routes it to support workflows."""
from __future__ import annotations

from langchain_core.messages import AIMessage

from utils import logger


async def feedback_agent(state):
    """Acknowledge feedback/complaints without invoking expensive LLM calls."""
    language = state.get("language", "en-IN")
    user_context = state.get("user_context", {})
    user_name = user_context.get("name")
    feedback_bucket = state.get("feedback_bucket")

    if language == "hi-IN":
        message = (
            f"{user_name or 'जी'}, आपके सुझाव और प्रतिक्रिया के लिए धन्यवाद। "
            "मैंने इसे हमारी सहायता टीम के साथ साझा कर दिया है ताकि हम तुरंत कार्रवाई कर सकें।"
        )
    else:
        message = (
            f"Thanks for sharing that, {user_name or 'friend'}. "
            "I’ve logged your feedback with our support team so we can follow up quickly."
        )

    if feedback_bucket:
        if language == "hi-IN":
            message += "\nहम इसे श्रेणी: {} के अंतर्गत ट्रैक कर रहे हैं।".format(feedback_bucket)
        else:
            message += f"\nWe’re tracking this under the '{feedback_bucket}' category."

    state.setdefault("messages", []).append(AIMessage(content=message))
    state["current_intent"] = "feedback"
    state.setdefault("structured_data", {})
    state["structured_data"].update({
        "type": "system_hint",
        "hint": "feedback_acknowledgement",
    })

    logger.info("feedback_agent_response", bucket=feedback_bucket, language=language)
    return state
