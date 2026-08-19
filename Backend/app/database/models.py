import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ============================================================
# 1. User
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    )
    

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'user'"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        back_populates="uploader",
    )

    answers: Mapped[list["Answer"]] = relationship(
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


# ============================================================
# 2. Document
# ============================================================

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    uploader: Mapped["User"] = relationship(
        back_populates="documents",
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_documents_uploaded_by",
            "uploaded_by",
        ),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, file_name={self.file_name})>"



# ============================================================
# 3. Chunk
# ============================================================
class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,)

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
    "text",
    Text,
    nullable=False,
    )

    chunk_metadata: Mapped[dict | None] = mapped_column(
    "metadata",
    JSONB,
    nullable=True,
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        back_populates="chunks",
    )

    retrieval_results: Mapped[list["RetrievalResult"]] = relationship(
        back_populates="chunk",
    )

    __table_args__ = (
        Index(
            "idx_chunks_document_id",
            "document_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Chunk("
            f"id={self.id}, "
            f"document_id={self.document_id}, "
            f"chunk_index={self.chunk_index}"
            f")>"
        )
# ============================================================
# 4. Answer
# ============================================================

class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'pending'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="answers",
    )

    retrieval_results: Mapped[list["RetrievalResult"]] = relationship(
        back_populates="answer",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_answers_user_id",
            "user_id",
        ),
    )

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question={self.question})>"


# ============================================================
# 5. Retrieval Result
# ============================================================

class RetrievalResult(Base):
    __tablename__ = "retrieval_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id"),
        nullable=False,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    similarity_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    rerank_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    answer: Mapped["Answer"] = relationship(
        back_populates="retrieval_results",
    )

    chunk: Mapped["Chunk"] = relationship(
        back_populates="retrieval_results",
    )

    def __repr__(self) -> str:
        return f"<RetrievalResult(id={self.id}, answer_id={self.answer_id}, chunk_id={self.chunk_id})>"

    __table_args__ = (
        Index(
            "idx_retrieval_results_answer_id",
            "answer_id",
        ),
        Index(
            "idx_retrieval_results_chunk_id",
            "chunk_id",
        ),
    )