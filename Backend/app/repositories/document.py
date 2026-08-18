from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, file_name: str, uploaded_by: UUID) -> Document:
        new_document = Document(file_name=file_name, uploaded_by=uploaded_by)
        self.db.add(new_document)
        self.db.commit()
        self.db.refresh(new_document)
        return new_document

    def get_by_id(self, document_id: UUID) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_user(self, user_id: UUID) -> list[Document]:
        return self.db.query(Document).filter(Document.uploaded_by == user_id).all()