from pydantic import BaseModel, EmailStr
from app.domains.auth.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    nickname: str | None = None
    role: UserRole