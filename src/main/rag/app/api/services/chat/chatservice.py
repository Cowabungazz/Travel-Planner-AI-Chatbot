from fastapi import HTTPException, BackgroundTasks, Request, Depends, APIRouter
from sqlalchemy.orm import Session
from app.db.database import get_db, ChatSession, Message as DBMessage
from app.engine.engine import get_chat_engine
from app.engine.query_filter import generate_filters
from app.api.routers.llm.models import ChatData
from app.api.routers.llm.vercel_response import VercelStreamResponse
from app.api.services.authentication.authservice import AuthService
from pydantic import BaseModel
from typing import List
from app.db.database import User, Response
import logging
from app.db.database import Message
from app.api.routers.llm.events import EventCallbackHandler
from app.api.services.context.retrieve_user_context import RetrieveUserContext
from app.api.services.context.update_session_context import UpdateSessionContext
from app.api.services.context.update_user_embeddings import UpdateUserEmbeddings
from app.api.services.context.update_user_preference import UpdateUserPreference

logger = logging.getLogger("uvicorn")

class StreamingAgentChatResponse:
    def __init__(self, response_text):
        self.response_text = response_text

    def __aiter__(self):
        return self._stream_response()

    async def _stream_response(self):
        for chunk in self.response_text.split():  # ✅ Simulates streaming chunks
            yield chunk


class ChatService:
    @staticmethod
    def create_chat_session(user, db: Session):
        new_session = ChatSession(user_id=user.id)
        db.add(new_session)
        db.commit()
        return {"session_id": new_session.id}
    
    @staticmethod
    def get_user_sessions(user, db: Session):
        """Fetch all chat sessions for a given user"""
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).all()
        return {"sessions": [{"session_id": session.id, "created_at": session.created_at} for session in sessions]}

    @staticmethod
    async def chat(request: Request, data: ChatData, background_tasks: BackgroundTasks, user, db: Session):
        session = db.query(ChatSession).filter(
            ChatSession.id == data.session_id, ChatSession.user_id == user.id
        ).first()

        #call update_session_context function 
        #call update_user_embeddings function 
        #call update_user_preference function

        if not session:
            raise HTTPException(status_code=400, detail="Invalid session ID")

        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages(db)  # Query DB for history #NO longer used

        # 🔹 Step 1: Retrieve the existing user context
        user_context = RetrieveUserContext.retrieve_user_context(user.id, session.id, last_message_content, db)

        # 🔹 Step 2: Update session context with new information
        UpdateSessionContext.update_session_context(session, last_message_content, db)

        # 🔹 Step 3: Update user embeddings in Pinecone
        UpdateUserEmbeddings.update_user_embeddings(user.id, session.id, last_message_content)

        # 🔹 Step 4: Update user preferences
        UpdateUserPreference.update_user_preferences(user, last_message_content, db)

        filters = generate_filters(data.get_chat_document_ids())  # Query DB for doc IDs
        chat_engine = get_chat_engine(filters=filters)
        response = await chat_engine.astream_chat(last_message_content, user_context)
        #print(dir(response)) #see what methods are available

        #Store user message in DB
        new_message = Message(
            session_id=session.id, role="user", content=last_message_content
        )
        db.add(new_message)
        db.commit()
        event_handler = EventCallbackHandler()

        new_response = Response(
            session_id=session.id,
            message_id=new_message.id, 
            content=response.response
        )
        db.add(new_response)
        db.commit()

        return VercelStreamResponse(request, event_handler, response, data, background_tasks)

    @staticmethod
    def get_chat_messages(user, session_id: int, db: Session):
        """Fetch all messages for a given chat session"""
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id, ChatSession.user_id == user.id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
        return {
            "session_id": session_id,
            "messages": [
                {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": msg.created_at}
                for msg in messages
            ],
        }