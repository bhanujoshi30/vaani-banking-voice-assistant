# AI Module Documentation

## Overview

The AI module is the conversational intelligence layer of Vaani, built with **LangGraph**, **Ollama (Qwen 2.5)**, and **LangSmith**. It handles natural language understanding, intent classification, banking operations, and provides bilingual (Hindi/English) support through a multi-agent architecture.

**Port**: 8001  
**Tech Stack**: FastAPI, LangGraph, Ollama, LangSmith, ChromaDB

---

## Architecture

```
ai/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── run.sh                       # Startup script
├── start.sh                     # Setup and startup script
│
├── agents/                      # LangGraph agents
│   ├── agent_graph.py          # Main orchestration graph
│   ├── intent_classifier.py    # Intent classification
│   ├── banking_agent.py        # Banking operations agent
│   ├── upi_agent.py            # UPI payment agent
│   ├── rag_agent.py            # RAG supervisor agent
│   ├── greeting_agent.py       # Greeting and chitchat
│   ├── feedback_agent.py       # User feedback handling
│   ├── router.py               # Agent routing logic
│   └── rag_agents/             # Specialized RAG agents
│       ├── customer_support_agent.py  # Customer support queries
│       ├── loan_agent.py              # Loan product information
│       └── investment_agent.py        # Investment scheme information
│
├── orchestrator/                # Hybrid supervisor pattern
│   ├── supervisor.py           # Main supervisor
│   ├── state.py                # Conversation state management
│   └── router.py               # Intent-based routing
│
├── services/                    # External service integrations
│   ├── llm_service.py          # Unified LLM interface
│   ├── ollama_service.py       # Ollama integration
│   ├── openai_service.py       # OpenAI integration
│   ├── azure_tts_service.py    # Azure Text-to-Speech
│   ├── rag_service.py          # RAG service with vector database
│   └── guardrail_service.py    # Guardrails for content safety, PII detection, prompt injection protection
│
├── tools/                       # LangChain tools for agents
│   ├── banking_tools.py        # Banking operations tools
│   └── upi_tools.py            # UPI payment tools
│
├── utils/                       # Utilities
│   ├── logging.py              # Structured logging
│   ├── exceptions.py           # Custom exceptions
│   └── db_helper.py            # Database helpers
│
├── core/                        # Core components
│   ├── memory/                 # Conversation memory
│   ├── supervisor/             # Supervisor patterns
│   └── workers/                # Worker agents
│
├── chroma_db/                   # Vector databases for RAG
│   ├── loan_products/          # English loan documents
│   ├── loan_products_hindi/    # Hindi loan documents
│   ├── investment_schemes/     # English investment documents
│   └── investment_schemes_hindi/ # Hindi investment documents
├── documents/                   # Documents for RAG ingestion
├── ingest_documents.py          # English document ingestion script
├── ingest_documents_hindi.py    # Hindi document ingestion script
├── ingest_investment_documents.py # Investment scheme ingestion
└── logs/                        # Application logs
```

---

## Core Components

### 1. Hybrid Supervisor (`orchestrator/supervisor.py`)

The supervisor orchestrates the entire conversation flow using a hybrid pattern that combines routing and delegation.

**Key Features:**
- Intent-based routing to specialized agents
- Conversation state management
- Multi-turn conversation support
- Error handling and fallback

**Process Flow:**
```
User Message
    ↓
Supervisor receives message
    ↓
Intent Classification
    ↓
Route to appropriate agent
    ↓
Agent processes with tools
    ↓
Response returned to user
```

**Methods:**

#### `process(message, user_id, session_id, language, user_context, message_history, upi_mode)`
- Main entry point for message processing
- Classifies intent
- Routes to appropriate agent
- Manages conversation state
- Returns response

**Supported Intents:**
- `banking_operation`: Balance, transactions, transfers
- `upi_payment`: UPI payments and transfers
- `general_faq`: General banking questions
- `greeting`: Greetings and chitchat
- `feedback`: User feedback
- `authentication`: Login and verification

### 2. Intent Classifier (`agents/intent_classifier.py`)

Determines user intent from natural language input using a fast LLM.

**Model Used**: Llama 3.2 3B (fast, < 200ms)

**Key Features:**
- Multi-language support (English, Hindi, Hinglish)
- Context-aware classification
- UPI mode detection
- Balance keyword detection

**Intent Categories:**

