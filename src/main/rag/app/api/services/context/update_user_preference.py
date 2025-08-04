import logging

from app.db.database import PersistentStorage, User  # Ensure correct imports
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

logger = logging.getLogger(__name__)

class UpdateUserPreference:
    """
    LlamaIndex Tool to update long-term user travel preferences dynamically.
    """

    PREFERENCE_KEYS = {
        "home_airport": ["airport", "home airport", "depart from"],
        "preferred_airline": ["airline", "flight preference", "carrier"],
        "travel_style": ["budget", "luxury", "adventure", "family-friendly"],
        "dietary_preferences": ["vegan", "vegetarian", "halal", "kosher", "gluten-free"],
        "loyalty_programmes": ["loyalty program", "frequent flyer", "membership", "reward points"],
    }

    @staticmethod
    def update_user_preferences(user: User, message: str, db: Session = Depends(get_db)):
        """
        Automatically updates user travel preferences based on chat input.
        """

        extracted_prefs = UpdateUserPreference.extract_preferences_from_message(message)
        
        if not extracted_prefs:
            return "No relevant preferences found in the message."

        for key, new_value in extracted_prefs.items():
            existing_value = UpdateUserPreference.get_existing_preference(user.id, key, db)
            merged_value = UpdateUserPreference.merge_preferences(key, existing_value, new_value)

            # Insert or update the database
            UpdateUserPreference.update_persistent_storage(user.id, key, merged_value, db)
        
        return f"Updated preferences: {extracted_prefs}"

    @staticmethod
    def extract_preferences_from_message(message: str):
        """
        Extracts travel-related preferences from user messages dynamically.
        """
        message_lower = message.lower()
        extracted_prefs = {}

        for key, keywords in UpdateUserPreference.PREFERENCE_KEYS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    extracted_prefs[key] = message
                    break  # Stop checking once a match is found

        return extracted_prefs

    @staticmethod
    def get_existing_preference(user_id: int, key: str, db: Session= Depends(get_db)):
        """
        Retrieves the existing stored preference from the database.
        """
        existing_entry = db.query(PersistentStorage).filter_by(user_id=user_id, key=key).first()
        return existing_entry.value if existing_entry else None

    @staticmethod
    def merge_preferences(key: str, existing_value: str, new_value: str) -> str:
        """
        Generalized merging logic:
        - Replace values if they belong to mutually exclusive categories.
        - Append if the values can coexist.
        - Multi-selection fields (e.g., loyalty_programmes) always append.
        """
        if not existing_value:
            return new_value  # Store directly if no prior data

        # ✅ Detect contradictions dynamically
        contradictory_keywords = [
            ("cheap", "expensive"),
            ("budget", "luxury"),
            ("economy", "first class"),
            ("short trip", "long vacation"),
            ("direct flight", "layover"),
            ("basic", "premium"),
        ]

        for old_value, new_option in contradictory_keywords:
            if old_value in existing_value and new_option in new_value:
                return new_value  # ✅ Replace conflicting value

        existing_values = set(existing_value.split(", "))
        new_values = set(new_value.split(", "))

        # ✅ Replace if a single value exists and differs from the new one (except for multi-selection fields)
        multi_selection_fields = ["loyalty_programmes", "dietary_preferences"]
        
        if len(existing_values) == 1 and key not in multi_selection_fields:
            return new_value  # ✅ Replace single-valued fields (e.g., `preferred_airline`)

        # ✅ Otherwise, merge values (avoiding duplicates)
        merged_values = existing_values.union(new_values)
        return ", ".join(sorted(merged_values))

    @staticmethod
    def update_persistent_storage(user_id: int, key: str, value: str, db: Session= Depends(get_db)):
        """
        Inserts or updates the persistent storage in the database.
        """
        existing_entry = db.query(PersistentStorage).filter_by(user_id=user_id, key=key).first()

        if existing_entry:
            existing_entry.value = value  # Update
        else:
            new_entry = PersistentStorage(user_id=user_id, key=key, value=value)
            db.add(new_entry)

        db.commit()
        logger.info(f"Updated {key} for user {user_id}: {value}")

