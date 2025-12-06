from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    approver = "approver"


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8, max_length=256)


class UserOut(UserBase):
    id: int
    role: RoleEnum

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
