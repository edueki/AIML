# rag/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class IndexRequest(BaseModel):
    rebuild: bool = True  # wipe before reindex

class SearchResponseItem(BaseModel):
    course_id: int
    slug: str
    title: str
    score: float
    snippet: str

class SearchResponse(BaseModel):
    query: str
    items: List[SearchResponseItem]

class AskRequest(BaseModel):
    query: str
    top_k: int = 6

class AskResponse(BaseModel):
    answer: str
    sources: List[SearchResponseItem]
    