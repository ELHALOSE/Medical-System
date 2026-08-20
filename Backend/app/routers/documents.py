from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.document import DocumentProcessResponse, DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db)
    return service.upload_document(file=file, user_id=current_user.id)


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db)
    return service.process_document(document_id=document_id, user_id=current_user.id)