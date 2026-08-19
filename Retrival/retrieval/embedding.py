"""
embedding.py
------------
Thin wrapper around sentence-transformers so the rest of the package depends
on this interface, not on the library directly - swapping the embedding
model later means changing one line in config.py, not hunting through the
codebase.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_id: str, batch_size: int = 64):
        self.model_id = model_id
        self.batch_size = batch_size
        self._model = SentenceTransformer(model_id)

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str], show_progress: bool = False) -> list[list[float]]:
        """Batch-embed texts. Normalized so cosine similarity == dot product,
        which is what the vector store's distance metric assumes."""
        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
