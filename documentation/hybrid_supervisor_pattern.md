# Hybrid Supervisor Multi-Agent Pattern

This document explains the new supervisor-led orchestration that powers the Vaani banking assistant. The goal is to combine deterministic control (intent routing) with the existing specialist agents so we can add new skills without touching their business logic.

## Why a Hybrid Supervisor?
- **Deterministic control:** The supervisor normalises context, invokes the intent classifier, and deterministically selects the right specialist. No hidden agent-to-agent chatter.
- **Business logic reuse:** Banking/UPI/RAG agents stay untouched. They keep returning the same state dictionary they always have.
- **Clean separation of concerns:** Conversation state management, routing, and specialist execution now live in `ai/orchestrator/` instead of being intertwined with LangGraph scaffolding.
- **Observability:** Each phase logs uniform events (`conversation_context_created`, `intent_router_decision`, `invoking_specialist`) so production tracing is simpler.

## Key Modules
| File | Responsibility |
| --- | --- |
| `ai/orchestrator/state.py` | Defines `ConversationState`, a dataclass mirror of the old `AgentState` dict. Handles message lists, context, syncing structured data, etc. |
| `ai/orchestrator/router.py` | Wraps the legacy `classify_intent` node. Updates the state, records the detected intent, and maps it to an agent key. |
| `ai/orchestrator/supervisor.py` | Implements `HybridSupervisor` which builds context, asks the router for an intent, executes the chosen specialist, and shapes the final response payload. |
| `ai/agents/rag_agent.py` + `ai/agents/rag_agents/` | RAG supervisor that now fans-in loan, investment, and customer-support specialists while preserving shared logic. |
| `ai/agents/greeting_agent.py` | Returns a deterministic welcome script (localized + contextual) so greetings don’t incur LLM latency. |
| `ai/agents/feedback_agent.py` | Acknowledges complaints/suggestions and tags them for downstream support tooling. |
| `ai/agents/agent_graph.py` | Public entry point. All API/UI integrations call `process_message`, which now delegates to `HybridSupervisor`. |

## Message Lifecycle
1. **Context build:** `HybridSupervisor._build_context` converts `message_history` into LangChain `HumanMessage`/`AIMessage` objects, infers UPI mode (frontend flag > history text > `structured_data` hints), and creates a `ConversationState` instance.
2. **Intent classification:** `IntentRouter.assign_intent` sends the state dict through `classify_intent`. Any fields mutated by the classifier are merged back into the dataclass.
3. **Routing:** `IntentRouter.resolve_route` maps the high-level intent (`upi_payment`, `banking_operation`, `general_faq`, `greeting`, `feedback`, etc.) to a concrete specialist key.
4. **Specialist execution:** The supervisor calls the selected agent (`banking_agent`, `upi_agent`, `rag_agent`, `greeting_agent`, or `feedback_agent`). The RAG supervisor further delegates to its loan/investment/customer-support specialists. Returned state fields (messages, structured data, statements, UPI mode) are applied back onto the shared context.
5. **Response shaping:** `_build_response` extracts the final assistant message plus any structured payloads and timestamp so HTTP clients receive the same schema as before.

## Supervisor Contract
- **Input:** `message`, `user_id`, `session_id`, optional `language`, `user_context`, `message_history`, `upi_mode`.
- **Output:** Dict with `success`, `response`, `intent`, `language`, optional `statement_data` / `structured_data`, timestamp ISO string.
- **Error handling:** `agent_graph.process_message` wraps `HybridSupervisor.process` and returns the same bilingual fallback messages when something breaks.

## Edge Cases & Safeguards
- **UPI wake word:** Even if the frontend forgets to pass `upi_mode`, recent assistant replies and structured UI payloads are scanned for UPI activation phrases/types.
- **Missing agent data:** If a specialist forgets to append an AI reply, `_build_response` still returns an empty string instead of crashing.
- **Unknown intents:** Router falls back to `rag_agent` through `DEFAULT_ROUTE`, so user always receives a graceful response.
- **Greeting & feedback guardrails:** Deterministic agents handle small-talk and CSAT acknowledgements immediately, preventing FAQ prompts from being polluted.
- **State sync:** `ConversationState.apply_agent_state` whitelists which fields can be mutated to avoid surprises.

## Extending the Pattern
1. Implement a new specialist (e.g., `loans_agent`) that accepts/returns the familiar state dict.
2. Add the agent to `SPECIALIST_MAP` in `supervisor.py`.
3. Teach `INTENT_TO_ROUTE` in `router.py` how to map the new intent label to the agent key.
4. (Optional) Update the classifier prompt to emit the new intent keyword.

No LangGraph wiring or shared mutable globals required—the supervisor orchestrates everything.

## Testing Checklist
- `pytest ai/test_upi_mode_routing.py` — validates UPI wake word handling & routing.
- `pytest ai/test_balance_queries.py` — sanity checks for banking agent responses.
- End-to-end smoke test: call `ai.main.process_message` with a mock session to verify payload schema.

## Operational Notes
- **Logging:** All supervisor logs use structured key/value pairs so they flow through the existing JSON log pipeline.
- **Observability hook:** Call `ConversationState.snapshot()` if you need to emit a sanitized state for tracing dashboards.
- **Migration:** The old LangGraph build lives in `ai/agents/agent_graph_old.py` for reference; removing it is optional once confidence is high.

For architectural visuals, see `documents/hybrid_supervisor_architecture.mmd`.
