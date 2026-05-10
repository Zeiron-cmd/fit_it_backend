from urllib.parse import urlencode

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from app.config import get_settings
from app.database import get_session
from app.models.user import User
from app.schemas.auth import OAuthProviderRead, Token, UserLogin, UserRead, UserRegister
from app.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.services.oauth_service import (
    create_token_for_user,
    enabled_oauth_providers,
    fetch_oauth_profile,
    get_oauth_client,
    get_or_create_oauth_user,
)


router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer()
settings = get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить пользователя из токена",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegister,
    session: Session = Depends(get_session),
):
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login_user(
    user_data: UserLogin,
    session: Session = Depends(get_session),
):
    return _authenticate_with_email_and_password(
        email=user_data.email,
        password=user_data.password,
        session=session,
    )


@router.post("/token", response_model=Token)
def issue_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """OAuth2-compatible password grant endpoint for Swagger and mobile clients."""
    return _authenticate_with_email_and_password(
        email=form_data.username,
        password=form_data.password,
        session=session,
    )


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/oauth/providers", response_model=list[OAuthProviderRead])
def list_oauth_providers():
    return enabled_oauth_providers()


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    client = get_oauth_client(provider)
    redirect_uri = f"{settings.BACKEND_PUBLIC_URL}/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback", name="oauth_callback")
async def oauth_callback(
    provider: str,
    request: Request,
    session: Session = Depends(get_session),
):
    client = get_oauth_client(provider)

    try:
        token = await client.authorize_access_token(request)
        profile = await fetch_oauth_profile(provider, client, token)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка OAuth: {exc.error}",
        ) from exc

    user = get_or_create_oauth_user(profile, session)
    token_data = create_token_for_user(user)

    if settings.FRONTEND_OAUTH_REDIRECT_URL:
        query = urlencode(token_data)
        return RedirectResponse(f"{settings.FRONTEND_OAUTH_REDIRECT_URL}?{query}")

    return token_data


def _authenticate_with_email_and_password(
    email: str,
    password: str,
    session: Session,
) -> dict[str, str]:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный email или пароль",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
