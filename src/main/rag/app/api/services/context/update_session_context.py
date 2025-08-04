from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.database import TemporaryStorage, ChatSession  # Ensure correct import paths
import logging

logger = logging.getLogger(__name__)

class UpdateSessionContext:
    """
    LlamaIndex Tool to update session-specific temporary storage dynamically.
    """

    TEMP_STORAGE_KEYS = {
        "trip_origin": ["departing from", "trip origin", "leaving from"],
        "trip_destination": ["going to", "traveling to", "trip destination"],
        "date_range": ["trip dates", "departure on", "return on"],
        "max_budget": ["budget limit", "maximum spending", "not exceeding"],
        "number_of_travellers": ["traveling with", "group size", "number of people"],
        "trip_purpose": ["business trip", "vacation", "honeymoon"],
        "current_booking_stage": ["now booking", "step", "choosing"],
        "selected_flight_id": ["flight option", "choosing flight"],
        "selected_hotel_id": ["hotel option", "choosing hotel"],
        "selected_car_rental_id": ["car rental option", "choosing car"],
        "selected_activities": ["booking activities", "things to do"],
        "currency_preference": ["convert prices to", "currency preference"],
        "language_preference": ["language setting", "chat in"],
        "time_zone_preference": ["use time zone", "show times in"],
        "chatting_preference": ["summarize", "detailed response"]
    }

    @staticmethod
    def update_session_context(session: ChatSession, message: str, db: Session= Depends(get_db)):
        """
        Automatically updates session-specific temporary storage based on chat input.
        """

        extracted_prefs = UpdateSessionContext.extract_preferences_from_message(message)
        
        if not extracted_prefs:
            return "No relevant temporary storage updates found in the message."

        for key, new_value in extracted_prefs.items():
            existing_value = UpdateSessionContext.get_existing_value(session.id, key, db)
            merged_value = UpdateSessionContext.merge_values(key, existing_value, new_value)

            # Insert or update the database
            UpdateSessionContext.update_storage(session.id, key, merged_value, db)
        
        return f"Updated temporary storage: {extracted_prefs}"


    @staticmethod
    def extract_preferences_from_message(message: str):
        """
        Extracts relevant temporary storage values from user messages dynamically.
        """
        message_lower = message.lower()
        extracted_prefs = {}

        for key, keywords in UpdateSessionContext.TEMP_STORAGE_KEYS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    extracted_prefs[key] = message
                    break  # Stop checking once a match is found

        return extracted_prefs

    @staticmethod
    def get_existing_value(session_id: int, key: str, db: Session= Depends(get_db)):
        """
        Retrieves the existing stored value from temporary storage.
        """
        existing_entry = db.query(TemporaryStorage).filter_by(session_id=session_id, key=key).first()
        return existing_entry.value if existing_entry else None

    @staticmethod
    def merge_values(key: str, existing_value: str, new_value: str) -> str:
        """
        Generalized merging logic:
        - Replace values if they belong to mutually exclusive categories.
        - Append if the values can coexist.
        - Multi-selection fields (e.g., `selected_activities`) always append.
        """
        if not existing_value:
            return new_value  # ✅ Store directly if no prior data

        # **Auto-detect contradictions based on opposites**
        contradictory_keywords = [
            ("cheap", "expensive"),
            ("budget", "luxury"),
            ("economy", "first class"),
            ("short trip", "long vacation"),
            ("direct flight", "layover"),
            ("basic", "premium"),
        ]

        # **Check if existing value contains a contradiction**
        for old_value, new_option in contradictory_keywords:
            if old_value in existing_value and new_option in new_value:
                return new_value  # ✅ Replace conflicting value

        existing_values = set(existing_value.split(", "))
        new_values = set(new_value.split(", "))

        # **If key is a single-value field, replace the existing value**
        single_value_fields = ["trip_origin", "trip_destination", "date_range", "max_budget", "trip_purpose", 
                            "current_booking_stage", "currency_preference", "language_preference", "time_zone_preference"]
        
        if key in single_value_fields:
            return new_value  # ✅ Replace single-valued fields

        # **Otherwise, merge values (avoiding duplicates)**
        merged_values = existing_values.union(new_values)
        return ", ".join(sorted(merged_values))



    @staticmethod
    def update_storage(session_id: int, key: str, value: str, db: Session= Depends(get_db)):
        """
        Inserts or updates temporary storage in the database.
        """
        existing_entry = db.query(TemporaryStorage).filter_by(session_id=session_id, key=key).first()

        if existing_entry:
            existing_entry.value = value  # Update
        else:
            new_entry = TemporaryStorage(session_id=session_id, key=key, value=value)
            db.add(new_entry)

        db.commit()
        logger.info(f"Updated temporary storage '{key}' for session {session_id}: {value}")

