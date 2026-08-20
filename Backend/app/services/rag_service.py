import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.answer import AnswerRepository
from app.repositories.chunk import ChunkRepository
from app.schemas.retrieval import RetrievedChunk
from app.services.rag_index_service import (
    build_bm25_index,
    get_query_embedder,
    get_reranker,
    get_vector_store,
    to_retrieval_chunk,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
RETRIEVAL_ROOT = REPO_ROOT / "Retrival"
DEFAULT_CHUNKS_PATH = REPO_ROOT / "output.json"


class RAGService:
    """Coordinates retrieval, generation, evaluation, and answer persistence."""

    def __init__(self, db: Session | None = None):
        self.db = db
        self.answer_repository = AnswerRepository(db) if db else None
        self.chunk_repository = ChunkRepository(db) if db else None

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        user_id: UUID | None = None,
    ) -> list[RetrievedChunk]:
        if self.chunk_repository and user_id:
            return self._retrieve_from_processed_documents(
                query=query,
                top_k=top_k,
                user_id=user_id,
            )
        return self._retrieve_from_offline_index(query=query, top_k=top_k)

    def generate(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        chat_history: list[dict[str, str]] | None = None,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        if not chunks:
            return {
                "query": query,
                "answer": (
                    "No relevant processed medical documents were found for this "
                    "question. Upload and process documents before requesting an "
                    "evidence-grounded answer."
                ),
                "sources": [],
                "evaluation": {"faithfulness_score": 0.0, "relevance_score": 0.0},
                "model_id": None,
                "latency_seconds": 0.0,
            }

        generation_result = _get_generation_pipeline().generate_answer(
            query=query,
            retrieved_chunks=[_chunk_for_generation(chunk) for chunk in chunks],
            chat_history=chat_history,
            temperature=temperature,
        )
        return {
            "query": query,
            "answer": generation_result["answer"],
            "sources": generation_result.get("sources", []),
            "evaluation": generation_result.get("evaluation", {}),
            "model_id": generation_result.get("model_id"),
            "latency_seconds": generation_result.get("latency_seconds"),
        }

    def answer_question(
        self,
        user_id: UUID,
        query: str,
        top_k: int = 5,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        if not self.answer_repository:
            raise RuntimeError("answer_question requires a database session")

        answer_row = self.answer_repository.create_answer(user_id=user_id, question=query)

        try:
            chunks = self.retrieve(query=query, top_k=top_k, user_id=user_id)
            generation_result = self.generate(
                query=query,
                chunks=chunks,
                temperature=temperature,
            )
            self.answer_repository.update_answer(answer_row.id, generation_result["answer"])
        except Exception:
            self.answer_repository.mark_failed(answer_row.id)
            raise

        return {
            "answer_id": str(answer_row.id),
            "retrieved_chunks": chunks,
            **generation_result,
        }

    def _retrieve_from_processed_documents(
        self,
        query: str,
        top_k: int,
        user_id: UUID,
    ) -> list[RetrievedChunk]:
        db_chunks = self.chunk_repository.list_for_user(user_id)
        if not db_chunks:
            return []

        chunk_lookup = {str(chunk.id): chunk for chunk in db_chunks}
        candidate_pool = max(top_k * 4, top_k)
        query_embedding = get_query_embedder().embed_one(query)
        dense_ids = [
            chunk_id
            for chunk_id in get_vector_store().query(query_embedding, top_k=candidate_pool)
            if chunk_id in chunk_lookup
        ]
        bm25_index = build_bm25_index(db_chunks)
        lexical_ids = bm25_index.search(query, top_k=candidate_pool)
        fused_ids = _reciprocal_rank_fusion([dense_ids, lexical_ids], top_k=candidate_pool)
        candidates = [to_retrieval_chunk(chunk_lookup[chunk_id]) for chunk_id in fused_ids]
        reranked = get_reranker().rerank(query, candidates, top_k=top_k)

        return [
            _retrieved_chunk_response(
                db_chunk=chunk_lookup[chunk.chunk_id],
                score=float(score),
            )
            for chunk, score in reranked
        ]

    def _retrieve_from_offline_index(self, query: str, top_k: int) -> list[RetrievedChunk]:
        retriever, _ = _get_retriever()

        try:
            results = retriever.retrieve(query, top_k=top_k)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"RAG index data is not available: {exc}",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Retrieval pipeline failed: {exc}",
            ) from exc

        return [
            RetrievedChunk(
                chunk_id=str(chunk.chunk_id),
                text=chunk.text,
                document_id=None,
                source=chunk.title or None,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                score=float(score),
            )
            for chunk, score in results
        ]


@lru_cache(maxsize=1)
def _get_retriever():
    _ensure_retrieval_import_path()

    from retrieval.config import RetrievalConfig
    from retrieval.pipeline import Retriever
    from retrieval.schemas import load_chunks

    config = RetrievalConfig(
        chroma_path=os.getenv("CHROMA_PATH", str(RETRIEVAL_ROOT / "data" / "chroma_db")),
        bm25_index_path=os.getenv("BM25_INDEX_PATH", str(RETRIEVAL_ROOT / "data" / "bm25_index.pkl")),
        output_path=os.getenv("RETRIEVAL_OUTPUT", str(REPO_ROOT / "retrieval_output.json")),
    )
    chunks_path = Path(os.getenv("RAG_CHUNKS_PATH", str(DEFAULT_CHUNKS_PATH)))
    chunks = load_chunks(chunks_path)
    return Retriever.load(config, chunks), chunks


@lru_cache(maxsize=1)
def _get_generation_pipeline():
    _ensure_repo_import_path()

    from Generation_Evaluation.pipeline import GenerationPipeline

    return GenerationPipeline(model_id=os.getenv(
        "GENERATION_MODEL_ID",
        ),
    hf_token=os.getenv("HF_TOKEN"),
    )


def _ensure_repo_import_path() -> None:
    repo_path = str(REPO_ROOT)
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)


def _ensure_retrieval_import_path() -> None:
    _ensure_repo_import_path()
    retrieval_path = str(RETRIEVAL_ROOT)
    if retrieval_path not in sys.path:
        sys.path.insert(0, retrieval_path)


def _chunk_for_generation(chunk: RetrievedChunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "text": chunk.text,
        "metadata": {
            "source_doc": chunk.source,
            "page_number": chunk.page_start,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
        },
        "score": chunk.score,
    }


def _retrieved_chunk_response(db_chunk, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=str(db_chunk.id),
        document_id=str(db_chunk.document_id),
        text=db_chunk.chunk_text,
        source=db_chunk.document.file_name if db_chunk.document else None,
        page_start=_metadata_int(db_chunk.chunk_metadata, "page_start"),
        page_end=_metadata_int(db_chunk.chunk_metadata, "page_end"),
        score=score,
    )


def _reciprocal_rank_fusion(
    rankings: list[list[str]],
    top_k: int,
    rrf_k: int = 60,
) -> list[str]:
    fused_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking):
            fused_scores[item_id] = fused_scores.get(item_id, 0.0) + 1.0 / (rrf_k + rank + 1)
    return sorted(fused_scores, key=fused_scores.get, reverse=True)[:top_k]


def _metadata_int(metadata: dict | None, key: str) -> int | None:
    if not metadata or metadata.get(key) is None:
        return None
    return int(metadata[key])