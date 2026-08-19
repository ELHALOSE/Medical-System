"""
embedding.py
------------
Thin wrapper around sentence-transformers so the rest of the package depends
on this interface, not on the library directly.
"""

from __future__ import annotations

from pathlib import Path

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_id: str, cache_dir: str | None = None, batch_size: int = 64):
        self.model_id = model_id
        self.batch_size = batch_size
        if cache_dir:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self._model = SentenceTransformer(model_id, cache_folder=cache_dir)

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str], show_progress: bool = False) -> list[list[float]]:
        """Batch-embed texts. Normalized so cosine similarity == dot product."""
        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