| Intent | Description | Examples |
|--------|-------------|----------|
| `banking_operation` | Account operations | "Check balance", "Show transactions" |
| `upi_payment` | UPI transfers | "Pay ₹500 to John", "Hello Vaani pay..." |
| `general_faq` | General queries | "Interest rates?", "Branch hours?" |
| `greeting` | Greetings | "Hello", "Namaste" |
| `feedback` | User feedback | "This is helpful", "Not working" |
| `authentication` | Login queries | "Forgot password", "How to login" |

**Methods:**

#### `classify_intent(message, language, upi_mode, message_history)`
- Analyzes user message
- Detects intent from predefined categories
- Considers conversation context
- Returns intent string

### 3. Banking Agent (`agents/banking_agent.py`)

Handles banking operations using database tools.

**Model Used**: Qwen 2.5 7B (high quality)

**Capabilities:**
- Account balance queries
- Transaction history
- Fund transfers (with confirmation)
- Account statement download
- Multi-account management
- Reminder management

**Tools Available:**
- `get_user_accounts`: List all user accounts
- `get_account_balance`: Get balance for specific account
- `get_transaction_history`: Retrieve transactions
- `transfer_between_accounts`: Transfer funds
- `download_statement`: Get account statement
- `get_reminders`: List reminders
- `set_reminder`: Create new reminder

**Agent Behavior:**
1. Understands user request
2. Selects appropriate tool(s)
3. Executes tool with parameters
4. Formats response in user's language
5. Handles errors gracefully

### 4. UPI Agent (`agents/upi_agent.py`)

Specialized agent for UPI payments following RBI guidelines.

**Model Used**: Qwen 2.5 7B

**Features:**
- Hello UPI wake-phrase detection
- Payment amount extraction
- Recipient resolution (UPI ID, phone, name)
- Account selection
- PIN verification flow
- Transaction confirmation

**UPI Flow:**
1. Wake phrase: "Hello Vaani" / "Hello UPI"
2. Payment command parsing
3. Recipient resolution
4. PIN entry prompt
5. Payment initiation
6. Confirmation response

**Tools Available:**
- `resolve_upi_id`: Find recipient by UPI ID, phone, or name
- `initiate_upi_payment`: Process UPI payment
- `get_upi_balance`: Check balance for UPI payment

**Compliance:**
- PIN never spoken (manual entry only)
- User consent required
- Transaction verification
- RBI guideline adherence

### 5. RAG Agent System

The RAG (Retrieval-Augmented Generation) agent is a specialized supervisor that orchestrates multiple sub-agents to handle questions about banking products, loans, investments, and customer support using document retrieval.

**Architecture**: Hybrid supervisor pattern with 3 specialized agents:
1. **Loan Agent**: Handles loan product queries
2. **Investment Agent**: Handles investment scheme queries  
3. **Customer Support Agent**: Handles contact and general support queries

**Model Used**: Qwen 2.5 7B (primary), Llama 3.2 3B (extraction)

#### RAG Supervisor (`agents/rag_agent.py`)

The main coordinator that routes queries to specialized agents.

**Routing Logic:**
- Detects query type (loan, investment, customer support)
- Identifies specific products (e.g., "home loan", "PPF")
- Routes to appropriate specialist agent
- Handles general queries with LLM

**Query Detection:**
```python
# Loan keywords
"loan", "interest rate", "emi", "eligibility", "home loan", 
"personal loan", "auto loan", "education loan", etc.

# Investment keywords  
"investment", "scheme", "ppf", "nps", "ssy", "fixed deposit",
"tax saving", "retirement", etc.

# Customer support keywords
"customer support", "contact", "phone number", "email", 
"address", "branch", "helpline", etc.
```

**Hindi Support:**
- Fully bilingual (English and Hindi)
- Detects Hindi keywords: "लोन", "निवेश", "योजना", etc.
- Routes to Hindi vector database when language=`hi-IN`

#### Loan Agent (`agents/rag_agents/loan_agent.py`)

Handles loan product queries using RAG with PDF documents.

**Capabilities:**
- Retrieves context from loan product PDFs
- Generates structured loan information cards
- Handles 7 loan types: Home, Personal, Auto, Education, Business, Gold, Loan Against Property
- Provides general loan exploration interface

**Loan Types Supported:**

