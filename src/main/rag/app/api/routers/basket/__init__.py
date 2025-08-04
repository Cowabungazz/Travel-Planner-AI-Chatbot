from fastapi import APIRouter

from .activity import activity_router

basket_router = APIRouter(prefix="/basket", tags=["Basket"])
basket_router.include_router(activity_router, prefix="/activity")