from typing import Dict, List, Optional
import logging

from app.api.services.bmg.products import get_product_details
from app.api.routers.basket.models import Activity

logger = logging.getLogger("uvicorn")

# TODO: Connect to postgres and change implementation for CRUD
# Simulated database (Replace with an actual database like PostgreSQL, Redis, or MongoDB)
USER_ACTIVITIES: Dict[str, List[Activity]] = {}

class ActivityManager:
    @staticmethod
    async def get_activities(user_id: str, activity_id: Optional[str] = None) -> List[Activity]:
        """
        Retrieves activities for a user. If `activity_id` is provided, returns only that activity.
        """
        activities = USER_ACTIVITIES.get(user_id, [])

        if activity_id:
            filtered_activities = [activity for activity in activities if activity["uuid"] == activity_id]
            if not filtered_activities:
                raise ValueError("Activity not found")
            return filtered_activities

        return activities

    @staticmethod
    async def add_activity(user_id: str, activity_id: str) -> Activity:
        """
        Adds an activity to the user's list.
        """
        if user_id not in USER_ACTIVITIES:
            USER_ACTIVITIES[user_id] = []
        
        # Check if activity already exists
        for existing_activity in USER_ACTIVITIES[user_id]:
            if existing_activity["uuid"] == activity_id:
                raise ValueError("Activity already exists in basket")
            
        activity_details = await get_product_details(activity_id)

        USER_ACTIVITIES[user_id].append(activity_details)

        logger.info(USER_ACTIVITIES)

        return activity_details

    @staticmethod
    async def delete_activity(user_id: str, activity_id: str) -> bool:
        """
        Deletes an activity from the user's list.
        """
        if user_id not in USER_ACTIVITIES:
            raise ValueError("User not found")

        initial_count = len(USER_ACTIVITIES[user_id])
        USER_ACTIVITIES[user_id] = [a for a in USER_ACTIVITIES[user_id] if a["uuid"] != activity_id]

        if len(USER_ACTIVITIES[user_id]) == initial_count:
            raise ValueError("Activity not found")
        
        logger.info(USER_ACTIVITIES)
        
        return True
