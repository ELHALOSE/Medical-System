from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer_id: UUID
    question: str
    answer: str