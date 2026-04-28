
import json
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI
from groq import Groq

from schema import OrchestrateIn, OrchestrateOut
from config import MCP_HTTP_URL, ORCH_TIMEOUT_SECONDS, GROQ_API_KEY, GROQ_MODEL
from mcp_client import MCPClient
from intent import intent_select

app = FastAPI(title="ValAgent Orchestrator API", version="0.7.0")

mcp = MCPClient(MCP_HTTP_URL, timeout=ORCH_TIMEOUT_SECONDS)
groq_client = Groq(api_key=GROQ_API_KEY)

# Only these tools require bearer token validation
PROTECTED_TOOLS = {"create_payment_intent", "enroll_course"}


# ----------------------------
# Small helpers
# ----------------------------

def _strip_fences(text: str) -> str:
    """Remove ``` or ```json fences if LLM wraps the JSON."""
    s = text.strip()
    if s.startswith("```json"):
        s = s[len("```json") :].strip()
    elif s.startswith("```"):
        s = s[len("```") :].strip()
    if s.endswith("```"):
        s = s[: -3].strip()
    return s


def _merge_context_from_result(tool_name: str, result: Any, ctx: Dict[str, Any]) -> None:
    """
    Pull useful IDs/fields from tool results into context so later steps
    can use them (user_id, course_id, payment_id, enrollment_id, etc.).
    """
    if not isinstance(result, dict):
        return

    for key in ("user_id", "course_id", "payment_id", "enrollment_id"):
        if key in result and result[key] not in (None, 0, "", []):
            ctx[key] = result[key]

    data = result.get("data")
    if isinstance(data, dict):
        for key in ("user_id", "course_id", "payment_id", "enrollment_id"):
            if key in data and data[key] not in (None, 0, "", []):
                ctx[key] = data[key]

    ctx[f"{tool_name}_result"] = result


def _fill_args_from_context(
    args: Dict[str, Any],
    ctx: Dict[str, Any],
) -> (Dict[str, Any], List[str]):
    """
    Recursively fill in arguments where values are None/0/"" from context
    when keys match (user_id, course_id, payment_id, etc.).
    Returns (resolved_args, missing_fields_paths).
    """
    resolved = json.loads(json.dumps(args))  # deep copy
    missing: List[str] = []

    def _walk(node: Any, path: str) -> None:
        nonlocal missing
        if isinstance(node, dict):
            for k, v in node.items():
                full = f"{path}.{k}" if path else k
                if isinstance(v, dict):
                    _walk(v, full)
                else:
                    if v in (None, 0, "") and k in ctx and ctx[k] not in (None, "", 0):
                        node[k] = ctx[k]
                    elif v in (None, 0, ""):
                        missing.append(full)

    _walk(resolved, "")
    return resolved, missing


# ----------------------------
# Groq Planner (uses intent only)
# ----------------------------

PLANNER_SYSTEM_PROMPT = """
You are ValAgent Planner for the EDUeki course platform.

You receive:
- user_query: what the user asked
- intent: output from the intent selector (single or multi, with tool_candidates)
- context: known data (ids, tokens, etc.)

Your job:
- Design an EXECUTION PLAN as JSON.
- Each step calls exactly ONE tool with some arguments.
- You do NOT execute tools. You only produce the plan.

IMPORTANT:
- You MUST only use tools that appear in intent.tool_candidates (their "name" fields).
- You may change the ORDER of tool_candidates to make the flow logical
  (e.g., signup -> signin -> discounts -> payment -> enroll).
- You may SKIP tool_candidates that are clearly unnecessary.
- You may RE-USE a tool candidate more than once if it makes sense (e.g., multiple lookups).

ARGUMENTS:
- Follow each tool's input schema from the intent (inputSchema).
- If you don't know a value:
    - string  -> "placeholder"
    - email   -> "user@example.com"
    - number  -> 0
- The orchestrator will:
    - Fill ids (user_id, course_id, payment_id, enrollment_id) from context and previous tool results.
    - Stop and ask the user if required fields are still missing during execution.

OUTPUT FORMAT (STRICT):

{
  "steps": [
    {
      "id": "step-1",
      "tool": "<tool_name>",
      "arguments": { ... },
      "description": "short explanation"
    },
    ...
  ]
}

No extra text, no markdown, no comments.

EXAMPLE (FOR STYLE ONLY, DO NOT COPY VERBATIM):

User query:
"Can you create an account raja with email id raja@rose.com with password 1234567 then enroll to the course AIML with available discount codes."

Intent (simplified):
- type: "multi"
- tool_candidates contain: signup, signin, list_discounts, apply_discount, create_payment_intent, enroll_course, and possibly course lookup tools.

A GOOD PLAN:

{
  "steps": [
    {
      "id": "step-1",
      "tool": "signup",
      "arguments": {
        "email": "raja@rose.com",
        "password": "1234567",
        "name": "raja"
      },
      "description": "Create a new user account for raja."
    },
    {
      "id": "step-2",
      "tool": "signin",
      "arguments": {
        "email": "raja@rose.com",
        "password": "1234567"
      },
      "description": "Sign in to obtain user identity/token."
    },
    {
      "id": "step-3",
      "tool": "list_discounts",
      "arguments": {},
      "description": "Retrieve available discount codes."
    },
    {
      "id": "step-4",
      "tool": "apply_discount",
      "arguments": {
        "discount_input": {
          "course_id": 0,
          "code": "placeholder"
        }
      },
      "description": "Apply a discount to the AIML course once course_id and discount code are known."
    },
    {
      "id": "step-5",
      "tool": "create_payment_intent",
      "arguments": {
        "payment_input": {
          "user_id": 0,
          "course_id": 0,
          "amount_cents": 0
        }
      },
      "description": "Create a payment for the AIML course using the (possibly discounted) price."
    },
    {
      "id": "step-6",
      "tool": "enroll_course",
      "arguments": {
        "enroll_input": {
          "user_id": 0,
          "course_id": 0,
          "payment_id": 0
        }
      },
      "description": "Enroll the user in the AIML course after payment."
    }
  ]
}

Remember:
- Use ONLY tools from intent.tool_candidates.
- Use placeholders where exact values are unknown.
- The orchestrator will handle missing values and user follow-up.
""".strip()


