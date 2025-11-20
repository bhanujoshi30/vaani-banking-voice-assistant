"""
LangGraph Agent System
Multi-agent orchestration for banking conversations
"""
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from config import settings
from .intent_classifier import classify_intent
from .banking_agent import banking_agent
from .upi_agent import upi_agent
from .faq_agent import faq_agent
from .router import route_to_agent
from utils import logger, AgentExecutionError


# State definition for conversation
class AgentState(TypedDict):
    """State passed between agents in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str  # UUID string
    session_id: str
    language: str
    user_context: Dict[str, Any]  # account_number, name, etc.
    current_intent: str
    authenticated: bool
    next_action: str
    upi_mode: bool  # UPI mode flag for wake-up phrase
    statement_data: Dict[str, Any]  # Account statement data for download
    structured_data: Dict[str, Any]  # Structured data for UI components (transactions, balances, etc.)


# Build the graph
def create_agent_graph():
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("banking_agent", banking_agent)
    workflow.add_node("upi_agent", upi_agent)
    workflow.add_node("faq_agent", faq_agent)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "classify_intent",
        route_to_agent,
        {
            "banking_agent": "banking_agent",
            "upi_agent": "upi_agent",
            "faq_agent": "faq_agent",
            "end": END,
        }
    )
    
    # All agents end the conversation
    workflow.add_edge("banking_agent", END)
    workflow.add_edge("upi_agent", END)
    workflow.add_edge("faq_agent", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    logger.info("agent_graph_initialized", nodes=["classify_intent", "banking_agent", "upi_agent", "faq_agent"])
    
    return graph


# Create the graph instance
agent_graph = create_agent_graph()


async def process_message(
    message: str,
    user_id: str,  # UUID string
    session_id: str,
    language: str = "en-IN",
    user_context: Dict[str, Any] = None,
    message_history: List[Dict[str, str]] = None,
    upi_mode: bool = None  # UPI mode from frontend (optional)
) -> Dict[str, Any]:
    """
    Process a user message through the agent graph
    
    Args:
        message: User's message
        user_id: User ID (UUID string)
        session_id: Session ID
        language: Language code
        user_context: User context (account_number, name, etc.)
        message_history: Previous conversation history
        
    Returns:
        Dictionary with response and metadata
    """
    try:
        # Build message list
        messages = []
        if message_history:
            for msg in message_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=message))
        
        # Determine UPI mode status:
        # 1. Use explicit upi_mode from frontend if provided (most reliable)
        # 2. Otherwise, check conversation history for UPI mode indicators
        upi_mode_active = False
        if upi_mode is not None:
            # Use explicit value from frontend
            upi_mode_active = upi_mode
            logger.info("using_upi_mode_from_frontend", 
                       upi_mode=upi_mode, 
                       message=message[:100],
                       user_id=user_id)
        elif message_history:
            logger.info("upi_mode_not_provided_from_frontend", 
                       upi_mode_param=upi_mode,
                       message=message[:100])
            # Check last few assistant messages for UPI mode indicators
            for msg in reversed(message_history[-10:]):  # Check last 10 messages
                if msg.get("role") == "assistant":
                    content = msg.get("content", "").lower()
                    # Check if message mentions UPI mode activation
                    if any(phrase in content for phrase in [
                        "upi mode", "upi मोड", "upi mode active", "upi mode activated",
                        "i'm in upi mode", "मैं upi मोड में", "upi mode में"
                    ]):
                        upi_mode_active = True
                        logger.info("detected_upi_mode_from_history", message=content[:100])
                        break
                    # Check structured data if available (from previous responses)
                    # Note: structured_data might not be in message_history, but we check anyway
                    if "structured_data" in msg:
                        sd = msg.get("structured_data", {})
                        if sd.get("type") in ["upi_mode_activation", "upi_payment", "upi_balance_check"]:
                            upi_mode_active = True
                            logger.info("detected_upi_mode_from_structured_data", type=sd.get("type"))
                            break
        
        # Create initial state
        initial_state = AgentState(
            messages=messages,
            user_id=user_id,
            session_id=session_id,
            language=language,
            user_context=user_context or {},
            current_intent="",
            authenticated=bool(user_id),
            next_action="",
            upi_mode=upi_mode_active,  # Set based on conversation history
            statement_data={},
            structured_data={}
        )
        
        # Log initial state for debugging
        logger.info("initial_state_created",
                   upi_mode=upi_mode_active,
                   message=message[:100],
                   session_id=session_id)
        
        logger.info(
            "processing_message",
            session_id=session_id,
            language=language,
            message_length=len(message)
        )
        
        # Run through the graph
        final_state = await agent_graph.ainvoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        response = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # Get final intent
        final_intent = final_state.get("current_intent", "unknown")
        final_upi_mode = final_state.get("upi_mode", False)
        
        # DEBUG: Log final state
        logger.info("final_state_before_response",
                   final_intent=final_intent,
                   final_upi_mode=final_upi_mode,
                   message=message[:100],
                   response_preview=response[:100])
        
        # Build response dict
        response_dict = {
            "success": True,
            "response": response,
            "intent": final_intent,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add statement data if present
        if "statement_data" in final_state and final_state["statement_data"]:
            response_dict["statement_data"] = final_state["statement_data"]
        
        # Add structured data if present
        if "structured_data" in final_state and final_state["structured_data"]:
            response_dict["structured_data"] = final_state["structured_data"]
        
        return response_dict
        
    except Exception as e:
        logger.error("message_processing_error", error=str(e), session_id=session_id)
        
        # Return error response in appropriate language
        error_response = (
            "मुझे खेद है, मुझे आपकी मदद करने में समस्या हो रही है। कृपया पुनः प्रयास करें।"
            if language == "hi-IN"
            else "I'm sorry, I'm having trouble helping you right now. Please try again."
        )
        
        return {
            "success": False,
            "response": error_response,
            "language": language,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


__all__ = ["agent_graph", "process_message", "AgentState"]
