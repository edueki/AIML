# rag/retriever.py
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict

_EMBED = None
def get_embedder():
    global _EMBED
    if _EMBED is None:
        _EMBED = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _EMBED

def get_collection(path: str = "./.chroma", name: str = "courses"):
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

def semantic_search(query: str, top_k: int = 8, persist_dir: str = "./.chroma"):
    col = get_collection(persist_dir)
    embed = get_embedder()
    qvec = embed.encode([query], normalize_embeddings=True).tolist()
    res = col.query(query_embeddings=qvec, n_results=top_k, where={"doc_type": "course"})
    items = []
    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0] if "distances" in res else [None] * len(ids)
    for i in range(len(ids)):
        meta = metas[i]
        doc = docs[i]
        dist = dists[i]
        score = 1.0 - float(dist) if dist is not None else 0.0
        items.append({
            "course_id": int(meta["course_id"]),
            "slug": meta["slug"],
            "title": meta["title"],
            "score": round(score, 4),
            "snippet": doc[:300],
        })
    return items

def compose_answer(query: str, items: List[Dict], max_items: int = 3) -> str:
    if not items:
        return "I couldn't find any relevant courses."
    lines = [f"- {it['title']} (ID {it['course_id']}) — {it['snippet']}" for it in items[:max_items]]
    return "Here are relevant courses I found:\n" + "\n".join(lines)
