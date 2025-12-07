from sqlalchemy.orm import Session

from app.model.draft import Draft
from app.schemas.draft import DraftSave


def get_draft_for_user(db: Session, user_id: int) -> Draft | None:
    return db.query(Draft).filter(Draft.user_id == user_id).first()


def save_or_update_draft(
    db: Session,
    user_id: int,
    data: DraftSave,
) -> Draft:
    draft = get_draft_for_user(db, user_id)
    if draft is None:
        draft = Draft(
            user_id=user_id,
            title=data.title,
            content=data.content,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        return draft

    draft.title = data.title
    draft.content = data.content

    db.commit()
    db.refresh(draft)
    return draft
