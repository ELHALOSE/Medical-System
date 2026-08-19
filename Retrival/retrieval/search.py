"""
search.py
---------
Hybrid search: dense (VectorStore) + lexical (BM25), combined with
Reciprocal Rank Fusion (RRF). Dense embeddings alone tend to miss exact
drug-class acronyms (ACEi, ARB, BB, CCB) that BM25 catches reliably, which
matters a lot for a pharmacological guideline.

`reciprocal_rank_fusion` is a pure function (rankings in, fused ranking
out) deliberately kept independent of any model or index, so it's fast to
unit test - see tests/test_search_fusion.py.
"""

from __future__ import annotations

import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from retrieval.embedding import Embedder
from retrieval.schemas import Chunk
from retrieval.vectorstore import VectorStore


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Index:
    """Lexical index over chunk text. Cheap enough to rebuild, but
    save/load is provided so `scripts/build_index.py` only pays that cost
    once per reindex, not once per query-CLI session."""

    def __init__(self, chunk_ids: list[str], index: BM25Okapi):
        self.chunk_ids = chunk_ids
        self._index = index

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "BM25Index":
        tokenized_corpus = [_tokenize(c.text) for c in chunks]
        return cls(chunk_ids=[c.chunk_id for c in chunks], index=BM25Okapi(tokenized_corpus))

    def search(self, query: str, top_k: int) -> list[str]:
        scores = self._index.get_scores(_tokenize(query))
        top_positions = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.chunk_ids[i] for i in top_positions]

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"chunk_ids": self.chunk_ids, "index": self._index}, f)

    @classmethod
    def load(cls, path: str | Path) -> "BM25Index":
        with open(path, "rb") as f:
            data = pickle.load(f)
        return cls(chunk_ids=data["chunk_ids"], index=data["index"])


def reciprocal_rank_fusion(
    rankings: list[list[str]], top_k: int, rrf_k: int = 60
) -> list[str]:
    """
    Fuse N ranked id lists into one. RRF only needs each ranking's
    *position*, not comparable scores, which is what makes it a robust way
    to combine dense similarity and BM25 scores that live on totally
    different scales.

    score(id) = sum over rankings of 1 / (rrf_k + rank_in_that_ranking + 1)
    """
    fused_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking):
            fused_scores[item_id] = fused_scores.get(item_id, 0.0) + 1.0 / (rrf_k + rank + 1)

    return sorted(fused_scores, key=fused_scores.get, reverse=True)[:top_k]


class HybridSearcher:
    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedder: Embedder,
        chunk_lookup: dict[str, Chunk],
        rrf_k: int = 60,
    ):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedder
        self.chunk_lookup = chunk_lookup
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int) -> list[Chunk]:
        query_embedding = self.embedder.embed_one(query)
        dense_ids = self.vector_store.query(query_embedding, top_k=top_k)
        lexical_ids = self.bm25_index.search(query, top_k=top_k)

        fused_ids = reciprocal_rank_fusion([dense_ids, lexical_ids], top_k=top_k, rrf_k=self.rrf_k)
        return [self.chunk_lookup[chunk_id] for chunk_id in fused_ids]
