# rag/main.py
from fastapi import FastAPI, APIRouter, Query
from db import fetch_active_courses
from indexer import build_index
from retriever import semantic_search, compose_answer
from schema import IndexRequest, SearchResponse, SearchResponseItem, AskRequest, AskResponse

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/index")
def rag_index(payload: IndexRequest):
    courses = fetch_active_courses()
    stats = build_index(courses, wipe=payload.rebuild, persist_dir="./.chroma")
    return {"ok": True, "stats": stats}

@router.get("/search", response_model=SearchResponse)
def search(q: str = Query(...), top_k: int = Query(8, ge=1, le=50)):
    items = semantic_search(q, top_k=top_k, persist_dir="./.chroma")
    return SearchResponse(query=q, items=[SearchResponseItem(**it) for it in items])

@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    items = semantic_search(payload.query, top_k=payload.top_k, persist_dir="./.chroma")
    answer = compose_answer(payload.query, items)
    return AskResponse(answer=answer, sources=[SearchResponseItem(**it) for it in items])