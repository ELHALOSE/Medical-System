"""
build_index.py
---------------
Run once (and whenever output.json changes) to embed all chunks and build
both indices that HybridSearcher needs at query time.

Usage:
    python -m cli.build_index --chunks-path output.json
"""

from __future__ import annotations

import argparse
import sys

from retrieval.config import RetrievalConfig
from retrieval.embedding import Embedder
from retrieval.schemas import load_chunks
from retrieval.search import BM25Index
from retrieval.vectorstore import VectorStore


def _embedding_text(chunk) -> str:
    """Combine title and text for richer embeddings."""
    if chunk.title:
        return f"{chunk.title}\n{chunk.text}"
    return chunk.text


def build_index(chunks_path: str, config: RetrievalConfig) -> None:
    print(f"[1/4] Loading chunks from {chunks_path}")
    chunks = load_chunks(chunks_path)
    print(f"       {len(chunks)} chunks")

    print(f"[2/4] Embedding with {config.embedding_model_id}")
    embedder = Embedder(config.embedding_model_id, cache_dir=config.model_cache_dir)
    embeddings = embedder.embed([_embedding_text(c) for c in chunks], show_progress=True)

    print(f"[3/4] Indexing into Chroma at {config.chroma_path}")
    vector_store = VectorStore(config.chroma_path, config.collection_name)
    vector_store.reset()
    vector_store.upsert(chunks, embeddings)
    print(f"       {vector_store.count()} vectors indexed")

    print(f"[4/4] Building BM25 index -> {config.bm25_index_path}")
    bm25_index = BM25Index.build(chunks)
    bm25_index.save(config.bm25_index_path)

    print("\nDone. Retriever.load(config, chunks) is ready to use.")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chunks-path",
        required=True,
        help="Path to output.json produced by the chunking pipeline",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    build_index(chunks_path=args.chunks_path, config=RetrievalConfig())
