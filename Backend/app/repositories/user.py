from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User



class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password_hash: str, role: str = "user") -> User:
        new_user = User(email=email, password_hash=password_hash, role=role)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()