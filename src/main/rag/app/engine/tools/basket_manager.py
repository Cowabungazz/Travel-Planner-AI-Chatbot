from typing import Dict, List
import logging

from llama_index.core.tools import FunctionTool
from app.api.routers.basket.models import Basket

logger = logging.getLogger(__name__)


# CURRENTLY NOT USED

# Simulated database to store user baskets
USER_BASKETS: Dict[str, Basket] = {}

class BasketManager:

    @classmethod
    def manage_basket(
        cls, 
        user_id: str, 
        #session_id: str, 
        item: dict, 
        action: str, 
        category: str, 
    ) -> None:
        """
        Use this tool to add, remove, or update a trip, flight, accommodation, or activity in the user's basket.

        Args:
            user_id (str): The user's ID.
            session_id (str): The session's ID.
            item (dict): The item to add, remove, or update.
            action (str): The action to perform ('add', 'remove', 'update').
            category (str): The category of the item ('destinations', 'flights', 'accommodation', 'itinerary').

        Returns:
            Basket: The updated basket.
        """

        basket = USER_BASKETS.get(user_id)

        # Ensure the category exists in the basket
        category_items: List[dict] = getattr(basket, category, [])

        # Perform the action
        if action == "add":
            category_items.append(item)
        elif action == "remove":
            category_items = [i for i in category_items if i.get("id") != item.get("id")]
        elif action == "update":
            for i in category_items:
                if i.get("id") == item.get("id"):
                    i.update(item)
        else:
            raise ValueError("Invalid action. Use 'add', 'remove', or 'update'.")

        # Update the basket category
        setattr(basket, category, category_items)
        USER_BASKETS[user_id] = basket

        logger.info(f"User {user_id} basket updated: {basket}")

        return basket
    
def get_tools(**kwargs):
    return [FunctionTool.from_defaults(BasketManager.manage_basket)]