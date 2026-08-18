from sqlalchemy.orm import Session

from app.config.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserLogin
from fastapi import HTTPException, status


class AuthService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register(self, data: UserCreate):

        existing_user = self.user_repository.get_by_email(
            data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        password_hash = hash_password(data.password)

        return self.user_repository.create_user(
            email=data.email,
            password_hash=password_hash,
        )
        

    def login(self, data: UserLogin):

        user = self.user_repository.get_by_email(
            data.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
            }
        )

        return access_token