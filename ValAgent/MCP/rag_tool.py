
from server import mcp
from server import http_get, http_post
from config import RAG_URL
from typing import Any, Dict
from models import RagAskInput


@mcp.tool(
    name="rag_search",
    description="Perform a RAG vector search over courses and FAQs."
)
async def rag_search(q: str, top_k: int = 8) -> Dict[str, Any]:
    """
    Calls: GET /rag/search?q=<query>&top_k=<top_k>
    """
    url = (
        f"{RAG_URL.rstrip('/')}/rag/search"
        f"?q={q}"
        f"&top_k={top_k}"
    )
    return await http_get(url, headers={"accept": "application/json"})

@mcp.tool(
    name="rag_ask",
    description="Ask the RAG system a question to retrieve relevant courses or FAQ answers."
)
async def rag_ask(askinput: RagAskInput) -> Dict[str, Any]:
    """
    Calls POST /rag/ask with: { query: str, top_k: int }
    Used to retrieve semantic answers from course metadata + FAQs.
    """
    url = f"{RAG_URL.rstrip('/')}/rag/ask"
    payload = {
        "query": askinput.query,
        "top_k": askinput.top_k
    }
    return await http_post(url, headers={"accept": "application/json"}, body=payload, )
