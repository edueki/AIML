from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import uuid
import time
import json
from groq import Groq
from config import settings
import uvicorn

GROQ_MODEL = settings.GROQ_MODEL
GROQ_API_KEY = settings.GROQ_API_KEY

ORCHESTRATOR_URL = "http://localhost:9000/orchestrate"

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="VALAGENT Context Manager")


# ------------------------------
# MODELS
# ------------------------------
class UserQuery(BaseModel):
    session_id: str
    query: str
    debug: bool = False
    # we keep this for possible programmatic clients, but normally token comes from text
    bearer_token: Optional[str] = None


class SessionData(BaseModel):
    chat_history: List[Dict[str, Any]]
    total_tokens: int
    last_updated: float
    bearer_token: Optional[str] = None  # stored token for this session


# ------------------------------
# IN-MEMORY SESSION STORE
# ------------------------------
SESSIONS: Dict[str, SessionData] = {}


def new_session() -> str:
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = SessionData(
        chat_history=[],
        total_tokens=0,
        last_updated=time.time(),
        bearer_token=None,
    )
    return session_id


def ensure_session(session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionData(
            chat_history=[],
            total_tokens=0,
            last_updated=time.time(),
            bearer_token=None,
        )


def update_session(session_id: str, role: str, content: Any, tokens: int = 0):
    session = SESSIONS[session_id]
    session.chat_history.append({"role": role, "content": content})
    session.total_tokens += tokens
    session.last_updated = time.time()


# ------------------------------
# Helper: strip fences (for JSON outputs)
# ------------------------------
def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```json"):
        s = s[len("```json") :].strip()
    elif s.startswith("```"):
        s = s[len("```") :].strip()
    if s.endswith("```"):
        s = s[:-3].strip()
    return s


# ------------------------------
# LLM-based token extractor
# ------------------------------
def extract_token_with_llm(
    user_query: str, chat_history: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Ask Groq to look at the latest user message (and a bit of history)
    and extract a bearer token / JWT if present.

    The model MUST respond with a single JSON object:
      { "bearer_token": "<string or null>" }
    """

    system_prompt = """
You are a strict information extractor.

Your ONLY job:
- Look at the latest user message (and a bit of context).
- Detect if the user has provided a bearer token / JWT.
- A token is usually a long opaque string, commonly in one of these forms:
    - A JWT like: header.payload.signature (3 dot-separated base64url parts)
    - Or any long opaque token that is clearly meant to be a "token" in context.

Rules:
- If you find a token, return it as a string in JSON under "bearer_token".
- If you do NOT find any token, return null as the value.
- NEVER make up or hallucinate a token.
- If you are unsure, return null.

You MUST respond with ONLY a single JSON object, no extra text, in this format:

{
  "bearer_token": "<string or null>"
}
""".strip()

    payload = {
        "latest_user_message": user_query,
        "recent_history": chat_history[-1:],
    }

    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.0,
        response_format={"type": "text"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, indent=2),
            },
        ],
    )

    raw = completion.choices[0].message.content or "{}"
    raw = _strip_fences(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    token = data.get("bearer_token")
    if token in (None, "", "null"):
        return None
    return str(token)


# ------------------------------
# LLM RENDERER (Groq)
# ------------------------------
def render_llm_response(
    user_query: str,
    orchestrator_resp: Dict[str, Any],
    chat_history: List[Dict[str, Any]],
    debug: bool,
) -> str:
    """
    Convert orchestrator response into a user-facing answer using Groq LLM.
    This is aligned with OrchestrateOut:
      ok: bool
      message: str
      answer: Optional[Union[str, Dict[str, Any]]]
      trace: Optional[Dict[str, Any]]
    """

    orch_ok = orchestrator_resp.get("ok", False)
    orch_message = orchestrator_resp.get("message", "")
    answer = orchestrator_resp.get("answer")
    trace = orchestrator_resp.get("trace") if debug else None

    answer_type = None
    if isinstance(answer, dict):
        answer_type = answer.get("type")
    elif isinstance(answer, str):
        # If orchestrator ever returns a plain string, treat as final text
        return answer

    system_prompt = """
You are VALAGENT, the conversational layer on top of the ValAgent Orchestrator.

You see:
- The original user query.
- A small slice of recent chat history.
- The orchestrator result with:
  - ok: success or failure
  - message: short status
  - answer: structured payload with a "type" field
  - trace: internal steps (shown only when debug=true)

You must output ONLY a natural language reply to the user. No JSON. No code.

Interpret answer.type as follows:

1) type = "final"
   - The orchestrator successfully completed the tools workflow.
   - answer.result contains the last tool's output (e.g., signup result, enrollment result, payment result, etc).
   - Summarize what happened in a simple way, focusing on what the user cares about:
     - Was the account created?
     - Was the payment completed?
     - Was the enrollment created?
   - Use any human-facing message inside the result if present (like "User registered successfully").
   - Do not dump raw JSON. Rephrase it.

2) type = "missing_arguments"
   - The orchestrator could not continue because some fields are missing (answer.missing_fields).
   - Politely ask the user for those missing details.
   - Convert any field paths like "discount_input.code" or "enroll_input.payment_id" into friendly wording:
     - e.g., ask: "Which discount code would you like to apply?"
     - e.g., ask: "What is the payment ID for this enrollment?"

