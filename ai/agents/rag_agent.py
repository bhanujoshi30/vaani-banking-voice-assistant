"""Hybrid RAG supervisor agent that orchestrates specialist sub-agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage

from agents.rag_agents.customer_support_agent import handle_customer_support_query
from agents.rag_agents.investment_agent import (
    handle_general_investment_query,
    handle_investment_query,
)
from agents.rag_agents.loan_agent import (
    handle_general_loan_query,
    handle_loan_query,
)
from utils import logger


@dataclass
class QuerySignals:
    """Represents detected intents for the RAG supervisor."""

    is_loan_query: bool
    is_general_loan_query: bool
    is_investment_query: bool
    is_general_investment_query: bool
    detected_loan_type: Optional[str]
    detected_investment_type: Optional[str]


async def rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for the RAG supervisor. Delegates to specialist agents."""
    from services import get_llm_service

    llm = get_llm_service()
    language = state.get("language", "en-IN")
    user_query = _extract_latest_user_query(state) or "Hello"

    signals = _detect_query_signals(user_query)
    logger.info(
        "rag_supervisor_signals",
        is_loan=signals.is_loan_query,
        is_investment=signals.is_investment_query,
        detected_loan=signals.detected_loan_type,
        detected_investment=signals.detected_investment_type,
    )

    if signals.is_general_investment_query and not signals.detected_investment_type:
        return handle_general_investment_query(state, language)

    if signals.is_general_loan_query and not signals.detected_loan_type:
        return handle_general_loan_query(state, language)

    if signals.is_investment_query:
        await handle_investment_query(
            state,
            user_query=user_query,
            language=language,
            llm=llm,
            detected_investment_type=signals.detected_investment_type,
        )
        return state

    if signals.is_loan_query:
        await handle_loan_query(
            state,
            user_query=user_query,
            language=language,
            llm=llm,
            detected_loan_type=signals.detected_loan_type,
        )
        return state

    await handle_customer_support_query(state, user_query=user_query, llm=llm)
    return state


def _extract_latest_user_query(state: Dict[str, Any]) -> Optional[str]:
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    return user_messages[-1].content if user_messages else None


def _detect_query_signals(user_query: str) -> QuerySignals:
    query_lower = user_query.lower()

    loan_keywords = [
        "loan",
        "interest rate",
        "emi",
        "eligibility",
        "documents required",
        "home loan",
        "personal loan",
        "auto loan",
        "car loan",
        "education loan",
        "business loan",
        "gold loan",
        "property loan",
        "mortgage",
        "down payment",
        "processing fee",
        "prepayment",
        "tenure",
        "collateral",
    ]

    general_loan_queries = [
        "what loans",
        "which loans",
        "available loans",
        "types of loans",
        "loan types",
        "loan products",
        "tell me about loans",
        "loans available",
        "what kind of loans",
        "loan options",
        "loan schemes",
    ]

    investment_keywords = [
        "investment",
        "invest",
        "scheme",
        "ppf",
        "nps",
        "ssy",
        "sukanya",
        "elss",
        "fixed deposit",
        "fd",
        "recurring deposit",
        "rd",
        "nsc",
        "tax saving",
        "retirement",
        "pension",
        "savings",
        "mutual fund",
        "public provident fund",
        "national pension",
        "sukanya samriddhi",
        "equity linked",
        "national savings certificate",
    ]

    general_investment_queries = [
        "what investments",
        "which investments",
        "available investments",
        "investment schemes",
        "investment types",
        "investment options",
        "tell me about investments",
        "investments available",
        "what investment schemes",
        "investment plans",
        "savings schemes",
        "tax saving schemes",
        "show me investment",
        "investment options available",
    ]

    specific_loan_types = {
        "home loan": "home_loan",
        "home_loan": "home_loan",
        "personal loan": "personal_loan",
        "personal_loan": "personal_loan",
        "auto loan": "auto_loan",
        "auto_loan": "auto_loan",
        "car loan": "auto_loan",
        "education loan": "education_loan",
        "education_loan": "education_loan",
        "business loan": "business_loan",
        "business_loan": "business_loan",
        "gold loan": "gold_loan",
        "gold_loan": "gold_loan",
        "loan against property": "loan_against_property",
        "loan_against_property": "loan_against_property",
        "property loan": "loan_against_property",
        "lap": "loan_against_property",
    }

    specific_investment_types = {
        "ppf": "ppf",
        "public provident fund": "ppf",
        "nps": "nps",
        "national pension": "nps",
        "national pension system": "nps",
        "ssy": "ssy",
        "sukanya": "ssy",
        "sukanya samriddhi": "ssy",
        "sukanya samriddhi yojana": "ssy",
        "sukanya samridhi": "ssy",
        "sukanya samridhi yojana": "ssy",
        "elss": "elss",
        "tax saving mutual fund": "elss",
        "equity linked savings scheme": "elss",
        "fixed deposit": "fd",
        "fd": "fd",
        "recurring deposit": "rd",
        "rd": "rd",
        "nsc": "nsc",
        "national savings certificate": "nsc",
    }

    detected_loan_type = None
    for loan_name, loan_type in specific_loan_types.items():
        if loan_name in query_lower:
            detected_loan_type = loan_type
            break

    detected_investment_type = None
    sorted_types = sorted(specific_investment_types.items(), key=lambda item: len(item[0]), reverse=True)
    for investment_name, investment_type in sorted_types:
        if investment_name in query_lower:
            detected_investment_type = investment_type
            break

    return QuerySignals(
        is_loan_query=any(keyword in query_lower for keyword in loan_keywords),
        is_general_loan_query=any(phrase in query_lower for phrase in general_loan_queries),
        is_investment_query=any(keyword in query_lower for keyword in investment_keywords),
        is_general_investment_query=any(phrase in query_lower for phrase in general_investment_queries),
        detected_loan_type=detected_loan_type,
        detected_investment_type=detected_investment_type,
    )
