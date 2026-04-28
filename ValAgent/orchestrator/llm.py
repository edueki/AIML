from typing import Any, Dict, Optional
import re
import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

groq_client = Groq(api_key=GROQ_API_KEY)

_CODE_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.MULTILINE)

def _strip_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text or "").strip()

def _drop_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


async def groq_summarize(query: str, tool_name: Optional[str], tool_resp: Any) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    messages = [
        {"role": "system", "content": "You are a precise summarizer for an AI orchestrator. Convert structured tool results into a concise, factual answer. Do not invent facts."},
        {"role": "user", "content": json.dumps({"query": query, "tool_name": tool_name, "result": tool_resp}, ensure_ascii=False)}
    ]
    body = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 600}
    async with httpx.AsyncClient(timeout=ORCH_TIMEOUT_SECONDS) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
