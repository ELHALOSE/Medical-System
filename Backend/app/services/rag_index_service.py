# import os
# import sys
# from functools import lru_cache
# from pathlib import Path

# from app.database.models import Chunk as DBChunk


# REPO_ROOT = Path(__file__).resolve().parents[3]
# RETRIEVAL_ROOT = REPO_ROOT / "Retrival"
# API_CHROMA_PATH = os.getenv(
#     "RAG_CHROMA_PATH",
#     str(REPO_ROOT / "Backend" / "vector_db" / "chroma"),
# )
# API_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "medical_documents")
# RAG_DEVICE = os.getenv("RAG_DEVICE", "cpu")


# class RAGIndexService:
#     """Embeds processed chunks and stores their vectors in the API vector DB."""

#     def upsert_chunks(self, chunks: list[DBChunk]) -> None:
#         if not chunks:
#             return

#         retrieval_chunks = [_to_retrieval_chunk(chunk) for chunk in chunks]
#         embeddings = _get_embedder().embed(
#             [_embedding_text(chunk) for chunk in retrieval_chunks],
#             show_progress=False,
#         )
#         _get_vector_store().upsert(retrieval_chunks, embeddings)

#     def delete_chunks(self, chunk_ids: list[str]) -> None:
#         if chunk_ids:
#             _get_vector_store().delete(chunk_ids)


# def build_bm25_index(chunks: list[DBChunk]):
#     retrieval_chunks = [_to_retrieval_chunk(chunk) for chunk in chunks]
#     return _get_bm25_class().build(retrieval_chunks)


# def get_query_embedder():
#     return _get_embedder()


# def get_reranker():
#     return _get_reranker()


# def get_vector_store():
#     return _get_vector_store()


# def to_retrieval_chunk(chunk: DBChunk):
#     return _to_retrieval_chunk(chunk)


# @lru_cache(maxsize=1)
# def _get_embedder():
#     _ensure_retrieval_import_path()

#     from retrieval.config import RetrievalConfig
#     from retrieval.embedding import Embedder

#     config = RetrievalConfig()
#     return Embedder(
#         config.embedding_model_id,
#         cache_dir=config.model_cache_dir,
#         device=RAG_DEVICE,
#     )


# @lru_cache(maxsize=1)
# def _get_reranker():
#     _ensure_retrieval_import_path()

#     from retrieval.config import RetrievalConfig
#     from retrieval.reranker import Reranker

#     config = RetrievalConfig()
#     return Reranker(
#         config.reranker_model_id,
#         cache_dir=config.model_cache_dir,
#         device=RAG_DEVICE,
#     )


# @lru_cache(maxsize=1)
# def _get_vector_store():
#     _ensure_retrieval_import_path()

#     from retrieval.vectorstore import VectorStore

#     return VectorStore(API_CHROMA_PATH, API_COLLECTION_NAME)


# @lru_cache(maxsize=1)
# def _get_bm25_class():
#     _ensure_retrieval_import_path()

#     from retrieval.search import BM25Index

#     return BM25Index


# def _ensure_retrieval_import_path() -> None:
#     repo_path = str(REPO_ROOT)
#     if repo_path not in sys.path:
#         sys.path.insert(0, repo_path)
#     retrieval_path = str(RETRIEVAL_ROOT)
#     if retrieval_path not in sys.path:
#         sys.path.insert(0, retrieval_path)


# def _to_retrieval_chunk(chunk: DBChunk):
#     _ensure_retrieval_import_path()

#     from retrieval.schemas import Chunk

#     metadata = chunk.chunk_metadata or {}
#     return Chunk(
#         chunk_id=str(chunk.id),
#         text=chunk.chunk_text,
#         title=metadata.get("title") or "",
#         page_start=metadata.get("page_start") or 0,
#         page_end=metadata.get("page_end") or 0,
#     )


# def _embedding_text(chunk) -> str:
#     if chunk.title:
#         return f"{chunk.title}\n{chunk.text}"
#     return chunk.text

