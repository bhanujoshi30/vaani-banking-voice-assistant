# Demo Logging Guide

## Overview

Enhanced logging system designed specifically for demo video recordings. The logging provides clear visual indicators and structured output that makes it easy to understand the flow of operations during a demo session.

## Features

### Visual Separators
- Clear box-drawing characters (╔═ ═╗, ║, ╚═╝) for easy visual separation
- Color-coded sections using ANSI color codes
- Timestamps for each operation

### Logged Operations

#### 1. API Requests & Responses
- **Location**: `backend/app.py` middleware
- **What's logged**:
  - HTTP method and path
  - Query parameters
  - Client IP
  - Response status code
  - Response duration in milliseconds
  - Content type

#### 2. Chat Requests
- **Location**: `ai/main.py` chat endpoint
- **What's logged**:
  - User message (preview)
  - User ID and session ID
  - Language and voice mode
  - UPI mode status

#### 3. State Transitions
- **Location**: `ai/main.py` chat endpoint
- **What's logged**:
  - State changes (USER SPEAKING → PROCESSING → AI SPEAKING)
  - Reason for transition

#### 4. Agent Routing Decisions
- **Location**: `ai/orchestrator/supervisor.py`
- **What's logged**:
  - Selected agent name
  - Detected intent
  - Confidence score (if available)
  - Language and UPI mode

#### 5. RAG Retrieval
- **Location**: `ai/services/rag_service.py`
- **What's logged**:
  - Query text
  - Collection name
  - Top-K value
  - Metadata filters
  - Retrieved documents with:
    - Document type (loan/investment)
    - Source file
    - Similarity scores
    - Content previews

#### 6. LLM API Calls
- **Location**: `ai/services/llm_service.py`
- **What's logged**:
  - Model name
  - Prompt length (characters)
  - Response length (characters)
  - Tokens used (if available)
  - Duration in milliseconds

#### 7. Tool Execution
- **Location**: `ai/tools/banking_tools.py`
- **What's logged**:
  - Tool name
  - Success/failure status
  - Duration in milliseconds
  - Result summary or error message

#### 8. AI Responses
- **Location**: `ai/main.py` chat endpoint
- **What's logged**:
  - Response text (preview)
  - Agent that generated it
  - Language

## Color Coding

- **Blue** (╔═ ═╗): API requests, chat requests, user messages
- **Green** (╔═ ═╗): API responses, AI responses, successful operations
- **Yellow** (╔═ ═╗): Agent routing decisions
- **Cyan** (╔═ ═╗): RAG operations
- **Magenta** (╔═ ═╗): State transitions, data processing
- **Red** (╔═ ═╗): Errors, failed operations

## Example Log Output

```
════════════════════════════════════════════════════════════════════════════
╔═ 💬 CHAT REQUEST RECEIVED ═══════════════════════════════════════════════╗
║  Timestamp: 14:30:45.123                                                 ║
║  User Message: What is the interest rate for home loans?                ║
║  User ID: 123e4567-e89b-12d3-a456-426614174000 │ Session: abc123...     ║
║  Language: en-IN                                                         ║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🔄 STATE TRANSITION ════════════════════════════════════════════════════╗
║  USER SPEAKING        → PROCESSING                                       ║
║  Reason: Message received, routing to agent                             ║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🎯 AGENT ROUTING DECISION ══════════════════════════════════════════════╗
║  Selected Agent: rag_agent                                              ║
║  Detected Intent: general_faq                                           ║
║  Confidence: 85.00%                                                     ║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🔍 RAG RETRIEVAL ═══════════════════════════════════════════════════════╗
║  Query: What is the interest rate for home loans?                       ║
║  Collection: loan_products │ Top-K:   4                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 📚 RAG RETRIEVAL RESULTS ══════════════════════════════════════════════╗
║  Documents Found: 4                                                      ║
║  [1] Home Loan          │ home_loan_product_guide.pdf (Score: 0.892)   ║
║      └─ Home loans are available at competitive interest rates starting...║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🤖 LLM API CALL ═══════════════════════════════════════════════════════╗
║  Model: llama3.2:3b                                                      ║
║  Prompt Length:   1234 chars │ Response Length:    567 chars            ║
║  Duration: 1234.56ms                                                     ║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🤖 AI RESPONSE ════════════════════════════════════════════════════════╗
║  Agent: rag_agent │ Language: en-IN                                      ║
║  Response: Home loans are available at interest rates ranging from 8.35%...║
╚══════════════════════════════════════════════════════════════════════════╝

╔═ 🔄 STATE TRANSITION ════════════════════════════════════════════════════╗
║  PROCESSING        → AI SPEAKING                                         ║
║  Reason: Response generated, sending to user                             ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## Usage

The logging is automatically enabled when the backend services are running. No additional configuration is needed.

### For Demo Recording

1. **Terminal Setup**: 
   - Position terminal window adjacent to browser
   - Ensure terminal has sufficient width (80+ characters) for proper display
   - Use a terminal that supports ANSI color codes (most modern terminals do)

2. **Recording Tips**:
   - The visual separators make it easy to follow the flow
   - Color coding helps distinguish different types of operations
   - Timestamps show the timing of each operation
   - Each major operation is clearly marked with emoji icons

## Technical Details

### Files Modified

1. **Backend**:
   - `backend/utils/demo_logging.py` - Demo logger implementation
   - `backend/app.py` - Middleware for API request/response logging

2. **AI Backend**:
   - `ai/utils/demo_logging.py` - Demo logger implementation
   - `ai/main.py` - Chat endpoint logging
   - `ai/orchestrator/supervisor.py` - Agent routing logging
   - `ai/services/rag_service.py` - RAG retrieval logging
   - `ai/services/llm_service.py` - LLM call logging
   - `ai/tools/banking_tools.py` - Tool execution logging

### Performance Impact

- Minimal overhead: Logging adds <1ms per operation
- Non-blocking: All logging is synchronous but fast
- No external dependencies: Uses only Python standard library and existing logging infrastructure

## Best Practices for Demo

1. **Clear Terminal**: Clear terminal before starting demo for cleaner output
2. **Focus Areas**: Key areas to highlight:
   - RAG retrieval showing document selection
   - Agent routing decisions
   - Tool execution results
   - State transitions
3. **Timing**: The timestamps help show response times and processing duration
4. **Error Handling**: Errors are clearly marked in red for visibility

## Future Enhancements

Potential improvements for future versions:
- Log aggregation and filtering
- Export logs to structured format (JSON)
- Real-time log streaming to dashboard
- Performance metrics aggregation
- User session tracking across multiple requests


