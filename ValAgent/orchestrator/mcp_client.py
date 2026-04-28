# mcp_client.py
import uuid
import httpx
from typing import Any, Dict, Optional, List
from utils import rpc_response_processor

ACCEPT = "application/json, text/event-stream"
CT = "application/json"

class MCPClient:
    def __init__(self, base_url: str, timeout: float = 15.0, protocol_version: str = "2024-11-05"):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.protocol_version = protocol_version
        self.session_id: Optional[str] = None

    async def _post(self, payload: Dict[str, Any], session: Optional[str] = None) -> httpx.Response:
        url = self.base_url
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(url, headers={"Accept": ACCEPT, "Content-Type": CT}, json=payload)

    async def initialize(self) -> None:
            r = await self._post({
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {
                    "get": True,
                    "list": True,
                    "call": True
                    }},
                    "clientInfo": {"name": "ValOrchestrator", "version": "0.1.0"}
                }
            })
            r.raise_for_status()
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            sid = hdrs.get("mcp-session-id") or hdrs.get("mcp-session") or hdrs.get("x-session-id")
            if sid:
                self.session_id = sid
                return

    async def rpc(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method, "params": params}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                "mcp-session-id": self.session_id,  # 👈 Send session ID in header
            }
            r = await client.post(self.base_url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.text
            response = rpc_response_processor(data)
            return response


    async def list_tools(self) -> List[Dict[str, Any]]:
        res = await self.rpc("tools/list", params={})
        return res.get("tools", []) if isinstance(res, dict) else []

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await self.rpc("tools/call", {"name": name, "arguments": arguments})

    async def ping(self) -> Dict[str, Any]:
        return await self.rpc("ping", params={})