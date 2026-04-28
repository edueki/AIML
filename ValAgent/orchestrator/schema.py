from pydantic import BaseModel
from typing import Any, Dict, Optional, Union

class OrchestrateIn(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    bearer_token: Optional[str] = None

class OrchestrateOut(BaseModel):
    ok: bool
    message: str
    answer: Optional[Union[str, Dict[str, Any]]] = None
    trace: Optional[Dict[str, Any]] = None