# 05_src/assignment_chat/core/llm.py
"""
Clean OpenAI wrapper for the API Gateway setup.

This module provides:
- chat(...)   -> for normal chat + function calling
- embed(...)  -> for embeddings (semantic search / Chroma ingestion)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import (
    OPENAI_MODEL,
    OPENAI_EMBED_MODEL,
    BASE_URL,
    API_GATEWAY_KEY,
)

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not BASE_URL:
            raise RuntimeError("Missing BASE_URL in config.py")
        if not API_GATEWAY_KEY:
            raise RuntimeError(
                "Missing API_GATEWAY_KEY environment variable. "
                "Load it from .env/.secrets or export it before running."
            )

        _client = OpenAI(
            base_url=BASE_URL,
            api_key="dummy",  # required by SDK; gateway uses x-api-key instead
            default_headers={"x-api-key": API_GATEWAY_KEY},
        )
    return _client


def chat(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
    temperature: float = 0.4,
) -> Dict[str, Any]:
    """
    Wrapper for chat completions.
    Returns:
      {"content": str|None, "tool_calls": list|None}
    """
    client = get_client()

    kwargs: Dict[str, Any] = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if tools is not None:
        kwargs["tools"] = tools
    if tool_choice is not None:
        kwargs["tool_choice"] = tool_choice

    resp = client.chat.completions.create(**kwargs)
    msg = resp.choices[0].message

    # SDK returns tool_calls only when the model decides to call tools
    tool_calls = getattr(msg, "tool_calls", None)
    return {"content": msg.content, "tool_calls": tool_calls}


def embed(texts: List[str]) -> List[List[float]]:
    """
    Wrapper for embeddings.
    Returns: list of vectors aligned with `texts`.
    """
    if not texts:
        return []

    client = get_client()
    resp = client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=texts,
    )
    return [d.embedding for d in resp.data]
