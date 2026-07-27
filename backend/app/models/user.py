from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(20), default="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())