"""
agent_service.py

Initializes the LangGraph ReAct agent that orchestrates our construction tools.
Uses MemorySaver to persist conversation history within a specific `page_session_id`.
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from prompts import AGENT_SYSTEM_PROMPT

# Global in-memory checkpointer.
# Thread IDs map to page_session_idx so memory resets when the user uploads a new plan.
memory = MemorySaver()


def _build_llm() -> ChatOpenAI:
    """Build the agent LLM, honoring a custom OpenAI-compatible gateway.

    - Model name comes from OPENAI_MODEL (defaults to gpt-4o).
    - When OPENAI_PROVIDER=custom, route through OPENAI_BASE_URL.
    """
    kwargs = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "temperature": 0,
    }
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        kwargs["api_key"] = api_key
    if os.getenv("OPENAI_PROVIDER", "").strip().lower() == "custom":
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


# Use OPENAI_MODEL for complex reasoning steps and tool calling
llm = _build_llm()

SYSTEM_PROMPT = AGENT_SYSTEM_PROMPT

