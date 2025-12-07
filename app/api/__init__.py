from fastapi import APIRouter

from app.api import auth, blogs,notifications, feature_requests,session

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(feature_requests.router, prefix="/feature-requests", tags=["feature-requests"])
api_router.include_router(session.router, prefix="/session", tags=["session"])