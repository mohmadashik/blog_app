from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_role, get_user_by_username
from app.model.blog import BlogStatus
from app.model.user import Role, User
from app.model.blog import BlogStatus
from app.schemas.blog import BlogCreate, BlogUpdate, BlogOut
from app.crud import blog_crud as blog_crud
from app.services.notifications import notifier
from app.services.chat import blog_chat_manager
from app.core.security import decode_token


router = APIRouter()


# -------------------------
# Admin / Approver: list pending blogs
# -------------------------
@router.get("/pending", response_model=list[BlogOut])
def list_pending_blogs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(Role.admin, Role.approver)),
):
    """
    List all blogs with status 'pending'.
    Only admin or approver can see this.
    """
    return blog_crud.list_pending(db)



# -------------------------
# Public: list all approved blogs
# -------------------------
@router.get("/", response_model=list[BlogOut])
def list_public_blogs(db: Session = Depends(get_db)):
    blogs = blog_crud.list_approved(db)
    return blogs



# # -------------------------
# # Authenticated: create blog (status = pending)
# # -------------------------
# @router.post(
#     "/",
#     response_model=BlogOut,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_blog(
#     blog_in: BlogCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return blog_crud.create_blog(db, current_user.id, blog_in)


# -------------------------
# Authenticated: create blog (status = pending) with SSE notification
# -------------------------
@router.post(
    "/",
    response_model=BlogOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_blog(
    blog_in: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = blog_crud.create_blog(db, current_user.id, blog_in)

    # Publish SSE event for new pending blog
    if blog.status == BlogStatus.pending:
        await notifier.publish(
            {
                "type": "blog_pending",
                "blog_id": blog.id,
                "title": blog.title,
                "author_id": blog.author_id,
                "created_at": blog.created_at.isoformat(),
            }
        )

    return blog


# -------------------------
# Public: get a single blog
# Only approved are visible publicly
# -------------------------
@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog or blog.status != BlogStatus.approved:
        # Spec says: only approved articles are public
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


# -------------------------
# Author: update blog if still pending
# -------------------------
@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: int,
    blog_update: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your blog")

    if blog.status != BlogStatus.pending:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit a blog that is already approved or rejected.",
        )

    return blog_crud.update_blog(db, blog, blog_update)

# -------------------------
# Author: delete blog
# -------------------------
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your blog")

    blog_crud.delete_blog(db, blog)
    return None



# -------------------------
# Admin / Approver: approve
# -------------------------
@router.post("/{blog_id}/approve", response_model=BlogOut)
def approve_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(Role.admin, Role.approver)),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog_crud.approve_blog(db, blog)


# -------------------------
# Admin / Approver: reject
# -------------------------
@router.post("/{blog_id}/reject", response_model=BlogOut)
def reject_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(Role.admin, Role.approver)),
):
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog_crud.reject_blog(db, blog)

# -------------------------
# WebSocket: blog chat
# -------------------------

@router.websocket("/{blog_id}/ws")
async def blog_chat_ws(
    websocket: WebSocket,
    blog_id: int,
    db: Session = Depends(get_db),
):
    """
    WebSocket chat for a specific blog.

    Auth:
    - expects ?token=<JWT> query parameter
    - token must be a valid user JWT
    """

    # ---- Auth via token query param ----
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # Policy Violation
        return

    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            await websocket.close(code=1008)
            return
        user = get_user_by_username(db, username=username)
        if not user or not user.is_active:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    # ---- Ensure blog exists ----
    blog = blog_crud.get_blog(db, blog_id)
    if not blog:
        await websocket.close(code=1008)
        return

    # ---- Connect ----
    await blog_chat_manager.connect(blog_id, websocket)

    try:
        while True:
            text = await websocket.receive_text()
            # You can format messages however you like
            message = f"{user.username}: {text}"
            await blog_chat_manager.broadcast(blog_id, message)
    except WebSocketDisconnect:
        blog_chat_manager.disconnect(blog_id, websocket)
    except Exception:
        blog_chat_manager.disconnect(blog_id, websocket)
        try:
            await websocket.close()
        except Exception:
            pass


