"""
LangGraph Agent System
Multi-agent orchestration for banking conversations
"""
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from config import settings
from .intent_classifier import classify_intent
from .banking_agent import banking_agent
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


# Create the agent graph
def create_agent_graph():
    
    logger.info(
        "routing_decision",
        intent=intent,
        route=route
    )
    
    return route


# Banking Agent
async def banking_agent(state: AgentState) -> AgentState:
    """
    Agent for banking operations using tools
    Handles: balance checks, transactions, transfers, reminders
    """
    ollama = await get_ollama_service()
    language = state.get("language", "en-IN")
    user_context = state.get("user_context", {})
    
    # Get system prompt based on language
    if language == "hi-IN":
        system_prompt = """आप वाणी हैं, Sun National Bank की बैंकिंग सहायक।
आप उपयोगकर्ता की बैंकिंग गतिविधियों में मदद करती हैं।

उपलब्ध उपकरण (Tools):
- get_account_balance: खाते का बैलेंस चेक करें
- get_transaction_history: हाल के लेनदेन देखें
- transfer_funds: पैसे ट्रांसफर करें (पुष्टि के बाद)
- get_reminders: रिमाइंडर देखें
- set_reminder: नया रिमाइंडर सेट करें

हमेशा विनम्र और सहायक रहें। संवेदनशील जानकारी को सुरक्षित रखें।"""
    else:
        system_prompt = """You are Vaani, the banking assistant for Sun National Bank.
You help users with their banking activities.

Available tools:
- get_account_balance: Check account balance
- get_transaction_history: View recent transactions
- transfer_funds: Transfer money (confirm before executing)
- get_reminders: View payment reminders
- set_reminder: Set new reminder

Always be polite and helpful. Keep sensitive information secure.
For transfers, ALWAYS confirm amount and recipient before executing."""
    
    # Add user context to prompt
    if user_context.get("account_number"):
        system_prompt += f"\n\nUser's account: {user_context['account_number']}"
    if user_context.get("name"):
        system_prompt += f"\nUser's name: {user_context['name']}"
    
    # Build message history
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    
    try:
        # For this agent, we'll use a simple tool-calling approach
        # In production, you'd use LangChain's AgentExecutor with ReAct
        
        last_user_message = state["messages"][-1].content
        
        # Determine which tool to call based on intent
        response_content = ""
        
        # Simple keyword-based tool selection (in production, use better intent detection)
        if any(word in last_user_message.lower() for word in ["balance", "बैलेंस"]):
            # Detect account type from message
            account_type_requested = None
            if any(word in last_user_message.lower() for word in ["savings", "बचत", "saving"]):
                account_type_requested = "savings"
            elif any(word in last_user_message.lower() for word in ["current", "चालू", "checking"]):
                account_type_requested = "current"
            
            # Get user's accounts to find the right one
            user_id = state.get("user_id")
            if not user_id:
                response_content = "कृपया लॉगिन करें।" if language == "hi-IN" else "Please login first."
                state["messages"].append(AIMessage(content=response_content))
                state["next_action"] = "end"
                return state
            
            from tools import get_user_accounts
            accounts_result = get_user_accounts.invoke({"user_id": user_id})
            
            if accounts_result["success"] and accounts_result["accounts"]:
                if account_type_requested:
                    # Find matching account type
                    target_account = None
                    for acc in accounts_result["accounts"]:
                        if account_type_requested.lower() in acc["account_type"].lower():
                            target_account = acc
                            break
                    
                    if target_account:
                        # Return balance for specific account type
                        if language == "hi-IN":
                            account_type_text = target_account["account_type"].replace("AccountType.", "")
                            response_content = f"आपके {account_type_text} खाते का बैलेंस ₹{target_account['balance']:,.2f} है।"
                        else:
                            account_type_text = target_account["account_type"].replace("AccountType.", "")
                            response_content = f"Your {account_type_text} account balance is ₹{target_account['balance']:,.2f}."
                    else:
                        # Account type requested but not found
                        if language == "hi-IN":
                            response_content = f"आपके पास {account_type_requested} खाता नहीं है।"
                        else:
                            response_content = f"You don't have a {account_type_requested} account."
                else:
                    # No specific type requested - show all accounts
                    if language == "hi-IN":
                        response_content = "आपके खातों का बैलेंस:\n\n"
                        for acc in accounts_result["accounts"]:
                            acc_type = acc["account_type"].replace("AccountType.", "")
                            response_content += f"• {acc_type}: ₹{acc['balance']:,.2f}\n"
                    else:
                        response_content = "Your account balances:\n\n"
                        for acc in accounts_result["accounts"]:
                            acc_type = acc["account_type"].replace("AccountType.", "")
                            response_content += f"• {acc_type}: ₹{acc['balance']:,.2f}\n"
            else:
                response_content = "कोई खाता नहीं मिला।" if language == "hi-IN" else "No accounts found."
        
        elif any(word in last_user_message.lower() for word in ["transaction", "लेनदेन", "transactions"]):
            # Call transaction history tool
            if user_context.get("account_number"):
                from tools import get_transaction_history
                result = get_transaction_history.invoke({
                    "account_number": user_context["account_number"],
                    "days": 30,
                    "limit": 5
                })
                
                if result["success"] and result["transactions"]:
                    if language == "hi-IN":
                        response_content = f"आपके पिछले {len(result['transactions'])} लेनदेन:\n\n"
                    else:
                        response_content = f"Your last {len(result['transactions'])} transactions:\n\n"
                    
                    for txn in result["transactions"]:
                        response_content += f"• {txn['date']}: {txn['type']} ₹{txn['amount']:,.2f} - {txn['description']}\n"
                else:
                    response_content = "कोई लेनदेन नहीं मिला।" if language == "hi-IN" else "No transactions found."
            else:
                response_content = "कृपया अपना खाता नंबर बताएं।" if language == "hi-IN" else "Please provide your account number."
        
        else:
            # General response using LLM
            response_content = await ollama.chat(messages, use_fast_model=False)
        
        # Add AI response to state
        ai_message = AIMessage(content=response_content)
        state["messages"].append(ai_message)
        
        logger.info(
            "banking_agent_response",
            response_length=len(response_content)
        )
        
    except Exception as e:
        logger.error("banking_agent_error", error=str(e))
        error_msg = "मुझे खेद है, एक त्रुटि हुई।" if language == "hi-IN" else "I'm sorry, an error occurred."
        state["messages"].append(AIMessage(content=error_msg))
    
    return state


