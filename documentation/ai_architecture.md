# AI Module Architecture

This document describes how the `ai/` microservice turns a chat request into a structured response using a hybrid supervisor and specialist agents.

Diagram: `documentation/ai_architecture.mmd`

---

## Purpose
- Orchestrate banking conversations
- Use RAG for loans/investments/support
- Emit `structured_data` and `statement_data` for the UI

## Orchestrator
- Entry: `agent_graph.process_message`
- HybridSupervisor builds a `ConversationState` (messages, user/session IDs, language, UPI mode, user context), classifies intent via `IntentRouter`, dispatches one agent, then shapes the final response back to the backend.
- ConversationState keeps a safe, predictable structure between agents and supervisor.

## Agents
- **Banking Agent**: balances, transactions, reminders, transfers (uses domain tools + LLM)
- **UPI Agent**: UPI payment flows (emits multi‑step `structured_data`)
- **RAG Supervisor**: routes loan/investment/support queries to specialized agents
- **Greeting Agent**: deterministic greetings
- **Feedback Agent**: collects ratings/complaints

## RAG Specialists
The RAG system uses a supervisor pattern with three specialized agents:

### Loan Agent (`ai/agents/rag_agents/loan_agent.py`)
- Handles 7 loan types: Home, Personal, Car, Education, Business, Gold, Agriculture
- Retrieves from `loan_products` (English) and `loan_products_hindi` (Hindi) vector databases
- Returns structured loan cards with interest rates, eligibility, features
- Keywords: loan, ऋण, कर्ज, होम लोन, personal loan, etc.

### Investment Agent (`ai/agents/rag_agents/investment_agent.py`)
- Handles 7 investment schemes: PPF, NPS, SSY, ELSS, FD, RD, NSC
- Retrieves from `investment_schemes` (English) and `investment_schemes_hindi` (Hindi) vector databases
- Returns structured investment cards with returns, tenure, tax benefits
- Keywords: investment, निवेश, scheme, योजना, PPF, NPS, etc.

### Customer Support Agent (`ai/agents/rag_agents/customer_support_agent.py`)
- Provides contact information (email, phone, hours)
- Handles general support queries
- Keywords: help, support, contact, सहायता, संपर्क, etc.

All specialists retrieve context via `RAGService` (ChromaDB + HuggingFace embeddings) and generate responses with `LLMService`.

## Shared Services
- **LLMService**: wraps Ollama/OpenAI providers (models set in `ai/.env`)
  - Primary model: `qwen2.5:7b` (comprehensive responses)
  - Fast model: `llama3.2:3b` (quick classification)
- **RAGService**: ingestion, retrieval, and context assembly with lightweight caching
  - 4 vector databases: `loan_products`, `loan_products_hindi`, `investment_schemes`, `investment_schemes_hindi`
  - HuggingFace embeddings: `sentence-transformers/all-MiniLM-L6-v2`
  - ChromaDB for vector storage
  - Semantic chunking (section-aware, preserves tables/FAQs, multilingual support)
  - 120-second context cache (TTL)
  - Metadata filtering by language and document type
- **GuardrailService**: input/output safety checks and content moderation
  - Input guardrails: content moderation, PII detection, prompt injection protection, rate limiting
  - Output guardrails: language consistency, response safety, PII leakage prevention
  - Integrated at supervisor level (before intent routing and after response generation)
  - Open-source only, no external API dependencies
- **Tools**: safe interfaces for backend banking/UPI operations

## Request → Response
1. Backend posts `/api/chat` with message and session info
2. Supervisor validates input via GuardrailService (content moderation, PII detection, prompt injection)
3. If valid, supervisor builds state and selects an agent
4. Agent may call tools, LLM, and/or RAG
5. Supervisor sanitizes output via GuardrailService (language consistency, safety checks, PII redaction)
6. Supervisor returns `{ response, structured_data?, statement_data? }`

## Localization
- **Current implementation**: Bilingual RAG with separate vector databases
  - English databases: `loan_products`, `investment_schemes`
  - Hindi databases: `loan_products_hindi`, `investment_schemes_hindi`
  - Language detection from user query
  - Same HuggingFace embeddings for both languages
- **Short‑term optimization**: translate non‑English → English for retrieval, translate answer back
- **Medium‑term upgrade**: switch to multilingual embeddings (e.g., `paraphrase-multilingual-MiniLM-L12-v2`) and re‑index
- **Long‑term vision**: add multi‑language corpora with language filters and regional language support

## Extensibility
- New intent/agent: update classifier prompt + router, implement agent, register route key
- New RAG domain: add specialist and documents with metadata
- Provider swap: set `LLM_PROVIDER` and models in `ai/.env`

## Testing & Observability
- Tests cover intent routing, RAG retrieval, UPI flows, balance logic
- Logs: `intent_router_decision`, `rag_cache_hit`, `invoking_specialist`
- Optional LangSmith tracing via `.env` toggles
