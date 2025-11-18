# Architecture Diagram: LLM Provider Switching

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VAANI AI BACKEND                                  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                          AGENTS                                   │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   Intent     │  │   Banking    │  │     FAQ      │           │  │
│  │  │ Classifier   │  │    Agent     │  │    Agent     │           │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │  │
│  │         │                 │                 │                    │  │
│  │         └─────────────────┴─────────────────┘                    │  │
│  │                           │                                       │  │
│  │                  get_llm_service()                               │  │
│  │                           │                                       │  │
│  └───────────────────────────┼───────────────────────────────────────┘  │
│                              │                                          │
│  ┌───────────────────────────┼───────────────────────────────────────┐  │
│  │          UNIFIED LLM SERVICE (llm_service.py)                    │  │
│  │                           │                                       │  │
│  │     ┌─────────────────────┴──────────────────────┐              │  │
│  │     │  LLMService(provider: LLMProvider)         │              │  │
│  │     │  - chat()                                  │              │  │
│  │     │  - chat_stream()                           │              │  │
│  │     │  - generate_embeddings()                   │              │  │
│  │     │  - health_check()                          │              │  │
│  │     └─────────────────────┬──────────────────────┘              │  │
│  │                           │                                       │  │
│  │              ┌────────────┴────────────┐                         │  │
│  │              │                         │                         │  │
│  │         LLM_PROVIDER=?                │                         │  │
│  │         (from .env)                   │                         │  │
│  │              │                         │                         │  │
│  └──────────────┼─────────────────────────┼─────────────────────────┘  │
│                 │                         │                            │
│    ┌────────────▼──────────┐  ┌──────────▼───────────┐                │
│    │   OLLAMA SERVICE      │  │   OPENAI SERVICE     │                │
│    │  (ollama_service.py)  │  │  (openai_service.py) │                │
│    │                       │  │                      │                │
│    │  • chat()             │  │  • chat()            │                │
│    │  • chat_stream()      │  │  • chat_stream()     │                │
│    │  • embeddings()       │  │  • embeddings()      │                │
│    │  • health_check()     │  │  • health_check()    │                │
│    └───────────┬───────────┘  └──────────┬───────────┘                │
│                │                         │                            │
└────────────────┼─────────────────────────┼────────────────────────────┘
                 │                         │
                 │                         │
      ┌──────────▼──────────┐   ┌─────────▼──────────┐
      │   LOCAL OLLAMA      │   │   OPENAI API       │
      │                     │   │   (Cloud)          │
      │  • qwen2.5:7b      │   │                    │
      │  • llama3.2:3b     │   │  • gpt-3.5-turbo  │
      │                     │   │  • gpt-4          │
      │  localhost:11434    │   │  api.openai.com   │
      └─────────────────────┘   └────────────────────┘
           FREE, LOCAL              PAID, CLOUD
```

## Configuration Flow

```
.env file
  │
  ├─── LLM_PROVIDER=ollama ──────┐
  │                               │
  ├─── LLM_PROVIDER=openai ──────┤
  │                               │
  └───────────────────────────────┴─────► config.py
                                           │
                                           ▼
                                    LLMService.__init__()
                                           │
                    ┌──────────────────────┴───────────────────┐
                    │                                          │
                    ▼                                          ▼
            OllamaService()                           OpenAIService()
```

## Message Flow

```
User Input: "Check my balance"
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Agent (e.g., Banking Agent)                            │
│                                                          │
│  llm = get_llm_service()  ← Reads LLM_PROVIDER from .env│
│  response = await llm.chat(messages)                    │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  LLMService                                              │
│                                                          │
│  if provider == OLLAMA:                                  │
│      return ollama_service.chat(messages)                │
│  elif provider == OPENAI:                                │
│      return openai_service.chat(messages)                │
└──────────────────────────────────────────────────────────┘
       │
       ├────────────────┬─────────────────┐
       ▼                ▼                 ▼
   [Ollama]         [OpenAI]          [Future: Others]
   localhost        api.openai.com
       │                │
       ▼                ▼
   Response         Response
       │                │
       └────────┬───────┘
                ▼
          AI Response
                │
                ▼
            User Gets Answer
```

## Interface Compatibility

```
┌─────────────────────────────────────────────────────────┐
│  Common Interface (Both Providers Support)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  async def chat(                                        │
│      messages: List[Dict],                              │
│      use_fast_model: bool = False,  ← Only Ollama uses │
│      temperature: float = None,                         │
│      max_tokens: int = None                             │
│  ) -> str                                               │
│                                                         │
│  async def chat_stream(                                 │
│      messages: List[Dict],                              │
│      use_fast_model: bool = False,                      │
│      temperature: float = None                          │
│  ) -> AsyncGenerator[str, None]                         │
│                                                         │
│  async def generate_embeddings(                         │
│      text: str                                          │
│  ) -> List[float]                                       │
│                                                         │
│  async def health_check() -> bool                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Switching Process

```
┌─────────────────────────────────────────────────────┐
│  1. Edit .env                                       │
│     LLM_PROVIDER=ollama  → LLM_PROVIDER=openai     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  2. Restart AI Backend                              │
│     cd ai && ./run.sh                               │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  3. LLMService reads new config                     │
│     provider = settings.llm_provider                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  4. Initializes correct service                     │
│     OpenAIService() or OllamaService()              │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  5. All agents now use new provider                 │
│     Intent, Banking, FAQ agents → new LLM           │
└─────────────────────────────────────────────────────┘
```

## File Structure

```
ai/
├── services/
│   ├── __init__.py              ← Exports all services
│   ├── ollama_service.py        ← Local LLM (existing)
│   ├── openai_service.py        ← Cloud LLM (NEW)
│   └── llm_service.py           ← Unified interface (NEW)
│
├── agents/
│   ├── intent_classifier.py    ← Updated to use LLMService
│   ├── banking_agent.py         ← Updated to use LLMService
│   └── faq_agent.py             ← Updated to use LLMService
│
├── config.py                    ← Added OpenAI settings
├── .env                         ← LLM_PROVIDER setting
├── .env.example                 ← Config template
│
└── docs/
    ├── LLM_PROVIDER_GUIDE.md    ← Full guide
    ├── QUICK_REFERENCE.md        ← Quick ref
    └── OPENAI_INTEGRATION.md     ← This summary
```

## Decision Tree

```
                    Start
                      │
                      ▼
              Need LLM Service?
                      │
                      ▼
            get_llm_service()
                      │
                      ▼
              Read .env config
                      │
          ┌───────────┴───────────┐
          │                       │
     LLM_PROVIDER=ollama    LLM_PROVIDER=openai
          │                       │
          ▼                       ▼
   ┌──────────────┐        ┌─────────────┐
   │ Free?        │        │ Have API    │
   │ Private?     │        │ key?        │
   │ Offline OK?  │        │ Budget?     │
   └──────┬───────┘        └──────┬──────┘
          │                       │
          ▼                       ▼
    OllamaService           OpenAIService
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
              Same Interface
         (chat, stream, embeddings)
                      │
                      ▼
                  Response
```
