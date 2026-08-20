from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.database.models import Chunk


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_document(self, document_id: UUID) -> list[Chunk]:
        return self.db.query(Chunk).filter(Chunk.document_id == document_id).all()

    def replace_document_chunks(self, document_id: UUID, chunks: list[dict]) -> list[Chunk]:
        self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        db_chunks = [
            Chunk(
                document_id=document_id,
                chunk_index=index,
                chunk_text=item["text"],
                chunk_metadata={
                    "source_chunk_id": item.get("chunk_id"),
                    "page_start": item.get("page_start"),
                    "page_end": item.get("page_end"),
                    "title": item.get("title"),
                },
            )
            for index, item in enumerate(chunks, start=1)
        ]
        self.db.add_all(db_chunks)
        self.db.commit()
        for chunk in db_chunks:
            self.db.refresh(chunk)
        return db_chunks

    def list_for_user(self, user_id: UUID) -> list[Chunk]:
        return (
            self.db.query(Chunk)
            .options(joinedload(Chunk.document))
            .filter(Chunk.document.has(uploaded_by=user_id))
            .all()
        )