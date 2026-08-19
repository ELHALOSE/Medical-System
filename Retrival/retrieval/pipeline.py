"""
pipeline.py
-----------
`Retriever` is the single integration point for the rest of the team:
whoever owns prompting/generation should only ever need

    retriever = Retriever.load(config, chunks)
    results = retriever.retrieve(query)   # -> list[(Chunk, score)]

everything upstream of that (embedding model choice, Chroma vs. another
vector store, BM25 fusion details, which reranker) is this module's
implementation detail and can change without touching their code.
"""

from __future__ import annotations

from retrieval.config import RetrievalConfig
from retrieval.embedding import Embedder
from retrieval.reranker import Reranker
from retrieval.schemas import Chunk
from retrieval.search import BM25Index, HybridSearcher
from retrieval.vectorstore import VectorStore


class Retriever:
    def __init__(
        self,
        config: RetrievalConfig,
        embedder: Embedder,
        searcher: HybridSearcher,
        reranker: Reranker,
    ):
        self.config = config
        self.embedder = embedder
        self.searcher = searcher
        self.reranker = reranker

    @classmethod
    def load(cls, config: RetrievalConfig, chunks: list[Chunk]) -> "Retriever":
        """
        Load a Retriever against an *already-built* index (see
        scripts/build_index.py). Fast - no embedding happens here, only
        model loading and index reads.
        """
        embedder = Embedder(config.embedding_model_id)
        vector_store = VectorStore(config.chroma_path, config.collection_name)
        bm25_index = BM25Index.load(config.bm25_index_path)
        chunk_lookup = {c.chunk_id: c for c in chunks}

        searcher = HybridSearcher(
            vector_store=vector_store,
            bm25_index=bm25_index,
            embedder=embedder,
            chunk_lookup=chunk_lookup,
            rrf_k=config.rrf_k,
        )
        reranker = Reranker(config.reranker_model_id)

        return cls(config=config, embedder=embedder, searcher=searcher, reranker=reranker)

    def retrieve(self, query: str, top_k: int | None = None) -> list[tuple[Chunk, float]]:
        """Hybrid search shortlist -> cross-encoder rerank -> top_k results."""
        top_k = top_k or self.config.top_k
        candidates = self.searcher.search(query, top_k=self.config.candidate_pool)
        return self.reranker.rerank(query, candidates, top_k=top_k)
