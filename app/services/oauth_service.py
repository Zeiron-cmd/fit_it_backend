from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.config import get_settings
from app.models.user import User
from app.services.auth_service import create_access_token


settings = get_settings()
oauth = OAuth()


OAUTH_PROVIDERS = ("google", "github", "yandex")


def configure_oauth_clients() -> None:
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
        oauth.register(
            name="github",
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url="https://github.com/login/oauth/access_token",
            api_base_url="https://api.github.com/",
            client_kwargs={"scope": "read:user user:email"},
        )

    if settings.YANDEX_CLIENT_ID and settings.YANDEX_CLIENT_SECRET:
        oauth.register(
            name="yandex",
            client_id=settings.YANDEX_CLIENT_ID,
            client_secret=settings.YANDEX_CLIENT_SECRET,
            authorize_url="https://oauth.yandex.com/authorize",
            access_token_url="https://oauth.yandex.com/token",
            api_base_url="https://login.yandex.ru/",
            client_kwargs={"scope": "login:email login:info"},
        )


def enabled_oauth_providers() -> list[dict[str, bool | str]]:
    return [
        {"provider": "google", "enabled": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)},
        {"provider": "github", "enabled": bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)},
        {"provider": "yandex", "enabled": bool(settings.YANDEX_CLIENT_ID and settings.YANDEX_CLIENT_SECRET)},
    ]


def get_oauth_client(provider: str):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth-провайдер не поддерживается",
        )

    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth-провайдер не настроен в переменных окружения",
        )

    return client


async def fetch_oauth_profile(provider: str, client, token: dict[str, Any]) -> dict[str, Any]:
    if provider == "google":
        userinfo = token.get("userinfo")
        if userinfo is None:
            userinfo = await client.userinfo(token=token)

        return {
            "provider": provider,
            "subject": str(userinfo.get("sub")),
            "email": userinfo.get("email"),
            "full_name": userinfo.get("name"),
            "avatar_url": userinfo.get("picture"),
        }

    if provider == "github":
        response = await client.get("user", token=token)
        data = response.json()
        email = data.get("email")

        if not email:
            emails_response = await client.get("user/emails", token=token)
            emails = emails_response.json()
            primary_email = next(
                (
                    item.get("email")
                    for item in emails
                    if item.get("primary") and item.get("verified")
                ),
                None,
            )
            email = primary_email or (emails[0].get("email") if emails else None)

        return {
            "provider": provider,
            "subject": str(data.get("id")),
            "email": email,
            "full_name": data.get("name") or data.get("login"),
            "avatar_url": data.get("avatar_url"),
        }

    if provider == "yandex":
        response = await client.get("info?format=json", token=token)
        data = response.json()
        emails = data.get("emails") or []

        return {
            "provider": provider,
            "subject": str(data.get("id")),
            "email": data.get("default_email") or (emails[0] if emails else None),
            "full_name": data.get("real_name") or data.get("display_name"),
            "avatar_url": _build_yandex_avatar_url(data.get("default_avatar_id")),
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="OAuth-провайдер не поддерживается",
    )


def get_or_create_oauth_user(profile: dict[str, Any], session: Session) -> User:
    email = profile.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth-провайдер не вернул email пользователя",
        )

    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if user is None:
        user = User(
            email=email,
            hashed_password=None,
            oauth_provider=profile.get("provider"),
            oauth_subject=profile.get("subject"),
            full_name=profile.get("full_name"),
            avatar_url=profile.get("avatar_url"),
        )
        session.add(user)
    else:
        user.oauth_provider = user.oauth_provider or profile.get("provider")
        user.oauth_subject = user.oauth_subject or profile.get("subject")
        user.full_name = profile.get("full_name") or user.full_name
        user.avatar_url = profile.get("avatar_url") or user.avatar_url
        session.add(user)

    session.commit()
    session.refresh(user)
    return user


def create_token_for_user(user: User) -> dict[str, str]:
    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "token_type": "bearer",
    }


def _build_yandex_avatar_url(avatar_id: str | None) -> str | None:
    if not avatar_id:
        return None
    return f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200"
