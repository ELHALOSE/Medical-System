from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.retrieval import (
    GenerateRequest,
    GenerateResponse,
    RAGRequest,
    RAGResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)
    chunks = service.retrieve(
        query=request.query,
        top_k=request.top_k,
        user_id=current_user.id,
    )
    return RetrievalResponse(chunks=chunks)


@router.post("/generate", response_model=GenerateResponse)
def generate_answer(request: GenerateRequest):
    service = RAGService()
    return service.generate(
        query=request.query,
        chunks=request.chunks,
        chat_history=request.chat_history,
        temperature=request.temperature,
    )


@router.post("/answer", response_model=RAGResponse)
def answer_question(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)
    return service.answer_question(
        user_id=current_user.id,
        query=request.query,
        top_k=request.top_k,
        temperature=request.temperature,
    )