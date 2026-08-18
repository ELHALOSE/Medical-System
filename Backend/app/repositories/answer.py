from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Answer


class AnswerRepository:
    def __init__(self, db:Session):
        self.db = db

    def create_answer(self, user_id: UUID, question: str) -> Answer:
        new_answer = Answer(user_id=user_id, question=question)
        self.db.add(new_answer)
        self.db.commit()
        self.db.refresh(new_answer)
        return new_answer


    def get_by_id(self, answer_id: UUID) -> Answer | None:
        return self.db.query(Answer).filter(Answer.id == answer_id).first()

    def update_answer(self, answer_id: UUID, answer_text: str) -> Answer :
        answer = self.get_by_id(answer_id)
        if answer:
            answer.answer = answer_text
            answer.status = "answered"
            self.db.commit()
            self.db.refresh(answer)
        return answer
    
    def mark_failed(self, answer_id: UUID) -> Answer:
        answer = self.get_by_id(answer_id)
        if answer:
            answer.status = "failed"
            self.db.commit()
            self.db.refresh(answer)
        return answer