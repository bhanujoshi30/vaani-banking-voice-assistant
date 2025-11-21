# Code Modularization - Vaani Banking Voice Assistant

## Frontend Modularization

### Hooks (`/frontend/src/hooks/`)

#### `useChatMessages.js`
- **Purpose**: Manages chat messages state and auto-scrolling
- **Exports**: 
  - `messages`, `setMessages` - Message state
  - `messagesEndRef` - Ref for scroll target
  - `addUserMessage()`, `addAssistantMessage()` - Helper functions
  - `scrollToBottom()` - Auto-scroll function

#### `useVoiceMode.js`
- **Purpose**: Orchestrates voice mode behavior
- **Features**:
  - Auto-start listening when voice mode enabled
  - Stop listening while AI is speaking (prevent feedback)
  - Auto-read assistant messages aloud
  - Auto-send messages after speech completes
  - Cleanup on voice mode disable

#### `useChatHandler.js`
- **Purpose**: Handles message sending and AI responses
- **Exports**:
  - `isTyping` - Loading state
  - `sendMessage()` - Send message and get AI response
  - `handleQuickAction()` - Handle sidebar quick action clicks
  - `handleSendMessage()` - Form submit handler

### Services (`/frontend/src/services/`)

#### `chatService.js`
- **Purpose**: AI chat service layer
- **Functions**:
  - `sendChatMessage()` - Send to AI backend with error handling
  - `buildUserContext()` - Extract context from session
  - `buildSessionId()` - Generate session ID
  - `formatMessageHistory()` - Format for AI backend

### Updated Components

#### `Chat.jsx` - Main Page
- **Refactored from**: 447 lines → ~200 lines
- **Now uses**: All modular hooks and services
- **Benefits**: Much cleaner, easier to maintain

## AI Backend Modularization

### Agents (`/ai/agents/`)

#### `intent_classifier.py`
- **Purpose**: Classify user intent for routing
- **Function**: `classify_intent(state)` 
- **Intents**: banking_operation, general_faq, greeting, feedback, other

#### `banking_agent.py`
- **Purpose**: Handle banking operations
- **Functions**:
  - `banking_agent(state)` - Main agent
  - `handle_balance_query()` - Balance checks
  - `handle_transaction_query()` - Transaction history
- **Features**: Multi-account support, Hindi/English responses

#### `rag_agent.py`
- **Purpose**: Supervisor for knowledge/RAG-style conversations
- **Function**: `rag_agent(state)` delegates to domain specialists
- **Specialists**: Loan agent, investment schemes agent, and customer support agent

#### `router.py`
- **Purpose**: Route to appropriate agent based on intent
- **Function**: `route_to_agent(state)`
- **Routes**: banking_agent, rag_agent, end

#### `agent_graph.py`
- **Purpose**: LangGraph workflow orchestration
- **Imports**: All modular agents
- **Exports**: `process_message()`, `agent_graph`
- **Refactored from**: 446 lines → 166 lines

## Benefits of Modularization

### Frontend
1. **Separation of Concerns**: Each hook handles one responsibility
2. **Reusability**: Hooks can be used in other components
3. **Testability**: Easier to unit test individual hooks
4. **Maintainability**: Bugs isolated to specific modules
5. **Readability**: Chat.jsx is now much cleaner

### AI Backend
1. **Single Responsibility**: Each agent file has one purpose
2. **Easy to Extend**: Add new agents without touching others
3. **Better Testing**: Test each agent independently
4. **Clear Structure**: Intent → Router → Specialized Agent
5. **Debugging**: Easier to track issues to specific agent

## File Structure

```
frontend/src/
├── hooks/
│   ├── useChatMessages.js       # NEW: Message management
│   ├── useVoiceMode.js           # NEW: Voice mode orchestration
│   ├── useChatHandler.js         # NEW: Message sending
│   ├── useSpeechRecognition.js   # Existing
│   └── useTextToSpeech.js        # Existing
├── services/
│   ├── chatService.js            # NEW: AI service layer
│   └── ... 
├── pages/
│   └── Chat.jsx                  # REFACTORED: Now uses hooks
└── ...

ai/
├── agents/
│   ├── intent_classifier.py      # NEW: Intent classification
│   ├── banking_agent.py          # NEW: Banking operations
│   ├── rag_agent.py             # NEW: Hybrid RAG supervisor
│   ├── rag_agents/              # NEW: Loan/Investment/Support specialists
│   ├── router.py                 # NEW: Agent routing
│   ├── agent_graph.py            # REFACTORED: Orchestration only
│   └── agent_graph_old.py        # Backup of original
├── services/
│   ├── ollama_service.py         # Existing
│   └── azure_tts_service.py      # Existing
├── tools/
│   └── banking_tools.py          # Existing
└── ...
```

## Testing the Modular Code

### Frontend
```bash
cd frontend
npm run dev
```

### AI Backend
```bash
cd ai
./run.sh
```

All functionality remains the same, just better organized!

## Migration Notes

- Old `agent_graph.py` backed up as `agent_graph_old.py`
- All imports updated to use new modular structure
- No breaking changes - API remains the same
- Can safely delete `agent_graph_old.py` after verification

## Next Steps

1. ✅ Frontend hooks created
2. ✅ AI agents modularized  
3. ✅ All code refactored
4. 🔄 Testing in progress
5. 📝 Add unit tests for each module
6. 📝 Add type hints/PropTypes validation
7. 📝 Add error boundaries for React components
