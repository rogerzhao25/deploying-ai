# 05_src/assignment_chat/services/semantic_service.py

"""
Service 2: Semantic Search (CSV + Embeddings + Chroma Persistent DB)

Pipeline:
CSV dataset -> embeddings -> Chroma persistent storage -> similarity search

Used for:
- "Nearby attractions"
- "Transit tips"
- "What to do in Toronto?"
- Planner tool (Service 3)

This uses Chroma PersistentClient (file persistence), NOT SQLite.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import os
import pandas as pd
import chromadb
from chromadb.config import Settings

from assignment_chat.core.config import (
    CSV_PATH,
    CHROMA_DIR,
    COLLECTION_NAME,
)
from assignment_chat.core.llm import embed


# --------------------------------------------------
# 1. Get or create persistent Chroma collection
# --------------------------------------------------
def get_collection():
    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# --------------------------------------------------
# 2. Build / rebuild vector DB from CSV
# --------------------------------------------------
def build_chroma_from_csv(force_rebuild: bool = False) -> str:
    """
    Reads toronto_travel_tips.csv and ingests into Chroma.
    Run once before chatting.
    """
    if not os.path.exists(CSV_PATH):
        return f"CSV not found at {CSV_PATH}"

    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

    if force_rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    df = pd.read_csv(CSV_PATH)

    if "text" not in df.columns:
        return "CSV must contain a 'text' column for embeddings."

    ids = df["id"].astype(str).tolist()
    documents = df["text"].astype(str).tolist()

    batch_size = 64
    total = len(documents)

    for i in range(0, total, batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]

        vectors = embed(batch_docs)

        metas: List[Dict] = []
        for _, row in df.iloc[i:i + batch_size].iterrows():
            metas.append({
                "name": str(row.get("name", "")),
                "category": str(row.get("category", "")),
                "neighborhood": str(row.get("neighborhood", "")),
                "transit": str(row.get("transit", "")),
                "price_level": str(row.get("price_level", "")),
                "duration_hours": str(row.get("duration_hours", "")),
                "best_for": str(row.get("best_for", "")),
                "highlights": str(row.get("highlights", "")),
                "tips": str(row.get("tips", "")),
            })

        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            embeddings=vectors,
            metadatas=metas,
        )

    return f"Chroma DB ready: {total} rows indexed."


# --------------------------------------------------
# 3. Semantic search
# --------------------------------------------------
def semantic_search(query: str, k: int = 5) -> List[Tuple[str, Dict]]:
    """
    Returns top-k results as:
    [
        (document_text, metadata_dict),
        ...
    ]
    """
    collection = get_collection()

    query_vector = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances", "ids"],
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output: List[Tuple[str, Dict]] = []

    for doc, meta, _id, dist in zip(docs, metas, ids, distances):
        meta = dict(meta or {})
        meta["id"] = _id
        meta["distance"] = dist
        output.append((doc, meta))

    return output