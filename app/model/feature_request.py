from datetime import datetime
import enum

from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base


class FeatureRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class FeatureRequest(Base):
    __tablename__ = "feature_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    status = Column(
        Enum(FeatureRequestStatus),
        default=FeatureRequestStatus.pending,
        nullable=False,
        index=True,
    )

    # simple integer priority (1–5, etc.)
    priority = Column(Integer, default=1, nullable=False)
    # optional rating (e.g., internal ranking)
    rating = Column(Integer, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User")
