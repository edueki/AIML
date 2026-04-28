import json
import uvicorn
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from config import settings  # expects GROQ_API_KEY and GROQ_MODEL
from schema import *
from llm import *

app = FastAPI(title="ValAgent Intent Server (Groq, candidates only)", version="1.2.0")
client = Groq(api_key=settings.GROQ_API_KEY)
MODEL  = settings.GROQ_MODEL

# ---------- FastAPI ----------
@app.post("/intent", response_model=IntentOut)
async def detect_intent(inp: IntentIn):
    try:
        print (inp)
        tools_payload = [t.model_dump() for t in inp.tools]  # pass-through
        llm = call_llm(inp.query, tools_payload, inp.context)

        itype = (llm.get("type") or "").lower()
        confidence = float(llm.get("confidence", 0.0))
        reason = llm.get("reason") or "Selected by LLM."

        if itype == "single":
            return IntentOut(
                type="single",
                tool_name=llm.get("tool"),
                arguments=llm.get("arguments") or {},
                confidence=confidence,
                reason=reason,
                tool_candidates=None,
            )

        if itype == "multi":
            # Normalize to 'tool_candidates' for orchestrator
            cands = llm.get("toolCandidates") or []
            # Ensure each candidate only uses tools present in inp.tools
            allowed = {t.name for t in inp.tools}
            filtered: List[Dict[str, Any]] = []
            for c in cands:
                if isinstance(c, dict) and c.get("name") in allowed:
                    filtered.append({
                        "name": c["name"],
                        # optional hints; orchestrator may ignore
                        "suggestedArguments": c.get("suggestedArguments"),
                        "note": c.get("note"),
                    })
            return IntentOut(
                type="multi",
                tool_name=None,
                arguments=None,
                tool_candidates=filtered,
                confidence=confidence,
                reason=reason,
            )

        # Fallback: no actionable tool
        return IntentOut(
            type="single",
            tool_name=None,
            arguments={},
            confidence=confidence,
            reason="LLM could not determine a tool; returning no-op.",
            tool_candidates=None,
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"LLM returned non-JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent server error: {e}")

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8087, reload=True)
