import logging
from fastapi import APIRouter, HTTPException, status

from app.api.services.basket.activity import ActivityManager

activity_router = r = APIRouter()

logger = logging.getLogger("uvicorn")

@r.get("")
async def get_activities(user_id: str, activity_id: str = None):
    """
    Retrieves all activities for a user. If `activity_id` is provided, returns only that activity.
    """
    try:
        activities = await ActivityManager.get_activities(user_id, activity_id)
        return {"activities": activities}
    except ValueError as e:
        logger.error(f"Error getting activities: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while getting activities", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@r.post("")
async def add_activity(user_id: str, activity_id: str):
    """
    Adds a new activity to the user's basket.
    """
    try:
        added_activity = await ActivityManager.add_activity(user_id, activity_id)
        return {"message": "Activity added successfully", "activity": added_activity}
    except ValueError as e:
        logger.error(f"Error adding activity: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while adding activity", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@r.delete("")
async def delete_activity(user_id: str, activity_id: str):
    """
    Deletes an activity from the user's basket.
    """
    try:
        success = await ActivityManager.delete_activity(user_id, activity_id)
        return {"message": "Activity deleted successfully"} if success else {"message": "No changes made"}
    except ValueError as e:
        logger.error(f"Error deleting activity: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while deleting activity", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")