| Loan Type | Identifier | Features |
|-----------|------------|----------|
| Home Loan | `home_loan` | Interest: 8.35-9.50%, Up to ₹5 crore, 30 years |
| Personal Loan | `personal_loan` | Interest: 10.49-18%, Up to ₹25 lakh, No collateral |
| Auto Loan | `auto_loan` | Interest: 8.75-12.5%, Up to ₹50 lakh, New/used cars |
| Education Loan | `education_loan` | Interest: 8.5-12%, Up to ₹50 lakh, India/abroad |
| Business Loan | `business_loan` | Interest: 11-18%, Up to ₹50 lakh, MSME/SME |
| Gold Loan | `gold_loan` | Interest: 10-15%, Up to ₹25 lakh, Quick approval |
| Loan Against Property | `loan_against_property` | Interest: 9.5-12.5%, Up to ₹5 crore, 15 years |

**Features:**
- **RAG Retrieval**: Fetches relevant sections from PDF documents
- **Metadata Filtering**: Filters by specific loan type for precision
- **Structured Cards**: Extracts key information into JSON format
- **Fallback Data**: Provides default information if extraction fails
- **General Exploration**: Shows interactive loan selection table
- **Hindi/English Text Cleaning**: Removes mixed scripts in English mode

**Query Flow:**
1. Detect if general loan query ("what loans available?")
2. If general → Return loan selection table
3. If specific loan → Detect loan type
4. Retrieve context from vector database (with metadata filter)
5. Extract structured information using LLM
6. Generate loan information card
7. Fallback to default data if extraction fails

**Structured Data Format:**
```json
{
  "type": "loan",
  "loanInfo": {
    "name": "Home Loan",
    "interest_rate": "8.35% - 9.50% p.a.",
    "min_amount": "Rs. 5 lakhs",
    "max_amount": "Rs. 5 crores",
    "tenure": "Up to 30 years",
    "eligibility": "Age 21-65 years, minimum income Rs. 25,000 per month",
    "description": "Comprehensive home loan scheme to buy your dream home",
    "features": [
      "Competitive interest rates",
      "Long tenure (up to 30 years)",
      "Loan-to-value ratio up to 90%",
      "Floating and fixed rate options"
    ]
  }
}
```

#### Investment Agent (`agents/rag_agents/investment_agent.py`)

Handles investment scheme queries using RAG with PDF documents.

**Capabilities:**
- Retrieves context from investment scheme PDFs
- Generates structured investment information cards
- Handles 7 investment schemes: PPF, NPS, SSY, ELSS, FD, RD, NSC
- Provides general investment exploration interface

**Investment Schemes Supported:**

| Scheme | Identifier | Features |
|--------|------------|----------|
| PPF | `ppf` | Interest: 7.1%, ₹500-₹1.5L/year, 15 years, Tax-free |
| NPS | `nps` | Returns: 8-12%, No limit, Retirement scheme, Extra ₹50K tax deduction |
| Sukanya Samriddhi Yojana | `ssy` | Interest: 8.2%, ₹250-₹1.5L/year, Girl child scheme, 21 years |
| ELSS | `elss` | Market-linked, ₹500+, 3-year lock-in, Tax saving mutual fund |
| Fixed Deposit | `fd` | Interest: 6-8%, ₹1000+, 7 days-10 years, Safe investment |
| Recurring Deposit | `rd` | Interest: 6-7.5%, ₹100/month, Regular savings |
| NSC | `nsc` | Interest: 7-9%, ₹1000+, 5 years, Government backed |

**Features:**
- **RAG Retrieval**: Fetches relevant sections from PDF documents
- **Metadata Filtering**: Filters by specific scheme type for precision
- **Structured Cards**: Extracts key information into JSON format
- **Fallback Data**: Provides default information if extraction fails
- **General Exploration**: Shows interactive investment selection table
- **Hindi/English Text Cleaning**: Removes mixed scripts in English mode
- **Validation**: Ensures extracted data matches detected scheme type

**Query Flow:**
1. Detect if general investment query ("what investments available?")
2. If general → Return investment selection table
3. If specific scheme → Detect scheme type
4. Retrieve context from vector database (with metadata filter)
5. Extract structured information using LLM
6. Validate extracted data matches scheme type
7. Generate investment information card
8. Fallback to default data if extraction/validation fails

