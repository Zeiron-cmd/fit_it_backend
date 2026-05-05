from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr


class Message(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str