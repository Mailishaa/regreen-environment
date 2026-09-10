
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import LoginRequest, UserCreate, UserOut, Token
from app.services.auth_service import authenticate, register
from app.routes.deps import current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    _, token = authenticate(db, data.email, data.password)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return register(db, data)


@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user

