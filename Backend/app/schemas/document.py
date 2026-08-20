from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: UUID
    uploaded_by: UUID
    file_name: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessResponse(BaseModel):
    document: DocumentResponse
    chunk_count: int
    page_count: int
    table_count: int