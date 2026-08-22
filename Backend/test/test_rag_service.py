import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.retrieval import RetrievedChunk
from app.services.rag_service import RAGService


class RAGServiceTests(unittest.TestCase):
    def test_answer_question_persists_retrieved_chunks(self):
        answer_id = uuid4()
        chunks = [
            RetrievedChunk(
                chunk_id=str(uuid4()),
                text="Evidence",
                score=0.98,
            )
        ]
        answer_repository = Mock()
        answer_repository.create_answer.return_value = SimpleNamespace(id=answer_id)
        retrieval_result_repository = Mock()

        service = object.__new__(RAGService)
        service.answer_repository = answer_repository
        service.retrieval_result_repository = retrieval_result_repository
        service.retrieve = Mock(return_value=chunks)
        service.generate = Mock(return_value={"answer": "Generated answer"})

        result = service.answer_question(user_id=uuid4(), query="Question")

        retrieval_result_repository.create_for_answer.assert_called_once_with(
            answer_id=answer_id,
            chunks=chunks,
        )
        answer_repository.update_answer.assert_called_once_with(
            answer_id, "Generated answer"
        )
        self.assertEqual(result["answer_id"], str(answer_id))


if __name__ == "__main__":
    unittest.main()