# RAG Agent (legacy graph node)
async def rag_agent_node(state: AgentState) -> AgentState:
    """
    Agent for general inquiries and FAQs
    Handles: Product info, interest rates, branch info, general questions
    """
    ollama = await get_ollama_service()
    language = state.get("language", "en-IN")
    
    # Get system prompt based on language
    if language == "hi-IN":
        system_prompt = """आप वाणी हैं, Sun National Bank की सहायक।
आप बैंक के उत्पादों, सेवाओं और नीतियों के बारे में जानकारी देती हैं।

जानकारी:
- बचत खाता ब्याज दर: 4% प्रति वर्ष
- फिक्स्ड डिपॉजिट: 6.5% - 7.5% (1-5 साल)
- होम लोन: 8.5% प्रति वर्ष से शुरू
- ग्राहक सेवा: 1800-XXX-XXXX

संक्षिप्त, स्पष्ट और मददगार उत्तर दें। अगर जानकारी नहीं है तो कहें।"""
    else:
        system_prompt = """You are Vaani, the assistant for Sun National Bank.
You provide information about bank products, services, and policies.

Information:
- Savings Account Interest: 4% per annum
- Fixed Deposits: 6.5% - 7.5% (1-5 years)
- Home Loans: Starting at 8.5% per annum
- Customer Care: 1800-XXX-XXXX

Provide concise, clear, and helpful answers. If you don't have information, say so."""
    
    # Build message history
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    
    try:
        # Use quality model for FAQs
        response_content = await ollama.chat(messages, use_fast_model=False)
        
        # Add AI response to state
        ai_message = AIMessage(content=response_content)
        state["messages"].append(ai_message)
        
        logger.info(
            "rag_agent_response",
            response_length=len(response_content)
        )
        
    except Exception as e:
        logger.error("rag_agent_error", error=str(e))
        error_msg = "मुझे खेद है, एक त्रुटि हुई।" if language == "hi-IN" else "I'm sorry, an error occurred."
        state["messages"].append(AIMessage(content=error_msg))
    
    return state


# Build the graph
def create_agent_graph():
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("banking_agent", banking_agent)
    workflow.add_node("rag_agent", rag_agent_node)
    
    # Add edges
    workflow.set_entry_point("classify_intent")
    
    # Conditional routing after intent classification
    workflow.add_conditional_edges(
        "classify_intent",
        route_to_agent,
        {
            "banking_agent": "banking_agent",
            "rag_agent": "rag_agent",
            "end": END,
        }
    )
    
    # Both agents end the conversation
    workflow.add_edge("banking_agent", END)
    workflow.add_edge("rag_agent", END)
    
    return workflow.compile()


# Create the compiled graph
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
            authenticated=True,  # Assuming authenticated from session
            next_action=""
        )
        
        # Run the graph
        final_state = await agent_graph.ainvoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        response_content = last_message.content if isinstance(last_message, AIMessage) else message
        
        return {
            "success": True,
            "response": response_content,
            "intent": final_state.get("current_intent", "unknown"),
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("agent_graph_error", error=str(e))
        raise AgentExecutionError(f"Agent execution failed: {e}")
