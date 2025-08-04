import logging
from app.db.pinecone import store_embeddings

logger = logging.getLogger(__name__)

class UpdateUserEmbeddings:
    """
    LlamaIndex Tool to update and retrieve user embeddings dynamically using Pinecone.
    """

    @staticmethod
    def update_user_embeddings(user_id: str, session_id: str, message: str):
        """
        Updates the user's persistent and temporary embeddings in Pinecone based on the chat input.
        - Persistent vectors -> Indexed as "{user_id}-persistent-{i}"
        - Temporary vectors -> Indexed as "{user_id}-{session_id}-temp-{i}"
        """
        try:
            store_embeddings(user_id, session_id, message)
            return f"Successfully updated embeddings for user {user_id} in session {session_id}."
        except Exception as e:
            logger.error(f"Error updating embeddings for user {user_id}: {str(e)}")
            return f"Failed to update embeddings due to an error: {str(e)}"