**Structured Data Format:**
```json
{
  "type": "investment",
  "investmentInfo": {
    "name": "PPF",
    "interest_rate": "7.1% per annum",
    "min_amount": "Rs. 500",
    "max_amount": "Rs. 1.5 lakhs",
    "tenure": "15 years",
    "eligibility": "Any Indian resident can open PPF account",
    "tax_benefits": "Section 80C: Up to Rs. 1.5 lakhs deduction, tax-free interest and maturity",
    "description": "Long-term tax-saving investment scheme backed by Government of India",
    "features": [
      "Government guaranteed - zero risk",
      "Tax-free interest and maturity",
      "Flexible investment options",
      "Partial withdrawal after 7 years"
    ]
  }
}
```

#### Customer Support Agent (`agents/rag_agents/customer_support_agent.py`)

Handles customer support and contact information queries.

**Capabilities:**
- Detects contact/support queries
- Returns structured customer support card
- Provides bank contact information
- Handles non-banking queries with polite redirects

**Contact Keywords Detected:**
```
"customer support", "customer care", "contact", "phone number", 
"email", "address", "headquarters", "branch address", "website",
"helpline", "support", "call", "location", etc.
```

**Structured Data Format:**
```json
{
  "type": "customer_support",
  "supportInfo": {
    "headquarters_address": "Sun National Bank Tower, 123 Banking Street, Connaught Place, New Delhi - 110001, India",
    "customer_care_number": "+91-1800-123-4567",
    "branch_address": "Visit any of our 500+ branches across India. Find nearest branch at sunnationalbank.online/branches",
    "email": "customercare@sunnationalbank.online",
    "website": "sunnationalbank.online",
    "business_hours": "Monday to Friday: 9:00 AM - 6:00 PM, Saturday: 9:00 AM - 2:00 PM (IST)"
  }
}
```

**Default Behavior:**
For non-contact queries, uses LLM to provide general banking assistance with:
- Polite acknowledgment
- Banking service focus
- Warm, professional tone
- Gentle redirect to banking topics

### 6. Greeting Agent (`agents/greeting_agent.py`)

Handles greetings and chitchat.

**Model Used**: Llama 3.2 3B (fast)

**Responses:**
- Welcome messages
- Casual conversation
- Polite redirects to banking topics
- Multi-language greetings

### 7. Feedback Agent (`agents/feedback_agent.py`)

Collects and processes user feedback.

**Features:**
- Acknowledges feedback
- Categorizes sentiment
- Logs for improvement
- Thanks user

---

## Tools (LangChain Tools)

### Banking Tools (`tools/banking_tools.py`)

Database-backed tools for banking operations.

#### `get_user_accounts(user_id)`
**Purpose**: Get all accounts for a user

**Returns**:
```json
{
  "success": true,
  "accounts": [
    {
      "account_number": "ACC001",
      "account_type": "SAVINGS",
      "balance": 10000.00,
      "currency": "INR"
    }
  ]
}
```

#### `get_account_balance(account_number)`
**Purpose**: Get balance for specific account

**Returns**:
```json
{
  "success": true,
  "account_number": "ACC001",
  "balance": 10000.00,
  "currency": "INR"
}
```

#### `get_transaction_history(account_number, days=30, limit=10)`
**Purpose**: Retrieve recent transactions

**Returns**:
```json
{
  "success": true,
  "transactions": [
    {
      "date": "2025-11-20",
      "type": "DEBIT",
      "amount": 500.00,
      "description": "UPI Payment",
      "balance_after": 9500.00
    }
  ]
}
```

#### `transfer_between_accounts(from_account, to_account, amount, description, channel, user_id, session_id)`
**Purpose**: Transfer funds between accounts

**Validation:**
- Checks account existence
- Verifies sufficient balance
- Atomic transaction

**Returns**:
```json
{
  "success": true,
  "reference_id": "TXN-20251120-143022",
  "amount": 5000.00,
  "from_account": "ACC001",
  "to_account": "ACC002"
}
```

#### `download_statement(account_number, from_date, to_date, period_type)`
**Purpose**: Get account statement for date range

**Returns**:
```json
{
  "success": true,
  "statement_data": {
    "account_number": "ACC001",
    "period": "2025-11-01 to 2025-11-20",
    "opening_balance": 15000.00,
    "closing_balance": 10000.00,
    "transactions": [...]
  }
}
```

#### `get_reminders(user_id)`
**Purpose**: List all reminders for user

