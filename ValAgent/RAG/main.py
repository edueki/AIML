# rag/main.py
from fastapi import FastAPI, Query
from db import fetch_active_courses
from indexer import build_index
from retriever import semantic_search, compose_answer
from schema import IndexRequest, SearchResponse, SearchResponseItem, AskRequest, AskResponse
import controller

app = FastAPI(title="RAG Service")
app.include_router(controller.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8085, reload=True)
