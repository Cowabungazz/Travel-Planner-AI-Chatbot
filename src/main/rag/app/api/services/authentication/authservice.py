from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.database import get_db, User

import logging
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")  # ✅ Define this


logger = logging.getLogger("uvicorn")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return password_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return password_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        # ✅ Ensure the `sub` field is always a string
        if "sub" in to_encode:
            to_encode["sub"] = str(to_encode["sub"])

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        try:
            logger.info(f"Decoding token: {token}")  # ✅ Add logging
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user_id: str = payload.get("sub")  # ✅ Read as a string

            if not user_id:
                logger.error("Token is missing user ID")
                raise HTTPException(status_code=401, detail="Invalid authentication")

            # ✅ Ensure user_id is converted to an integer for database query
            user = db.query(User).filter(User.id == int(user_id)).first()

            if user is None:
                logger.error(f"User with ID {user_id} not found")
                raise HTTPException(status_code=401, detail="User not found")

            return user
        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