#### `set_reminder(user_id, reminder_type, message, remind_at, account_id, channel, recurrence_rule)`
**Purpose**: Create new payment reminder

### UPI Tools (`tools/upi_tools.py`)

Specialized tools for UPI operations.

#### `resolve_upi_id(recipient_identifier, user_id)`
**Purpose**: Resolve UPI ID, phone, or name to account

**Input Types:**
- UPI ID: `9876543210@sunbank`
- Phone: `9876543210`
- Name: `John Doe`
- Beneficiary: `first`, `last`

**Returns**:
```json
{
  "success": true,
  "account_number": "ACC002",
  "upi_id": "9876543210@sunbank",
  "name": "John Doe"
}
```

#### `initiate_upi_payment(source_account, destination_account, amount, remarks, user_id, session_id)`
**Purpose**: Process UPI payment

**Features:**
- Generates UPI reference ID
- Creates debit/credit transactions
- Updates balances
- Marks as UPI channel

**Returns**:
```json
{
  "success": true,
  "reference_id": "UPI-20251120-143022",
  "amount": 500.00,
  "recipient": "John Doe"
}
```

#### `get_upi_balance(account_number)`
**Purpose**: Get balance specifically for UPI payment

---

## Services

### LLM Service (`services/llm_service.py`)

Unified interface for LLM providers.

**Supported Providers:**
- Ollama (local, default)
- OpenAI (cloud, optional)

**Methods:**

#### `chat(messages, use_fast_model=False, temperature=None, max_tokens=None)`
**Purpose**: Send chat completion request

**Parameters:**
- `messages`: List of message dicts `[{"role": "user", "content": "..."}]`
- `use_fast_model`: Use fast model (Llama 3.2 3B) instead of primary
- `temperature`: Sampling temperature (0.0-1.0)
- `max_tokens`: Maximum response tokens

**Returns**: String response

#### `stream_chat(messages, use_fast_model=False)`
**Purpose**: Stream chat completion (token-by-token)

**Returns**: AsyncGenerator yielding tokens

**Model Selection:**
- **Primary Model**: Qwen 2.5 7B (quality)
- **Fast Model**: Llama 3.2 3B (speed)
- **Voice Mode**: Automatically uses fast model

### Ollama Service (`services/ollama_service.py`)

Integration with local Ollama server.

**Features:**
- Local model execution
- No data sent to cloud
- Fast inference on M-series Macs
- Streaming support

**Configuration:**
```python
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_FAST_MODEL = "llama3.2:3b"
```

**Methods:**
- `chat(messages, model, temperature, max_tokens)`: Chat completion
- `stream_chat(messages, model)`: Streaming chat
- `check_health()`: Verify Ollama is running

### OpenAI Service (`services/openai_service.py`)

Integration with OpenAI API (optional).

**Features:**
- GPT-4 and GPT-3.5 support
- Cloud-based inference
- Higher quality for complex queries
- Streaming support

**Configuration:**
```python
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4"
OPENAI_FAST_MODEL = "gpt-3.5-turbo"
```

---

Retrieval-Augmented Generation service for document-based Q&A.

**Features:**
- PDF document ingestion
- Vector database with ChromaDB
- Semantic similarity search
- Metadata filtering
- Context caching (120s TTL, 128 entries)
- Multi-language support (English, Hindi)
- Multiple document types (loans, investments)

**Architecture:**
```
Documents (PDFs)
    ↓
Load & Parse (PyPDFLoader)
    ↓
Chunk Text (RecursiveCharacterTextSplitter)
    ↓
Generate Embeddings (HuggingFace)
    ↓
Store in ChromaDB (Vector Database)
    ↓
Retrieve on Query (Similarity Search)
    ↓
Return Context to LLM
```

**Embedding Model:**
- `sentence-transformers/all-MiniLM-L6-v2`
- 384 dimensions
- CPU-optimized
- Supports 100+ languages
- No external API calls

**Configuration:**
```python
chunk_size = 1000        # Characters per chunk
chunk_overlap = 200      # Overlap between chunks
k = 4                    # Number of retrieved documents
```

**Methods:**

#### `__init__(documents_path, persist_directory, collection_name, chunk_size, chunk_overlap)`
**Purpose**: Initialize RAG service

**Parameters:**
- `documents_path`: Path to PDF documents folder
- `persist_directory`: Where to store vector database
- `collection_name`: ChromaDB collection name
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Chunk overlap (default: 200)

