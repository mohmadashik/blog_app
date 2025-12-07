from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_role
from app.model.user import User, Role
from app.schemas import (
    FeatureRequestCreate,
    FeatureRequestUpdateStatus,
    FeatureRequestOut,
)
from app.crud import feature_request_crud as fr_crud

router = APIRouter()


# -------------------------
# List feature requests (User)
# -------------------------
@router.get("/", response_model=list[FeatureRequestOut])
def list_feature_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # spec says auth: User; we don't filter by user here, but we could if needed
    return fr_crud.list_feature_requests(db)


# -------------------------
# Create feature request (User)
# -------------------------
@router.post(
    "/",
    response_model=FeatureRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_feature_request(
    fr_in: FeatureRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return fr_crud.create_feature_request(db, current_user.id, fr_in)


# -------------------------
# Update status (Admin / Approver)
# -------------------------
@router.patch("/{fr_id}", response_model=FeatureRequestOut)
def update_feature_request_status(
    fr_id: int,
    changes: FeatureRequestUpdateStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(Role.admin, Role.approver)),
):
    fr = fr_crud.get_feature_request(db, fr_id)
    if not fr:
        raise HTTPException(status_code=404, detail="Feature request not found")

    return fr_crud.update_feature_request_status(db, fr, changes)
