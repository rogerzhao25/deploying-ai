import os
from openai import OpenAI
from .config import BASE_URL, API_GATEWAY_KEY, OPENAI_MODEL, OPENAI_EMBED_MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key="dummy",  # required but unused
    default_headers={"x-api-key": API_GATEWAY_KEY},
)

def chat(messages, tools=None):
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=tools
    )
    msg = resp.choices[0].message
    return msg.content, getattr(msg, "tool_calls", None)

def embed(texts):
    resp = client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=texts
    )
    return [d.embedding for d in resp.data]