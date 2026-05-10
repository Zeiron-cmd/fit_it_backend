from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)

    # Password can be empty for users created through OAuth providers.
    hashed_password: Optional[str] = None

    oauth_provider: Optional[str] = Field(default=None, index=True)
    oauth_subject: Optional[str] = Field(default=None, index=True)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    created_at: datetime = Field(default_factory=utc_now)
