"""
vectorstore.py
--------------
Thin wrapper around a persistent Chroma collection. Stores only scalar
metadata (Chroma's constraint) - the full Chunk objects live in memory;
this store just does id <-> vector <-> lightweight-metadata lookups.
"""

from __future__ import annotations

import chromadb

from retrieval.schemas import Chunk


class VectorStore:
    def __init__(self, persist_path: str, collection_name: str):
        self.collection_name = collection_name
        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        """Drop and recreate the collection - use before a full reindex so
        stale chunks from a previous run don't linger."""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"got {len(chunks)} chunks but {len(embeddings)} embeddings")

        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "title": c.title,
                    "page_start": c.page_start,
                    "page_end": c.page_end,
                }
                for c in chunks
            ],
        )

    def query(self, query_embedding: list[float], top_k: int) -> list[str]:
        """Returns chunk_ids ranked by similarity, most similar first."""
        results = self._collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results["ids"][0]

    def count(self) -> int:
        return self._collection.count()
