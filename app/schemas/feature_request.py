from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class FeatureRequestStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class FeatureRequestBase(BaseModel):
    title: str
    description: str
    priority: int = 1


class FeatureRequestCreate(FeatureRequestBase):
    pass


class FeatureRequestUpdateStatus(BaseModel):
    status: FeatureRequestStatusEnum
    rating: Optional[int] = None


class FeatureRequestOut(FeatureRequestBase):
    id: int
    status: FeatureRequestStatusEnum
    rating: Optional[int]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
