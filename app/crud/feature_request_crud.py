from sqlalchemy.orm import Session

from app.model.feature_request import FeatureRequest, FeatureRequestStatus
from app.schemas.feature_request import FeatureRequestCreate, FeatureRequestUpdateStatus


def create_feature_request(
    db: Session,
    user_id: int,
    fr_in: FeatureRequestCreate,
) -> FeatureRequest:
    fr = FeatureRequest(
        title=fr_in.title,
        description=fr_in.description,
        priority=fr_in.priority,
        user_id=user_id,
        status=FeatureRequestStatus.pending,
    )
    db.add(fr)
    db.commit()
    db.refresh(fr)
    return fr


def list_feature_requests(db: Session) -> list[FeatureRequest]:
    return (
        db.query(FeatureRequest)
        .order_by(FeatureRequest.created_at.desc())
        .all()
    )


def get_feature_request(db: Session, fr_id: int) -> FeatureRequest | None:
    return db.query(FeatureRequest).filter(FeatureRequest.id == fr_id).first()


def update_feature_request_status(
    db: Session,
    fr: FeatureRequest,
    changes: FeatureRequestUpdateStatus,
) -> FeatureRequest:
    fr.status = FeatureRequestStatus(changes.status.value)
    fr.rating = changes.rating
    db.commit()
    db.refresh(fr)
    return fr
