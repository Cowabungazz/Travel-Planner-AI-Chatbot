from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db, User
from app.api.services.authentication.authservice import AuthService
from fastapi import APIRouter, Depends
from datetime import timedelta


class UserService:
    @staticmethod
    def register_user(username: str, password: str, db: Session = Depends(get_db)):
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = AuthService.get_password_hash(password)
        new_user = User(username=username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        return {"message": "User registered successfully"}

    @staticmethod
    def login_user(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid username or password")
        access_token = AuthService.create_access_token({"sub": user.id}, timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
