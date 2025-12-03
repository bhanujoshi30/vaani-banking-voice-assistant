"""LangSmith/LangChain wrapper around Ollama for tracing.

This module lets us keep the existing OllamaService for normal calls,
but route selected requests through LangChain's ChatOllama so that
LangSmith picks up traces automatically when LANGCHAIN_* env vars
are configured.

Usage: called from LLMService.chat() when tracing is enabled.
"""

from typing import List, Dict

from anyio.to_thread import run_sync
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import settings


def _build_model(use_fast_model: bool) -> ChatOllama:
    """Create a ChatOllama instance using settings and fast/slow model flag."""

    model_name = settings.ollama_fast_model if use_fast_model else settings.ollama_model

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model_name,
        temperature=settings.llm_temperature,
    )


def _to_langchain_messages(messages: List[Dict[str, str]]):
    """Convert our simple role/content dicts into LangChain Message objects."""

    lc_messages = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))

    return lc_messages


async def chat_with_tracing(
    messages: List[Dict[str, str]],
    use_fast_model: bool = False,
) -> str:
    """Invoke Ollama via LangChain so that LangSmith receives traces.

    ChatOllama's invoke() API is synchronous, so we run it in a worker
    thread using anyio.run_sync. This keeps our public interface async
    without blocking the event loop.
    """

    lc_model = _build_model(use_fast_model)
    lc_messages = _to_langchain_messages(messages)

    def _invoke() -> str:
        result = lc_model.invoke(lc_messages)
        # ChatOllama returns a BaseMessage; we only need the text content.
        return result.content

    return await run_sync(_invoke)
