from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.security import verify_password
from app.crud.user import (
    create_user,
    get_user_by_username,
    get_user_by_email,
)
from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import (
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    return create_user(db, user)


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = get_user_by_username(
        db,
        form_data.username,
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not verify_password(
        form_data.password,
        db_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {"sub": db_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }