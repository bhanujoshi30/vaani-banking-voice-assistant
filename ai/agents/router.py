"""
Router Agent
Routes conversation to appropriate specialized agent
"""
from typing import Literal
from utils import logger


def route_to_agent(state) -> Literal["banking_agent", "faq_agent", "end"]:
    """
    Route to appropriate agent based on classified intent
    
    Args:
        state: AgentState with current_intent set
        
    Returns:
        Agent name to route to
    """
    intent = state.get("current_intent", "other")
    
    routing_map = {
        "banking_operation": "banking_agent",
        "general_faq": "faq_agent",
        "greeting": "faq_agent",
        "feedback": "faq_agent",
        "other": "faq_agent",
    }
    
    route = routing_map.get(intent, "faq_agent")
    
    logger.info("routing_decision", intent=intent, route=route)
    
    return route
