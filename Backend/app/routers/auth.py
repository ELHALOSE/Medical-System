from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)



@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(user)
    return user

@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token = service.login(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me",response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user