#### `load_pdf_documents()`
**Purpose**: Load all PDFs from documents folder

**Metadata Added:**
- `source`: PDF filename
- `loan_type` or `scheme_type`: Product identifier
- `document_type`: "loan" or "investment"

**Returns**: List of Document objects

#### `chunk_documents(documents)`
**Purpose**: Split documents into smaller chunks

**Uses**: `RecursiveCharacterTextSplitter`

**Separators**: `\n\n`, `\n`, `.`, `!`, `?`, `,`, ` `

**Returns**: List of chunked documents

#### `create_vector_store(documents)`
**Purpose**: Create vector database from documents

**Process:**
1. Generate embeddings for all chunks
2. Store in ChromaDB with metadata
3. Persist to disk
4. Return Chroma instance

**Returns**: Chroma vector store

#### `load_vector_store()`
**Purpose**: Load existing vector database from disk

**Returns**: Chroma instance or None

#### `initialize(force_rebuild=False)`
**Purpose**: Initialize RAG system

**Behavior:**
- If `force_rebuild=False`: Load existing vector store
- If not exists or `force_rebuild=True`: Create new vector store
- Logs initialization mode

#### `retrieve(query, k=4, filter=None)`
**Purpose**: Retrieve relevant documents for a query

**Parameters:**
- `query`: Search query string
- `k`: Number of documents to retrieve
- `filter`: Optional metadata filter (e.g., `{"loan_type": "home_loan"}`)

**Returns**: List of Document objects with content and metadata

**Example:**
```python
# Retrieve with filter
results = rag_service.retrieve(
    query="What is the interest rate?",
    k=2,
    filter={"loan_type": "home_loan"}
)
```

#### `retrieve_with_scores(query, k=4)`
**Purpose**: Retrieve documents with similarity scores

**Returns**: List of (Document, score) tuples

#### `get_context_for_query(query, k=4, filter=None)`
**Purpose**: Get formatted context string for LLM

**Process:**
1. Check cache for query
2. If miss, retrieve documents
3. Format with source metadata
4. Cache result (120s TTL)
5. Return formatted string

**Caching:**
- Cache key: `normalized_query|k=N|filter={...}`
- TTL: 120 seconds
- Max size: 128 entries
- LRU eviction

**Context Format:**
```
[Source 1: Home Loan - home_loan_product_guide.pdf]
Interest Rate: 8.35% - 9.50% per annum
Minimum Loan Amount: Rs. 5 lakhs
...

[Source 2: Home Loan - home_loan_product_guide.pdf]
Eligibility Criteria:
- Age: 21 to 65 years
...
```

**Returns**: Formatted context string

#### `get_rag_service(documents_type="loan", language="en-IN")`
**Purpose**: Get or create RAG service instance (singleton pattern)

**Parameters:**
- `documents_type`: `"loan"` or `"investment"`
- `language`: `"en-IN"` or `"hi-IN"`

**Returns**: Cached RAG service instance

**Database Mapping:**

| Type | Language | Documents Path | Collection Name | Persist Directory |
|------|----------|---------------|----------------|------------------|
| loan | en-IN | backend/documents/loan_products | loan_products | chroma_db/loan_products |
| loan | hi-IN | backend/documents/loan_products_hindi | loan_products_hindi | chroma_db/loan_products_hindi |
| investment | en-IN | backend/documents/investment_schemes | investment_schemes | chroma_db/investment_schemes |
| investment | hi-IN | backend/documents/investment_schemes_hindi | investment_schemes_hindi | chroma_db/investment_schemes_hindi |

**Example Usage:**
```python
# Get English loan service
loan_service = get_rag_service("loan", "en-IN")

# Get Hindi investment service
investment_service = get_rag_service("investment", "hi-IN")

# Retrieve context
context = loan_service.get_context_for_query(
    "What is the interest rate for home loans?",
    k=3,
    filter={"loan_type": "home_loan"}
)
```

**Performance:**
- First call: Loads/creates vector store (~1-5s)
- Subsequent calls: Instant (cached instance)
- Retrieval: 50-200ms depending on query complexity
- Cache hit: <1ms

**Hindi Support:**
- Same embedding model works for Hindi (multilingual)
- Separate vector databases for Hindi documents
- Automatic routing based on language parameter
- Preserves Devanagari script in context

---

## API Endpoints

### Chat Endpoint

**POST /api/chat**