async def _plan_with_llm(
    req: OrchestrateIn,
    intent: Dict[str, Any],
    context: Dict[str, Any],
    trace: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Call Groq LLM to get a plan:
    { "steps": [ { "id", "tool", "arguments", "description" }, ... ] }

    Planner input uses:
      - user_query
      - intent (including tool_candidates)
      - context
    It does NOT receive the full MCP tools list again.
    """
    planner_input = {
        "user_query": req.query,
        "intent": intent,
        "context": context,
    }

    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.1,
        response_format={"type": "text"},
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(planner_input, ensure_ascii=False)},
        ],
    )

    raw = completion.choices[0].message.content or "{}"
    raw = _strip_fences(raw)

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        plan = {"steps": [], "_raw": raw}

    trace["steps"].append({"step": "planner", "plan": plan})
    return plan


# ----------------------------
# Auth helper – per-execution
# ----------------------------

async def _ensure_auth_for_protected_tool(
    tool_name: str,
    effective_token: Optional[str],
    auth_state: Dict[str, Any],
    trace: Dict[str, Any],
) -> Optional[OrchestrateOut]:
    """
    For PROTECTED_TOOLS, ensure we have a valid token.
    Returns:
      - None -> token is valid, proceed
      - OrchestrateOut -> stop and return this error to caller
    """
    if tool_name not in PROTECTED_TOOLS:
        return None

    if not effective_token:
        trace["steps"].append({"step": "missing_token", "tool": tool_name})
        return OrchestrateOut(
            ok=False,
            message="Bearer token is required for payment/enrollment.",
            answer={
                "type": "auth_required",
                "tool": tool_name,
                "missing_fields": ["bearer_token"],
                "reason": "Payment and enrollment require a valid bearer token.",
            },
            trace=trace,
        )

    if auth_state.get("validated", False):
        return None

    args = {"bearer_token": effective_token}
    res = await mcp.call_tool("validate_auth_token", args)
    trace["steps"].append(
        {
            "step": "auth_call",
            "tool": "validate_auth_token",
            "args": args,
            "raw_result": res,
        }
    )

    valid = True
    if isinstance(res, dict):
        if res.get("valid") is False:
            valid = False

    if not valid:
        return OrchestrateOut(
            ok=False,
            message="Authentication failed for payment/enrollment.",
            answer={
                "type": "auth_error",
                "details": {
                    "reason": "Invalid or expired bearer token.",
                    "validate_result": res,
                },
            },
            trace=trace,
        )

    auth_state["validated"] = True
    if isinstance(res, dict):
        sub = res.get("sub")
        if sub is not None:
            try:
                auth_state["user_id_from_token"] = int(sub)
            except ValueError:
                auth_state["user_sub"] = sub

    return None


# ----------------------------
# Plan execution (multi-turn)
# ----------------------------

async def _execute_plan(
    plan: Dict[str, Any],
    base_context: Dict[str, Any],
    req: OrchestrateIn,
    trace: Dict[str, Any],
) -> OrchestrateOut:
    steps = plan.get("steps") or []
    if not steps:
        return OrchestrateOut(
            ok=False,
            message="Planner returned empty plan.",
            answer={
                "type": "planner_error",
                "details": {"reason": "No steps in plan.", "plan": plan},
            },
            trace=trace,
        )

    ctx: Dict[str, Any] = dict(base_context or {})
    if req.bearer_token:
        ctx["bearer_token"] = req.bearer_token

    last_result: Any = None
    auth_state: Dict[str, Any] = {"validated": False}

    for step in steps:
        tool_name = step.get("tool")
        if not tool_name:
            trace["steps"].append(
                {"step": "plan_error", "error": "Missing tool name in step", "step_obj": step}
            )
            continue

        effective_token = req.bearer_token or ctx.get("bearer_token")
        auth_out = await _ensure_auth_for_protected_tool(
            tool_name, effective_token, auth_state, trace
        )
        if auth_out is not None:
            return auth_out

        raw_args = step.get("arguments") or {}
        resolved_args, missing = _fill_args_from_context(raw_args, ctx)

        if missing:
            trace["steps"].append(
                {
                    "step": "missing_args",
                    "tool": tool_name,
                    "missing": missing,
                    "raw_args": raw_args,
                    "resolved_args": resolved_args,
                }
            )
            return OrchestrateOut(
                ok=False,
                message=f"Missing required details for tool '{tool_name}'.",
                answer={
                    "type": "missing_arguments",
                    "tool": tool_name,
                    "missing_fields": missing,
                    "step": step,
                },
                trace=trace,
            )

        res = await mcp.call_tool(tool_name, resolved_args)
        last_result = res

        trace["steps"].append(
            {
                "step": "tools/call",
                "tool": tool_name,
                "args": resolved_args,
                "raw_result": res,
            }
        )

        _merge_context_from_result(tool_name, res, ctx)

    context_updates = {}
    for key in ("user_id", "course_id", "payment_id", "enrollment_id"):
        if key in ctx:
            context_updates[key] = ctx[key]

    return OrchestrateOut(
        ok=True,
        message="Success (planned multi-turn).",
        answer={
            "type": "final",
            "tool": steps[-1].get("tool"),
            "result": last_result,
            "context_updates": context_updates,
        },
        trace=trace,
    )


# ----------------------------
# Single-turn execution
# ----------------------------

async def _execute_single(
    intent: Dict[str, Any],
    base_context: Dict[str, Any],
    req: OrchestrateIn,
    trace: Dict[str, Any],
) -> OrchestrateOut:
    tool_name = intent.get("tool_name")
    if not tool_name:
        return OrchestrateOut(
            ok=False,
            message="Intent type 'single' but no tool_name provided.",
            answer={"type": "intent_error", "details": intent},
            trace=trace,
        )

    args = (intent.get("arguments") or {})
    ctx = dict(base_context or {})

    effective_token = req.bearer_token or ctx.get("bearer_token")
    auth_state: Dict[str, Any] = {"validated": False}
    auth_out = await _ensure_auth_for_protected_tool(
        tool_name, effective_token, auth_state, trace
    )
    if auth_out is not None:
        return auth_out

    resolved_args, missing = _fill_args_from_context(args, ctx)
    if missing:
        trace["steps"].append(
            {
                "step": "missing_args",
                "tool": tool_name,
                "missing": missing,
                "raw_args": args,
                "resolved_args": resolved_args,
            }
        )
        return OrchestrateOut(
            ok=False,
            message=f"Missing required details for tool '{tool_name}'.",
            answer={
                "type": "missing_arguments",
                "tool": tool_name,
                "missing_fields": missing,
                "step": {"tool": tool_name, "arguments": args},
            },
            trace=trace,
        )

    res = await mcp.call_tool(tool_name, resolved_args)
    trace["steps"].append(
        {"step": "tools/call", "tool": tool_name, "args": resolved_args, "raw_result": res}
    )

    _merge_context_from_result(tool_name, res, ctx)

    context_updates = {}
    for key in ("user_id", "course_id", "payment_id", "enrollment_id"):
        if key in ctx:
            context_updates[key] = ctx[key]

    return OrchestrateOut(
        ok=True,
        message="Success (single-turn).",
        answer={
            "type": "final",
            "tool": tool_name,
            "result": res,
            "context_updates": context_updates,
        },
        trace=trace,
    )


# ----------------------------
# Main orchestrate endpoint
# ----------------------------

@app.post("/orchestrate", response_model=OrchestrateOut)
async def orchestrate(req: OrchestrateIn) -> OrchestrateOut:
    trace: Dict[str, Any] = {"steps": []}

    try:
        await mcp.initialize()
        trace["steps"].append({"step": "initialize", "session_id": mcp.session_id})

        tools = await mcp.list_tools()
        trace["steps"].append({"step": "tools/list", "count": len(tools)})

        base_context: Dict[str, Any] = dict(req.context or {})

        intent = await intent_select(req.query, tools, base_context)
        trace["steps"].append({"step": "intent", "intent": intent})

        itype = intent.get("type")

        if itype == "single":
            return await _execute_single(intent, base_context, req, trace)

        if itype == "multi":
            plan = await _plan_with_llm(req, intent, base_context, trace)
            return await _execute_plan(plan, base_context, req, trace)

        trace["steps"].append({"step": "unsupported_intent_type", "intent_type": itype})
        return OrchestrateOut(
            ok=False,
            message=f"Unsupported intent type: {itype}",
            answer={"type": "intent_error", "details": intent},
            trace=trace,
        )

    except httpx.HTTPStatusError as e:
        trace["steps"].append(
            {
                "step": "http_error",
                "status": e.response.status_code if e.response else None,
                "body": e.response.text if e.response else str(e),
            }
        )
        return OrchestrateOut(ok=False, message="HTTP error", answer=None, trace=trace)
    except Exception as e:
        trace["steps"].append({"step": "exception", "error": str(e)})
        return OrchestrateOut(ok=False, message="Unhandled error", answer=None, trace=trace)


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
