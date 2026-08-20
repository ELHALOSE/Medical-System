from pydantic import BaseModel, Field
from typing import Any


class RetrievalRequest(BaseModel):
    query: str
    filters: dict[str, Any] | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    document_id: str | None = None
    source: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float

class RetrievalResponse(BaseModel):
    chunks: list[RetrievedChunk]
    

class GenerateRequest(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
    chat_history: list[dict[str, str]] | None = None
    temperature: float = Field(default=0.1, ge=0, le=2)

class GenerateResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    model_id: str | None = None
    latency_seconds: float | None = None


class RAGRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.1, ge=0, le=2)


class RAGResponse(GenerateResponse):
    answer_id: str
    retrieved_chunks: list[RetrievedChunk]