3) type = "auth_required"
   - The orchestrator needs a bearer token to continue payment/enrollment.
   - Politely ask the user to provide their bearer token or to sign in so we can proceed.

4) type = "auth_error"
   - The provided token was invalid or expired.
   - Explain that the session seems invalid/expired and ask the user to sign in again or provide a fresh token.

5) Other error types (e.g., "planner_error", "system_error", or orchestrator ok=false with no type):
   - Apologize briefly and tell the user something went wrong on the system side.
   - Suggest they try again or adjust their request.

Additional rules:
- Be concise, friendly, and focused on the user's goal.
- Do NOT expose raw JSON, stack traces, or long technical details.
- If debug=true, you may add a short, high-level note like:
  "(internal: tools executed: signup -> create_payment_intent -> enroll_course)".
""".strip()

    user_payload = {
        "user_query": user_query,
        "recent_history": chat_history[-5:],
        "orchestrator_ok": orch_ok,
        "orchestrator_message": orch_message,
        "answer": answer,
        "answer_type": answer_type,
        "trace": trace if debug else "hidden",
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
    ]

    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=500,
        temperature=0.2,
    )

    return completion.choices[0].message.content


# ------------------------------
# ROUTES
# ------------------------------
@app.get("/new_session")
def create_session():
    session_id = new_session()
    return {"ok": True, "session_id": session_id}


@app.post("/query")
async def process_query(payload: UserQuery):
    """
    Main entry point for Streamlit / frontend.

    - Keeps the user query EXACT as sent.
    - Adds chat history into `context` for the orchestrator.
    - Uses LLM to extract bearer_token from text (if any) and store in session.
    - Calls orchestrator (which runs MCP tools).
    - Uses Groq LLM to render a nice natural language response.
    """

    ensure_session(payload.session_id)
    session = SESSIONS[payload.session_id]

    # Store user message
    update_session(payload.session_id, "user", payload.query)

    # 1) Try to extract a token via LLM from the latest user message + history
    try:
        token_from_llm = extract_token_with_llm(payload.query, session.chat_history)
    except Exception:
        token_from_llm = None

    # 2) Decide effective token: explicit payload wins, else LLM-extracted, else existing session token
    effective_token = payload.bearer_token or token_from_llm or session.bearer_token
    session.bearer_token = effective_token  # persist for future turns

    # 3) Build orchestrator input
    orchestrator_payload = {
        "query": payload.query,
        "session_id": payload.session_id,
        "context": {
            "chat_history": session.chat_history,
            "total_tokens": session.total_tokens,
        },
        "bearer_token": effective_token,
    }

    # 4) Call orchestrator
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(ORCHESTRATOR_URL, json=orchestrator_payload)
        resp.raise_for_status()
        orchestrator_resp = resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator error: {str(e)}",
        )

    # 5) Render final answer using Groq LLM
    try:
        final_answer = render_llm_response(
            user_query=payload.query,
            orchestrator_resp=orchestrator_resp,
            chat_history=session.chat_history,
            debug=payload.debug,
        )
    except Exception as e:
        raw_fallback = json.dumps(
            orchestrator_resp.get("answer", {}),
            ensure_ascii=False,
            indent=2,
        )
        final_answer = f"(LLM rendering failed: {e})\n\nRaw tool output:\n{raw_fallback}"

    # 6) Append assistant reply to chat history
    update_session(payload.session_id, "assistant", final_answer)

    return {
        "ok": orchestrator_resp.get("ok", True),
        "session_id": payload.session_id,
        "agent_response": final_answer,
        "debug_trace": orchestrator_resp.get("trace", {}) if payload.debug else None,
        "orchestrator_message": orchestrator_resp.get("message", ""),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8989, reload=True)
