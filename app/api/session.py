from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.model.user import User
from app.schemas.draft import DraftSave, DraftOut
from app.crud import draft_crud 

router = APIRouter()


@router.get("/draft", response_model=DraftOut)
def get_draft(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = draft_crud.get_draft_for_user(db, current_user.id)
    if not draft:
        # empty draft object for new users
        return DraftOut(title=None, content=None, updated_at=None)
    return draft


@router.post("/draft", response_model=DraftOut)
def save_draft(
    draft_in: DraftSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = draft_crud.save_or_update_draft(db, current_user.id, draft_in)
    return draft
