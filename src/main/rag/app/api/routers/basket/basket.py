import logging

from fastapi import APIRouter, HTTPException, status

from app.api.routers.basket.models import Basket
from app.api.routers.llm.models import (
    ChatData,
)
from app.api.services.basket.basket_manager import BasketManager

activity_router = r = APIRouter()

logger = logging.getLogger("uvicorn")


# CURRENTLY NOT USED

@r.post("")
async def update_basket(
    data: ChatData,
    basket: Basket,
):
    try:
        message = data.get_last_message_content()
        chat_history = data.get_history_messages()
        updated_basket = await BasketManager.update_basket(
            message,
            chat_history, 
            basket,
        )
        return updated_basket
    except Exception as e:
        logger.exception("Error updating basket", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating basket: {e}",
        ) from e