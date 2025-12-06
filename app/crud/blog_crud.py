from sqlalchemy.orm import Session

from app.model.blog import Blog, BlogStatus
from app.schemas.blog import BlogCreate, BlogUpdate


def create_blog(db: Session, user_id: int, blog_in: BlogCreate):
    blog = Blog(
        title=blog_in.title,
        content=blog_in.content,
        author_id=user_id,
        status=BlogStatus.pending,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def get_blog(db: Session, blog_id: int):
    return db.query(Blog).filter(Blog.id == blog_id).first()


def list_approved(db: Session) -> list[Blog]:
    return (
        db.query(Blog)
        .filter(Blog.status == BlogStatus.approved)
        .order_by(Blog.created_at.desc())
        .all()
    )


def update_blog(db: Session, blog: Blog, updates: BlogUpdate) -> Blog:
    if updates.title is not None:
        blog.title = updates.title
    if updates.content is not None:
        blog.content = updates.content

    db.commit()
    db.refresh(blog)
    return blog


def delete_blog(db: Session, blog: Blog) -> None:
    db.delete(blog)
    db.commit()


def approve_blog(db: Session, blog: Blog) -> Blog:
    blog.status = BlogStatus.approved
    db.commit()
    db.refresh(blog)
    return blog


def reject_blog(db: Session, blog: Blog) -> Blog:
    blog.status = BlogStatus.rejected
    db.commit()
    db.refresh(blog)
    return blog

def list_pending(db: Session) -> list[Blog]:
    return (
        db.query(Blog)
        .filter(Blog.status == BlogStatus.pending)
        .order_by(Blog.created_at.desc())
        .all()
    )

def list_rejected(db: Session) -> list[Blog]:
    return (
        db.query(Blog)
        .filter(Blog.status == BlogStatus.rejected)
        .order_by(Blog.created_at.desc())
        .all()
    )
