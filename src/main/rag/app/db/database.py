import os
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# # User Model
# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     chat_sessions = relationship("ChatSession", back_populates="user")

# # Chat Session Model
# class ChatSession(Base):
#     __tablename__ = "chat_sessions"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     user = relationship("User", back_populates="chat_sessions")
#     messages = relationship("Message", back_populates="session")

# # Message Model
# class Message(Base):
#     __tablename__ = "messages"

#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
#     role = Column(String, nullable=False)  # "user" or "assistant"
#     content = Column(String, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     session = relationship("ChatSession", back_populates="messages")

# Updated User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    chat_sessions = relationship("ChatSession", back_populates="user")
    persistent_storage = relationship("PersistentStorage", back_populates="user")

# Updated Chat Session Model
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session")
    responses = relationship("Response", back_populates="session")
    temporary_storage = relationship("TemporaryStorage", back_populates="session")

# Updated Message Model
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
    responses = relationship("Response", back_populates="message")


# Response Model
class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="responses")
    message = relationship("Message", back_populates="responses")

# Persistent Storage Model
class PersistentStorage(Base):
    __tablename__ = "persistent_storage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="persistent_storage")

# Temporary Storage Model
class TemporaryStorage(Base):
    __tablename__ = "temporary_storage"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="temporary_storage")


# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