Main endpoint for conversational AI.

**Request:**
```json
{
  "message": "Check my balance",
  "user_id": "uuid-string",
  "session_id": "session-uuid",
  "language": "en-IN",
  "user_context": {
    "account_number": "ACC001",
    "name": "John Doe"
  },
  "message_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "voice_mode": false,
  "upi_mode": false
}
```

**Response:**
```json
{
  "success": true,
  "response": "Your account balance is ₹10,000.00.",
  "intent": "banking_operation",
  "language": "en-IN",
  "timestamp": "2025-11-20T14:30:00",
  "statement_data": null,
  "structured_data": null
}
```

### Streaming Chat

**POST /api/chat/stream**

Server-Sent Events (SSE) for real-time responses.

**Request**: Same as `/api/chat`

**Response**: Stream of text chunks
```
data: Your
data: account
data: balance
data: is
data: ₹10,000.00
data: [DONE]
```

### Voice Verification

**POST /api/voice-verification**

AI-enhanced voice verification for authentication.

**Request:**
```json
{
  "similarity_score": 0.82,
  "threshold": 0.75,
  "user_context": {
    "user_id": "uuid",
    "device_trust_level": "TRUSTED"
  }
}
```

**Response:**
```json
{
  "confidence": 0.85,
  "risk_level": "LOW",
  "recommendation": "ACCEPT",
  "reasoning": "High similarity with low risk indicators"
}
```

### Health Check

**GET /health**

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "ollama_status": true,
  "azure_tts_available": false
}
```

---

## Configuration

### Environment Variables

**Core Settings:**
```env
# API Configuration
API_PORT=8001
API_HOST=0.0.0.0

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_FAST_MODEL=llama3.2:3b

# Database
DATABASE_URL=sqlite:///../backend/vaani.db

# LLM Provider (ollama or openai)
LLM_PROVIDER=ollama
```

**LangSmith Tracing (Recommended):**
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_key
LANGCHAIN_PROJECT=vaani-banking-assistant
```

**OpenAI (Optional):**
```env
OPENAI_API_KEY=sk-your_key
OPENAI_MODEL=gpt-4
OPENAI_FAST_MODEL=gpt-3.5-turbo
```

---

## Conversation State

The system maintains conversation state across turns.

**State Fields:**
- `message`: Current user message
- `language`: User's language preference
- `user_id`: User UUID
- `session_id`: Conversation session ID
- `user_context`: User profile and account info
- `message_history`: Previous messages
- `intent`: Classified intent
- `upi_mode`: Whether UPI mode is active
- `response`: Generated response
- `structured_data`: Data for UI components
- `statement_data`: Account statement data

---

## Logging and Monitoring

### Structured Logging

All logs use `structlog` for consistent, queryable logging.

**Log Levels:**
- DEBUG: Detailed debugging information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages

**Log Fields:**
- `event`: Event name
- `timestamp`: ISO timestamp
- `session_id`: Session identifier
- `user_id`: User identifier
- `duration`: Operation duration (seconds)
- Custom fields per event

**Example Logs:**
```json
{
  "event": "llm_call",
  "model": "qwen2.5:7b",
  "duration": 1.234,
  "tokens": 150
}

{
  "event": "tool_execution",
  "tool": "get_account_balance",
  "success": true,
  "duration": 0.042
}
```

### LangSmith Tracing

Comprehensive tracing of all LLM interactions.

**What's Traced:**
- LLM calls with input/output
- Agent decisions
- Tool executions
- Errors and exceptions
- Performance metrics

**Benefits:**
- Debug conversation flows
- Monitor performance
- Analyze user interactions
- Identify issues
- Optimize prompts

