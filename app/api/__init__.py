from fastapi import APIRouter

from app.api import auth, blogs,notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
