# rag/indexer.py
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

def _chunks_for_course(c: Dict) -> List[Dict]:
    chunks = []
    base = f"{c['title']}\n\n{(c.get('short_desc') or '').strip()}".strip()
    chunks.append({"text": base, "chunk": 0})
    long_desc = (c.get("long_desc") or "").strip()
    if long_desc:
        parts = [p.strip() for p in long_desc.split("\n") if p.strip()]
        for i, p in enumerate(parts, start=1):
            chunks.append({"text": p, "chunk": i})
    return chunks

def build_index(courses: List[Dict], wipe: bool = True, persist_dir: str = "./.chroma"):
    col = get_collection(persist_dir)
    if wipe:
        try:
            col.delete(where={"doc_type": "course"})
        except Exception:
            pass

    embed = get_embedder()
    docs, ids, metas = [], [], []
    for c in courses:
        for ch in _chunks_for_course(c):
            ids.append(f"course:{int(c['id'])}:{ch['chunk']}")
            docs.append(ch["text"])
            metas.append({
                "doc_type": "course",
                "course_id": int(c["id"]),
                "slug": c["slug"],
                "title": c["title"],
                "price_cents": int(c["price_cents"]),
                "chunk": ch["chunk"],
            })
    if docs:
        vecs = embed.encode(docs, normalize_embeddings=True).tolist()
        col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vecs)
    return {"indexed_courses": len(courses), "indexed_chunks": len(docs)}
