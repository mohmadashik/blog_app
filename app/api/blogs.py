from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_role
from app.model.blog import BlogStatus
from app.model.user import Role
from app.schemas.blog import BlogCreate, BlogUpdate, BlogOut
from app.crud import blog_crud as blog_crud

router = APIRouter()


# -------------------------
# Public: list approved
# -------------------------
@router.get("/", response_model=list[BlogOut])
def list_public_blogs(db: Session = Depends(get_db)):
    blogs = blog_crud.list_approved(db)
    return blogs


# -------------------------
# Create blog (user)
# -------------------------
@router.post("/", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
def create_blog(
    blog_in: BlogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return blog_crud.create_blog(db, current_user.id, blog_in)


# -------------------------
# Get blog by ID
# -------------------------
@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(404, "Blog not found")
    return blog


# -------------------------
# Update blog (author only, only if still pending)
# -------------------------
@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: int,
    blog_update: BlogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(404, "Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(403, "Not your blog")

    if blog.status != BlogStatus.pending:
        raise HTTPException(400, "Cannot edit approved/rejected blog")

    return blog_crud.update_blog(db, blog, blog_update)


# -------------------------
# Delete blog (author)
# -------------------------
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(404, "Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(403, "Not your blog")

    blog_crud.delete_blog(db, blog)
    return None


# -------------------------
# Admin Approve
# -------------------------
@router.post("/{blog_id}/approve", response_model=BlogOut)
def approve_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_role(Role.admin, Role.approver)),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(404, "Blog not found")

    return blog_crud.approve_blog(db, blog)


# -------------------------
# Admin Reject
# -------------------------
@router.post("/{blog_id}/reject", response_model=BlogOut)
def reject_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_role(Role.admin, Role.approver)),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(404, "Blog not found")

    return blog_crud.reject_blog(db, blog)
