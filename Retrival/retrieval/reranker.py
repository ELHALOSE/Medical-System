"""
reranker.py
-----------
Cross-encoder reranker: scores (query, chunk) pairs jointly, which is far
more precise than bi-encoder similarity but too slow to run over a whole
corpus - so it only ever sees the hybrid search shortlist, never the full
collection.
"""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from retrieval.schemas import Chunk


class Reranker:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self._model = CrossEncoder(model_id)

    def rerank(self, query: str, candidates: list[Chunk], top_k: int) -> list[tuple[Chunk, float]]:
        if not candidates:
            return []

        pairs = [(query, c.text) for c in candidates]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return ranked[:top_k]