import os
import sys
from functools import lru_cache
from pathlib import Path

from app.database.models import Chunk as DBChunk


REPO_ROOT = Path(__file__).resolve().parents[3]

RETRIEVAL_ROOT = REPO_ROOT / "Retrival"

API_CHROMA_PATH = os.getenv(
    "RAG_CHROMA_PATH",
    str(REPO_ROOT / "Backend" / "vector_db" / "chroma"),
)

API_COLLECTION_NAME = os.getenv(
    "RAG_COLLECTION_NAME",
    "medical_documents",
)

RAG_DEVICE = os.getenv(
    "RAG_DEVICE",
    "cpu",
)


class RAGIndexService:
    """Embeds processed chunks and stores their vectors."""

    def upsert_chunks(
        self,
        chunks: list[DBChunk],
    ) -> None:

        if not chunks:
            return

        retrieval_chunks = [
            _to_retrieval_chunk(chunk)
            for chunk in chunks
        ]

        texts = [
            _embedding_text(chunk)
            for chunk in retrieval_chunks
        ]

        embeddings = _get_embedder().embed(
            texts,
            show_progress=False,
        )

        _get_vector_store().upsert(
            retrieval_chunks,
            embeddings,
        )

    def delete_chunks(
        self,
        chunk_ids: list[str],
    ) -> None:

        if not chunk_ids:
            return

        _get_vector_store().delete(
            chunk_ids
        )


def build_bm25_index(
    chunks: list[DBChunk],
):
    retrieval_chunks = [
        _to_retrieval_chunk(chunk)
        for chunk in chunks
    ]

    return _get_bm25_class().build(
        retrieval_chunks
    )


def get_query_embedder():
    return _get_embedder()


def get_reranker():
    return _get_reranker()


def get_vector_store():
    return _get_vector_store()


def to_retrieval_chunk(
    chunk: DBChunk,
):
    return _to_retrieval_chunk(chunk)


@lru_cache(maxsize=1)
def _get_embedder():

    _ensure_retrieval_import_path()

    from retrieval.config import RetrievalConfig
    from retrieval.embedding import Embedder

    config = RetrievalConfig()

    return Embedder(
        config.embedding_model_id,
        cache_dir=config.model_cache_dir,
        device=RAG_DEVICE,
    )


@lru_cache(maxsize=1)
def _get_reranker():

    _ensure_retrieval_import_path()

    from retrieval.config import RetrievalConfig
    from retrieval.reranker import Reranker

    config = RetrievalConfig()

    return Reranker(
        config.reranker_model_id,
        cache_dir=config.model_cache_dir,
        device=RAG_DEVICE,
    )


@lru_cache(maxsize=1)
def _get_vector_store():

    _ensure_retrieval_import_path()

    from retrieval.vectorstore import VectorStore

    return VectorStore(
        API_CHROMA_PATH,
        API_COLLECTION_NAME,
    )


@lru_cache(maxsize=1)
def _get_bm25_class():

    _ensure_retrieval_import_path()

    from retrieval.search import BM25Index

    return BM25Index


def _ensure_retrieval_import_path():

    repo_path = str(REPO_ROOT)

    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)

    retrieval_path = str(RETRIEVAL_ROOT)

    if retrieval_path not in sys.path:
        sys.path.insert(0, retrieval_path)


def _to_retrieval_chunk(
    chunk: DBChunk,
):

    _ensure_retrieval_import_path()

    from retrieval.schemas import Chunk

    metadata = chunk.chunk_metadata or {}

    return Chunk(
        chunk_id=str(chunk.id),
        text=chunk.chunk_text,
        title=metadata.get("title") or "",
        page_start=metadata.get("page_start") or 0,
        page_end=metadata.get("page_end") or 0,
    )


def _embedding_text(chunk) -> str:

    if chunk.title:
        return f"{chunk.title}\n{chunk.text}"

    return chunk.text