**Access**: [smith.langchain.com](https://smith.langchain.com)

---

## Performance

### Benchmarks (Apple M4 Max, 128GB RAM)

| Operation | Model | Latency | Quality |
|-----------|-------|---------|---------|
| Intent Classification | Llama 3.2 3B | 100-200ms | 90%+ |
| Balance Query | Qwen 2.5 7B | 500-800ms | 95%+ |
| General FAQ | Qwen 2.5 7B | 1-2s | 95%+ |
| Streaming First Token | Qwen 2.5 7B | 200-400ms | - |
| Voice Mode | Llama 3.2 3B | 300-800ms | 85%+ |
| UPI Payment | Qwen 2.5 7B | 1-1.5s | 95%+ |

### Optimization Tips

1. **Use Fast Model for Voice**: Set `voice_mode: true`
2. **Limit Message History**: Keep last 10 messages max
3. **Cache Embeddings**: For RAG operations (future)
4. **Parallel Tool Calls**: Execute multiple tools concurrently (future)
5. **Warm Start**: First request is slower, subsequent ones are fast

---

## Error Handling

### Error Types

1. **LLM Errors**: Model not responding, timeout
2. **Tool Errors**: Database error, insufficient funds
3. **Validation Errors**: Invalid input parameters
4. **Network Errors**: Ollama not reachable

### Error Response Format

```json
{
  "success": false,
  "response": "I'm sorry, I encountered an error.",
  "error": "Error description",
  "language": "en-IN",
  "timestamp": "2025-11-20T14:30:00"
}
```

### Retry Logic

- Automatic retry (3 attempts)
- Exponential backoff
- Graceful degradation
- Fallback to mock responses (if configured)

---

## Multi-Language Support

### Supported Languages

- **English (en-IN)**: Primary language
- **Hindi (hi-IN)**: Full support
- **Hinglish**: Code-switching support

### Language Detection

- User's `language` parameter
- Auto-detection from message content
- Preference stored in user context

### Response Generation

- System prompts in target language
- LLM generates responses in target language
- Tool outputs formatted per language
- Number formatting (₹ symbol)

**Example Prompts:**

**English:**
```
You are Vaani, a helpful banking assistant for Sun National Bank.
Answer questions about accounts, transactions, and banking services.
```

**Hindi:**
```
आप वाणी हैं, सन नेशनल बैंक की एक सहायक सहायक।
खातों, लेन-देन और बैंकिंग सेवाओं के बारे में सवालों का जवाब दें।
```

---

## Security Features

### Data Privacy

- All LLM processing is local (Ollama)
- No user data sent to external services (except optional LangSmith)
- Database queries use parameterized statements
- No raw credentials in logs

### Input Validation

- Pydantic models for all inputs
- Type checking
- Field validation
- SQL injection prevention (ORM)

### Authentication

- User ID verification
- Session validation
- Access token checks
- Tool authorization

---

## Testing

### Manual Testing

```bash
# Test chat endpoint
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check my balance",
    "user_id": "test-user",
    "session_id": "test-session",
    "language": "en-IN",
    "user_context": {"account_number": "ACC001"}
  }'
```

### Unit Tests

Located in `ai/test_*.py` files:
- `test_balance_logic.py`: Balance query tests
- `test_balance_queries.py`: Balance query variations
- `test_llm_providers.py`: LLM provider tests
- `test_rag_faq.py`: RAG FAQ tests
- `test_upi_mode_routing.py`: UPI routing tests

**Run tests:**
```bash
cd ai
pytest
```

---

## Future Enhancements

### RAG System
- Document Q&A for loan products
- Policy and procedure lookup
- FAQ database
- Vector similarity search

### Advanced Features
- Multi-turn context tracking
- User preference learning
- Proactive suggestions
- Sentiment analysis

### Performance
- Response caching (Redis)
- Parallel tool execution
- Model quantization
- Batch processing

### Capabilities
- Voice biometric integration
- Image understanding (QR codes, documents)
- Multi-modal interactions
- Regional language support (Tamil, Telugu, etc.)

---

## Troubleshooting

### Issue: Ollama connection error

**Solution:**
```bash
# Check Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Verify models
ollama list
```

### Issue: LangSmith not tracing

**Solution:**
- Verify `LANGCHAIN_TRACING_V2=true` (exact string)
- Check API key is correct
- Restart AI backend after changing `.env`

### Issue: Agent not using tools

**Solution:**
- Check tool definitions in logs
- Verify database connection
- Review LLM prompt templates
- Check LangSmith trace for tool calls

### Issue: Poor response quality

**Solution:**
- Use primary model (not fast model) for complex queries
- Increase context in prompts
- Improve tool descriptions
- Fine-tune temperature parameter

---

## Related Documentation

- [Setup Guide](./setup_guide.md) - Installation and configuration
- [Backend Documentation](./backend_modules.md) - Backend API details
- [Frontend Documentation](./frontend_modules.md) - Frontend components
- [UPI Payment Flow](./upi_payment_flow.md) - UPI implementation
- [API Reference](./api_reference.md) - Complete API docs
