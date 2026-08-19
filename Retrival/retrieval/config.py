"""
config.py
---------
All tunable knobs for the retrieval stage in one place, overridable via
environment variables so the same code runs unchanged in a notebook, a CI
test, and whatever the rest of the team wires up around it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


@dataclass(frozen=True)
class RetrievalConfig:
    # --- Model cache (download once, reuse forever) ---
    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./models")

    # --- Embedding ---
    embedding_model_id: str = os.getenv(
        "EMBEDDING_MODEL_ID", "NeuML/pubmedbert-base-embeddings"
    )

    # --- VectorDB (Chroma) ---
    chroma_path: str = os.getenv("CHROMA_PATH", "./data/chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "hypertension_guideline")

    # --- Search (BM25 + RRF fusion) ---
    bm25_index_path: str = os.getenv("BM25_INDEX_PATH", "./data/bm25_index.pkl")
    rrf_k: int = _env_int("RRF_K", 60)
    candidate_pool: int = _env_int("CANDIDATE_POOL", 20)

    # --- Reranker ---
    reranker_model_id: str = os.getenv("RERANKER_MODEL_ID", "BAAI/bge-reranker-v2-m3")

    # --- Output ---
    top_k: int = _env_int("TOP_K", 5)
    output_path: str = os.getenv("RETRIEVAL_OUTPUT", "./retrieval_output.json")


DEFAULT_CONFIG = RetrievalConfig()
