from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthProviderRead(BaseModel):
    provider: str
    enabled: bool

class TokenValidateResponse(BaseModel):
    valid: bool
    user_id: str
    email: str
