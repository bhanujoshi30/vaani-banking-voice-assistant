"""
Test script for RAG-enhanced FAQ agent
"""
import asyncio
from langchain_core.messages import HumanMessage
from agents.faq_agent import faq_agent
from services.rag_service import initialize_rag


async def test_faq_with_rag():
    """Test the FAQ agent with RAG for loan queries"""
    
    print("🔧 Initializing RAG service...")
    initialize_rag()
    print("✅ RAG service initialized\n")
    
    # Test cases
    test_queries = [
        "What is the interest rate for home loans?",
        "What documents do I need for a personal loan?",
        "What is the eligibility for education loans?",
        "Do you offer gold loans?",
        "Compare interest rates for home loan and auto loan",
        "What's the weather like?",  # Non-loan query to test fallback
    ]
    
    print("=" * 80)
    print("TESTING RAG-ENHANCED FAQ AGENT")
    print("=" * 80 + "\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {query}")
        print('─' * 80)
        
        # Create state
        state = {
            "messages": [HumanMessage(content=query)],
            "language": "en-IN",
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        # Call FAQ agent
        result = await faq_agent(state)
        
        # Get AI response
        ai_response = result["messages"][-1].content
        
        print(f"\n💬 RESPONSE:\n{ai_response}\n")
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_faq_with_rag())
