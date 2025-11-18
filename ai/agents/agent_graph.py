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
    statement_data: Dict[str, Any]  # Account statement data for download


# Build the graph
def create_agent_graph():
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("banking_agent", banking_agent)
    workflow.add_node("faq_agent", faq_agent)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "classify_intent",
        route_to_agent,
        {
            "banking_agent": "banking_agent",
            "faq_agent": "faq_agent",
            "end": END,
        }
    )
    
    # Both agents end the conversation
    workflow.add_edge("banking_agent", END)
    workflow.add_edge("faq_agent", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    logger.info("agent_graph_initialized", nodes=["classify_intent", "banking_agent", "faq_agent"])
    
    return graph


# Create the graph instance
agent_graph = create_agent_graph()


async def process_message(
    message: str,
    user_id: str,  # UUID string
    session_id: str,
    language: str = "en-IN",
    user_context: Dict[str, Any] = None,
    message_history: List[Dict[str, str]] = None
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
            statement_data={}
        )
        
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
        
        # Build response dict
        response_dict = {
            "success": True,
            "response": response,
            "intent": final_state.get("current_intent", "unknown"),
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add statement data if present
        if "statement_data" in final_state and final_state["statement_data"]:
            response_dict["statement_data"] = final_state["statement_data"]
        
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
