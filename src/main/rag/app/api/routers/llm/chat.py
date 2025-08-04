import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from llama_index.core.llms import MessageRole

from app.api.routers.llm.events import EventCallbackHandler
from app.api.routers.llm.models import (
    ChatData,
    Message,
    Result,
    SourceNodes,
)
from app.api.routers.llm.vercel_response import VercelStreamResponse
from app.engine.engine import get_chat_engine
from app.engine.query_filter import generate_filters
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
from app.db.database import User
import logging
from app.db.database import Message
from app.api.routers.llm.events import EventCallbackHandler
from app.api.services.chat.chatservice import ChatService


chat_router = r = APIRouter()

logger = logging.getLogger("uvicorn")


# streaming endpoint - delete if not needed
@r.post("")
async def chat(
    request: Request,
    data: ChatData,
    background_tasks: BackgroundTasks,
):
    try:
        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        params = data.data or {}
        logger.info(
            f"Creating chat engine with filters: {str(filters)}",
        )
        event_handler = EventCallbackHandler()
        chat_engine = get_chat_engine(
            filters=filters, params=params, event_handlers=[event_handler]
        )
        response = chat_engine.astream_chat(last_message_content, messages)

        return VercelStreamResponse(
            request, event_handler, response, data, background_tasks
        )
    except Exception as e:
        logger.exception("Error in chat engine", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e


# non-streaming endpoint - delete if not needed
@r.post("/request")
async def chat_request(
    data: ChatData,
) -> Result:
    last_message_content = data.get_last_message_content()
    messages = data.get_history_messages()

    doc_ids = data.get_chat_document_ids()
    filters = generate_filters(doc_ids)
    params = data.data or {}
    logger.info(
        f"Creating chat engine with filters: {str(filters)}",
    )

    chat_engine = get_chat_engine(filters=filters, params=params)

    response = await chat_engine.achat(last_message_content, messages)
    return Result(
        result=Message(role=MessageRole.ASSISTANT, content=response.response),
        nodes=SourceNodes.from_source_nodes(response.source_nodes),
    )



chat_router.post("/new_session")(lambda user=Depends(AuthService.get_current_user), db=Depends(get_db): ChatService.create_chat_session(user, db))
# chat_router.post("/chat")(lambda request, data, background_tasks, user=Depends(AuthService.get_current_user), db=Depends(get_db): ChatService.chat(request, data, background_tasks, user, db))

@chat_router.post("/chat")
async def chat_endpoint(
    request: Request,
    data: ChatData,  # ✅ Now FastAPI expects JSON body, not query params
    background_tasks: BackgroundTasks,
    user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):

    return await ChatService.chat(request, data, background_tasks, user, db)


@chat_router.get("/sessions")
def get_sessions(user: User = Depends(AuthService.get_current_user), db: Session = Depends(get_db)):
    return ChatService.get_user_sessions(user, db)


@chat_router.get("/messages/{session_id}")
def get_messages(
    session_id: int,
    user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    return ChatService.get_chat_messages(user, session_id, db)