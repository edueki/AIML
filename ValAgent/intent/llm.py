import json
import re
from typing import List, Dict, Any, Optional
from groq import Groq  # or whichever LLM client you use
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)
MODEL  = settings.GROQ_MODEL

def _strip_to_json(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`").strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()
    if t.endswith("```"):
        t = t[:-3].strip()
    return t

def _prompt(query: str, tools: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> str:
    return f"""
You are an intent selector for a tool orchestrator.

INPUT:
- user query
- available tools (name, description, inputSchema from MCP)
- optional context (e.g., tokens)

DECISION RULES:
1) Use tools description to determine which tools need it.
2) If exactly one tool is clearly relevant, return **SINGLE**. Do **NOT** return MULTI with only one candidate.
3) Return **MULTI** only when more than one distinct tool appears necessary or plausible.
4) Arguments MUST match each tool's inputSchema (field names & types). Do not invent fields.
5) For required fields with unknown values, provide a safe placeholder that respects the type:
   - string: "placeholder" (or "user@example.com" for emails)
   - number: 0
   - boolean: false
   - object: {{}}
   - array: []
6) If context includes a 'token' and the tool requires it, include it as 'token'.
7) Use only the tools provided below.

STRICT JSON ONLY (no markdown). One of:

SINGLE:
{{
  "type": "single",
  "tool": "<tool_name>",
  "arguments": {{ ... }},
  "confidence": 0.0,
  "reason": "brief justification"
}}

MULTI (unordered candidates, no plan):
{{
  "type": "multi",
  "toolCandidates": [
    {{
      "name": "<tool_name>",
      "suggestedArguments": {{ ... }},
      "note": "why this tool might be needed"
    }}
  ],
  "confidence": 0.0,
  "reason": "brief justification"
}}

USER QUERY:
{json.dumps(query, ensure_ascii=False)}

TOOLS:
{json.dumps([t for t in tools], ensure_ascii=False, indent=2)}

CONTEXT:
{json.dumps(context or {{}}, ensure_ascii=False, indent=2)}
""".strip()


def call_llm(query: str, tools: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    prompt = _prompt(query, tools, context)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a careful, schema-following intent selector."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    raw = resp.choices[0].message.content or ""
    cleaned = _strip_to_json(raw)
    return json.loads(cleaned)