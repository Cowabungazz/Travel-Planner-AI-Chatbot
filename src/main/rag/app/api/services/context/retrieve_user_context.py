from fastapi import Depends
from app.db.database import get_db
from app.db.database import PersistentStorage, TemporaryStorage
from app.db.pinecone import search_embeddings
import logging
from sqlalchemy.orm import Session
# from llama_index.core.schema import ChatMessage
from llama_index.core.llms import ChatMessage


logger = logging.getLogger(__name__)

class RetrieveUserContext:
    """
    LlamaIndex Tool to retrieve user context dynamically.
    - Fetches persistent storage (long-term user data).
    - Fetches temporary storage (session-specific data).
    - Searches embeddings for relevant context.
    - Passes all retrieved data as LLM context.
    """

    @staticmethod
    def retrieve_user_context(user_id: str, session_id: str, query: str, db: Session = Depends(get_db)) -> list:
        """
        Retrieves:
        - Persistent storage for the user
        - Temporary storage for the session
        - Relevant embeddings based on query
        Then, formats everything as a list of ChatMessage objects for the LLM.
        """

        # Step 1: Retrieve Persistent Storage (Long-term data)
        persistent_entries = db.query(PersistentStorage).filter_by(user_id=user_id).all()
        persistent_data = {entry.key: entry.value for entry in persistent_entries}

        # Step 2: Retrieve Temporary Storage (Session-specific data)
        temporary_entries = db.query(TemporaryStorage).filter_by(session_id=session_id).all()
        temporary_data = {entry.key: entry.value for entry in temporary_entries}

        # Step 3: Search Embeddings for Contextual Information
        embedding_results = search_embeddings(user_id, session_id, query, k=3)

        # Step 4: Format Context as a List of ChatMessage Objects
        chat_messages = []

        # Add persistent storage messages
        if persistent_data:
            chat_messages.append(ChatMessage(role="system", content="--- Persistent Storage ---"))
            for key, value in persistent_data.items():
                chat_messages.append(ChatMessage(role="system", content=f"{key}: {value}"))

        # Add temporary storage messages
        if temporary_data:
            chat_messages.append(ChatMessage(role="system", content="--- Temporary Storage ---"))
            for key, value in temporary_data.items():
                chat_messages.append(ChatMessage(role="system", content=f"{key}: {value}"))

        # Add retrieved embeddings messages
        if embedding_results:
            chat_messages.append(ChatMessage(role="system", content="--- Retrieved Embeddings ---"))
            for i, emb in enumerate(embedding_results):
                chat_messages.append(ChatMessage(role="system", content=f"Embedding {i+1}: {emb}"))

        # If no data is found, provide a fallback message
        if not chat_messages:
            chat_messages.append(ChatMessage(role="system", content="No user context available."))

        logger.info(f"Retrieved context for user {user_id}, session {session_id}: {chat_messages}")

        return chat_messages  # ✅ Returning as a list of ChatMessage objects

    
