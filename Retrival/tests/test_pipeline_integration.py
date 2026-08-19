"""
Integration test for the full Embedding -> VectorDB -> Search -> Reranker
path with real models. Downloads model weights and is slow, so it's
excluded from the default test run.

Run explicitly with:
    pytest tests/test_pipeline_integration.py -m integration
"""

import pytest

from retrieval.config import RetrievalConfig
from retrieval.embedding import Embedder
from retrieval.reranker import Reranker
from retrieval.search import BM25Index, HybridSearcher
from retrieval.vectorstore import VectorStore

pytestmark = pytest.mark.integration


def test_end_to_end_retrieve(sample_chunks, tmp_path):
    config = RetrievalConfig(
        chroma_path=str(tmp_path / "chroma_db"),
        collection_name="test_collection",
        bm25_index_path=str(tmp_path / "bm25.pkl"),
    )

    embedder = Embedder(config.embedding_model_id)
    embeddings = embedder.embed([c.contextualized_text for c in sample_chunks])

    vector_store = VectorStore(config.chroma_path, config.collection_name)
    vector_store.upsert(sample_chunks, embeddings)

    bm25_index = BM25Index.build(sample_chunks)
    chunk_lookup = {c.chunk_id: c for c in sample_chunks}

    searcher = HybridSearcher(vector_store, bm25_index, embedder, chunk_lookup)
    reranker = Reranker(config.reranker_model_id)

    candidates = searcher.search("what blood pressure threshold starts treatment?", top_k=3)
    results = reranker.rerank("what blood pressure threshold starts treatment?", candidates, top_k=1)

    assert results[0][0].chunk_id == "doc::0000"
