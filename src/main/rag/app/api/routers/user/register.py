from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db, User
from app.api.services.authentication.authservice import AuthService
from fastapi import APIRouter, Depends
from datetime import timedelta
from app.api.services.user.userservice import UserService

user_router = APIRouter()
@user_router.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    return UserService.register_user(username, password, db)