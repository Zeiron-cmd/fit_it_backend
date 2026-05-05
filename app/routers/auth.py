from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.schemas.auth import UserRegister, UserRead
from app.services.auth_service import hash_password


from app.services.auth_service import verify_password
from fastapi import HTTPException, status
from app.schemas.auth import UserRegister

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=UserRead)
def register_user(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.post("/login")
def login_user(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Неверный email или пароль"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Неверный email или пароль"
        )

    return {
        "message": "Успешный вход",
        "user_id": user.id
    }