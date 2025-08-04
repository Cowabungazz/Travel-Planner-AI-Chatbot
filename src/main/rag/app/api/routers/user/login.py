
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db, User
from app.api.services.authentication.authservice import AuthService
from fastapi import APIRouter, Depends
from datetime import timedelta
from app.api.services.user.userservice import UserService


login_router = APIRouter()

@login_router.post("/token")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return UserService.login_user(form_data, db)
