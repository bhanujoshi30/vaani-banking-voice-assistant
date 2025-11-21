"""
Router Agent
Routes conversation to appropriate specialized agent
"""
from typing import Literal
from utils import logger


def route_to_agent(state) -> Literal["banking_agent", "upi_agent", "rag_agent", "end"]:
    """
    Route to appropriate agent based on classified intent
    
    Args:
        state: AgentState with current_intent set
        
    Returns:
        Agent name to route to
    """
    intent = state.get("current_intent", "other")
    
    routing_map = {
        "upi_payment": "upi_agent",
        "banking_operation": "banking_agent",
        "general_faq": "rag_agent",
        "greeting": "rag_agent",
        "feedback": "rag_agent",
        "other": "rag_agent",
    }
    
    route = routing_map.get(intent, "rag_agent")
    
    # DEBUG: Log routing decision with UPI mode
    upi_mode = state.get("upi_mode", False)
    logger.info("routing_decision", 
               intent=intent, 
               route=route,
               upi_mode=upi_mode,
               message=state.get("messages", [])[-1].content[:100] if state.get("messages") else "")
    
    return route
