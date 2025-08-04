from fastapi import APIRouter
from app.api.routers.basket import basket_router
from app.api.routers.llm import llm_router
from app.api.routers.user import user1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(basket_router)
api_router.include_router(llm_router)
api_router.include_router(user1_router)