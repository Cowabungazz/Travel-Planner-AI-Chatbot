from fastapi import APIRouter

from .chat import chat_router  # noqa: F401
from .chat_config import config_router  # noqa: F401
from .upload import file_upload_router  # noqa: F401
from .query import query_router  # noqa: F401

llm_router = APIRouter(prefix="/llm", tags=["LLM"])
llm_router.include_router(chat_router, prefix="/chat")
llm_router.include_router(config_router, prefix="/chat/config")
llm_router.include_router(file_upload_router, prefix="/chat/upload")
llm_router.include_router(query_router, prefix="/query")

# Dynamically adding additional routers if they exist
try:
    from .sandbox import sandbox_router  # type: ignore

    llm_router.include_router(sandbox_router, prefix="/sandbox")
except ImportError:
    pass
