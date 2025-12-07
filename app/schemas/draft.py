from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DraftBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DraftSave(DraftBase):
    pass


class DraftOut(DraftBase):
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
