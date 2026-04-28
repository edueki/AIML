from pydantic import Field, EmailStr
from typing import Optional, Dict, Any, Annotated
import httpx

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ValAgent Student Assistant MCP")

# --- HTTP helpers (async, timeouts, consistent shape) ---
_DEFAULT_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}

async def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    h = {**_DEFAULT_HEADERS, **(headers or {})}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            resp = await client.get(url, headers=h, params=params)
            resp.raise_for_status()
            return {"ok": True, "status_code": resp.status_code, "data": resp.json()}
    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "status_code": e.response.status_code if e.response else None,
            "error": e.response.text if e.response is not None else str(e),
        }
    except httpx.RequestError as e:
        return {"ok": False, "status_code": None, "error": str(e)}

async def http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    h = {**_DEFAULT_HEADERS, **(headers or {})}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            resp = await client.post(url, headers=h, json=body or {})
            resp.raise_for_status()
            # Handle endpoints that may return empty body
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") and resp.text else None
            return {"ok": True, "status_code": resp.status_code, "data": data}
    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "status_code": e.response.status_code if e.response else None,
            "error": e.response.text if e.response is not None else str(e),
        }
    except httpx.RequestError as e:
        return {"ok": False, "status_code": None, "error": str(e)}
