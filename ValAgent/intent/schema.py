from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# ---------- IO models ----------
class ToolSchema(BaseModel):
    name: str
    description: Optional[str] = None
    inputSchema: Optional[Dict[str, Any]] = None  # passthrough from MCP

class IntentIn(BaseModel):
    query: str
    tools: List[ToolSchema]
    context: Optional[Dict[str, Any]] = None

class IntentOut(BaseModel):
    # single
    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    # multi (unordered list of viable tools; NO plan/sequence)
    tool_candidates: Optional[List[Dict[str, Any]]] = None  # [{name, suggestedArguments?, note?}]
    # common
    type: str
    confidence: float
    reason: str