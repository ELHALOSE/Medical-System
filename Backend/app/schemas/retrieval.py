from uuid import UUID

from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    filters: dict | None = None
    top_k: int = 5


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    text: str
    document_id: UUID
    source: str | None = None
    score: float


class RetrievalResponse(BaseModel):
    chunks: list[RetrievedChunk]
    

class RAGRequest(BaseModel):
    query: str
    chunks: list[RetrievedChunk]


class RAGResponse(BaseModel):
    answer: str
    used_sources: list[str]

