from fastapi import APIRouter

from .login import login_router  # noqa: F401
from .register import user_router  # noqa: F401


user1_router = APIRouter(prefix="/auth", tags=["User"])
user1_router.include_router(user_router, prefix="")
user1_router.include_router(login_router, prefix="")

# Dynamically adding additional routers if they exist
try:
    from .sandbox import sandbox_router  # type: ignore

    user_router.include_router(sandbox_router, prefix="/sandbox")
except ImportError:
    pass
