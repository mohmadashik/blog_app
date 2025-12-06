from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime


class BlogStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class BlogBase(BaseModel):
    title: str
    content: str


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class BlogOut(BlogBase):
    id: int
    status: BlogStatusEnum
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
