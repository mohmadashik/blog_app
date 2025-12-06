from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum

from app.db import Base


class Role(str, enum.Enum):
    user = "user"
    admin = "admin"
    approver = "approver"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.user)
    is_active = Column(Boolean, default=True)
