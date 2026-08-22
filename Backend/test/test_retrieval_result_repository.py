import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.repositories.retrieval_result import RetrievalResultRepository
from app.schemas.retrieval import RetrievedChunk


class FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.refreshed = []

    def add_all(self, items):
        self.added.extend(items)

    def commit(self):
        self.commits += 1

    def refresh(self, item):
        self.refreshed.append(item)


class RetrievalResultRepositoryTests(unittest.TestCase):
    def test_create_for_answer_records_rank_and_rerank_score(self):
        db = FakeSession()
        answer_id = uuid4()
        first_chunk_id = uuid4()
        second_chunk_id = uuid4()
        chunks = [
            RetrievedChunk(chunk_id=str(first_chunk_id), text="First", score=0.95),
            RetrievedChunk(chunk_id=str(second_chunk_id), text="Second", score=0.82),
        ]

        results = RetrievalResultRepository(db).create_for_answer(answer_id, chunks)

        self.assertEqual([result.answer_id for result in results], [answer_id, answer_id])
        self.assertEqual([result.chunk_id for result in results], [first_chunk_id, second_chunk_id])
        self.assertEqual([result.rank for result in results], [1, 2])
        self.assertEqual([result.rerank_score for result in results], [0.95, 0.82])
        self.assertEqual(db.commits, 1)
        self.assertEqual(db.refreshed, results)

    def test_create_for_answer_does_not_commit_when_no_chunks_are_retrieved(self):
        db = FakeSession()

        results = RetrievalResultRepository(db).create_for_answer(uuid4(), [])

        self.assertEqual(results, [])
        self.assertEqual(db.commits, 0)


if __name__ == "__main__":
    unittest.main()