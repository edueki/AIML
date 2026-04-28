from typing import Optional, Dict,List, Any
import httpx
from config import  INTENT_SERVER_URL, ORCH_TIMEOUT_SECONDS

async def intent_select(query: str, tools: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    payload = {"query": query, "tools": tools, "context": context or {}}
    async with httpx.AsyncClient(timeout=ORCH_TIMEOUT_SECONDS) as client:
        r = await client.post(INTENT_SERVER_URL, json=payload)
        r.raise_for_status()
        return r.json()