from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models import RetrievalResult
from app.schemas.retrieval import RetrievedChunk


class RetrievalResultRepository:
    """Persists the chunks selected as evidence for an answer."""

    def __init__(self, db: Session):
        self.db = db

    def create_for_answer(self, answer_id: UUID, chunks: Sequence[RetrievedChunk] ) -> list[RetrievalResult]:
        retrieval_results = [
                            RetrievalResult(
                                answer_id=answer_id,
                                chunk_id=UUID(chunk.chunk_id),
                                rank=rank,
                                rerank_score=chunk.score,
                            )
                            for rank, chunk in enumerate(chunks, start=1)
        ]

        if not retrieval_results:
            return []

        self.db.add_all(retrieval_results)
        self.db.commit()
        for result in retrieval_results:
            self.db.refresh(result)
        return retrieval_results