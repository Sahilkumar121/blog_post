from fastapi import APIRouter

from .post import route as post_router
from .user import route as user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["USER"])
api_router.include_router(post_router, prefix="/post", tags=["POST"])
