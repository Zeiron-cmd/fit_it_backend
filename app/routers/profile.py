from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/me", response_model=ProfileRead)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = session.exec(statement).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль ещё не создан"
        )

    return profile


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = session.exec(statement).first()

    if profile is None:
        profile = UserProfile(user_id=current_user.id)
        session.add(profile)

    update_data = profile_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile